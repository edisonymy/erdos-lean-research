#!/usr/bin/env python3
"""Build the hash manifest for the bounded non-Cayley #151 package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "MANIFEST.json"
ROLES = {
    "REPORT.md": "human-readable outcome and claim boundary",
    "PROVENANCE.json": "primary-source URLs and retrieval hashes",
    "BOUNDED_CORE_ATTEMPT.json": "machine-readable resource gate",
    "HoG_51171.g6": "43-vertex published edge-arrowing seed",
    "HoG_51177.g6": "63-vertex published vertex-arrowing seed",
    "HoG_51288.g6": "11-vertex published edge-arrowing seed",
    "audit_literature_seeds.py": "independent exact seed audit",
    "audit_literature_seeds.result.json": "canonical audit output",
    "minimize_hog51171.py": "bounded UNSAT-core/edge-minimization implementation",
    "make_manifest.py": "this manifest generator",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    audit = json.loads((HERE / "audit_literature_seeds.result.json").read_text(encoding="utf-8"))
    records = audit["records"]
    assert records["51171"]["beta"] == 25
    assert records["51177"]["beta"] == 37
    assert records["51177"]["edge_arrows_3_3"] is False
    assert records["51288"]["beta"] == 10
    assert records["51288"]["edge_arrows_3_3"] is True
    assert records["51171"]["all_43_vertex_deleted_subgraphs_nonarrowing"] is True
    files = []
    for name, role in sorted(ROLES.items()):
        path = HERE / name
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": sha256(path), "role": role})
    manifest = {
        "schema": "erdos151-noncayley-folkman-package-manifest-v1",
        "status": "KILL_DEMOTE_NO_CANDIDATE",
        "headline_checks": [
            "HoG 51171: exact beta=25, H(43)=10, published edge-arrowing claim",
            "HoG 51177: exact beta=37 and independently non-edge-arrowing",
            "HoG 51288: exact beta=10 and independently edge-arrowing",
            "All 43 vertex deletions of HoG 51171 independently nonarrowing",
            "No full or one-away Erdos #151 candidate",
        ],
        "files": files,
    }
    OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "status": manifest["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
