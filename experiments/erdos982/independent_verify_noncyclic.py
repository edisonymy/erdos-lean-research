#!/usr/bin/env python3
"""Independent exact verifier for noncyclic Erdős-982 search records.

This intentionally shares no imports with the search.  Convexity is checked
by all edge/vertex half-plane incidences, distance counts by sorting integer
values, and cocircularity by an integer 4-by-4 determinant.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Sequence

Point = tuple[int, int]


def det(matrix: Sequence[Sequence[int]]) -> int:
    """Leibniz determinant (only used at dimension four)."""
    total = 0
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(len(permutation)) for j in range(i + 1, len(permutation))
        )
        product = 1
        for row, column in enumerate(permutation):
            product *= matrix[row][column]
        total += (-1 if inversions % 2 else 1) * product
    return total


def incircle_determinant(a: Point, b: Point, c: Point, d: Point) -> int:
    return det([
        [x * x + y * y, x, y, 1]
        for x, y in (a, b, c, d)
    ])


def verify_points(raw_points: Sequence[object]) -> dict[str, object]:
    points: list[Point] = []
    for p in raw_points:
        if isinstance(p, dict):
            points.append((int(p["X"]), int(p["Y"])))
        else:
            points.append(tuple(map(int, p)))
    n = len(points)
    assert len(set(points)) == n

    # For a strictly CCW convex polygon, every other vertex is strictly left
    # of every oriented edge (apart from that edge's two endpoints).
    edge_determinants: list[int] = []
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % n]
        for j, (x, y) in enumerate(points):
            if j in (i, (i + 1) % n):
                continue
            value = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
            edge_determinants.append(value)
            assert value > 0, (i, j, value)

    counts: list[int] = []
    sorted_distance_rows: list[list[int]] = []
    for i, (x, y) in enumerate(points):
        values = sorted(
            (x - u) ** 2 + (y - v) ** 2
            for j, (u, v) in enumerate(points) if j != i
        )
        sorted_distance_rows.append(values)
        counts.append(1 + sum(values[k] != values[k - 1] for k in range(1, len(values))))

    circle_determinants = [
        incircle_determinant(points[0], points[1], points[2], points[i])
        for i in range(3, n)
    ]
    cocircular = all(value == 0 for value in circle_determinants)
    threshold = n // 2
    verified = {
        "n": n,
        "strictly_convex_counterclockwise": True,
        "minimum_edge_vertex_determinant": min(edge_determinants),
        "distinct_squared_distance_counts": counts,
        "maximum": max(counts),
        "threshold": threshold,
        "margin": max(counts) - threshold,
        "counterexample": max(counts) < threshold,
        "cocircular": cocircular,
        "circle_determinants": circle_determinants,
        "sorted_squared_distances": sorted_distance_rows,
    }
    assert cocircular is False
    return verified


def verify_record(record: dict[str, object]) -> dict[str, object]:
    verified = verify_points(record["points_counterclockwise"])
    assert verified["n"] == record["n"]
    assert verified["distinct_squared_distance_counts"] == record["distinct_squared_distance_counts"]
    assert verified["maximum"] == record["maximum"]
    return verified


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if "results" in payload:
        verified = [
            verify_record(record)
            for record in payload["results"]
            if "points_counterclockwise" in record
        ]
    elif "sides" in payload:
        verified = []
        for side in payload["sides"]:
            if side["best_polygon"] is None:
                continue
            item = verify_points(side["best_polygon"])
            assert item["maximum"] == side["best_maximum"]
            item["coordinate_span"] = side["side"]
            verified.append(item)
    else:
        raise ValueError("unrecognized search-output schema")
    result = {"source": str(args.input), "verified_results": verified}
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
