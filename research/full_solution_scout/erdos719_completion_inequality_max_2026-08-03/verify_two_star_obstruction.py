#!/usr/bin/env python3
"""Check the two-star equality model and its realizability obstruction."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def packing_number(quads: list[frozenset[int]]) -> int:
    best = 0
    for mask in range(1 << len(quads)):
        if mask.bit_count() <= best:
            continue
        chosen = [quads[i] for i in range(len(quads)) if mask >> i & 1]
        if all(len(a & b) <= 2 for i, a in enumerate(chosen) for b in chosen[i + 1 :]):
            best = len(chosen)
    return best


def analyze(a: frozenset[int], b: frozenset[int]) -> dict:
    quads = [
        frozenset(Q)
        for Q in itertools.combinations(range(10), 4)
        if a <= frozenset(Q) or b <= frozenset(Q)
    ]
    shadow = {
        frozenset(e)
        for Q in quads
        for e in itertools.combinations(sorted(Q), 3)
    }
    forced_extra = [
        frozenset(Q)
        for Q in itertools.combinations(range(10), 4)
        if frozenset(Q) not in quads
        and all(frozenset(e) in shadow for e in itertools.combinations(Q, 3))
    ]
    return {
        "center_intersection": len(a & b),
        "quad_count": len(quads),
        "packing_number": packing_number(quads),
        "forced_present_triple_count": len(shadow),
        "forced_extra_quads": [sorted(Q) for Q in forced_extra],
        "realizable_as_exact_clean_family": not forced_extra,
    }


def main() -> None:
    a = frozenset((0, 1, 2))
    result = {
        "disjoint_centers": analyze(a, frozenset((3, 4, 5))),
        "one_point_intersection": analyze(a, frozenset((2, 3, 4))),
        "two_point_intersection_control": analyze(a, frozenset((1, 2, 3))),
    }
    assert result["disjoint_centers"]["quad_count"] == 14
    assert result["one_point_intersection"]["quad_count"] == 14
    assert result["disjoint_centers"]["packing_number"] == 2
    assert result["one_point_intersection"]["packing_number"] == 2
    assert not result["disjoint_centers"]["realizable_as_exact_clean_family"]
    assert not result["one_point_intersection"]["realizable_as_exact_clean_family"]
    out = Path(__file__).with_name("two_star_obstruction_check.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
