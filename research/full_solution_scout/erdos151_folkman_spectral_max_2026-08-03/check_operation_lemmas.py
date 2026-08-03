#!/usr/bin/env python3
"""Exhaustive small-graph checks for the blow-up and join identities in REPORT.md.

This is not used to prove the identities; their proofs are in the report.  It is a
regression checker for definitions, isolated-vertex edge cases, and the code's
interpretation of ``beta`` and ``gamma``.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
OUT = HERE / "check_operation_lemmas.result.json"


def labelled_graphs(n: int):
    edges = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(edges)):
        graph = nx.Graph()
        graph.add_nodes_from(range(n))
        graph.add_edges_from(edge for i, edge in enumerate(edges) if mask >> i & 1)
        yield graph


def clique_masks(graph: nx.Graph, include_singletons: bool) -> list[int]:
    masks = []
    for clique in nx.find_cliques(graph):
        if include_singletons or len(clique) >= 2:
            masks.append(sum(1 << v for v in clique))
    return masks


def avoidance_number(graph: nx.Graph, include_singletons: bool) -> int:
    forbidden = clique_masks(graph, include_singletons)
    n = graph.number_of_nodes()
    best = 0
    for selected in range(1 << n):
        if selected.bit_count() <= best:
            continue
        if all(selected & clique != clique for clique in forbidden):
            best = selected.bit_count()
    return best


def beta(graph: nx.Graph) -> int:
    return avoidance_number(graph, include_singletons=False)


def gamma(graph: nx.Graph) -> int:
    return avoidance_number(graph, include_singletons=True)


def independent_blowup(graph: nx.Graph, t: int) -> nx.Graph:
    n = graph.number_of_nodes()
    result = nx.Graph()
    result.add_nodes_from(range(n * t))
    for u, v in graph.edges():
        result.add_edges_from((u * t + i, v * t + j) for i in range(t) for j in range(t))
    return result


def clique_blowup(graph: nx.Graph, t: int) -> nx.Graph:
    result = independent_blowup(graph, t)
    for v in graph.nodes():
        result.add_edges_from(itertools.combinations(range(v * t, (v + 1) * t), 2))
    return result


def join(graph: nx.Graph, other: nx.Graph) -> nx.Graph:
    n = graph.number_of_nodes()
    m = other.number_of_nodes()
    result = nx.disjoint_union(graph, other)
    result.add_edges_from((u, n + v) for u in range(n) for v in range(m))
    return result


def main() -> None:
    independent_cases = 0
    clique_cases = 0
    join_cases = 0

    # All labelled simple graphs through four vertices, with both t=2 and t=3.
    for n in range(1, 5):
        for graph in labelled_graphs(n):
            beta_g = beta(graph)
            gamma_g = gamma(graph)
            for t in (2, 3):
                observed = beta(independent_blowup(graph, t))
                expected = t * beta_g
                assert observed == expected, ("independent blow-up", n, t, observed, expected)
                independent_cases += 1

                observed = beta(clique_blowup(graph, t))
                expected = (t - 1) * n + gamma_g
                assert observed == expected, ("clique blow-up", n, t, observed, expected)
                clique_cases += 1

    # Every ordered pair of nonempty labelled graphs through three vertices.
    small_graphs = [graph for n in range(1, 4) for graph in labelled_graphs(n)]
    for graph in small_graphs:
        for other in small_graphs:
            observed = beta(join(graph, other))
            expected = max(
                gamma(graph) + other.number_of_nodes(),
                graph.number_of_nodes() + gamma(other),
            )
            assert observed == expected, (
                "join",
                graph.number_of_nodes(),
                other.number_of_nodes(),
                observed,
                expected,
            )
            join_cases += 1

    result = {
        "schema": "erdos151-operation-lemma-check-v1",
        "status": "all assertions passed",
        "definitions": {
            "beta": "largest vertex set containing no inclusion-maximal clique of size at least two",
            "gamma": "largest vertex set containing no inclusion-maximal clique, including singleton maximal cliques",
        },
        "coverage": {
            "independent_blowup": {
                "identity": "beta(G[empty_t]) = t beta(G)",
                "labelled_base_graph_orders": [1, 2, 3, 4],
                "t_values": [2, 3],
                "cases": independent_cases,
            },
            "clique_blowup": {
                "identity": "beta(G[K_t]) = (t-1)|V(G)| + gamma(G)",
                "labelled_base_graph_orders": [1, 2, 3, 4],
                "t_values": [2, 3],
                "cases": clique_cases,
            },
            "join": {
                "identity": "beta(G join H) = max(gamma(G)+|H|, |G|+gamma(H))",
                "ordered_base_graph_orders": [1, 2, 3],
                "cases": join_cases,
            },
        },
        "note": "These finite checks guard implementation semantics; the report supplies general proofs.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
