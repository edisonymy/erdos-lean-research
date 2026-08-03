#!/usr/bin/env python3
"""Definition-level checks for the finite local facts in THRESHOLD7_LINE_GRAPH.md."""

from __future__ import annotations

import itertools
import json


def graph(n: int, edges: list[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for a, b in edges:
        assert a != b and b not in adj[a]
        adj[a].add(b)
        adj[b].add(a)
    return adj


def triangles(adj: list[set[int]]) -> list[tuple[int, int, int]]:
    return [
        triple
        for triple in itertools.combinations(range(len(adj)), 3)
        if all(b in adj[a] for a, b in itertools.combinations(triple, 2))
    ]


def induced_edges(adj: list[set[int]], vertices: set[int]) -> int:
    return sum(b in adj[a] for a, b in itertools.combinations(vertices, 2))


def connected(adj: list[set[int]], vertices: set[int]) -> bool:
    if not vertices:
        return True
    seen = {next(iter(vertices))}
    todo = list(seen)
    while todo:
        a = todo.pop()
        for b in adj[a] & vertices:
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen == vertices


def audit() -> dict:
    types = {
        "B": graph(5, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]),
        "D": graph(5, [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]),
        "J": graph(6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3)]),
    }
    expected_degrees = {
        "B": [2, 2, 2, 2, 4],
        "D": [2, 2, 3, 3, 4],
        "J": [2, 2, 2, 2, 3, 3],
    }
    rows = {}
    for name, adj in types.items():
        tris = triangles(adj)
        assert sorted(map(len, adj)) == expected_degrees[name]
        if name in {"B", "J"}:
            assert len(tris) == 2
            assert set().union(*map(set, tris)) == set(range(len(adj)))
        degree_three_neighbour_shapes = []
        for v, nbrs in enumerate(adj):
            if len(nbrs) == 3:
                degree_three_neighbour_shapes.append(
                    {
                        "vertex": v,
                        "edges": induced_edges(adj, nbrs),
                        "connected": connected(adj, nbrs),
                    }
                )
        rows[name] = {
            "degree_sequence": sorted(map(len, adj)),
            "triangles": tris,
            "degree_three_neighbour_shapes": degree_three_neighbour_shapes,
        }

    assert all(row["edges"] == 2 and row["connected"] for row in rows["D"]["degree_three_neighbour_shapes"])
    assert all(row["edges"] == 1 and not row["connected"] for row in rows["J"]["degree_three_neighbour_shapes"])

    d = types["D"]
    adjacent_true_twins = []
    for a in range(len(d)):
        for b in d[a]:
            if a < b and d[a] | {a} == d[b] | {b}:
                adjacent_true_twins.append([a, b])
    assert adjacent_true_twins == []

    return {
        "status": "VERIFIED",
        "scope": "local graph identities used in the D-link elimination and Krausz-cover step",
        "types": rows,
        "D_adjacent_true_twins": adjacent_true_twins,
        "checks": {
            "D_degree3_neighbourhood_is_P3": True,
            "J_degree3_neighbourhood_is_K2_plus_isolate": True,
            "D_has_no_adjacent_true_twins": True,
            "B_and_J_each_have_two_triangles_covering_all_vertices": True,
        },
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
