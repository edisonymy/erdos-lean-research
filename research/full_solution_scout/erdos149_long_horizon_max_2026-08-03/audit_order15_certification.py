#!/usr/bin/env python3
"""Meta-audit every file hash and numerical claim in CERTIFICATION_ORDER15."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    certificate = json.loads((here / "CERTIFICATION_ORDER15.json").read_text(encoding="utf-8"))
    file_checks = []

    def visit(value, location="root"):
        if isinstance(value, dict):
            if {"path", "bytes", "sha256"} <= value.keys():
                path = here / value["path"]
                file_checks.append(
                    {
                        "location": location,
                        "path": value["path"],
                        "exists": path.is_file(),
                        "bytes_match": path.is_file() and path.stat().st_size == value["bytes"],
                        "sha256_match": path.is_file() and sha256(path) == value["sha256"],
                    }
                )
            for key, child in value.items():
                visit(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]")

    visit(certificate)
    theta = json.loads((here / "n15_theta_core_result.json").read_text(encoding="utf-8"))
    theta_fresh = json.loads((here / "n15_theta_core_fresh_audit.json").read_text(encoding="utf-8"))
    regular = json.loads((here / "n15_regular_result.json").read_text(encoding="utf-8"))
    regular_fresh = json.loads((here / "n15_regular_fresh_audit.json").read_text(encoding="utf-8"))
    structural_cases = [
        {"m": m, "t": 60 - 2 * m, "survives_packing": 3 * (60 - 2 * m) <= 15 - (60 - 2 * m)}
        for m in range(23, 31)
    ]
    assertions = {
        "all_dependency_files_match": all(
            item["exists"] and item["bytes_match"] and item["sha256_match"] for item in file_checks
        ),
        "structural_survivors_are_29_30": [item["m"] for item in structural_cases if item["survives_packing"]] == [29, 30],
        "theta_primary_verified": theta["status"] == "VERIFIED" and not theta["failures"] and theta["certified_matching_lower_bound_distribution"] == {"9": 5256},
        "theta_fresh_verified": theta_fresh["status"] == "VERIFIED" and not theta_fresh["failures"] and theta_fresh["fresh_reverse_matchings_of_nine"] == 5256,
        "theta_counts_agree": theta["counts"] == theta_fresh["counts"],
        "regular_primary_verified": regular["status"] == "VERIFIED" and not regular["failures"] and regular["catalogue"]["records_checked"] == 805491,
        "regular_fresh_verified": regular_fresh["status"] == "VERIFIED" and not regular_fresh["failures"] and regular_fresh["fresh_reverse_matchings_of_ten"] == 805491,
    }
    result = {
        "schema": "erdos149-order15-certification-meta-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "dependency_file_checks": file_checks,
        "structural_cases": structural_cases,
        "assertions": assertions,
        "claim_boundary": "This meta-audit validates the bounded order-at-most-15 certificate only.",
    }
    (here / "order15_certification_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "file_checks": len(file_checks), "assertions": assertions}, sort_keys=True))


if __name__ == "__main__":
    main()
