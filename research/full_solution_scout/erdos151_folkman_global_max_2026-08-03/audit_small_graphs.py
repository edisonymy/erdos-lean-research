#!/usr/bin/env python3
"""Exact small-graph audit for the global Erdős #151 / Folkman lane.

The script uses only the Python standard library and enumerates every labelled
simple graph on at most six vertices.  It checks:

* edge-arrowing (3,3) implies vertex-arrowing (3,3);
* the explicit edge colouring induced by a two-part triangle-free vertex
  partition really has no monochromatic triangle;
* triangle vertex-deletion number at most two precludes edge-arrowing (3,3);
* K5 separates vertex-arrowing from edge-arrowing, while K6 edge-arrows;
* beta(G-e) <= beta(G)+1 for every present edge.

Here beta is the largest size of a vertex set containing no nontrivial
inclusion-maximal clique of the ambient graph.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


@dataclass(frozen=True)
class Universe:
    n: int
    edges: tuple[tuple[int, int], ...]
    edge_index: dict[tuple[int, int], int]
    clique_edges: tuple[int, ...]
    triangles: tuple[tuple[int, int], ...]


def make_universe(n: int) -> Universe:
    edges = tuple(combinations(range(n), 2))
    edge_index = {e: i for i, e in enumerate(edges)}
    clique_edges: list[int] = []
    for vertices in range(1 << n):
        mask = 0
        members = [v for v in range(n) if vertices & (1 << v)]
        for u, v in combinations(members, 2):
            mask |= 1 << edge_index[(u, v)]
        clique_edges.append(mask)
    triangles = tuple(
        (sum(1 << v for v in tri), clique_edges[sum(1 << v for v in tri)])
        for tri in combinations(range(n), 3)
    )
    return Universe(n, edges, edge_index, tuple(clique_edges), triangles)


def present_triangles(universe: Universe, graph: int) -> tuple[tuple[int, int], ...]:
    return tuple((vs, es) for vs, es in universe.triangles if es & ~graph == 0)


def triangle_free_on(triangles: tuple[tuple[int, int], ...], vertices: int) -> bool:
    return all(vs & ~vertices != 0 for vs, _ in triangles)


def good_vertex_partition(universe: Universe, graph: int) -> int | None:
    """Return one side of a partition into two triangle-free sets, if one exists."""
    triangles = present_triangles(universe, graph)
    all_vertices = (1 << universe.n) - 1
    for side in range(1 << universe.n):
        if triangle_free_on(triangles, side) and triangle_free_on(
            triangles, all_vertices ^ side
        ):
            return side
    return None


def partition_edge_colouring(universe: Universe, graph: int, side: int) -> int:
    """Return the red edges: endpoints in the same side; cross edges are blue."""
    red = 0
    for i, (u, v) in enumerate(universe.edges):
        if not (graph & (1 << i)):
            continue
        if bool(side & (1 << u)) == bool(side & (1 << v)):
            red |= 1 << i
    return red


def colouring_is_good(universe: Universe, graph: int, red: int) -> bool:
    blue = graph ^ red
    for _, triangle in present_triangles(universe, graph):
        if triangle & ~red == 0 or triangle & ~blue == 0:
            return False
    return True


def edge_arrows_33(universe: Universe, graph: int) -> bool:
    """True iff every red/blue edge-colouring has a monochromatic triangle."""
    triangles = tuple(es for _, es in present_triangles(universe, graph))
    if not triangles:
        return False
    red = graph
    while True:
        blue = graph ^ red
        if all(t & ~red != 0 and t & ~blue != 0 for t in triangles):
            return False
        if red == 0:
            break
        red = (red - 1) & graph
    return True


def triangle_deletion_at_most_two(universe: Universe, graph: int) -> bool:
    triangles = present_triangles(universe, graph)
    all_vertices = (1 << universe.n) - 1
    for deleted in range(1 << universe.n):
        if deleted.bit_count() <= 2 and triangle_free_on(
            triangles, all_vertices ^ deleted
        ):
            return True
    return False


def maximal_nontrivial_cliques(universe: Universe, graph: int) -> tuple[int, ...]:
    result: list[int] = []
    all_vertices = (1 << universe.n) - 1
    for clique in range(1 << universe.n):
        if clique.bit_count() < 2:
            continue
        if universe.clique_edges[clique] & ~graph:
            continue
        outside = all_vertices ^ clique
        maximal = True
        while outside:
            bit = outside & -outside
            outside ^= bit
            if universe.clique_edges[clique | bit] & ~graph == 0:
                maximal = False
                break
        if maximal:
            result.append(clique)
    return tuple(result)


def beta(universe: Universe, graph: int) -> int:
    maximal_cliques = maximal_nontrivial_cliques(universe, graph)
    candidates = sorted(range(1 << universe.n), key=int.bit_count, reverse=True)
    for vertices in candidates:
        if all(clique & ~vertices != 0 for clique in maximal_cliques):
            return vertices.bit_count()
    raise AssertionError("the empty set must be admissible")


def complete_graph(universe: Universe) -> int:
    return (1 << len(universe.edges)) - 1


def main() -> None:
    totals = {
        "graphs": 0,
        "edge_arrowing_graphs": 0,
        "vertex_arrowing_graphs": 0,
        "strict_vertex_not_edge_examples": 0,
        "present_edges_checked_for_beta_lipschitz": 0,
    }
    violations = {
        "edge_arrow_implies_vertex_arrow": [],
        "partition_colour_construction": [],
        "deletion_at_most_two_precludes_edge_arrow": [],
        "beta_edge_deletion_lipschitz": [],
    }
    by_n: dict[str, dict[str, int]] = {}

    for n in range(1, 7):
        universe = make_universe(n)
        graph_count = 1 << len(universe.edges)
        beta_cache = [beta(universe, graph) for graph in range(graph_count)]
        row = {
            "graphs": graph_count,
            "edge_arrowing_graphs": 0,
            "vertex_arrowing_graphs": 0,
        }
        for graph in range(graph_count):
            totals["graphs"] += 1
            side = good_vertex_partition(universe, graph)
            vertex_arrow = side is None
            edge_arrow = edge_arrows_33(universe, graph)
            if vertex_arrow:
                totals["vertex_arrowing_graphs"] += 1
                row["vertex_arrowing_graphs"] += 1
            else:
                red = partition_edge_colouring(universe, graph, side)
                if not colouring_is_good(universe, graph, red):
                    violations["partition_colour_construction"].append([n, graph, side])
            if edge_arrow:
                totals["edge_arrowing_graphs"] += 1
                row["edge_arrowing_graphs"] += 1
                if not vertex_arrow:
                    violations["edge_arrow_implies_vertex_arrow"].append([n, graph])
            if vertex_arrow and not edge_arrow:
                totals["strict_vertex_not_edge_examples"] += 1
            if triangle_deletion_at_most_two(universe, graph) and edge_arrow:
                violations["deletion_at_most_two_precludes_edge_arrow"].append([n, graph])

            for edge_index in range(len(universe.edges)):
                edge_bit = 1 << edge_index
                if not (graph & edge_bit):
                    continue
                totals["present_edges_checked_for_beta_lipschitz"] += 1
                deleted = graph ^ edge_bit
                if beta_cache[deleted] > beta_cache[graph] + 1:
                    violations["beta_edge_deletion_lipschitz"].append(
                        [n, graph, edge_index, beta_cache[graph], beta_cache[deleted]]
                    )
        by_n[str(n)] = row

    u5 = make_universe(5)
    u6 = make_universe(6)
    k5 = complete_graph(u5)
    k6 = complete_graph(u6)
    named_checks = {
        "K5_vertex_arrows_33": good_vertex_partition(u5, k5) is None,
        "K5_edge_arrows_33": edge_arrows_33(u5, k5),
        "K6_edge_arrows_33": edge_arrows_33(u6, k6),
        "K5_beta": beta(u5, k5),
        "K6_beta": beta(u6, k6),
    }
    source = Path(__file__).read_bytes()
    result = {
        "scope": "all labelled simple graphs on 1..6 vertices",
        "totals": totals,
        "by_n": by_n,
        "violations": violations,
        "named_checks": named_checks,
        "script_sha256": hashlib.sha256(source).hexdigest(),
        "all_assertions_pass": all(not items for items in violations.values())
        and named_checks["K5_vertex_arrows_33"]
        and not named_checks["K5_edge_arrows_33"]
        and named_checks["K6_edge_arrows_33"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
