#!/usr/bin/env python3
"""Enumerate abstract complete-bipartite block profiles in the #128 d=3 case.

This does not enumerate graphs or neighbourhood labels.  The classification
lemma says G[O] is a disjoint union of complete bipartite blocks and isolated
vertices.  We list only the integer block-size profiles on ten vertices that
have alpha(G[O]) <= 6 and whose every eight vertices span at least six edges.
"""

from __future__ import annotations

import itertools
import json


def min_after_delete_two(blocks: tuple[tuple[int, int], ...], isolates: int) -> int:
    # Represent only the abstract block graph; exact over all pairs deleted.
    vertices: list[tuple[int, int]] = []
    for j, (p, q) in enumerate(blocks):
        vertices += [(j, 0)] * p + [(j, 1)] * q
    vertices += [(-1, k) for k in range(isolates)]
    best = 10**9
    for deleted in itertools.combinations(range(len(vertices)), 2):
        counts = [[p, q] for p, q in blocks]
        for idx in deleted:
            j, side = vertices[idx]
            if j >= 0:
                counts[j][side] -= 1
        best = min(best, sum(p * q for p, q in counts))
    return best


def main() -> None:
    profiles = set()
    possible = [(p, q) for p in range(1, 11) for q in range(p, 11)
                if p + q <= 10]

    def block_profiles(remaining: int, start: int = 0):
        if remaining == 0:
            yield ()
        for j in range(start, len(possible)):
            block = possible[j]
            used = sum(block)
            if used > remaining:
                continue
            for tail in block_profiles(remaining - used, j):
                yield (block,) + tail

    for isolates in range(11):
        for blocks in block_profiles(10 - isolates):
            alpha = isolates + sum(q for _, q in blocks)
            if alpha > 6:
                continue
            minimum = min_after_delete_two(blocks, isolates)
            if minimum >= 6:
                profiles.add((isolates, blocks, alpha, minimum))
    out = [{"isolates": s, "blocks": b, "alpha_O": a, "min_edges_on_8": m}
           for s, b, a, m in sorted(profiles)]
    print(json.dumps({"count": len(out), "profiles": out}, indent=2))


if __name__ == "__main__":
    main()
