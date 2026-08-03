#!/usr/bin/env python3
"""Create the frozen SHA-256 manifest for this scoped research directory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INCLUDED = [
    "12_4reg.txt",
    "N11_ANALYTIC.md",
    "PRIORITY_AUDIT.md",
    "README.md",
    "REPORT.md",
    "RESULTS.md",
    "STRUCTURAL_NOTES.md",
    "make_manifest.py",
    "n12_networkx_audit.json",
    "structured_pulse.py",
    "structured_pulse_result.json",
    "verify_n12_networkx.py",
]


def main() -> int:
    files = {}
    for name in INCLUDED:
        payload = (ROOT / name).read_bytes()
        files[name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    manifest = {
        "schema": "erdos149-structural-lane-manifest-v1",
        "frozen_date": "2026-08-03",
        "claim_scope": (
            "analytic n<=11 theorem; exhaustive connected 4-regular n=12 catalogue "
            "check plus disconnected reduction; explicitly scoped construction families"
        ),
        "files": files,
    }
    (ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
