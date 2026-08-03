#!/usr/bin/env python3
"""Exact bounded probe of the eleven K11-plus-one-vertex isomorphism types.

K11 is a tight odd-order graph for the stronger floor(n/2) bound.  Adding one
vertex in all possible ways gives only eleven isomorphism types, determined by
the new vertex's positive degree.  This is a small structured family at the
first unverified order for Erdős #583.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import networkx as nx

from search_gallai_n12_random import check_decomposition, graph6, solve_six_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-graph-ms", type=int, default=30000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.time()
    results = []
    candidate = None
    for attachment_degree in range(1, 12):
        G = nx.complete_graph(11)
        G.add_node(11)
        G.add_edges_from((11, v) for v in range(attachment_degree))
        status, paths, elapsed, detail = solve_six_paths(G, args.per_graph_ms)
        row = {
            "attachment_degree": attachment_degree,
            "graph6": graph6(G),
            "edges": G.number_of_edges(),
            "status": status,
            "solve_seconds": elapsed,
            "detail": detail,
        }
        if status == "sat":
            assert paths is not None
            check_decomposition(G, paths)
            row["decomposition"] = paths
        elif status == "unsat":
            row["warning"] = "unverified candidate; needs independent UNSAT proof"
            candidate = row
        results.append(row)
        if candidate is not None:
            break

    payload = {
        "schema": "erdos583-n12-k11-extension-v1",
        "scope": "exhaustive over K11 plus one nonisolated vertex, up to isomorphism",
        "elapsed_seconds": time.time() - started,
        "per_graph_ms": args.per_graph_ms,
        "candidate": candidate,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
