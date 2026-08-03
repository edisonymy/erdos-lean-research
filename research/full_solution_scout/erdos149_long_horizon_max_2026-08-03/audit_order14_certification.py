#!/usr/bin/env python3
"""Meta-audit every file hash and numerical claim in CERTIFICATION_ORDER14."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    certificate = json.loads((here / "CERTIFICATION_ORDER14.json").read_text(encoding="utf-8"))
    checks = []

    def walk(value, location="root"):
        if isinstance(value, dict):
            if {"path", "bytes", "sha256"} <= value.keys():
                path = here / value["path"]
                checks.append(
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
    primary27 = json.loads((here / "n14_m27_result.json").read_text(encoding="utf-8"))
    primary28 = json.loads((here / "n14_m28_result.json").read_text(encoding="utf-8"))
    fresh27 = json.loads((here / "n14_m27_fresh_audit.json").read_text(encoding="utf-8"))
    fresh28 = json.loads((here / "n14_m28_fresh_audit.json").read_text(encoding="utf-8"))
    structural_cases = [
        {"m": m, "t": 56 - 2 * m, "survives_packing": 3 * (56 - 2 * m) <= 14 - (56 - 2 * m)}
        for m in range(21, 29)
    ]
    assertions = {
        "all_dependency_files_match": all(
            item["exists"] and item["bytes_match"] and item["sha256_match"] for item in checks
        ),
        "structural_survivors_are_27_28": [item["m"] for item in structural_cases if item["survives_packing"]] == [27, 28],
        "m27_primary_verified": primary27["status"] == "VERIFIED" and not primary27["failures"] and primary27["catalogue"]["records_checked"] == 2771069,
        "m27_fresh_verified": fresh27["status"] == "VERIFIED" and not fresh27["failures"] and fresh27["fresh_reverse_matchings"] == 2771069,
        "m28_primary_verified": primary28["status"] == "VERIFIED" and not primary28["failures"] and primary28["catalogue"]["records_checked"] == 88168,
        "m28_fresh_verified": fresh28["status"] == "VERIFIED" and not fresh28["failures"] and fresh28["fresh_reverse_matchings"] == 88168,
    }
    result = {
        "schema": "erdos149-order14-certification-meta-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "dependency_file_checks": checks,
        "structural_cases": structural_cases,
        "assertions": assertions,
        "claim_boundary": "This meta-audit validates the bounded order-at-most-14 certificate only.",
    }
    (here / "order14_certification_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "file_checks": len(checks), "assertions": assertions}, sort_keys=True))


if __name__ == "__main__":
    main()
