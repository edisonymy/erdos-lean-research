#!/usr/bin/env python3
"""Independent exhaustive audit of the C# lattice enumerator at small spans.

This uses angular sorting about the exact centroid rather than a monotone-chain
hull.  The default span 4 audit is small enough for a standard-library Python
run and reproduces all C# counts and objective histograms there.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
from pathlib import Path

Point = tuple[int, int]


def determinant4(matrix: list[list[int]]) -> int:
    total = 0
    for permutation in itertools.permutations(range(4)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(4) for j in range(i + 1, 4)
        )
        product = 1
        for row in range(4):
            product *= matrix[row][permutation[row]]
        total += (-1 if inversions % 2 else 1) * product
    return total


def incircle(a: Point, b: Point, c: Point, d: Point) -> int:
    return determinant4([[x * x + y * y, x, y, 1] for x, y in (a, b, c, d)])


def angular_order(points: tuple[Point, ...]) -> list[Point]:
    n = len(points)
    sum_x = sum(x for x, _ in points)
    sum_y = sum(y for _, y in points)

    def compare(a: Point, b: Point) -> int:
        ax, ay = n * a[0] - sum_x, n * a[1] - sum_y
        bx, by = n * b[0] - sum_x, n * b[1] - sum_y
        half_a = 0 if ay > 0 or (ay == 0 and ax >= 0) else 1
        half_b = 0 if by > 0 or (by == 0 and bx >= 0) else 1
        if half_a != half_b:
            return -1 if half_a < half_b else 1
        value = ax * by - ay * bx
        if value:
            return -1 if value > 0 else 1
        norm_a, norm_b = ax * ax + ay * ay, bx * bx + by * by
        return (norm_a > norm_b) - (norm_a < norm_b)

    return sorted(points, key=functools.cmp_to_key(compare))


def strict_polygon(points: tuple[Point, ...]) -> list[Point] | None:
    ordered = angular_order(points)
    n = len(ordered)
    turns = []
    for i in range(n):
        a, b, c = ordered[i], ordered[(i + 1) % n], ordered[(i + 2) % n]
        turns.append((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
    return ordered if all(value > 0 for value in turns) else None


def maximum_distinct(points: list[Point]) -> int:
    return max(
        len({
            (x - u) ** 2 + (y - v) ** 2
            for j, (u, v) in enumerate(points) if i != j
        })
        for i, (x, y) in enumerate(points)
    )


def audit_side(side: int) -> dict[str, object]:
    lattice = tuple((x, y) for x in range(side + 1) for y in range(side + 1))
    normalized = convex = noncocircular = 0
    histogram: dict[int, int] = {}
    for subset in itertools.combinations(lattice, 8):
        if subset[0][0] != 0 or subset[-1][0] != side or not any(y == 0 for _, y in subset):
            continue
        normalized += 1
        polygon = strict_polygon(subset)
        if polygon is None:
            continue
        convex += 1
        if all(incircle(polygon[0], polygon[1], polygon[2], p) == 0 for p in polygon[3:]):
            continue
        noncocircular += 1
        maximum = maximum_distinct(polygon)
        histogram[maximum] = histogram.get(maximum, 0) + 1
    return {
        "side": side,
        "normalized_subsets": normalized,
        "strictly_convex": convex,
        "noncocircular": noncocircular,
        "maximum_histogram": histogram,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--max-side", type=int, default=4)
    args = parser.parse_args()
    stored = json.loads(args.run.read_text(encoding="utf-8"))
    stored_by_side = {entry["side"]: entry for entry in stored["sides"]}
    audited = []
    for side in range(2, args.max_side + 1):
        result = audit_side(side)
        reference = stored_by_side[side]
        expected_histogram = {
            entry["maximum"]: entry["count"]
            for entry in reference["maximum_histogram"]
        }
        assert result["normalized_subsets"] == reference["normalized_subsets"]
        assert result["strictly_convex"] == reference["strictly_convex"]
        assert result["noncocircular"] == reference["noncocircular"]
        assert result["maximum_histogram"] == expected_histogram
        audited.append(result | {"matches": True})
    print(json.dumps({"source": str(args.run), "audited": audited}, indent=2))


if __name__ == "__main__":
    main()
