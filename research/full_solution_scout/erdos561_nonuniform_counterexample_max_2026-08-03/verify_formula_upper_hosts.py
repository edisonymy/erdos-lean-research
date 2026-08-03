#!/usr/bin/env python3
"""Directly verify the formula-size star-union upper hosts for three tuples."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
OUT = HERE / "formula_upper_host_verification.json"

CASES = (
    {"red": (2, 1), "blue": (2, 2), "layers": (3, 3, 2)},
    {"red": (2, 1), "blue": (3, 2), "layers": (4, 3, 2)},
    {"red": (2, 2), "blue": (3, 1), "layers": (4, 4, 2)},
)


def disjoint_star_forest(degrees):
    graph = nx.Graph()
    cursor = 0
    for degree in degrees:
        center = cursor
        graph.add_node(center)
        cursor += 1
        for _ in range(degree):
            graph.add_edge(center, cursor)
            cursor += 1
    return graph


def contains(host, target):
    if host.number_of_nodes() < target.number_of_nodes() or host.number_of_edges() < target.number_of_edges():
        return False
    return nx.algorithms.isomorphism.GraphMatcher(host, target).subgraph_is_monomorphic()


def verify_case(case):
    host = disjoint_star_forest(case["layers"])
    red_target = disjoint_star_forest(case["red"])
    blue_target = disjoint_star_forest(case["blue"])
    edges = tuple(sorted(tuple(sorted(edge)) for edge in host.edges()))
    avoiding = []
    for red_mask in range(1 << len(edges)):
        red = nx.Graph()
        blue = nx.Graph()
        red.add_nodes_from(host.nodes())
        blue.add_nodes_from(host.nodes())
        red.add_edges_from(edges[i] for i in range(len(edges)) if red_mask >> i & 1)
        blue.add_edges_from(edges[i] for i in range(len(edges)) if not (red_mask >> i & 1))
        if not contains(red, red_target) and not contains(blue, blue_target):
            avoiding.append(red_mask)
    return {
        "red_degrees": list(case["red"]),
        "blue_degrees": list(case["blue"]),
        "formula_layers": list(case["layers"]),
        "host": " disjoint-union ".join(f"K_{{1,{degree}}}" for degree in case["layers"]),
        "host_n": host.number_of_nodes(),
        "host_m": host.number_of_edges(),
        "host_edges": [list(edge) for edge in edges],
        "colorings_checked": 1 << len(edges),
        "avoiding_red_masks": avoiding,
        "arrows": not avoiding,
    }


def main():
    checks = [verify_case(case) for case in CASES]
    verified = all(row["arrows"] for row in checks)
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "method": "explicit formula host; all edge colorings; NetworkX VF2 non-induced monomorphism",
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
