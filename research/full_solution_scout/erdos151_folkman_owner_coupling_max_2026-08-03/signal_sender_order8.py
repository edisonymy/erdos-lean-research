#!/usr/bin/env python3
"""Targeted exact K4-free triangle signal-sender census at order eight.

This is a continuation of ``signal_sender_atlas.py`` beyond the seven-vertex
NetworkX atlas.  ``geng`` supplies every connected unlabeled order-eight graph;
we reject graphs containing K4 and use SAT assumptions to test whether two
vertex-disjoint edges can realize both possible colour parities in good
triangle-free edge-colourings.  Any claimed sender is replayed by direct
enumeration of all edge colourings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical195, Glucose42


def contains_k4(g: nx.Graph) -> bool:
    return any(len(c) >= 4 for c in nx.find_cliques(g))


def triangle_variables(
    g: nx.Graph, edge_index: dict[tuple[int, int], int]
) -> list[tuple[int, int, int]]:
    clauses = []
    for a in range(8):
        for b in range(a + 1, 8):
            if not g.has_edge(a, b):
                continue
            for c in range(b + 1, 8):
                if g.has_edge(a, c) and g.has_edge(b, c):
                    clauses.append(
                        (
                            edge_index[(a, b)],
                            edge_index[(a, c)],
                            edge_index[(b, c)],
                        )
                    )
    return clauses


def cnf_for(clauses: list[tuple[int, int, int]]) -> list[list[int]]:
    cnf = []
    for clause in clauses:
        positive = [x + 1 for x in clause]
        cnf.append(positive)
        cnf.append([-x for x in positive])
    return cnf


def direct_parities(
    edge_count: int,
    clauses: list[tuple[int, int, int]],
    i: int,
    j: int,
) -> set[int]:
    masks = [sum(1 << x for x in clause) for clause in clauses]
    out = set()
    for colouring in range(1 << edge_count):
        if colouring & 1:  # quotient global colour complement
            continue
        if all((colouring & mask) not in (0, mask) for mask in masks):
            out.add(((colouring >> i) & 1) ^ ((colouring >> j) & 1))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    completed = subprocess.run(
        [str(args.geng), "-cq", "8"],
        check=True,
        capture_output=True,
        text=True,
    )
    graph6_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    scanned_k4free = 0
    sat_queries = 0
    records = []
    for graph6 in graph6_lines:
        g = nx.from_graph6_bytes(graph6.encode())
        if contains_k4(g):
            continue
        scanned_k4free += 1
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        edge_index = {e: i for i, e in enumerate(edges)}
        clauses = triangle_variables(g, edge_index)
        cnf = cnf_for(clauses)
        relations = []
        with Glucose42(bootstrap_with=cnf) as solver, Cadical195(
            bootstrap_with=cnf
        ) as audit:
            if not solver.solve() or not audit.solve():
                raise AssertionError((graph6, "unexpected order-eight arrowing graph"))
            for i, e in enumerate(edges):
                for j in range(i + 1, len(edges)):
                    f = edges[j]
                    if set(e).intersection(f):
                        continue
                    same_exists = solver.solve(assumptions=[i + 1, j + 1])
                    different_exists = solver.solve(assumptions=[i + 1, -(j + 1)])
                    audit_same = audit.solve(assumptions=[i + 1, j + 1])
                    audit_different = audit.solve(assumptions=[i + 1, -(j + 1)])
                    sat_queries += 2
                    if (audit_same, audit_different) != (same_exists, different_exists):
                        raise AssertionError((graph6, "solver disagreement", e, f))
                    if same_exists and different_exists:
                        continue
                    relation = "same" if not different_exists else "different"
                    direct = direct_parities(len(edges), clauses, i, j)
                    expected = {0} if relation == "same" else {1}
                    if direct != expected:
                        raise AssertionError((graph6, e, f, relation, direct))
                    relations.append(
                        {
                            "edge_a": list(e),
                            "edge_b": list(f),
                            "relation": relation,
                            "endpoint_distance": min(
                                nx.shortest_path_length(g, a, b) for a in e for b in f
                            ),
                            "direct_good_parities": sorted(direct),
                        }
                    )
        if relations:
            records.append(
                {
                    "graph6": graph6,
                    "m": len(edges),
                    "degree_sequence": sorted((d for _, d in g.degree()), reverse=True),
                    "triangle_count": len(clauses),
                    "relations": relations,
                }
            )

    payload = {
        "schema": "erdos151-k4free-signal-sender-order8-v1",
        "scope": "all connected unlabeled K4-free graphs on eight vertices",
        "geng": {
            "path": str(args.geng),
            "sha256": hashlib.sha256(args.geng.read_bytes()).hexdigest(),
            "connected_order8_graphs": len(graph6_lines),
        },
        "k4free_graphs": scanned_k4free,
        "solvers": ["Glucose42", "Cadical195"],
        "all_assumption_queries_agree": True,
        "sat_assumption_queries": sat_queries,
        "sender_graph_count": len(records),
        "same_sender_graph_count": sum(
            any(x["relation"] == "same" for x in r["relations"]) for r in records
        ),
        "different_sender_graph_count": sum(
            any(x["relation"] == "different" for x in r["relations"]) for r in records
        ),
        "claimed_relations_additionally_checked_by": "direct all-edge-colouring enumeration",
        "records": records,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
