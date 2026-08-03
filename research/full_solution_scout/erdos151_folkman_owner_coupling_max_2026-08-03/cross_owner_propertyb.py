#!/usr/bin/env python3
"""Exact replay of the 11-vertex cyclic cross-owner Property-B seed.

The eight base triples are taken from Steven Van Overberghe's
``quasi_folkman.ipynb``.  We close them under Z/11Z translation, regard each
pair as an edge variable, and verify non-Property-B in two independent ways:

* a small purpose-built NAE backtracker with propagation; and
* a CNF encoding solved independently by two PySAT engines.

We also expose the unique ownership of K_11 by its five circular-distance
Hamilton cycles.  Thus no owner contains a triangle and every selected clause
triangle is genuinely cross-owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical195, Glucose42


N = 11
BASES = [
    (0, 1, 2),
    (0, 1, 3),
    (0, 1, 5),
    (0, 1, 6),
    (0, 2, 4),
    (0, 2, 7),
    (0, 3, 6),
    (0, 3, 7),
]


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def triangles() -> list[tuple[int, int, int]]:
    return sorted(
        {
            tuple(sorted(((a + shift) % N, (b + shift) % N, (c + shift) % N)))
            for a, b, c in BASES
            for shift in range(N)
        }
    )


def owner(u: int, v: int) -> int:
    d = (u - v) % N
    return min(d, N - d)


def custom_nae_unsat(
    clauses: list[tuple[int, int, int]], variable_count: int
) -> tuple[bool, int]:
    """Return (UNSAT, search nodes) for monotone 3-NAE clauses.

    Values are -1/unassigned, 0, or 1.  A clause with two equal assigned
    values forces the remaining variable to the opposite value.  Global
    colour-complement symmetry is broken by fixing variable zero to zero.
    """

    occurrences: list[list[int]] = [[] for _ in range(variable_count)]
    for ci, clause in enumerate(clauses):
        for variable in clause:
            occurrences[variable].append(ci)
    assignment = [-1] * variable_count
    nodes = 0

    def propagate(seed: list[tuple[int, int]]) -> tuple[bool, list[int]]:
        queue = list(seed)
        changed: list[int] = []
        while queue:
            variable, value = queue.pop()
            if assignment[variable] != -1:
                if assignment[variable] != value:
                    return False, changed
                continue
            assignment[variable] = value
            changed.append(variable)
            for ci in occurrences[variable]:
                clause = clauses[ci]
                values = [assignment[x] for x in clause]
                known = [value for value in values if value != -1]
                if len(known) == 3 and known[0] == known[1] == known[2]:
                    return False, changed
                if len(known) == 2 and known[0] == known[1]:
                    missing = next(x for x in clause if assignment[x] == -1)
                    queue.append((missing, 1 - known[0]))
        return True, changed

    def search(seed: list[tuple[int, int]]) -> bool:
        nonlocal nodes
        nodes += 1
        ok, changed = propagate(seed)
        if not ok:
            for variable in reversed(changed):
                assignment[variable] = -1
            return False
        if all(value != -1 for value in assignment):
            for variable in reversed(changed):
                assignment[variable] = -1
            return True

        # Prefer a variable occurring most often in clauses not yet satisfied.
        scores = [0] * variable_count
        for clause in clauses:
            values = [assignment[x] for x in clause]
            if 0 in values and 1 in values:
                continue
            for variable in clause:
                if assignment[variable] == -1:
                    scores[variable] += 1
        variable = max((x for x in range(variable_count) if assignment[x] == -1),
                       key=lambda x: scores[x])
        sat = search([(variable, 0)]) or search([(variable, 1)])
        for changed_variable in reversed(changed):
            assignment[changed_variable] = -1
        return sat

    satisfiable = search([(0, 0)])
    return not satisfiable, nodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    selected = triangles()
    shadow_edges = sorted(
        {
            edge(u, v)
            for triple in selected
            for u, v in ((triple[0], triple[1]), (triple[0], triple[2]), (triple[1], triple[2]))
        }
    )
    edge_index = {e: i for i, e in enumerate(shadow_edges)}
    nae_clauses = [tuple(edge_index[edge(u, v)] for u, v in
                         ((a, b), (a, c), (b, c))) for a, b, c in selected]

    custom_unsat, custom_nodes = custom_nae_unsat(nae_clauses, len(shadow_edges))

    cnf: list[list[int]] = []
    for clause in nae_clauses:
        variables = [x + 1 for x in clause]
        cnf.append(variables)
        cnf.append([-x for x in variables])
    solver_results: dict[str, bool] = {}
    for name, solver_type in (("Cadical195", Cadical195), ("Glucose42", Glucose42)):
        with solver_type(bootstrap_with=cnf) as solver:
            solver_results[name] = not solver.solve()

    graph = nx.Graph()
    graph.add_nodes_from(range(N))
    graph.add_edges_from(shadow_edges)
    owner_edges = {
        str(distance): sorted([list(e) for e in shadow_edges if owner(*e) == distance])
        for distance in range(1, (N + 1) // 2)
    }
    owner_graph_checks = {}
    for distance, edges in owner_edges.items():
        owner_graph = nx.Graph()
        owner_graph.add_nodes_from(range(N))
        owner_graph.add_edges_from(edges)
        owner_graph_checks[distance] = {
            "edge_count": owner_graph.number_of_edges(),
            "connected": nx.is_connected(owner_graph),
            "degree_sequence": sorted(dict(owner_graph.degree()).values()),
            "triangle_count": sum(nx.triangles(owner_graph).values()) // 3,
        }

    selected_four_set_counts = Counter(
        tuple(sorted(vertices))
        for vertices in __import__("itertools").combinations(range(N), 4)
        if sum(set(triple).issubset(vertices) for triple in selected) == 4
    )
    selected_owner_patterns = Counter(
        tuple(sorted((owner(a, b), owner(a, c), owner(b, c))))
        for a, b, c in selected
    )
    variable_occurrences = Counter(variable for clause in nae_clauses for variable in clause)

    source_payload = json.dumps(BASES, separators=(",", ":")).encode()
    result = {
        "schema": "erdos151-cross-owner-propertyb-v1",
        "source": {
            "repository": "Steven-VO/quasiFolkman",
            "path": "quasi_folkman.ipynb",
            "notebook_sha": "de3b753999ed352612b44b9be2fb6432e70c86b2",
            "base_triples_sha256": hashlib.sha256(source_payload).hexdigest(),
        },
        "order": N,
        "base_triangle_count": len(BASES),
        "selected_triangle_count": len(selected),
        "selected_triangles": [list(t) for t in selected],
        "shadow": {
            "edge_count": graph.number_of_edges(),
            "is_complete": graph.number_of_edges() == N * (N - 1) // 2,
            "clique_number": max(map(len, nx.find_cliques(graph))),
            "tf3": 2 if graph.number_of_edges() == N * (N - 1) // 2 else None,
            "beta": N - 1 if graph.number_of_edges() == N * (N - 1) // 2 else None,
            "H_order": 4,
            "beta_less_than_H": False,
        },
        "owner_decomposition": {
            "rule": "circular distance min((u-v) mod 11,(v-u) mod 11) in {1,...,5}",
            "unique_edge_ownership": sum(len(edges) for edges in owner_edges.values()) == len(shadow_edges),
            "checks": owner_graph_checks,
            "all_selected_triangles_cross_owner": all(
                len({owner(a, b), owner(a, c), owner(b, c)}) >= 2 for a, b, c in selected
            ),
            "selected_owner_pattern_counts": {
                ",".join(map(str, pattern)): count
                for pattern, count in sorted(selected_owner_patterns.items())
            },
        },
        "property_b": {
            "variables": len(shadow_edges),
            "clauses": len(nae_clauses),
            "custom_backtracker_unsat": custom_unsat,
            "custom_backtracker_nodes": custom_nodes,
            "pysat_unsat": solver_results,
            "all_three_checkers_agree_unsat": custom_unsat and all(solver_results.values()),
            "variable_occurrence_histogram": dict(sorted(Counter(variable_occurrences.values()).items())),
        },
        "no_four_selected_triangles_span_K4": len(selected_four_set_counts) == 0,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
