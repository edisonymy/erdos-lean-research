#!/usr/bin/env python3
"""Finite audit of the two structural facts used in the n=9 proof note."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def main() -> None:
    four_sets = [frozenset(x) for x in itertools.combinations(range(9), 4)]
    checked_configurations = 0
    # If A,B are distinct members of a 3-intersecting 4-uniform family,
    # S=A∩B and U=A∪B.  Once some C omits part of S, every further member D
    # compatible with A,B,C must lie in U.
    for a_pos, a in enumerate(four_sets):
        for b in four_sets[a_pos + 1 :]:
            if len(a & b) != 3:
                continue
            s = a & b
            u = a | b
            for c in four_sets:
                if len(c & a) < 3 or len(c & b) < 3 or s <= c:
                    continue
                if not c <= u:
                    raise AssertionError("third member violates five-set classification")
                for d in four_sets:
                    if min(len(d & a), len(d & b), len(d & c)) >= 3:
                        checked_configurations += 1
                        if not d <= u:
                            raise AssertionError("fourth member violates five-set classification")

    u = frozenset(range(5))
    cover_triples = [frozenset((0, 1, 2)), frozenset((0, 3, 4)), frozenset((1, 2, 3))]
    internal_four_sets = [frozenset(x) for x in itertools.combinations(u, 4)]
    if not all(any(t <= q for t in cover_triples) for q in internal_four_sets):
        raise AssertionError("three-triple cover misses an internal four-set")

    payload = {
        "schema": "erdos719-n9-structure-check-v1",
        "status": "VERIFIED_FINITE_STRUCTURE",
        "four_set_count": len(four_sets),
        "classification_configurations_checked": checked_configurations,
        "internal_four_set_count": len(internal_four_sets),
        "internal_cover_triples": [sorted(x) for x in cover_triples],
        "consequence_with_t9_30": "missing>=27, hence edges<=57 and edges-3<=54",
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    out = Path(__file__).with_name("structure_checked.json")
    out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
