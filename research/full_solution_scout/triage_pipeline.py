"""Validate and merge target-acquisition triage records.

The script deliberately performs no web access.  It checks that human/agent
judgments cover the intended deterministic pool slice and that their machine-
checkable fields are internally consistent.

Example:
  python triage_pipeline.py validate --pool pool-2026-08-02.json \
    --scope formalized-open --output triage-2026-08-02/formalized-merged.json \
    triage-2026-08-02/range_*.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCORE_FIELDS = (
    "leverage",
    "uncertainty",
    "reachability",
    "collision",
    "verification",
)
COMMON_FIELDS = (
    "number",
    "ask",
    *SCORE_FIELDS,
    "total",
    "verdict",
    "probe_sketch",
    "stale_suspicion",
    "stale_why",
)
LIVE_FIELDS = (
    "status_flag",
    "checked_utc",
    "source_urls",
    "recognition_path",
)
VERDICTS = {"drop", "watch", "probe", "siege"}
STATUS_FLAGS = {
    "open_no_collision_found",
    "possible_collision",
    "known_partial",
    "known_full_solution",
    "unclear",
}


def is_probe_grade(row: dict[str, Any]) -> bool:
    """Return whether a row earns a bounded week-horizon probe.

    A high aggregate score cannot compensate for a believed-true conjecture
    or a witness region outside the campaign's one-week reach.  These two
    gates encode the target-acquisition review's central correction.
    """
    return (
        row["total"] >= 8
        and row["leverage"] >= 2
        and row["uncertainty"] >= 2
        and row["reachability"] >= 1
        and row["verification"] >= 1
        and row.get("recognition_path", True)
        and row.get("status_flag") != "known_full_solution"
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_numbers(pool_rows: list[dict], scope: str) -> set[int]:
    if scope == "all":
        chosen = pool_rows
    elif scope == "formalized-open":
        chosen = [row for row in pool_rows if row.get("research_open")]
    elif scope == "non-formalized-open":
        chosen = [row for row in pool_rows if not row.get("research_open")]
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(scope)
    return {int(row["number"]) for row in chosen}


def validate_iso_utc(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(0)


def validate_row(row: Any, source: Path, require_live: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(row, dict):
        return [f"{source}: row is not an object"]
    number = row.get("number", "?")
    for field in COMMON_FIELDS:
        if field not in row:
            errors.append(f"{source}: #{number}: missing {field}")
    if errors:
        return errors
    if not isinstance(number, int) or isinstance(number, bool):
        errors.append(f"{source}: invalid problem number {number!r}")
    for field in SCORE_FIELDS:
        value = row[field]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
            errors.append(f"{source}: #{number}: {field} must be an integer 0..3")
    if all(isinstance(row[f], int) and not isinstance(row[f], bool) for f in SCORE_FIELDS):
        wanted = sum(row[f] for f in SCORE_FIELDS)
        if row["total"] != wanted:
            errors.append(f"{source}: #{number}: total {row['total']} != {wanted}")
    if row["verdict"] not in VERDICTS:
        errors.append(f"{source}: #{number}: invalid verdict {row['verdict']!r}")
    if not isinstance(row["stale_suspicion"], bool):
        errors.append(f"{source}: #{number}: stale_suspicion must be Boolean")
    for field in ("ask", "probe_sketch"):
        if not isinstance(row[field], str) or not row[field].strip():
            errors.append(f"{source}: #{number}: {field} must be nonempty text")
    if not isinstance(row["stale_why"], str) or (
        row["stale_suspicion"] and not row["stale_why"].strip()
    ):
        errors.append(f"{source}: #{number}: stale_why required when suspicion is true")
    if require_live:
        for field in LIVE_FIELDS:
            if field not in row:
                errors.append(f"{source}: #{number}: missing live field {field}")
        if all(field in row for field in LIVE_FIELDS):
            if row["status_flag"] not in STATUS_FLAGS:
                errors.append(f"{source}: #{number}: invalid status_flag")
            if not validate_iso_utc(row["checked_utc"]):
                errors.append(f"{source}: #{number}: checked_utc must be ISO UTC")
            urls = row["source_urls"]
            if not isinstance(urls, list) or not urls or not all(
                isinstance(url, str) and url.startswith(("http://", "https://"))
                for url in urls
            ):
                errors.append(f"{source}: #{number}: source_urls must be nonempty URLs")
            elif (
                isinstance(number, int)
                and not isinstance(number, bool)
                and f"https://www.erdosproblems.com/{number}" not in urls
            ):
                errors.append(
                    f"{source}: #{number}: source_urls must include the live problem page"
                )
            if not isinstance(row["recognition_path"], bool):
                errors.append(f"{source}: #{number}: recognition_path must be Boolean")
    return errors


def command_validate(args: argparse.Namespace) -> int:
    pool_path = Path(args.pool)
    pool_doc = read_json(pool_path)
    pool_rows = pool_doc.get("pool")
    if not isinstance(pool_rows, list):
        raise SystemExit(f"{pool_path}: root.pool is not an array")
    expected = expected_numbers(pool_rows, args.scope)

    rows: list[dict] = []
    origins: dict[int, Path] = {}
    errors: list[str] = []
    inputs = [Path(value) for value in args.inputs]
    for path in inputs:
        data = read_json(path)
        if not isinstance(data, list):
            errors.append(f"{path}: root must be an array")
            continue
        for row in data:
            errors.extend(validate_row(row, path, args.require_live_evidence))
            if not isinstance(row, dict) or not isinstance(row.get("number"), int):
                continue
            number = row["number"]
            if number in origins:
                errors.append(f"duplicate #{number}: {origins[number]} and {path}")
            else:
                origins[number] = path
            if number not in expected:
                errors.append(f"{path}: #{number} is outside scope {args.scope}")
            rows.append(row)

    seen = set(origins)
    missing = sorted(expected - seen)
    if missing and not args.allow_partial:
        errors.append(f"missing {len(missing)} expected problems: {missing}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    rows.sort(key=lambda row: row["number"])
    probe_grade = [row["number"] for row in rows if is_probe_grade(row)]
    status_counts: dict[str, int] = {}
    for row in rows:
        flag = row.get("status_flag", "not_recorded")
        status_counts[flag] = status_counts.get(flag, 0) + 1
    output = {
        "schema": "erdos-target-triage-v2",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "pool": {"path": str(pool_path), "sha256": sha256(pool_path)},
        "scope": args.scope,
        "require_live_evidence": args.require_live_evidence,
        "complete": not missing,
        "expected_count": len(expected),
        "row_count": len(rows),
        "missing_numbers": missing,
        "probe_grade_numbers": probe_grade,
        "status_counts": status_counts,
        "inputs": [{"path": str(path), "sha256": sha256(path)} for path in inputs],
        "rows": rows,
    }
    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in (
        "scope", "complete", "expected_count", "row_count",
        "probe_grade_numbers", "status_counts")}, indent=2))
    print(f"wrote {out_path}")
    return 0


def balanced_chunks(rows: list[dict], count: int) -> list[list[dict]]:
    if count <= 0:
        raise ValueError("count must be positive")
    quotient, remainder = divmod(len(rows), count)
    chunks: list[list[dict]] = []
    start = 0
    for index in range(count):
        size = quotient + (1 if index < remainder else 0)
        chunks.append(rows[start:start + size])
        start += size
    return chunks


def command_prepare(args: argparse.Namespace) -> int:
    pool_path = Path(args.pool)
    pool_doc = read_json(pool_path)
    pool_rows = pool_doc.get("pool")
    if not isinstance(pool_rows, list):
        raise SystemExit(f"{pool_path}: root.pool is not an array")
    expected = expected_numbers(pool_rows, args.scope)
    selected = sorted(
        (row for row in pool_rows if int(row["number"]) in expected),
        key=lambda row: int(row["number"]),
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for index, rows in enumerate(balanced_chunks(selected, args.batches), start=1):
        if not rows:
            continue
        for row in rows:
            row["problem_url"] = f"https://www.erdosproblems.com/{row['number']}"
        first = rows[0]["number"]
        last = rows[-1]["number"]
        path = output_dir / f"{args.prefix}-{index:02d}-{first}-{last}.json"
        doc = {
            "schema": "erdos-target-triage-batch-v1",
            "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "pool": {"path": str(pool_path), "sha256": sha256(pool_path)},
            "scope": args.scope,
            "batch_index": index,
            "batch_count": args.batches,
            "row_count": len(rows),
            "numbers": [row["number"] for row in rows],
            "rows": rows,
        }
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append({"path": str(path), "count": len(rows), "first": first, "last": last})
    print(json.dumps({"scope": args.scope, "expected_count": len(selected), "batches": written}, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    sub = result.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--pool", required=True)
    validate.add_argument(
        "--scope",
        choices=("all", "formalized-open", "non-formalized-open"),
        required=True,
    )
    validate.add_argument("--output", required=True)
    validate.add_argument("--require-live-evidence", action="store_true")
    validate.add_argument("--allow-partial", action="store_true")
    validate.add_argument("inputs", nargs="+")
    validate.set_defaults(func=command_validate)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--pool", required=True)
    prepare.add_argument(
        "--scope",
        choices=("all", "formalized-open", "non-formalized-open"),
        required=True,
    )
    prepare.add_argument("--batches", type=int, default=4)
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--prefix", default="batch")
    prepare.set_defaults(func=command_prepare)
    return result


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
