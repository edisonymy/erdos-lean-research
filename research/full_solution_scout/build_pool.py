"""Tier-0 pool builder for the target-acquisition funnel.

Builds the unclaimed-open candidate pool deterministically from the local
database snapshots, per research/target-acquisition.md:

- erdosproblems-live/data/problems.yaml   -> status must be an open-state
  category ("open", "falsifiable", "decidable", or "verifiable")
- .tmp/vibemathed-live-*.json (newest)    -> any AI claim excludes
- llm-hunter-live/attacks/erdos/          -> flag only (collision risk)
- CAMPAIGN_TOUCHED                        -> problems already worked here
- formal-conjectures-live ErdosProblems   -> statement availability flags

Output: pool-<date>.json next to this script, plus a printed summary.
The snapshots are point-in-time; refresh them before a fresh sweep.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBLEMS_YAML = HERE / "erdosproblems-live" / "data" / "problems.yaml"
FORMAL_DIR = HERE / "formal-conjectures-live" / "FormalConjectures" / "ErdosProblems"
HUNTER_DIR = HERE / "llm-hunter-live" / "attacks" / "erdos"
HUNTER_REPO = HERE / "llm-hunter-live"
FORMAL_REPO = HERE / "formal-conjectures-live"
PROBLEMS_REPO = HERE / "erdosproblems-live"
PROBLEMS_URL = "https://github.com/teorth/erdosproblems.git"
FORMAL_URL = "https://github.com/google-deepmind/formal-conjectures.git"
HUNTER_URL = "https://github.com/mehmetmars7/Erdosproblems-llm-hunter.git"
VIBEMATHED_URL = "https://vibemathed.com/api/dataset"

# The database uses these three labels as refinements of an open problem, not
# as solved states.  In particular, they are the finite/mechanically checkable
# targets that this campaign most wants to retain.
OPEN_STATES = frozenset({"open", "falsifiable", "decidable", "verifiable"})

# Problems already active, paused, audited, scouted, or scratched in this
# campaign (dossier sections 5-7 plus untracked scratch directories).
CAMPAIGN_TOUCHED = {
    7, 23, 36, 64, 97, 106, 128, 137, 151, 167, 196, 203, 273, 274, 276, 287,
    307, 319, 366, 375, 409, 421, 458, 488, 548, 583, 617, 647, 672, 677,
    699,
    719, 742, 835, 850, 982, 993, 1041, 1082,
}


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(path: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip() or None


def public_path(path: Path | None) -> str | None:
    """Return a reproducible workspace-relative path without host details."""
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def source_record(
    path: Path | None,
    repo: Path | None = None,
    url: str | None = None,
) -> dict:
    return {
        "path": public_path(path),
        "url": url,
        "sha256": sha256_file(path),
        "git_commit": git_head(repo) if repo is not None else None,
        "modified_utc": (
            dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()
            if path is not None and path.exists()
            else None
        ),
    }


def parse_problems_yaml(path: Path) -> dict[int, dict]:
    problems: dict[int, dict] = {}
    current: dict | None = None
    block: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("- number:"):
            m = re.search(r'"(\d+)"', raw)
            current = {"tags": [], "prize": None, "status": None,
                       "status_updated": None, "formalized": None}
            problems[int(m.group(1))] = current
            block = None
            continue
        if current is None:
            continue
        if raw.startswith("    "):
            m = re.match(r'\s+state:\s*"([^"]+)"', raw)
            if m and block == "status":
                current["status"] = m.group(1)
            elif m and block == "formalized":
                current["formalized"] = m.group(1)
            m = re.match(r'\s+last_update:\s*"([^"]+)"', raw)
            if m and block == "status":
                current["status_updated"] = m.group(1)
        elif raw.startswith("  "):
            key = raw.strip().rstrip(":").split(":")[0]
            if raw.strip().startswith("prize:"):
                current["prize"] = raw.split(":", 1)[1].strip().strip('"')
                block = None
            elif raw.strip().startswith("tags:"):
                current["tags"] = re.findall(r'"([^"]+)"', raw)
                block = None
            else:
                block = key
    return problems


def newest_vibemathed() -> tuple[Path | None, set[int]]:
    candidates = sorted((ROOT / ".tmp").glob("vibemathed-live-*.json"))
    if not candidates:
        return None, set()
    path = candidates[-1]
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    claimed = set()
    for row in data.get("problems", []):
        try:
            claimed.add(int(row.get("problemNumber")))
        except (TypeError, ValueError):
            continue
    return path, claimed


def hunter_attacked() -> set[int]:
    attacked: set[int] = set()
    if not HUNTER_DIR.exists():
        return attacked
    for entry in HUNTER_DIR.rglob("*"):
        stem = entry.stem if entry.is_file() else entry.name
        if re.fullmatch(r"\d+", stem):
            attacked.add(int(stem))
    return attacked


def formal_flags(number: int) -> dict:
    path = FORMAL_DIR / f"{number}.lean"
    if not path.exists():
        return {"formal_file": False, "formal_path": None,
                "research_open": False,
                "question_form": False, "existential_iff": False}
    text = path.read_text(encoding="utf-8")
    compact = re.sub(r"\s+", " ", text)
    existential = bool(
        re.search(r"answer\(sorry\)\s*↔\s*∃", compact)
        or re.search(r"\(∃.{0,200}\)\s*↔\s*answer\(sorry\)", compact)
    )
    return {
        "formal_file": True,
        "formal_path": str(path.relative_to(FORMAL_REPO)),
        "research_open": "category research open" in text,
        "question_form": "answer(sorry)" in text,
        "existential_iff": existential,
    }


def eligible_status(status: str | None) -> bool:
    """Return whether a database research status belongs in the open pool."""
    return status in OPEN_STATES


def main() -> None:
    problems = parse_problems_yaml(PROBLEMS_YAML)
    vibe_path, claimed = newest_vibemathed()
    attacked = hunter_attacked()

    pool = []
    for number in sorted(problems):
        info = problems[number]
        if not eligible_status(info["status"]):
            continue
        if number in claimed or number in CAMPAIGN_TOUCHED:
            continue
        row = {"number": number, "status": info["status"],
               "prize": info["prize"],
               "tags": info["tags"], "status_updated": info["status_updated"],
               "llm_hunter_attacked": number in attacked}
        row.update(formal_flags(number))
        pool.append(row)

    out = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sources": {
            "problems_yaml": source_record(
                PROBLEMS_YAML, PROBLEMS_REPO, PROBLEMS_URL
            ),
            "vibemathed_snapshot": source_record(
                vibe_path, url=VIBEMATHED_URL
            ),
            "vibemathed_claimed_problem_numbers": sorted(claimed),
            "llm_hunter": source_record(None, HUNTER_REPO, HUNTER_URL),
            "formal_conjectures": source_record(
                None, FORMAL_REPO, FORMAL_URL
            ),
        },
        "counts": {
            "database_problems": len(problems),
            "database_open": sum(1 for p in problems.values()
                                 if p["status"] == "open"),
            "database_open_state_candidates":
                sum(1 for p in problems.values()
                    if eligible_status(p["status"])),
            "database_open_state_breakdown": {
                state: sum(1 for p in problems.values()
                           if p["status"] == state)
                for state in sorted(OPEN_STATES)
            },
            "vibemathed_claimed": len(claimed),
            "llm_hunter_attacked": len(attacked),
            "campaign_touched": len(CAMPAIGN_TOUCHED),
            "pool": len(pool),
            "pool_with_formal_open_statement":
                sum(1 for r in pool if r["research_open"]),
            "pool_with_any_formal_file":
                sum(1 for r in pool if r["formal_file"]),
            "pool_existential_iff":
                sum(1 for r in pool if r["existential_iff"]),
            "pool_flagged_llm_hunter":
                sum(1 for r in pool if r["llm_hunter_attacked"]),
        },
        "pool": pool,
    }

    stamp = dt.date.today().isoformat()
    out_path = HERE / f"pool-{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(json.dumps(out["counts"], indent=2))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
