#!/usr/bin/env python3
"""Independent VF2 audit of every saved avoiding coloring in the meta-sweep."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
RESULT = HERE / "meta_sweep_result.json"
WITNESSES = HERE / "meta_sweep_avoiding_colorings.json"
OUT = HERE / "meta_sweep_independent_witness_audit.json"


def target_graph(degrees):
    target = nx.Graph()
    cursor = 0
    for degree in degrees:
        center = cursor
        target.add_node(center)
        cursor += 1
        for _ in range(degree):
            target.add_edge(center, cursor)
            cursor += 1
    return target


def contains(host, target):
    if host.number_of_nodes() < target.number_of_nodes() or host.number_of_edges() < target.number_of_edges():
        return False
    return nx.algorithms.isomorphism.GraphMatcher(host, target).subgraph_is_monomorphic()


def check_row(row, red_target, blue_target):
    n = int(row["n"])
    edges = tuple(tuple(edge) for edge in row["edges"])
    red_mask = int(row["avoiding_red_mask"])
    red = nx.Graph()
    blue = nx.Graph()
    red.add_nodes_from(range(n))
    blue.add_nodes_from(range(n))
    red.add_edges_from(edges[i] for i in range(len(edges)) if red_mask >> i & 1)
    blue.add_edges_from(edges[i] for i in range(len(edges)) if not (red_mask >> i & 1))
    return not contains(red, red_target) and not contains(blue, blue_target)


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    witnesses = json.loads(WITNESSES.read_text(encoding="utf-8"))
    failures = {}
    counts = {}
    edge_histograms = {}
    count_agreement = True
    for target in witnesses["targets"]:
        rank = str(target["rank"])
        records = witnesses["records_by_rank"][rank]
        red_target = target_graph(target["a"])
        blue_target = target_graph(target["b"])
        failures[rank] = [
            index for index, row in enumerate(records)
            if not check_row(row, red_target, blue_target)
        ]
        counts[rank] = len(records)
        edge_histograms[rank] = dict(sorted(Counter(row["m"] for row in records).items()))
        expected = next(row for row in result["ranked_targets"] if row["rank"] == target["rank"])
        if len(records) != expected["hosts_checked"] or len(records) != expected["avoiding_colorings_saved"]:
            count_agreement = False
    hash_agreement = hashlib.sha256(WITNESSES.read_bytes()).hexdigest() == result["witness_file_sha256"]
    verified = (
        result["outcome"] == "NO_COUNTEREXAMPLE_IN_CAPPED_META_SWEEP"
        and all(not rows for rows in failures.values())
        and count_agreement
        and hash_agreement
    )
    payload = {
        "status": "VERIFIED" if verified else "FAILED",
        "result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "witness_file_sha256": hashlib.sha256(WITNESSES.read_bytes()).hexdigest(),
        "hash_agreement": hash_agreement,
        "method": "independent NetworkX VF2 non-induced monomorphism on every saved red/blue coloring",
        "checked_by_rank": counts,
        "edge_histograms_by_rank": edge_histograms,
        "failures_by_rank": failures,
        "count_agreement": count_agreement,
        "full_problem_resolved": False,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
