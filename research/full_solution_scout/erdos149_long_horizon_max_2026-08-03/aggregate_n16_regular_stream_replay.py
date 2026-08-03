#!/usr/bin/env python3
"""Aggregate the 16 independent regular n=16 replay shards."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


EXPECTED_RECORDS = 8_037_418
EXPECTED_GENG_SHA256 = "64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef"


def main() -> None:
    here = Path(__file__).resolve().parent
    primary = json.loads((here / "n16_regular_stream_primary_aggregate.json").read_text(encoding="utf-8"))
    shards = []
    methods = Counter()
    exact_sizes = Counter()
    records = stream_bytes = parser_samples = parser_mismatches = 0
    for residue in range(16):
        path = here / f"n16_regular_replay_shard_{residue:02d}_of_16.json"
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["status"] == "VERIFIED" and all(result["assertions"].values())
        assert result["shard"] == {"residue": residue, "modulus": 16, "text": f"{residue}/16"}
        assert result["generator"]["sha256"] == EXPECTED_GENG_SHA256
        records += result["stream"]["records"]
        stream_bytes += result["stream"]["bytes"]
        parser_samples += result["networkx_parser_samples"]
        parser_mismatches += result["networkx_parser_mismatches"]
        methods.update(result["methods"])
        exact_sizes.update({int(key): value for key, value in result["exact_fallback_sizes"].items()})
        shards.append(
            {
                "residue": residue,
                "records": result["stream"]["records"],
                "bytes": result["stream"]["bytes"],
                "stream_sha256": result["stream"]["sha256"],
                "primary_stream_sha256": result["primary_expectation"]["stream_sha256"],
                "methods": result["methods"],
                "parser_samples": result["networkx_parser_samples"],
                "elapsed_seconds": result["elapsed_seconds"],
                "result_path": path.name,
                "result_bytes": path.stat().st_size,
                "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    assertions = {
        "primary_verified": primary["status"] == "VERIFIED" and primary["records"] == EXPECTED_RECORDS,
        "replay_records_exact": records == EXPECTED_RECORDS,
        "all_stream_hashes_match_primary": all(shard["stream_sha256"] == shard["primary_stream_sha256"] for shard in shards),
        "parser_mismatches_zero": parser_mismatches == 0,
        "all_replay_records_witnessed": sum(methods.values()) == records,
        "all_exact_fallbacks_reach_target": all(size >= 12 for size in exact_sizes),
    }
    script = Path(__file__).resolve()
    output = {
        "schema": "erdos149-n16-regular-stream-replay-aggregate-v1",
        "status": "VERIFIED" if all(assertions.values()) else "CHECK_FAILED",
        "scope": "Independent full replay of all connected 4-regular order-16 graphs in canonical geng residue streams.",
        "generator": {
            "base_command": "geng -q -c -d4 -D4 16 32 RESIDUE/16",
            "sha256": EXPECTED_GENG_SHA256,
            "residue_partition": "0/16,...,15/16",
        },
        "records": records,
        "expected_records": EXPECTED_RECORDS,
        "stream_bytes": stream_bytes,
        "materialized_catalogue": False,
        "required_compatibility_matching": 12,
        "methods": dict(sorted(methods.items())),
        "exact_fallback_sizes": dict(sorted(exact_sizes.items())),
        "networkx_parser_samples": parser_samples,
        "networkx_parser_mismatches": parser_mismatches,
        "failures": [],
        "assertions": assertions,
        "shards": shards,
        "primary_aggregate": {
            "path": "n16_regular_stream_primary_aggregate.json",
            "bytes": (here / "n16_regular_stream_primary_aggregate.json").stat().st_size,
            "sha256": hashlib.sha256((here / "n16_regular_stream_primary_aggregate.json").read_bytes()).hexdigest(),
        },
        "script": {"bytes": script.stat().st_size, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()},
        "claim_boundary": "This completes the independent regular order-16 replay; the combined bounded theorem still depends on the separately audited t=2 and t=4 reductions.",
    }
    path = here / "n16_regular_stream_replay_aggregate.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "records": records, "methods": output["methods"], "exact_fallback_sizes": output["exact_fallback_sizes"], "parser_samples": parser_samples}, sort_keys=True))
    if output["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
