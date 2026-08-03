#!/usr/bin/env python3
"""Independent exact verifier for all threshold-7 local-core survivors.

This uses NetworkX isomorphism for links, CaDiCaL and Z3 independently for
triangle-avoiding edge colorings, and direct assignment checks.  It shares no
link classifier or graph6 parser with the C++ exhaustive scanner.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx
import z3
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "scan_through_12.json"
OUT = HERE / "survivor_verification.json"


def graph_from_edges(n, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(edges)
    return graph


TEMPLATES = {
    "K": graph_from_edges(4, itertools.combinations(range(4), 2)),
    "B": graph_from_edges(
        5, ((0, 1), (0, 4), (1, 4), (2, 3), (2, 4), (3, 4))
    ),
    "J": graph_from_edges(
        5, ((0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4))
    ),
    "D": graph_from_edges(
        6, ((0, 1), (0, 2), (0, 3), (1, 2), (3, 4), (3, 5), (4, 5))
    ),
}


def triangles(graph):
    return [
        triple
        for triple in itertools.combinations(graph.nodes(), 3)
        if all(graph.has_edge(a, b) for a, b in itertools.combinations(triple, 2))
    ]


def clique_number_at_most_four(graph):
    return not any(
        all(graph.has_edge(a, b) for a, b in itertools.combinations(vertices, 2))
        for vertices in itertools.combinations(graph.nodes(), 5)
    )


def classify_links(graph):
    labels = []
    for vertex in graph.nodes():
        link = graph.subgraph(list(graph.neighbors(vertex))).copy()
        hits = [name for name, template in TEMPLATES.items() if nx.is_isomorphic(link, template)]
        if len(hits) != 1:
            raise AssertionError(f"vertex {vertex} has template hits {hits}")
        labels.append(hits[0])
    return labels


def direct_avoids(mask, edge_count, triangle_edge_ids):
    for triangle in triangle_edge_ids:
        colors = [(mask >> edge_id) & 1 for edge_id in triangle]
        if colors[0] == colors[1] == colors[2]:
            return False
    return True


def cadical_coloring(edge_count, triangle_edge_ids):
    clauses = []
    for triangle in triangle_edge_ids:
        variables = [edge_id + 1 for edge_id in triangle]
        clauses.append(variables)
        clauses.append([-variable for variable in variables])
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        model = solver.get_model()
    return sum(
        1 << (variable - 1)
        for variable in model
        if 1 <= variable <= edge_count
    )


def z3_coloring(edge_count, triangle_edge_ids):
    colors = [z3.Bool(f"edge_{index}") for index in range(edge_count)]
    solver = z3.Solver()
    for triangle in triangle_edge_ids:
        values = [colors[index] for index in triangle]
        solver.add(z3.Or(values))
        solver.add(z3.Or([z3.Not(value) for value in values]))
    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return sum(
        1 << index
        for index, color in enumerate(colors)
        if z3.is_true(model.eval(color, model_completion=True))
    )


def verify_row(row):
    graph = nx.from_graph6_bytes(row["graph6"].encode("ascii"))
    edges = tuple(sorted(tuple(sorted(edge)) for edge in graph.edges()))
    edge_id = {edge: index for index, edge in enumerate(edges)}
    triangle_vertices = triangles(graph)
    triangle_edge_ids = [
        tuple(edge_id[tuple(sorted(edge))] for edge in itertools.combinations(triangle, 2))
        for triangle in triangle_vertices
    ]
    edge_triangle_counts = Counter(
        edge_id for triangle in triangle_edge_ids for edge_id in triangle
    )
    link_labels = classify_links(graph)
    cadical_mask = cadical_coloring(len(edges), triangle_edge_ids)
    z3_mask = z3_coloring(len(edges), triangle_edge_ids)
    constraints = {
        "connected": nx.is_connected(graph),
        "omega_at_most_4": clique_number_at_most_four(graph),
        "every_edge_in_at_least_2_triangles": min(edge_triangle_counts.values()) >= 2,
        "every_vertex_in_at_most_7_triangles": all(
            sum(vertex in triangle for triangle in triangle_vertices) <= 7
            for vertex in graph.nodes()
        ),
        "all_links_exact": "".join(link_labels) == row["vertex_types"],
        "cadical_found_avoiding_coloring": cadical_mask is not None,
        "z3_found_avoiding_coloring": z3_mask is not None,
        "cadical_coloring_directly_checked": (
            cadical_mask is not None
            and direct_avoids(cadical_mask, len(edges), triangle_edge_ids)
        ),
        "z3_coloring_directly_checked": (
            z3_mask is not None
            and direct_avoids(z3_mask, len(edges), triangle_edge_ids)
        ),
    }
    return {
        "graph6": row["graph6"],
        "n": graph.number_of_nodes(),
        "m": len(edges),
        "edge_order_for_masks": [list(edge) for edge in edges],
        "triangle_count": len(triangle_vertices),
        "link_type_counts": dict(sorted(Counter(link_labels).items())),
        "constraints": constraints,
        "cadical_red_mask": cadical_mask,
        "z3_red_mask": z3_mask,
        "nonarrowing": all(constraints.values()),
    }


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    checks = [verify_row(row) for row in payload["survivors"]]
    verified = (
        payload["status"] == "COMPLETE"
        and len(checks) == payload["survivor_count"]
        and all(row["nonarrowing"] for row in checks)
    )
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "method": "NetworkX exact link isomorphism; independent CaDiCaL and Z3 color SAT; direct witness checks",
        "checks": checks,
        "arrowing_survivors": [row["graph6"] for row in checks if not row["nonarrowing"]],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
