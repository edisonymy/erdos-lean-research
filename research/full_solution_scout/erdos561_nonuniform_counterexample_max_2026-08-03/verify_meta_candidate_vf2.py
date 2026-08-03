#!/usr/bin/env python3
"""Independent verifier 2 for meta_candidate.json: VF2 monomorphisms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "meta_candidate.json"
OUT = HERE / "meta_candidate_vf2_verification.json"


def target_graph(degrees):
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
    return nx.algorithms.isomorphism.GraphMatcher(host, target).subgraph_is_monomorphic()


def main():
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    n = int(candidate["n"])
    edges = tuple(tuple(edge) for edge in candidate["edges"])
    red_target = target_graph(candidate["red_degrees"])
    blue_target = target_graph(candidate["blue_degrees"])
    avoiding = []
    for red_mask in range(1 << len(edges)):
        red = nx.Graph()
        blue = nx.Graph()
        red.add_nodes_from(range(n))
        blue.add_nodes_from(range(n))
        red.add_edges_from(edges[i] for i in range(len(edges)) if red_mask >> i & 1)
        blue.add_edges_from(edges[i] for i in range(len(edges)) if not (red_mask >> i & 1))
        if not contains(red, red_target) and not contains(blue, blue_target):
            avoiding.append(red_mask)
    arrows = not avoiding
    result = {
        "status": "VERIFIED" if arrows else "FAILED",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "method": "NetworkX VF2 non-induced monomorphism; all edge colorings",
        "colorings_checked": 1 << len(edges),
        "avoiding_red_masks": avoiding,
        "arrows": arrows,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not arrows:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
