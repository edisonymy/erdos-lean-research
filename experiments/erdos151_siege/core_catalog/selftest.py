#!/usr/bin/env python3
"""Deterministic unit/smoke tests for the catalogue tools."""

from __future__ import annotations

import itertools
import random

from catalog_lib import (
    arrows_33,
    complement,
    decode_graph6,
    delete_edge,
    edges,
    encode_graph6,
    good_edge_coloring,
    is_minimal_ramsey_33,
    maximum_clique_size,
)
from filter_core_catalog import THRESHOLDS, candidate_cliques


def complete_graph(order: int) -> tuple[int, ...]:
    all_vertices = (1 << order) - 1
    return tuple(all_vertices ^ (1 << vertex) for vertex in range(order))


def random_graph(order: int, seed: int) -> tuple[int, ...]:
    generator = random.Random(seed)
    adjacency = [0] * order
    for upper in range(1, order):
        for lower in range(upper):
            if generator.randrange(2):
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
    return tuple(adjacency)


def brute_good_coloring(adjacency: tuple[int, ...]) -> bool:
    edge_list = edges(adjacency)
    edge_number = {edge: index for index, edge in enumerate(edge_list)}
    triangles = []
    for a, b, c in itertools.combinations(range(len(adjacency)), 3):
        if all(
            ((adjacency[u] >> v) & 1)
            for u, v in ((a, b), (a, c), (b, c))
        ):
            triangles.append(
                (edge_number[(a, b)], edge_number[(a, c)], edge_number[(b, c)])
            )
    for coloring in itertools.product((0, 1), repeat=len(edge_list)):
        if all(not (coloring[x] == coloring[y] == coloring[z]) for x, y, z in triangles):
            return True
    return False


def brute_clique_number(adjacency: tuple[int, ...]) -> int:
    for size in range(len(adjacency), 0, -1):
        for vertices in itertools.combinations(range(len(adjacency)), size):
            if all(
                (adjacency[u] >> v) & 1
                for offset, u in enumerate(vertices)
                for v in vertices[offset + 1 :]
            ):
                return size
    return 0


def main() -> None:
    for order in range(1, 15):
        graph = random_graph(order, 1000 + order)
        assert decode_graph6(encode_graph6(graph)) == graph
        assert complement(complement(graph)) == graph
        assert maximum_clique_size(graph) == brute_clique_number(graph)

    for order in range(1, 7):
        for seed in range(20):
            graph = random_graph(order, 10_000 * order + seed)
            assert (good_edge_coloring(graph) is not None) == brute_good_coloring(graph)

    k5 = complete_graph(5)
    k6 = complete_graph(6)
    assert not arrows_33(k5)
    assert arrows_33(k6)
    assert is_minimal_ramsey_33(k6)
    assert all(not arrows_33(delete_edge(k6, u, v)) for u, v in edges(k6))

    candidates = list(candidate_cliques(k6))
    assert {candidate.size for candidate in candidates} == {2, 3, 4, 5}
    expected = {k: 0 for k in THRESHOLDS}
    for size in THRESHOLDS:
        expected[size] = sum(1 for item in candidates if item.size == size)
    assert expected == {2: 15, 3: 20, 4: 15, 5: 6}
    qualifying_40 = {
        item.size
        for item in candidates
        if item.lhs(40, 6) >= THRESHOLDS[item.size]
    }
    qualifying_41 = {
        item.size
        for item in candidates
        if item.lhs(41, 6) >= THRESHOLDS[item.size]
    }
    assert qualifying_40 == {4, 5}
    assert qualifying_41 == {3, 4, 5}
    print("selftest: ok")


if __name__ == "__main__":
    main()
