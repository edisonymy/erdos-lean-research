#!/usr/bin/env python3
"""From-scratch definition-level checker for an exact82/nu2 candidate."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def main(candidate: Path) -> None:
    data = json.loads(candidate.read_text(encoding="utf-8"))
    triples = tuple(itertools.combinations(range(10), 3))
    tid = {e: i for i, e in enumerate(triples)}
    present_raw = [tuple(sorted(e)) for e in data["present_triples"]]
    assert len(present_raw) == 82
    assert len(set(present_raw)) == 82
    assert all(len(e) == 3 and 0 <= e[0] < e[1] < e[2] < 10 for e in present_raw)
    present = {tid[e] for e in present_raw}
    blocks = tuple(itertools.combinations(range(10), 4))
    bedges = tuple(frozenset(tid[e] for e in itertools.combinations(b, 3)) for b in blocks)
    clean = [i for i, es in enumerate(bedges) if es <= present]

    found3 = None
    for i, j, k in itertools.combinations(clean, 3):
        if bedges[i].isdisjoint(bedges[j]) and bedges[i].isdisjoint(bedges[k]) and bedges[j].isdisjoint(bedges[k]):
            found3 = (i, j, k)
            break
    assert found3 is None, [blocks[i] for i in found3]
    found2 = None
    for i, j in itertools.combinations(clean, 2):
        if bedges[i].isdisjoint(bedges[j]):
            found2 = (i, j)
            break
    assert found2 is not None
    report = {
        "status": "DEFINITION_LEVEL_CANDIDATE_VERIFIED",
        "present_edges": 82,
        "clean_tetrahedra": len(clean),
        "packing_number": 2,
        "decomposition_number": 76,
        "turan_input_ex3_10": 75,
        "strict_gap": 1,
        "packing_witness": [list(blocks[i]) for i in found2],
        "turan_dependency": "Published exact value T(10,4,3)=45, equivalently ex_3(10,K4^3)=120-45=75",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("candidate", type=Path)
    a = p.parse_args()
    main(a.candidate)
