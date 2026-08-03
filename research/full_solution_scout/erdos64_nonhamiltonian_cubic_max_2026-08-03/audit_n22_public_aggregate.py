#!/usr/bin/env python3
"""Independent aggregate/provenance audit for the full cubic order-22 run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_TOTAL = 7_319_447


def digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest().upper()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    aggregate = load(args.aggregate)
    assertions: dict[str, bool] = {
        "aggregate_status_complete": aggregate.get("status") == "complete",
        "eight_partitions_declared": aggregate.get("partition_count") == 8,
        "declared_total_exact": aggregate.get("total", {}).get("count") == EXPECTED_TOTAL,
        "declared_survivors_zero": aggregate.get("total", {}).get("survivors") == 0,
        "asymmetric_block_bounds_exact": aggregate.get("one_defect_block_bounds")
        == {
            "nonadjacent_terminal": 23,
            "adjacent_triangle_terminal": 25,
            "order_drops": {"nonadjacent": 1, "adjacent": 3},
        },
    }
    records = []
    for item in aggregate.get("partitions", []):
        part = int(item["part"])
        source = args.directory / f"cubic_n22_part{part}.g6"
        literal_path = args.directory / f"cubic_n22_part{part}_independent_core_audit.json"
        avoiding_path = args.directory / f"cubic_n22_part{part}_avoiding_core_audit.json"
        literal = load(literal_path)
        avoiding = load(avoiding_path)
        literal_record = literal["inputs"][0]
        literal_stats = literal_record["stats"]
        avoiding_stats = avoiding["stats"]
        source_bytes = source.stat().st_size
        source_hash = digest(source)
        expected = int(item["count"])
        checks = {
            "source_bytes": source_bytes == int(item["bytes"]) == 41 * expected,
            "source_hash": source_hash == str(item["sha256"]).upper(),
            "literal_complete": bool(literal_record["complete_empty_core_replay"]),
            "literal_count": literal_stats["validated_connected_simple_cubic"] == expected,
            "literal_empty": literal_stats["empty_dyadic_core"] == expected,
            "literal_no_survivor": literal_record["first_survivor"] is None,
            "literal_source_hash": literal_record["sha256"].upper() == source_hash,
            "avoiding_complete": bool(avoiding["complete"]),
            "avoiding_count": avoiding_stats["validated_connected_simple_cubic"] == expected,
            "avoiding_empty": avoiding_stats["empty_dyadic_core"] == expected,
            "avoiding_no_candidate": avoiding["candidate"] is None,
            "avoiding_source_hash": avoiding["sha256"].upper() == source_hash,
        }
        records.append({"part": part, "count": expected, "sha256": source_hash, "checks": checks})
        assertions[f"part_{part}_all_checks"] = all(checks.values())

    assertions["exactly_eight_live_records"] = len(records) == 8
    assertions["live_total_exact"] = sum(record["count"] for record in records) == EXPECTED_TOTAL
    assertions["source_hashes_unique"] = len({record["sha256"] for record in records}) == 8
    assertions["candidate_directory_absent"] = not (args.directory / "candidates_n22").exists()
    status = "VERIFIED" if all(assertions.values()) else "FAILED"
    payload = {
        "schema": "erdos64-n22-root-aggregate-audit-v1",
        "status": status,
        "aggregate_sha256": digest(args.aggregate),
        "expected_total": EXPECTED_TOTAL,
        "assertions": assertions,
        "records": records,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if status == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
