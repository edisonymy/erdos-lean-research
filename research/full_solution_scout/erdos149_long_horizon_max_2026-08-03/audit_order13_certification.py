#!/usr/bin/env python3
"""Meta-audit every file hash and numerical claim in CERTIFICATION_ORDER13."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    certificate = json.loads((here / "CERTIFICATION_ORDER13.json").read_text(encoding="utf-8"))
    file_checks = []

    def visit(value, logical_path="root"):
        if isinstance(value, dict):
            if {"path", "bytes", "sha256"} <= value.keys():
                path = here / value["path"]
                check = {
                    "logical_path": logical_path,
                    "path": value["path"],
                    "exists": path.is_file(),
                    "bytes_match": path.is_file() and path.stat().st_size == value["bytes"],
                    "sha256_match": path.is_file() and sha256(path) == value["sha256"],
                }
                file_checks.append(check)
            for key, child in value.items():
                visit(child, f"{logical_path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{logical_path}[{index}]")

    visit(certificate)
    m25 = json.loads((here / "n13_almost_regular_result.json").read_text(encoding="utf-8"))
    m25_fresh = json.loads((here / "n13_almost_regular_fresh_audit.json").read_text(encoding="utf-8"))
    m26 = json.loads((here / "n13_4regular_result.json").read_text(encoding="utf-8"))
    m26_fresh = json.loads((here / "n13_4regular_fresh_audit.json").read_text(encoding="utf-8"))
    target_hash_line = (here / "TARGET_LOCK.sha256").read_text(encoding="ascii").split()[0].lower()
    structural_cases = [
        {"m": m, "t": 52 - 2 * m, "survives_packing": 3 * (52 - 2 * m) <= 13 - (52 - 2 * m)}
        for m in range(20, 27)
    ]
    numerical_assertions = {
        "target_hash_file_matches": target_hash_line == certificate["target_lock"]["sha256"],
        "all_dependency_files_match": all(
            check["exists"] and check["bytes_match"] and check["sha256_match"]
            for check in file_checks
        ),
        "structural_survivors_are_25_26": [x["m"] for x in structural_cases if x["survives_packing"]] == [25, 26],
        "m25_primary_verified": m25["status"] == "VERIFIED" and not m25["failures"] and m25["catalogue"]["records"] == 300361,
        "m25_fresh_verified": m25_fresh["status"] == "VERIFIED" and not m25_fresh["fresh_checker"]["failures"],
        "m26_primary_verified": m26["status"] == "VERIFIED" and not m26["failures"] and m26["catalogue"]["records"] == 10778,
        "m26_fresh_verified": m26_fresh["status"] == "VERIFIED" and not m26_fresh["failures"],
    }
    output = {
        "schema": "erdos149-order13-certification-meta-audit-v1",
        "status": "VERIFIED" if all(numerical_assertions.values()) else "AUDIT_FAILURE",
        "dependency_file_checks": file_checks,
        "structural_cases": structural_cases,
        "assertions": numerical_assertions,
        "claim_boundary": "This meta-audit validates the bounded order-at-most-13 certificate only.",
    }
    (here / "order13_certification_audit.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": output["status"], "file_checks": len(file_checks), "assertions": numerical_assertions}, sort_keys=True))


if __name__ == "__main__":
    main()
