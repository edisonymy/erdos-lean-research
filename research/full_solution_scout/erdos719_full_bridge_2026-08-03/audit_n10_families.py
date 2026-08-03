#!/usr/bin/env python3
"""Reproduce two finite obstructions used in the n=10 counterexample scout.

This is not an exhaustive search for an 82-edge counterexample.  It audits:

1. the standard 75-edge (3,3,4)-part Turan construction; and
2. the deliberately restricted ansatz in which the clean tetrahedra are
   exactly the union of two triple-stars.
"""

from __future__ import annotations

import itertools
import json

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix


V = tuple(range(10))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {e: i for i, e in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))
BEDGES = tuple(frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in BLOCKS)


def turan_audit() -> dict:
    a, b, c = {0, 1, 2}, {3, 4, 5}, {6, 7, 8, 9}

    def present(e: tuple[int, int, int]) -> bool:
        counts = (len(set(e) & a), len(set(e) & b), len(set(e) & c))
        return counts in {(1, 1, 1), (2, 1, 0), (0, 2, 1), (1, 0, 2)}

    p = {i for i, e in enumerate(TRIPLES) if present(e)}
    h = set(range(len(TRIPLES))) - p
    missing_per_block = [len(es & h) for es in BEDGES]
    unique_charge = {i: 0 for i in h}
    for es in BEDGES:
        absent = es & h
        if len(absent) == 1:
            unique_charge[next(iter(absent))] += 1
    charge_distribution = {
        str(value): sum(count == value for count in unique_charge.values())
        for value in sorted(set(unique_charge.values()))
    }
    block_distribution = {
        str(value): missing_per_block.count(value)
        for value in sorted(set(missing_per_block))
    }
    assert len(p) == 75 and len(h) == 45
    assert charge_distribution == {"3": 35, "4": 10}
    assert block_distribution == {"1": 145, "2": 45, "4": 20}
    return {
        "present_edges": len(p),
        "missing_edges": len(h),
        "unique_new_tetrahedra_per_added_edge": charge_distribution,
        "tetrahedra_by_original_missing_edge_count": block_distribution,
        "consequence": "adding t missing edges creates at least 3t clean tetrahedra",
    }


def min_hitting_set(allowed: list[int], obligations: list[frozenset[int]]) -> int:
    position = {edge: j for j, edge in enumerate(allowed)}
    rows, cols = [], []
    for i, obligation in enumerate(obligations):
        choices = obligation & position.keys()
        assert choices
        for edge in choices:
            rows.append(i)
            cols.append(position[edge])
    matrix = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(obligations), len(allowed)))
    result = milp(
        c=np.ones(len(allowed)),
        integrality=np.ones(len(allowed)),
        bounds=Bounds(np.zeros(len(allowed)), np.ones(len(allowed))),
        constraints=LinearConstraint(matrix, np.ones(len(obligations)), np.full(len(obligations), np.inf)),
        options={"presolve": True},
    )
    assert result.success and result.fun is not None
    return int(round(result.fun))


def two_triple_star_audit(intersection: int) -> dict:
    first = (0, 1, 2)
    second = {
        0: (3, 4, 5),
        1: (0, 3, 4),
        2: (0, 1, 3),
    }[intersection]
    centers = (set(first), set(second))
    q = {
        i for i, block in enumerate(BLOCKS)
        if any(center <= set(block) for center in centers)
    }
    required_present = frozenset().union(*(BEDGES[i] for i in q))
    non_q = set(range(len(BLOCKS))) - q
    forced_extra = [i for i in non_q if BEDGES[i] <= required_present]
    result = {
        "center_intersection": intersection,
        "intended_clean_tetrahedra": len(q),
        "required_present_triples": len(required_present),
        "forced_extra_clean_tetrahedra": len(forced_extra),
    }
    if forced_extra:
        result["status"] = "UNREALIZABLE_EXACT_FAMILY"
    else:
        allowed_missing = sorted(set(range(len(TRIPLES))) - required_present)
        obligations = [BEDGES[i] for i in sorted(non_q)]
        optimum = min_hitting_set(allowed_missing, obligations)
        assert intersection == 2 and optimum == 48
        result.update({
            "status": "REALIZABLE_ONLY_WITH_TOO_MANY_MISSING_TRIPLES",
            "minimum_missing_triples": optimum,
            "exact82_target_missing_triples": 38,
        })
    return result


def main() -> None:
    report = {
        "scope": "structured-family audit only; not an exhaustive counterexample search",
        "turan_334": turan_audit(),
        "two_triple_stars": [two_triple_star_audit(i) for i in range(3)],
    }
    expected = [
        (14, 44, 9),
        (14, 40, 1),
        (13, 34, 0),
    ]
    observed = [
        (x["intended_clean_tetrahedra"], x["required_present_triples"], x["forced_extra_clean_tetrahedra"])
        for x in report["two_triple_stars"]
    ]
    assert observed == expected
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
