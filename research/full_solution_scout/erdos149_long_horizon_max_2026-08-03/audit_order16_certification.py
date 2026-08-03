#!/usr/bin/env python3
"""Meta-audit hashes, shard manifests, and counts for the order-16 theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


EXPECTED_RECORDS = 8_037_418


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    certificate = json.loads((here / "CERTIFICATION_ORDER16.json").read_text(encoding="utf-8"))
    dependency_checks = []

    def walk(value, location="root"):
        if isinstance(value, dict):
            if {"path", "bytes", "sha256"} <= value.keys():
                path = here / value["path"]
                dependency_checks.append(
                    {
                        "location": location,
                        "path": value["path"],
                        "exists": path.is_file(),
                        "bytes_match": path.is_file() and path.stat().st_size == value["bytes"],
                        "sha256_match": path.is_file() and digest(path) == value["sha256"],
                    }
                )
            for key, child in value.items():
                walk(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{location}[{index}]")

    walk(certificate)
    t2 = json.loads((here / "n16_t2_core_result.json").read_text(encoding="utf-8"))
    t4 = json.loads((here / "n16_t4_core_result.json").read_text(encoding="utf-8"))
    cores_fresh = json.loads((here / "n16_cores_fresh_audit.json").read_text(encoding="utf-8"))
    primary = json.loads((here / "n16_regular_stream_primary_aggregate.json").read_text(encoding="utf-8"))
    replay = json.loads((here / "n16_regular_stream_replay_aggregate.json").read_text(encoding="utf-8"))

    primary_shard_checks = []
    for shard in primary["shards"]:
        path = here / shard["result_path"]
        stored = json.loads(path.read_text(encoding="utf-8"))
        primary_shard_checks.append(
            {
                "residue": shard["residue"],
                "exists": path.is_file(),
                "bytes_match": path.stat().st_size == shard["result_bytes"],
                "sha256_match": digest(path) == shard["result_sha256"],
                "status_checked": stored["status"] == "CHECKED",
                "records_match": stored["stream"]["records"] == shard["records"],
                "stream_sha256_match": stored["stream"]["sha256"] == shard["stream_sha256"],
            }
        )

    replay_shard_checks = []
    for shard in replay["shards"]:
        path = here / shard["result_path"]
        stored = json.loads(path.read_text(encoding="utf-8"))
        replay_shard_checks.append(
            {
                "residue": shard["residue"],
                "exists": path.is_file(),
                "bytes_match": path.stat().st_size == shard["result_bytes"],
                "sha256_match": digest(path) == shard["result_sha256"],
                "status_verified": stored["status"] == "VERIFIED",
                "all_assertions_true": all(stored["assertions"].values()),
                "records_match": stored["stream"]["records"] == shard["records"],
                "stream_sha256_match": stored["stream"]["sha256"] == shard["stream_sha256"],
                "primary_stream_sha256_match": shard["stream_sha256"] == shard["primary_stream_sha256"],
            }
        )

    structural_cases = [
        {"m": m, "t": 64 - 2 * m, "survives_packing": 3 * (64 - 2 * m) <= 16 - (64 - 2 * m)}
        for m in range(24, 33)
    ]
    candidate_files = sorted(path.name for path in here.glob("n16_regular_*candidate*.json"))
    discrepancy_files = sorted(path.name for path in here.glob("n16_regular_*discrepancy*.json"))
    assertions = {
        "all_dependency_files_match": all(
            item["exists"] and item["bytes_match"] and item["sha256_match"]
            for item in dependency_checks
        ),
        "structural_survivors_are_30_31_32": [item["m"] for item in structural_cases if item["survives_packing"]] == [30, 31, 32],
        "t2_primary_verified": t2["status"] == "VERIFIED" and not t2["failures"] and sum(t2["counts"][key] for key in ("r1_internal_completions", "r2_internal_completions", "r3_internal_completions")) == 448772,
        "t4_primary_verified": t4["status"] == "VERIFIED" and not t4["failures"] and t4["counts"]["separated_partitions"] == 1,
        "nonregular_fresh_verified": cores_fresh["status"] == "VERIFIED" and all(cores_fresh["assertions"].values()),
        "primary_aggregate_verified": primary["status"] == "VERIFIED" and primary["records"] == EXPECTED_RECORDS and sum(primary["methods"].values()) == EXPECTED_RECORDS,
        "primary_residues_complete": [item["residue"] for item in primary_shard_checks] == list(range(16)),
        "primary_shard_manifests_valid": all(all(value for key, value in item.items() if key != "residue") for item in primary_shard_checks),
        "replay_aggregate_verified": replay["status"] == "VERIFIED" and replay["records"] == EXPECTED_RECORDS and all(replay["assertions"].values()),
        "replay_residues_complete": [item["residue"] for item in replay_shard_checks] == list(range(16)),
        "replay_shard_manifests_valid": all(all(value for key, value in item.items() if key != "residue") for item in replay_shard_checks),
        "primary_replay_counts_equal": primary["records"] == replay["records"] == EXPECTED_RECORDS,
        "candidate_files_absent": not candidate_files,
        "discrepancy_files_absent": not discrepancy_files,
    }
    result = {
        "schema": "erdos149-order16-certification-meta-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "dependency_file_checks": dependency_checks,
        "primary_shard_checks": primary_shard_checks,
        "replay_shard_checks": replay_shard_checks,
        "structural_cases": structural_cases,
        "candidate_files": candidate_files,
        "discrepancy_files": discrepancy_files,
        "assertions": assertions,
        "claim_boundary": "This meta-audit validates the bounded order-at-most-16 certificate only.",
    }
    path = here / "order16_certification_audit.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "dependencies": len(dependency_checks), "primary_shards": len(primary_shard_checks), "replay_shards": len(replay_shard_checks), "assertions": assertions}, sort_keys=True))
    if result["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
