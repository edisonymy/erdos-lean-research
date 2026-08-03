#!/usr/bin/env python3
"""Write or verify the SHA-256 manifest for this bounded scout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "MANIFEST.json"
FILES = (
    "README.md",
    "REPORT.md",
    "requirements.txt",
    "scan_circulants_n50.py",
    "scan_circulants_n50.result.json",
    "scan_abelian_n50.py",
    "scan_abelian_n50.result.json",
    "scan_circulants_n59.py",
    "scan_circulants_n59.result.json",
    "audit_orbits.py",
    "audit_orbits.result.json",
    "audit_beta_semantics.py",
    "audit_beta_semantics.result.json",
    "audit_family_minima.py",
    "audit_family_minima.result.json",
    "audit_global_near_miss.py",
    "audit_global_near_miss.result.json",
    "check_operation_lemmas.py",
    "check_operation_lemmas.result.json",
    "make_manifest.py",
)


def record(name: str) -> dict:
    payload = (HERE / name).read_bytes()
    return {
        "path": name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def current_manifest() -> dict:
    return {
        "schema": "erdos151-folkman-spectral-scout-manifest-v1",
        "hash_algorithm": "SHA-256",
        "frozen_date": "2026-08-03",
        "self_exclusion": "MANIFEST.json is excluded because a file cannot contain its own cryptographic hash.",
        "files": [record(name) for name in FILES],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="intentionally replace MANIFEST.json with hashes of the current artifact set",
    )
    args = parser.parse_args()
    observed = current_manifest()
    if args.write:
        MANIFEST.write_text(
            json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"wrote {MANIFEST} with {len(FILES)} file hashes")
        return 0

    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if observed != expected:
        expected_by_name = {item["path"]: item for item in expected.get("files", [])}
        observed_by_name = {item["path"]: item for item in observed["files"]}
        changed = sorted(
            name
            for name in set(expected_by_name) | set(observed_by_name)
            if expected_by_name.get(name) != observed_by_name.get(name)
        )
        print(json.dumps({"status": "FAIL", "changed": changed}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "files_verified": len(FILES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
