#!/usr/bin/env python3
"""Arithmetic replay for the order-50 pure protected-core exclusion.

The mathematical proof is in REPORT.md.  This script checks the finite
arithmetic, reads the authoritative ten-template census, and independently
rechecks the two link facts used in the degree-ten branch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx


def components_after_deleting_edge(g: nx.Graph, edge: tuple[int, int]) -> bool:
    h = g.copy()
    h.remove_edge(*edge)
    return nx.is_bipartite(h)


def universally_adaptable(g: nx.Graph) -> bool:
    """Hell--Zhu criterion, applied independently component by component."""
    for vertices in nx.connected_components(g):
        h = g.subgraph(vertices).copy()
        if not any(components_after_deleting_edge(h, e) for e in list(h.edges())):
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--order41-result", type=Path, required=True)
    parser.add_argument("--order41-proof", type=Path, required=True)
    parser.add_argument("--order41-audit", type=Path, required=True)
    parser.add_argument("--saturation-note", type=Path, required=True)
    parser.add_argument("--authoritative-target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dependencies = {
        "authoritative_target": (
            args.authoritative_target,
            "72130c15a223dfb18d2857ffba9f4236755f52f6aeb3ba11ec981e3c675391ca",
        ),
        "order41_proof": (
            args.order41_proof,
            "a06ddc79c5db44af51b098b404b2355055835866ddae0edfbee5606aa195e7a4",
        ),
        "order41_independent_audit": (
            args.order41_audit,
            "9ba41aeeecee2cf9241c133df9936a14426105b30a3f040e9c9689de4b1bfcc1",
        ),
        "degree_saturation_note": (
            args.saturation_note,
            "074fd98dedc0728913f95aeb9a57b9673c509bdf1552c5ee09a6a843266bf38c",
        ),
        "link_census": (
            args.census,
            "541141256a6defcc2377e903680f8be800128571b8cb511f0d4fa9367ed2b6a4",
        ),
    }
    dependency_hashes = {}
    for name, (path, expected) in dependencies.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        assert observed == expected, (name, observed, expected)
        dependency_hashes[name] = {"path": str(path), "sha256": observed}

    order41 = json.loads(args.order41_result.read_text(encoding="utf-8"))
    assert order41["status"] == "VERIFIED"
    assert order41["independent_audit"] == "PASS"
    assert order41["claim"] == "Every K4-free graph G on 41 vertices satisfies beta(G) >= 10."

    raw = args.census.read_bytes()
    census = json.loads(raw)
    records = census["all_obstructions"]
    assert len(records) == 10

    decoded = []
    for record in records:
        g = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        assert nx.number_of_nodes(g) == record["n"]
        assert nx.number_of_edges(g) == record["m"]
        assert min(dict(g.degree()).values()) >= 2
        assert sum(nx.triangles(g).values()) == 0
        assert not universally_adaptable(g)
        decoded.append((len(g), g.number_of_edges(), record["graph6"]))

    # On ten link vertices, minimum degree two and ten edges force C_10.
    # C_10 is bipartite, hence universally adaptable (deleting any edge
    # certainly leaves it bipartite).  The census consequently has no
    # (n,m)=(10,10) obstruction and exactly one (10,11) obstruction.
    assert not [x for x in decoded if x[:2] == (10, 10)]
    ten_eleven = [x for x in decoded if x[:2] == (10, 11)]
    assert len(ten_eleven) == 1

    n = 50
    degree = 10
    triangles_per_vertex = 11
    incidence_sum = n * triangles_per_vertex
    assert incidence_sum == 550
    assert incidence_sum % 3 == 1

    # In a proper nine-colouring of 50 vertices, the two largest colour
    # classes have total size at least ceil(2*50/9)=12.
    two_class_floor = (2 * n + 9 - 1) // 9
    assert two_class_floor == 12

    result = {
        "schema": "erdos151-n50-pure-core-gate-v1",
        "status": "VERIFIED_ARITHMETIC",
        "census_sha256": hashlib.sha256(raw).hexdigest(),
        "dependencies": dependency_hashes,
        "template_checks": {
            "obstruction_count": len(records),
            "order10_edges10_obstructions": 0,
            "order10_edges11_obstructions": len(ten_eleven),
            "independent_hell_zhu_recheck": True,
        },
        "ten_regular_branch": {
            "forced_triangle_incidence_sum": incidence_sum,
            "modulo_three": incidence_sum % 3,
            "contradiction": True,
        },
        "nine_regular_branch": {
            "brooks_colour_count": 9,
            "two_largest_classes_floor": two_class_floor,
            "contradicts_beta_at_most_10": two_class_floor > 10,
        },
        "degree_ladder_dependency": {
            "uses_unconditional_order41_k4free_beta_at_least_10": True,
            "uses_through49_chain": False,
            "uses_least_counterexample_hypothesis": False,
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
