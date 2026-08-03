#!/usr/bin/env python3
"""Exhaustively cross-check the static C8 predicate on small hypergraphs.

All families of subsets of size at least three on at most five points are
enumerated.  Among linear families, the packet's four-point quadrilateral
predicate is compared with a generic simple-cycle search on the incidence
graph.  This is independent of the SAT implementation.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


def is_linear(lines: tuple[frozenset[int], ...]) -> bool:
    seen = set()
    for line in lines:
        for pair in itertools.combinations(sorted(line), 2):
            if pair in seen:
                return False
            seen.add(pair)
    return True


def has_static_quadrilateral(sigma: int, lines: tuple[frozenset[int], ...]) -> bool:
    def collinear(a: int, b: int) -> bool:
        return any({a, b} <= line for line in lines)

    def triple(a: int, b: int, c: int) -> bool:
        return any({a, b, c} <= line for line in lines)

    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
            p0, p1, p2, p3 = cyc
            if (collinear(p0, p1) and collinear(p1, p2)
                    and collinear(p2, p3) and collinear(p3, p0)
                    and not triple(p0, p1, p2)
                    and not triple(p1, p2, p3)
                    and not triple(p2, p3, p0)
                    and not triple(p3, p0, p1)):
                return True
    return False


def has_incidence_c8(sigma: int, lines: tuple[frozenset[int], ...]) -> bool:
    n = sigma + len(lines)
    adj = [set() for _ in range(n)]
    for j, line in enumerate(lines):
        for p in line:
            adj[p].add(sigma + j)
            adj[sigma + j].add(p)
    length = 8
    for root in range(n):
        path = [root]
        used = {root}

        def dfs(v: int) -> bool:
            if len(path) == length:
                return root in adj[v]
            for w in adj[v]:
                if w <= root or w in used:
                    continue
                used.add(w)
                path.append(w)
                if dfs(w):
                    return True
                path.pop()
                used.remove(w)
            return False

        if dfs(root):
            return True
    return False


def main(output: Path) -> int:
    records = []
    total_mismatches = 0
    for sigma in (4, 5):
        possible = tuple(
            frozenset(subset)
            for size in range(3, sigma + 1)
            for subset in itertools.combinations(range(sigma), size)
        )
        linear_count = c8_count = mismatches = 0
        for mask in range(1 << len(possible)):
            lines = tuple(possible[j] for j in range(len(possible)) if mask >> j & 1)
            if not is_linear(lines):
                continue
            linear_count += 1
            actual = has_incidence_c8(sigma, lines)
            static = has_static_quadrilateral(sigma, lines)
            c8_count += int(actual)
            if actual != static:
                mismatches += 1
        total_mismatches += mismatches
        records.append({
            "family_class": "all lines of size at least three",
            "sigma": sigma,
            "all_families": 1 << len(possible),
            "linear_families": linear_count,
            "families_with_c8": c8_count,
            "mismatches": mismatches,
        })
    # A positive-pattern audit: every four-line 3-uniform family on eight
    # points.  This includes genuine quadrilaterals, unlike the tiny all-size
    # cases above, while remaining exhaustible.
    sigma = 8
    triples = tuple(frozenset(t) for t in itertools.combinations(range(sigma), 3))
    linear_count = c8_count = mismatches = 0
    for lines in itertools.combinations(triples, 4):
        if not is_linear(lines):
            continue
        linear_count += 1
        actual = has_incidence_c8(sigma, lines)
        static = has_static_quadrilateral(sigma, lines)
        c8_count += int(actual)
        if actual != static:
            mismatches += 1
    total_mismatches += mismatches
    records.append({
        "sigma": sigma,
        "family_class": "all four-line 3-uniform families",
        "all_families": 367290,
        "linear_families": linear_count,
        "families_with_c8": c8_count,
        "mismatches": mismatches,
    })
    result = {"records": records, "total_mismatches": total_mismatches,
              "verdict": "PASS" if total_mismatches == 0 else "FAIL"}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(total_mismatches != 0)


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
