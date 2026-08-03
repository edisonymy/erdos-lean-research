#!/usr/bin/env python3
"""Cross-audit maximal-clique semantics and all recorded beta witnesses."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scan_abelian_n50 as ab50  # noqa: E402
import scan_circulants_n50 as cy50  # noqa: E402
import scan_circulants_n59 as cy59  # noqa: E402


SCHEMA = "erdos151-cayley-beta-semantics-audit-v2"


def adj_for_record(family: str, record: dict) -> list[int]:
    if family == "cyclic_50":
        return cy50.adjacency(tuple(record["steps"]))
    if family == "abelian_50":
        indices = tuple(
            ab50.PAIR_INDEX[(epsilon, ab50.pair_rep((x, y)))]
            for epsilon, x, y in record["inverse_pair_generators"]
        )
        return ab50.adjacency(bool(record["involution"]), indices)
    if family == "cyclic_59":
        return cy59.adjacency(tuple(record["steps"]))
    raise ValueError(family)


def bitset_cliques(family: str, adj: list[int]) -> list[int]:
    return cy59.maximal_cliques(adj) if family == "cyclic_59" else cy50.maximal_cliques(adj)


def networkx_cliques(adj: list[int]) -> set[int]:
    n = len(adj)
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for u in range(n):
        mask = adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            bit = mask & -mask
            mask ^= bit
            graph.add_edge(u, bit.bit_length() - 1)
    return {
        sum(1 << v for v in clique)
        for clique in nx.find_cliques(graph)
        if len(clique) >= 2
    }


def audit_family(family: str, filename: str, target_size: int) -> dict:
    raw = json.loads((HERE / filename).read_text(encoding="utf-8"))
    if not raw["complete"] or raw["candidate_count"] != 0:
        raise AssertionError("expected a complete zero-candidate scan")
    records = raw["beta_near_misses"]
    clique_distributions = Counter()
    for record in records:
        adj = adj_for_record(family, record)
        first = set(bitset_cliques(family, adj))
        second = networkx_cliques(adj)
        if first != second:
            raise AssertionError(f"maximal-clique mismatch in {family}")
        witness = record["witness"]
        if len(witness) != target_size or len(set(witness)) != target_size:
            raise AssertionError("bad recorded witness cardinality")
        mask = sum(1 << v for v in witness)
        if any(clique & mask == clique for clique in first):
            raise AssertionError("recorded set contains a nontrivial maximal clique")
        clique_distributions[str(len(first))] += 1
    return {
        "complete_scan": True,
        "candidate_count": 0,
        "threshold_survivors_cross_checked": len(records),
        "recorded_admissible_witness_size": target_size,
        "maximal_clique_enumerators": [
            "custom bitset Bron--Kerbosch with pivot",
            "NetworkX find_cliques",
        ],
        "all_maximal_clique_sets_agree": True,
        "all_recorded_witnesses_definition_checked": True,
        "maximal_clique_count_distribution": dict(
            sorted(clique_distributions.items(), key=lambda x: int(x[0]))
        ),
    }


def main() -> int:
    minima = json.loads((HERE / "audit_family_minima.result.json").read_text(encoding="utf-8"))
    output = {
        "schema": SCHEMA,
        "families": {
            "cyclic_50": audit_family("cyclic_50", "scan_circulants_n50.result.json", 11),
            "abelian_50": audit_family("abelian_50", "scan_abelian_n50.result.json", 11),
            "cyclic_59": audit_family("cyclic_59", "scan_circulants_n59.result.json", 12),
        },
        "alpha_threshold_survivor_minima": {
            family: {
                "minimum_beta_among_alpha_threshold_survivors": data[
                    "minimum_beta_among_alpha_threshold_survivors"
                ],
                "minimum_record_count_at_that_value": data[
                    "minimum_record_count_at_that_value"
                ],
                "checker_a": data["checker_a"],
                "checker_b": data["checker_b"],
                "checked_values_agree": (
                    data["checked_minimizer"]["beta_checker_a"]
                    == data["checked_minimizer"]["beta_checker_b"]
                    == data["minimum_beta_among_alpha_threshold_survivors"]
                ),
            }
            for family, data in minima["families"].items()
        },
        "semantic_statement": "A set S is admissible iff no enumerated inclusion-maximal clique of size at least two is a subset of S; every SAT clique clause is exactly the negation of one such containment.",
        "translation_fix": "Every tested graph is Cayley and translations are graph automorphisms. Any nonempty admissible set can be translated to contain the identity vertex 0, so the unit clause x_0 is equisatisfiable.",
    }
    if not all(
        item["checked_values_agree"]
        for item in output["alpha_threshold_survivor_minima"].values()
    ):
        raise AssertionError("alpha-threshold survivor exact checkers disagree")
    path = HERE / "audit_beta_semantics.result.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
