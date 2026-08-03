#!/usr/bin/env python3
"""Exhaustive small K4-free triangle signal-sender audit through order seven.

For every unlabeled graph in NetworkX's graph atlas, enumerate all red/blue
edge-colourings with no monochromatic triangle.  Record graphs having two
vertex-disjoint signal edges whose colours have a fixed equality or inequality
relation in every good colouring.  This is a targeted replacement-gadget gate,
not a generic graph or #151 candidate scan.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.solvers import Glucose42


def contains_k4(g: nx.Graph) -> bool:
    for clique in nx.enumerate_all_cliques(g):
        if len(clique) == 4:
            return True
        if len(clique) > 4:
            return True
    return False


def triangle_masks(g: nx.Graph, edge_index: dict[tuple[int, int], int]) -> list[int]:
    out = []
    for u in g:
        for v in g:
            if v <= u or not g.has_edge(u, v):
                continue
            common = set(g[u]).intersection(g[v])
            for w in common:
                if w <= v:
                    continue
                mask = 0
                for e in ((u, v), (u, w), (v, w)):
                    mask |= 1 << edge_index[tuple(sorted(e))]
                out.append(mask)
    return out


def good_colourings(g: nx.Graph) -> tuple[list[tuple[int, int]], list[int]]:
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    index = {e: i for i, e in enumerate(edges)}
    tmasks = triangle_masks(g, index)
    full = (1 << len(edges)) - 1
    good = []
    # Fix edge 0 red to quotient the global colour swap when possible.
    for colouring in range(1 << len(edges)):
        if edges and colouring & 1:
            continue
        if all((colouring & t) not in (0, t) for t in tmasks):
            good.append(colouring)
    return edges, good


def edge_distance(g: nx.Graph, e: tuple[int, int], f: tuple[int, int]) -> int:
    return min(nx.shortest_path_length(g, a, b) for a in e for b in f)


def sat_relations(
    g: nx.Graph, edges: list[tuple[int, int]]
) -> tuple[bool, list[tuple[int, int, str]]]:
    """Independently recover forced disjoint-edge relations with a SAT solver."""

    index = {e: i + 1 for i, e in enumerate(edges)}
    cnf: list[list[int]] = []
    for clique in nx.enumerate_all_cliques(g):
        if len(clique) < 3:
            continue
        if len(clique) > 3:
            break
        a, b, c = sorted(clique)
        variables = [index[tuple(sorted(e))] for e in ((a, b), (a, c), (b, c))]
        cnf.append(variables)
        cnf.append([-x for x in variables])
    forced = []
    with Glucose42(bootstrap_with=cnf) as solver:
        satisfiable = solver.solve()
        for i, e in enumerate(edges):
            for j in range(i + 1, len(edges)):
                f = edges[j]
                if set(e).intersection(f):
                    continue
                # Colour-complement symmetry makes one orientation enough.
                same_exists = solver.solve(assumptions=[i + 1, j + 1])
                different_exists = solver.solve(assumptions=[i + 1, -(j + 1)])
                if not different_exists:
                    forced.append((i, j, "same"))
                if not same_exists:
                    forced.append((i, j, "different"))
    return satisfiable, forced


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = []
    scanned = Counter()
    sat_pair_queries = 0
    for atlas_id, raw in enumerate(nx.graph_atlas_g()):
        n = raw.number_of_nodes()
        if n < 3 or n > 7 or raw.number_of_edges() == 0:
            continue
        g = nx.convert_node_labels_to_integers(raw)
        if not nx.is_connected(g) or contains_k4(g):
            continue
        scanned[str(n)] += 1
        edges, goods = good_colourings(g)
        sat_good, sat_forced = sat_relations(g, edges)
        sat_pair_queries += 2 * sum(
            not set(e).intersection(f)
            for i, e in enumerate(edges)
            for f in edges[i + 1 :]
        )
        if not goods:
            # No K4-free arrowing graph should occur through this range.
            raise AssertionError((atlas_id, n, nx.to_graph6_bytes(g, header=False)))
        relations = []
        for i, e in enumerate(edges):
            for j in range(i + 1, len(edges)):
                f = edges[j]
                if set(e).intersection(f):
                    continue
                parity = {((c >> i) & 1) ^ ((c >> j) & 1) for c in goods}
                if len(parity) == 1:
                    relations.append(
                        {
                            "edge_a": list(e),
                            "edge_b": list(f),
                            "relation": "same" if next(iter(parity)) == 0 else "different",
                            "endpoint_distance": edge_distance(g, e, f),
                        }
                    )
        exhaustive_forced = sorted(
            (edges.index(tuple(x["edge_a"])), edges.index(tuple(x["edge_b"])), x["relation"])
            for x in relations
        )
        if not sat_good or exhaustive_forced != sorted(sat_forced):
            raise AssertionError(
                (atlas_id, "SAT/exhaustive disagreement", exhaustive_forced, sat_forced)
            )
        if relations:
            records.append(
                {
                    "atlas_id": atlas_id,
                    "n": n,
                    "m": len(edges),
                    "graph6": nx.to_graph6_bytes(g, header=False).decode().strip(),
                    "degrees": sorted((d for _, d in g.degree()), reverse=True),
                    "triangles": sum(nx.triangles(g).values()) // 3,
                    "good_colourings_mod_swap": len(goods),
                    "relations": relations,
                }
            )

    source = Path(inspect.getfile(nx.generators.atlas))
    payload = {
        "schema": "erdos151-k4free-signal-sender-atlas-v1",
        "scope": "all connected unlabeled K4-free graphs of orders 3 through 7 in NetworkX graph atlas",
        "atlas_source": {
            "networkx_version": nx.__version__,
            "path": str(source),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        "scanned_by_order": dict(sorted(scanned.items())),
        "independent_sat_audit": {
            "solver": "Glucose42",
            "assumption_queries": sat_pair_queries,
            "agreement_on_every_graph": True,
        },
        "sender_count": len(records),
        "same_sender_count": sum(
            any(x["relation"] == "same" for x in r["relations"]) for r in records
        ),
        "different_sender_count": sum(
            any(x["relation"] == "different" for x in r["relations"]) for r in records
        ),
        "records": records,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
