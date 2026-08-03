#!/usr/bin/env python3
"""Finite structural and formula-byte audit for the exact-61 certificates."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import runpy
from pathlib import Path


HERE = Path(__file__).resolve().parent
ns = runpy.run_path(str(HERE / "independent_certificate61.py"))
BLOCKS, BEDGES = ns["BLOCKS"], ns["BEDGES"]
edge_disjoint, CORES, build_formula = ns["edge_disjoint"], ns["CORES"], ns["build_formula"]
PACKING18 = (
    (0, 1, 3, 4), (0, 1, 5, 8), (0, 1, 6, 7), (0, 2, 3, 5),
    (0, 2, 4, 7), (0, 2, 6, 8), (0, 3, 7, 8), (0, 4, 5, 6),
    (1, 2, 3, 6), (1, 2, 4, 5), (1, 2, 7, 8), (1, 3, 5, 7),
    (1, 4, 6, 8), (2, 3, 4, 8), (2, 5, 6, 7), (3, 4, 6, 7),
    (3, 5, 6, 8), (4, 5, 7, 8),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    pack_edges = [BEDGES[BLOCKS.index(b)] for b in PACKING18]
    assert len(pack_edges) == 18
    assert all(a.isdisjoint(b) for a, b in itertools.combinations(pack_edges, 2))
    assert len(frozenset().union(*pack_edges)) == 72
    counts = collections.Counter()
    for a, b in itertools.combinations(BLOCKS, 2):
        if edge_disjoint(a, b):
            counts[len(set(a).intersection(b))] += 1
    assert counts == {0: 315, 1: 2520, 2: 3780}
    assert sum(counts.values()) == 6615

    certdir = HERE / "certificates"
    formulas = []
    for type_id, core in enumerate(CORES, 1):
        cnf, meta = build_formula(core)
        regenerated = certdir / f"type_{type_id:02d}.regenerated.cnf"
        cnf.to_file(str(regenerated))
        checked = certdir / f"type_{type_id:02d}.cnf"
        assert sha256(regenerated) == sha256(checked)
        regenerated.unlink()
        formulas.append({"type": type_id, "intersection": type_id - 1,
                         "compatible_blocks": meta["compatible_blocks"],
                         "cnf_sha256": sha256(checked)})
    manifest_path = certdir / "manifest.verified.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "ALL_THREE_EXACT61_INDEPENDENT_CERTIFICATES_NATIVE_VERIFIED"
    assert len(manifest["entries"]) == 3
    assert all(r["drat_check"]["verified_marker"] and r["lrat_check"]["verified_marker"]
               for r in manifest["entries"])
    result = {
        "status": "EXACT61_STRUCTURAL_AUDIT_PASS",
        "packing18_distinct_triples": 72,
        "labeled_two_packings": 6615,
        "core_types_by_intersection": {str(k): counts[k] for k in range(3)},
        "formulas": formulas,
        "verified_manifest_sha256": sha256(manifest_path),
    }
    path = HERE / "structural_audit61_result.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
