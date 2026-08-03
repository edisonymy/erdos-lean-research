#!/usr/bin/env python3
"""Independent definition-level checks for the retained #982 artifacts.

This file deliberately imports none of the search modules.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


N = 10
Q = 5
EDGES = tuple(itertools.combinations(range(N), 2))


def edge(a, b):
    return (a, b) if a < b else (b, a)


def crosses(e, f):
    a, b = e
    c, d = f
    return len({a, b, c, d}) == 4 and ((a < c < b < d) or (c < a < d < b))


def side(base, apex):
    a, b = base
    return 0 if a < apex < b else 1


def validate_pattern(record):
    values = tuple(int(x) for x in record["edge_colours"])
    assert len(values) == len(EDGES)
    assert set(values) == set(range(Q))
    colour = dict(zip(EDGES, values))

    local_counts = []
    for v in range(N):
        local_counts.append(len({colour[edge(v, w)] for w in range(N) if w != v}))
    assert max(local_counts) <= 4

    order0 = tuple(record["cap_order_at_0"])
    order4 = tuple(record["cap_order_at_4"])
    assert tuple(colour[edge(0, j)] for j in (1, 2, 3, 4)) == order0
    assert tuple(colour[edge(4, j)] for j in (3, 2, 1, 0)) == order4
    assert len(set(order0)) == len(set(order4)) == 4

    shortest = int(record["shortest_colour"])
    longest = int(record["longest_colour"])
    total_orders = []
    for order in itertools.permutations(range(Q)):
        if order[0] != shortest or order[-1] != longest:
            continue
        rank = {c: i for i, c in enumerate(order)}
        if all(rank[a] < rank[b] for a, b in zip(order0, order0[1:])) and all(
            rank[a] < rank[b] for a, b in zip(order4, order4[1:])
        ):
            total_orders.append(order)
    assert total_orders

    for base in EDGES:
        for which in (0, 1):
            count = 0
            for apex in range(N):
                if apex in base or side(base, apex) != which:
                    continue
                count += colour[edge(apex, base[0])] == colour[edge(apex, base[1])]
            assert count <= 1

    for quad in itertools.combinations(range(N), 4):
        assert len({colour[e] for e in itertools.combinations(quad, 2)}) > 1

    for e, f in itertools.combinations(EDGES, 2):
        if crosses(e, f):
            assert not (colour[e] == colour[f] == shortest)
        elif len(set(e + f)) == 4:
            assert not (colour[e] == colour[f] == longest)

    assert [values.count(c) for c in range(Q)] == record["edge_counts"]
    return {"compatible_total_orders": len(total_orders), "local_colour_counts": local_counts}


def tri_cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def tri_d2(a, b):
    x, y = a[0] - b[0], a[1] - b[1]
    return x * x + x * y + y * y


def validate_lattice(payload):
    best = payload["best"]
    points = tuple(tuple(map(int, p)) for p in best["axial_points_counterclockwise"])
    assert len(points) == len(set(points)) == 10
    turns = [tri_cross(points[i], points[(i + 1) % 10], points[(i + 2) % 10]) for i in range(10)]
    assert min(turns) > 0
    assert turns == best["turn_determinants"]
    sets = [
        sorted({tri_d2(p, q) for j, q in enumerate(points) if i != j})
        for i, p in enumerate(points)
    ]
    counts = [len(s) for s in sets]
    assert sets == best["squared_distance_sets"]
    assert counts == best["local_distance_counts"]
    assert max(counts) == best["maximum"] == 7
    assert not best["counterexample"]
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--patterns", type=Path, nargs="+", required=True)
    parser.add_argument("--lattice", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    pattern_results = []
    for path in args.patterns:
        payload = json.loads(path.read_text(encoding="utf-8"))
        checks = [validate_pattern(record) for record in payload["retained"]]
        pattern_results.append({
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "retained_checked": len(checks),
            "pattern_checks": checks,
            "verified": True,
        })

    lattice_payload = json.loads(args.lattice.read_text(encoding="utf-8"))
    lattice_counts = validate_lattice(lattice_payload)
    result = {
        "status": "VERIFIED",
        "pattern_files": pattern_results,
        "lattice": {
            "path": str(args.lattice),
            "sha256": hashlib.sha256(args.lattice.read_bytes()).hexdigest(),
            "best_profile": lattice_counts,
            "verified": True,
        },
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
