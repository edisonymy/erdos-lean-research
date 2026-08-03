#!/usr/bin/env python3
"""Enumerate tiny signed-link obstructions relevant to minimal (3,3)-Ramsey graphs.

For an edge-coloring sigma of a link L, a spoke coloring x is adapted when
no edge ab has sigma(ab)=x(a)=x(b).  The script independently checks all
signings and all spoke colorings; it also checks the published connected
characterization (delete one edge to obtain a bipartite graph).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx


def has_adapted_coloring(g: nx.Graph, signing: int) -> tuple[bool, int | None]:
    edges = list(g.edges())
    nodes = list(g.nodes())
    pos = {v: i for i, v in enumerate(nodes)}
    for coloring in range(1 << len(nodes)):
        okay = True
        for i, (u, v) in enumerate(edges):
            edge_color = (signing >> i) & 1
            if ((coloring >> pos[u]) & 1) == edge_color == ((coloring >> pos[v]) & 1):
                okay = False
                break
        if okay:
            return True, coloring
    return False, None


def bad_signing(g: nx.Graph) -> int | None:
    for signing in range(1 << g.number_of_edges()):
        okay, _ = has_adapted_coloring(g, signing)
        if not okay:
            return signing
    return None


def edge_deletion_bipartite(g: nx.Graph) -> tuple[bool, tuple[int, int] | None]:
    for e in list(g.edges()):
        h = g.copy()
        h.remove_edge(*e)
        if nx.is_bipartite(h):
            return True, tuple(sorted(e))
    return False, None


def triangles(g: nx.Graph) -> list[list[int]]:
    return [list(c) for c in nx.enumerate_all_cliques(g) if len(c) == 3]


def canonical_graph6(g: nx.Graph) -> str:
    h = nx.convert_node_labels_to_integers(g, ordering="sorted")
    return nx.to_graph6_bytes(h, header=False).decode().strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-edges", type=int, default=7)
    ap.add_argument("--out", type=Path, default=Path("signed_link_obstructions.result.json"))
    args = ap.parse_args()

    records = []
    checked = 0
    for g in nx.graph_atlas_g():
        n = g.number_of_nodes()
        m = g.number_of_edges()
        if n == 0 or m > args.max_edges or not nx.is_connected(g):
            continue
        if min(dict(g.degree()).values()) < 2:
            continue
        checked += 1
        signing = bad_signing(g)
        deletion_test, deleting_edge = edge_deletion_bipartite(g)
        if (signing is None) != deletion_test:
            raise AssertionError("exhaustive signing test disagrees with edge-deletion characterization")
        if signing is None:
            continue
        edges = [list(e) for e in g.edges()]
        records.append({
            "n": n,
            "m": m,
            "graph6": canonical_graph6(g),
            "degree_sequence": sorted((d for _, d in g.degree()), reverse=True),
            "clique_number": max(map(len, nx.find_cliques(g))),
            "triangles": triangles(g),
            "edges_in_enumeration_order": edges,
            "bad_signing_bits": signing,
            "bad_signing_edge_colors": [
                {"edge": edges[i], "color": (signing >> i) & 1}
                for i in range(m)
            ],
            "some_edge_deletion_bipartite": deletion_test,
            "deleting_edge": deleting_edge,
        })

    result = {
        "schema": "erdos151-signed-link-obstructions-v1",
        "scope": {
            "source": "NetworkX graph atlas: all unlabeled graphs through 7 vertices",
            "connected": True,
            "minimum_degree_at_least_2": True,
            "maximum_edges": args.max_edges,
        },
        "connected_min_degree_2_graphs_checked": checked,
        "non_adaptably_2_colorable_records": records,
        "counts_by_edges": {
            str(m): sum(r["m"] == m for r in records)
            for m in range(args.max_edges + 1)
        },
        "interpretation": "A link signing is the inherited coloring of rim edges after deleting a core vertex. A bad signing has no extension to its spokes.",
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.write_bytes(payload.encode())
    print(json.dumps({
        "checked": checked,
        "obstructions": len(records),
        "counts_by_edges": result["counts_by_edges"],
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
