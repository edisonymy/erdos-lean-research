#!/usr/bin/env python3
"""Exact parameterized local-link census for Folkman triangle thresholds.

This is deliberately independent of the campaign's threshold-seven scripts.
It asks nauty ``geng`` for every simple graph with minimum degree at least two
and at most a requested number of edges, then checks the Hell--Zhu universal adaptable
2-colourability criterion in two separately implemented ways.  It also records
the triangle-free obstruction types relevant to K4-free minimal Ramsey cores.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx


def custom_bipartite(n: int, edges: tuple[tuple[int, int], ...], skip: int | None = None) -> bool:
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if i == skip:
            continue
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n
    for root in range(n):
        if colour[root] >= 0:
            continue
        colour[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if colour[v] < 0:
                    colour[v] = 1 - colour[u]
                    stack.append(v)
                elif colour[v] == colour[u]:
                    return False
    return True


def custom_components(n: int, edges: tuple[tuple[int, int], ...]) -> list[tuple[set[int], list[int]]]:
    adj: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    seen: set[int] = set()
    out: list[tuple[set[int], list[int]]] = []
    for root in range(n):
        if root in seen:
            continue
        verts = {root}
        edge_ids: set[int] = set()
        seen.add(root)
        stack = [root]
        while stack:
            u = stack.pop()
            for v, i in adj[u]:
                edge_ids.add(i)
                if v not in seen:
                    seen.add(v)
                    verts.add(v)
                    stack.append(v)
        out.append((verts, sorted(edge_ids)))
    return out


def custom_universally_adaptable(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    """Hell--Zhu criterion, component by component, using bit-free DFS."""
    for verts, edge_ids in custom_components(n, edges):
        local_index = {v: i for i, v in enumerate(sorted(verts))}
        local_edges = tuple(
            (local_index[edges[i][0]], local_index[edges[i][1]]) for i in edge_ids
        )
        if not any(custom_bipartite(len(verts), local_edges, skip=i) for i in range(len(local_edges))):
            return False
    return True


def nx_universally_adaptable(g: nx.Graph) -> bool:
    for vertices in nx.connected_components(g):
        c = g.subgraph(vertices).copy()
        good = False
        for e in list(c.edges()):
            c.remove_edge(*e)
            if nx.is_bipartite(c):
                good = True
            c.add_edge(*e)
            if good:
                break
        if not good:
            return False
    return True


def direct_adaptable_for_every_signing(g: nx.Graph) -> bool:
    """Definition-level check; used through eleven edges in this packet."""
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    n = g.number_of_nodes()
    for signing in range(1 << len(edges)):
        adaptable = False
        for vertex_colours in range(1 << n):
            ok = True
            for i, (u, v) in enumerate(edges):
                sign = (signing >> i) & 1
                if ((vertex_colours >> u) & 1) == sign == ((vertex_colours >> v) & 1):
                    ok = False
                    break
            if ok:
                adaptable = True
                break
        if not adaptable:
            return False
    return True


def graph_record(g: nx.Graph, direct_limit: int) -> dict[str, object]:
    edges = tuple(sorted(tuple(sorted(e)) for e in g.edges()))
    a = custom_universally_adaptable(g.number_of_nodes(), edges)
    b = nx_universally_adaptable(g)
    c = direct_adaptable_for_every_signing(g) if len(edges) <= direct_limit else None
    if a != b or (c is not None and a != c):
        raise AssertionError((nx.to_graph6_bytes(g, header=False).strip(), a, b, c))
    triangles = sum(nx.triangles(g).values()) // 3
    return {
        "n": g.number_of_nodes(),
        "m": g.number_of_edges(),
        "graph6": nx.to_graph6_bytes(g, header=False).decode().strip(),
        "degree_sequence": sorted((d for _, d in g.degree()), reverse=True),
        "connected": nx.is_connected(g),
        "triangle_free": triangles == 0,
        "triangle_count": triangles,
        "universally_adaptable": a,
        "direct_definition_checked": c is not None,
    }


def geng_graphs(geng: Path, n: int, max_edges: int, triangle_free: bool) -> list[nx.Graph]:
    cmd = [str(geng), "-q", "-d2"]
    if triangle_free:
        cmd.append("-t")
    cmd.extend([str(n), f"{n}:{max_edges}"])
    proc = subprocess.run(cmd, check=True, capture_output=True)
    graphs = []
    for line in proc.stdout.splitlines():
        if line:
            graphs.append(nx.from_graph6_bytes(line))
    return graphs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--geng",
        type=Path,
        default=Path(".tmp/nauty-env/Library/bin/geng.exe"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-edges", type=int, default=8)
    parser.add_argument("--triangle-free", action="store_true")
    parser.add_argument("--direct-limit", type=int, default=8)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    # Minimum degree two and m <= M imply 3 <= n <= M.
    for n in range(3, args.max_edges + 1):
        for g in geng_graphs(args.geng, n, args.max_edges, args.triangle_free):
            records.append(graph_record(g, args.direct_limit))

    obstructions = [r for r in records if not r["universally_adaptable"]]
    at_eight = [r for r in obstructions if r["m"] == 8]
    tf_at_eight = [r for r in at_eight if r["triangle_free"]]
    old = [r for r in obstructions if r["m"] <= 7]
    payload = {
        "schema": "erdos151-threshold8-link-census-v1",
        "generator": {
            "path": str(args.geng),
            "sha256": hashlib.sha256(args.geng.read_bytes()).hexdigest(),
            "scope": (
                f"all unlabeled simple graphs with delta>=2 and m<={args.max_edges}"
                + (" and triangle-free" if args.triangle_free else "")
            ),
        },
        "definition_checks": [
            "custom componentwise edge-deletion bipartiteness",
            "NetworkX componentwise edge-deletion bipartiteness",
            "direct all-edge-signings/all-vertex-colourings adaptable definition",
        ],
        "parameters": {
            "max_edges": args.max_edges,
            "triangle_free": args.triangle_free,
            "direct_definition_edge_limit": args.direct_limit,
        },
        "counts": {
            "all_graphs": len(records),
            "by_n": dict(sorted(Counter(str(r["n"]) for r in records).items())),
            "nonuniversally_adaptable": len(obstructions),
            "old_m_at_most_7": len(old),
            "new_m_equal_8": len(at_eight),
            "new_m_equal_8_triangle_free": len(tf_at_eight),
        },
        "old_obstructions": old,
        "eight_edge_obstructions": at_eight,
        "eight_edge_triangle_free_obstructions": tf_at_eight,
        "all_obstructions": obstructions,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
