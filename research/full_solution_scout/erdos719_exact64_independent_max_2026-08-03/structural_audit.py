#!/usr/bin/env python3
"""Finite structural checks supporting the independent exact-64 proof."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import runpy
from pathlib import Path


HERE = Path(__file__).resolve().parent
ns = runpy.run_path(str(HERE / "independent_certificate.py"))
BLOCKS = ns["BLOCKS"]
BLOCK_EDGES = ns["BLOCK_EDGES"]
disjoint = ns["disjoint_as_hypergraphs"]
signature = ns["membership_signature"]
build_formula = ns["build_formula"]

PACKING18 = (
    (0, 1, 3, 4), (0, 1, 5, 8), (0, 1, 6, 7),
    (0, 2, 3, 5), (0, 2, 4, 7), (0, 2, 6, 8),
    (0, 3, 7, 8), (0, 4, 5, 6), (1, 2, 3, 6),
    (1, 2, 4, 5), (1, 2, 7, 8), (1, 3, 5, 7),
    (1, 4, 6, 8), (2, 3, 4, 8), (2, 5, 6, 7),
    (3, 4, 6, 7), (3, 5, 6, 8), (4, 5, 7, 8),
)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    # The fixed packing has 18 blocks and 72 distinct constituent triples.
    packing_edges = [BLOCK_EDGES[BLOCKS.index(block)] for block in PACKING18]
    assert len(PACKING18) == 18
    assert all(a.isdisjoint(b) for a, b in itertools.combinations(packing_edges, 2))
    assert len(frozenset().union(*packing_edges)) == 72

    # Enumerate every unordered three-packing and classify it independently.
    classes: dict[tuple[int, ...], list[tuple[tuple[int, ...], ...]]] = collections.defaultdict(list)
    for core in itertools.combinations(BLOCKS, 3):
        if all(disjoint(a, b) for a, b in itertools.combinations(core, 2)):
            classes[signature(core)].append(core)
    assert len(classes) == 10
    orbit_counts = [len(classes[key]) for key in sorted(classes)]
    assert orbit_counts == [15120, 7560, 7560, 11340, 45360, 45360, 3780, 22680, 30240, 1260]
    assert sum(orbit_counts) == 190260

    # Regenerate each mathematical CNF and demand byte identity with the
    # checked DIMACS.  This catches mismatched core order or stale artifacts.
    certdir = HERE / "certificates"
    formula_rows = []
    for type_id, key in enumerate(sorted(classes), 1):
        core = classes[key][0]
        cnf, meta = build_formula(core)
        expected = certdir / f"type_{type_id:02d}.regenerated.cnf"
        cnf.to_file(str(expected))
        checked = certdir / f"type_{type_id:02d}.cnf"
        assert file_hash(expected) == file_hash(checked), type_id
        expected.unlink()
        formula_rows.append({
            "type": type_id,
            "signature": list(key),
            "labeled_cores": orbit_counts[type_id - 1],
            "compatible_blocks": meta["compatible_blocks"],
            "cnf_sha256": file_hash(checked),
        })

    manifest = json.loads((certdir / "manifest.verified.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ALL_TEN_INDEPENDENT_CERTIFICATES_NATIVE_VERIFIED"
    assert len(manifest["entries"]) == 10
    assert all(row["drat_check"]["verified_marker"] and row["lrat_check"]["verified_marker"]
               for row in manifest["entries"])

    result = {
        "status": "STRUCTURAL_AUDIT_PASS",
        "packing18_blocks": 18,
        "packing18_distinct_triples": 72,
        "labeled_three_packings": 190260,
        "core_isomorphism_types": 10,
        "orbit_counts": orbit_counts,
        "formulas": formula_rows,
        "verified_manifest_sha256": file_hash(certdir / "manifest.verified.json"),
    }
    path = HERE / "structural_audit_result.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
