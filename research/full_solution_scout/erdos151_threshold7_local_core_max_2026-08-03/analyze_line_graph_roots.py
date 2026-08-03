#!/usr/bin/env python3
"""Recover loopless 4-regular multigraph roots of the four local cores."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx
import z3

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "scan_through_12.json"
OUT = HERE / "line_graph_root_analysis.json"


def k4s(graph):
    return [
        tuple(vertices)
        for vertices in itertools.combinations(graph.nodes(), 4)
        if all(graph.has_edge(a, b) for a, b in itertools.combinations(vertices, 2))
    ]


def recover_root(line_graph):
    cliques = k4s(line_graph)
    multiplicities = [z3.Int(f"clique_{index}") for index in range(len(cliques))]
    solver = z3.Solver()
    for variable in multiplicities:
        solver.add(variable >= 0, variable <= 2)
    for vertex in line_graph.nodes():
        solver.add(
            sum(
                multiplicities[index]
                for index, clique in enumerate(cliques)
                if vertex in clique
            )
            == 2
        )
    for a, b in line_graph.edges():
        solver.add(
            sum(
                multiplicities[index]
                for index, clique in enumerate(cliques)
                if a in clique and b in clique
            )
            >= 1
        )
    solver.add(sum(multiplicities) == line_graph.number_of_nodes() // 2)
    if solver.check() != z3.sat:
        return None
    model = solver.model()
    selected = []
    for index, clique in enumerate(cliques):
        selected.extend([clique] * model[multiplicities[index]].as_long())

    root = nx.MultiGraph()
    root.add_nodes_from(range(len(selected)))
    qvertex_to_root_edge = {}
    for qvertex in line_graph.nodes():
        endpoints = [index for index, clique in enumerate(selected) if qvertex in clique]
        if len(endpoints) != 2:
            raise AssertionError((qvertex, endpoints))
        root.add_edge(endpoints[0], endpoints[1], qvertex=qvertex)
        qvertex_to_root_edge[qvertex] = endpoints
    return root, selected, qvertex_to_root_edge


def exact_chromatic_number(graph):
    for color_count in range(1, graph.number_of_nodes() + 1):
        colors = [z3.Int(f"v_{vertex}_k_{color_count}") for vertex in graph.nodes()]
        solver = z3.Solver()
        for color in colors:
            solver.add(color >= 0, color < color_count)
        for a, b in graph.edges():
            solver.add(colors[a] != colors[b])
        if solver.check() == z3.sat:
            model = solver.model()
            assignment = [model.eval(color).as_long() for color in colors]
            return color_count, assignment
    raise AssertionError("finite graph had no coloring")


def root_description(root):
    pair_multiplicity = Counter(tuple(sorted((a, b))) for a, b in root.edges())
    support = nx.Graph()
    support.add_nodes_from(root.nodes())
    support.add_edges_from(pair_multiplicity)
    doubled = [edge for edge, value in pair_multiplicity.items() if value == 2]
    simple = [edge for edge, value in pair_multiplicity.items() if value == 1]
    if len(doubled) == support.number_of_edges() and all(degree == 2 for _, degree in support.degree()):
        structure = f"cycle_C{root.number_of_nodes()}_with_every_edge_doubled"
    else:
        doubled_graph = nx.Graph(doubled)
        simple_graph = nx.Graph(simple)
        doubled_is_perfect_matching = (
            len(doubled) * 2 == root.number_of_nodes()
            and all(degree == 1 for _, degree in doubled_graph.degree())
        )
        simple_components = [simple_graph.subgraph(c).copy() for c in nx.connected_components(simple_graph)]
        simple_is_two_triangles = (
            len(simple_components) == 2
            and all(len(component) == 3 and component.number_of_edges() == 3 for component in simple_components)
        )
        structure = (
            "two_disjoint_triangles_joined_by_a_doubled_perfect_matching"
            if doubled_is_perfect_matching and simple_is_two_triangles
            else "unclassified_4_regular_multigraph"
        )
    return pair_multiplicity, structure


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for survivor in payload["survivors"]:
        q = nx.from_graph6_bytes(survivor["graph6"].encode("ascii"))
        recovered = recover_root(q)
        if recovered is None:
            rows.append({"graph6": survivor["graph6"], "root_found": False})
            continue
        root, selected, qvertex_to_root_edge = recovered
        reconstructed = nx.Graph(nx.line_graph(root))
        is_line_graph = nx.is_isomorphic(q, reconstructed)
        pair_multiplicity, structure = root_description(root)
        chromatic_number, coloring = exact_chromatic_number(q)
        rows.append(
            {
                "graph6": survivor["graph6"],
                "root_found": True,
                "root_order": root.number_of_nodes(),
                "root_size_with_multiplicity": root.number_of_edges(),
                "root_degrees": [degree for _, degree in sorted(root.degree())],
                "root_loopless": nx.number_of_selfloops(root) == 0,
                "root_edge_multiplicities": [
                    {"edge": list(edge), "multiplicity": multiplicity}
                    for edge, multiplicity in sorted(pair_multiplicity.items())
                ],
                "root_structure": structure,
                "selected_incident_K4s": [list(clique) for clique in selected],
                "qvertex_to_root_edge": {
                    str(vertex): endpoints for vertex, endpoints in qvertex_to_root_edge.items()
                },
                "reconstructed_line_graph_isomorphic": is_line_graph,
                "exact_chromatic_number": chromatic_number,
                "chromatic_coloring": coloring,
            }
        )
    verified = all(
        row.get("root_found")
        and row["root_loopless"]
        and set(row["root_degrees"]) == {4}
        and row["reconstructed_line_graph_isomorphic"]
        for row in rows
    )
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "interpretation": "all four finite survivors are line graphs of loopless 4-regular multigraphs; this is evidence for, not a proof of, the general structural hypothesis",
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
