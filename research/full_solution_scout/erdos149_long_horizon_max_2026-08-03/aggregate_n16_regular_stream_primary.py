#!/usr/bin/env python3
"""Aggregate the 16 disjoint primary streaming shards for regular n=16."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


EXPECTED_RECORDS = 8_037_418
EXPECTED_GENG_SHA256 = "64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef"


def main() -> None:
    here = Path(__file__).resolve().parent
    shards = []
    methods = Counter()
    exact_fallback_sizes = Counter()
    total_records = total_bytes = 0
    for residue in range(16):
        path = here / f"n16_regular_stream_shard_{residue:02d}_of_16.json"
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["status"] == "CHECKED"
        assert result["shard"] == {"residue": residue, "modulus": 16, "text": f"{residue}/16"}
        assert result["generator"]["sha256"] == EXPECTED_GENG_SHA256
        assert result["generator"]["return_code"] == 0
        assert result["required_compatibility_matching"] == 12
        assert not result["failures"]
        total_records += result["stream"]["records"]
        total_bytes += result["stream"]["bytes"]
        methods.update(result["methods"])
        exact_fallback_sizes.update({int(key): value for key, value in result["exact_fallback_sizes"].items()})
        shards.append(
            {
                "residue": residue,
                "records": result["stream"]["records"],
                "bytes": result["stream"]["bytes"],
                "stream_sha256": result["stream"]["sha256"],
                "methods": result["methods"],
                "elapsed_seconds": result["elapsed_seconds"],
                "result_path": path.name,
                "result_bytes": path.stat().st_size,
                "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    script = Path(__file__).resolve()
    output = {
        "schema": "erdos149-n16-regular-stream-primary-aggregate-v1",
        "status": "VERIFIED" if total_records == EXPECTED_RECORDS and not exact_fallback_sizes else "CHECK_FAILED",
        "scope": "All connected 4-regular order-16 graphs, partitioned by canonical geng residues 0/16 through 15/16.",
        "generator": {
            "base_command": "geng -q -c -d4 -D4 16 32 RESIDUE/16",
            "sha256": EXPECTED_GENG_SHA256,
            "residue_partition": "0/16,...,15/16",
        },
        "records": total_records,
        "expected_records": EXPECTED_RECORDS,
        "stream_bytes": total_bytes,
        "materialized_catalogue": False,
        "required_compatibility_matching": 12,
        "methods": dict(sorted(methods.items())),
        "exact_fallback_sizes": dict(sorted(exact_fallback_sizes.items())),
        "failures": [],
        "shards": shards,
        "excluded_partial_run": {
            "path": "n16_regular_stream_primary_checkpoint.json",
            "records": 4018709,
            "reason": "Monolithic process was interrupted by the host after its 50% checkpoint; it is not included in aggregate coverage."
        },
        "script": {"bytes": script.stat().st_size, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()},
        "claim_boundary": "This is primary witness pass 1. A differently implemented full replay is required before the regular slice is treated as independently audited.",
    }
    path = here / "n16_regular_stream_primary_aggregate.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "records": total_records, "methods": output["methods"], "shards": len(shards)}, sort_keys=True))
    if output["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
