#!/usr/bin/env python3
"""Determine beta minima among the scans' alpha-threshold survivors.

This file deliberately does not claim minima over the whole Cayley families:
the fast scans do not retain representatives rejected by an independent set.
See audit_global_near_miss.py for the genuine all-representative minima.

Checker A uses the scan's bitset Bron--Kerbosch clique enumerator plus plain
CaDiCaL cardinality SAT, increasing the requested admissible-set size until
the first UNSAT instance.  Translation symmetry fixes vertex 0.

Checker B is run on one deterministically selected minimum-hash minimizer per
family. It reconstructs an ordinary NetworkX graph, independently enumerates maximal
cliques, and computes beta exactly with RC2 weighted MaxSAT.  Agreement is a
semantics-level cross-check; these are filtered survivors, not counterexamples.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import scan_abelian_n50 as ab50  # noqa: E402
import scan_circulants_n50 as cy50  # noqa: E402
import scan_circulants_n59 as cy59  # noqa: E402


SCHEMA = "erdos151-cayley-alpha-threshold-survivor-minima-audit-v2"


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
    if family in ("cyclic_50", "abelian_50"):
        return cy50.maximal_cliques(adj)
    return cy59.maximal_cliques(adj)


def record_id(family: str, record: dict) -> str:
    parameters = (
        record["steps"]
        if family.startswith("cyclic")
        else [record["involution"], record["inverse_pair_generators"]]
    )
    return hashlib.sha256(
        (family + ":" + json.dumps(parameters, separators=(",", ":"))).encode("utf-8")
    ).hexdigest()


def admissible_model(n: int, cliques: list[int], size: int) -> list[int] | None:
    clauses = [
        [-(v + 1) for v in range(n) if clique >> v & 1]
        for clique in cliques
    ]
    clauses.append([1])
    pool = IDPool(start_from=n + 1)
    clauses.extend(
        CardEnc.equals(
            list(range(1, n + 1)),
            size,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        positive = {lit for lit in solver.get_model() if 1 <= lit <= n}
    witness = [v for v in range(n) if v + 1 in positive]
    if len(witness) != size or 0 not in witness:
        raise AssertionError("bad cardinality model")
    mask = sum(1 << v for v in witness)
    if any(clique & mask == clique for clique in cliques):
        raise AssertionError("SAT witness contains a maximal clique")
    return witness


def graph_from_adj(adj: list[int]) -> nx.Graph:
    n = len(adj)
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for u in range(n):
        mask = adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            bit = mask & -mask
            mask ^= bit
            graph.add_edge(u, bit.bit_length() - 1)
    return graph


def beta_networkx_rc2(graph: nx.Graph) -> tuple[int, list[int], list[list[int]]]:
    cliques = [sorted(clique) for clique in nx.find_cliques(graph) if len(clique) >= 2]
    wcnf = WCNF()
    for clique in cliques:
        wcnf.append([-(vertex + 1) for vertex in clique])
    for vertex in graph.nodes():
        wcnf.append([vertex + 1], weight=1)
    with RC2(wcnf) as solver:
        model = solver.compute()
        beta = graph.number_of_nodes() - solver.cost
    positive = {lit for lit in model if 1 <= lit <= graph.number_of_nodes()}
    witness = [v for v in graph.nodes() if v + 1 in positive]
    if len(witness) != beta:
        raise AssertionError("RC2 size mismatch")
    chosen = set(witness)
    if any(set(clique) <= chosen for clique in cliques):
        raise AssertionError("RC2 witness contains a maximal clique")
    return beta, witness, cliques


def exact_alpha(graph: nx.Graph) -> int:
    return max(len(clique) for clique in nx.find_cliques(nx.complement(graph)))


def spectral_profile(graph: nx.Graph, cliques: list[list[int]]) -> dict:
    n = graph.number_of_nodes()
    degree = next(iter(dict(graph.degree()).values()))
    eigenvalues = np.linalg.eigvalsh(nx.to_numpy_array(graph, nodelist=range(n)))
    least = float(eigenvalues[0])
    hoffman = n * (-least) / (degree - least)
    l_graph = nx.Graph()
    l_graph.add_nodes_from(graph.nodes())
    l_graph.add_edges_from(clique for clique in cliques if len(clique) == 2)
    l_eigenvalues = np.linalg.eigvalsh(nx.to_numpy_array(l_graph, nodelist=range(n)))
    l_degrees = list(dict(l_graph.degree()).values())
    l_record = {
        "edge_count": l_graph.number_of_edges(),
        "degree_min": min(l_degrees),
        "degree_max": max(l_degrees),
        "lambda_min": float(l_eigenvalues[0]),
        "lambda_max": float(l_eigenvalues[-1]),
        "triangle_count": sum(nx.triangles(l_graph).values()) // 3,
    }
    if len(set(l_degrees)) == 1 and l_degrees[0] > 0 and l_eigenvalues[0] < -1e-10:
        l_hoffman = n * (-float(l_eigenvalues[0])) / (l_degrees[0] - float(l_eigenvalues[0]))
        l_record["hoffman_independence_upper_bound_real"] = l_hoffman
        l_record["hoffman_independence_upper_bound_integer"] = math.floor(l_hoffman + 1e-9)
    return {
        "lambda_min": least,
        "lambda_second": float(eigenvalues[-2]),
        "lambda_max": float(eigenvalues[-1]),
        "hoffman_independence_upper_bound_real": float(hoffman),
        "hoffman_independence_upper_bound_integer": math.floor(hoffman + 1e-9),
        "triangle_free_edge_graph": l_record,
    }


def audit_family(family: str, path: Path, base_size: int) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    sources = raw["beta_near_misses"]
    states = []
    for source in sources:
        adj = adj_for_record(family, source)
        states.append(
            {
                "source": source,
                "id": record_id(family, source),
                "adj": adj,
                "cliques": bitset_cliques(family, adj),
                "last_witness": source["witness"],
            }
        )

    tested_levels = []
    level = base_size + 1
    while True:
        failures = []
        for state in states:
            witness = admissible_model(len(state["adj"]), state["cliques"], level)
            if witness is None:
                failures.append(state)
            else:
                state["last_witness"] = witness
        tested_levels.append(
            {"size": level, "sat_count": len(states) - len(failures), "unsat_count": len(failures)}
        )
        if failures:
            minimum_beta = level - 1
            minimizers = failures
            break
        level += 1
        if level > len(states[0]["adj"]):
            raise AssertionError("no beta ceiling found")

    chosen = min(minimizers, key=lambda state: state["id"])
    graph = graph_from_adj(chosen["adj"])
    beta_b, witness_b, cliques_b = beta_networkx_rc2(graph)
    if beta_b != minimum_beta:
        raise AssertionError(f"checker disagreement: {minimum_beta} versus {beta_b}")
    clique_masks_b = {sum(1 << v for v in clique) for clique in cliques_b}
    if clique_masks_b != set(chosen["cliques"]):
        raise AssertionError("independent maximal-clique enumerations disagree")

    parameters = (
        {"steps": chosen["source"]["steps"]}
        if family.startswith("cyclic")
        else {
            "involution": chosen["source"]["involution"],
            "inverse_pair_generators": chosen["source"]["inverse_pair_generators"],
        }
    )
    return {
        "input": str(path.relative_to(ROOT)),
        "threshold_survivor_count": len(states),
        "tested_levels": tested_levels,
        "minimum_beta_among_alpha_threshold_survivors": minimum_beta,
        "minimum_record_count_at_that_value": len(minimizers),
        "checker_a": "bitset Bron--Kerbosch plus CaDiCaL exact-cardinality SAT",
        "checker_b": "NetworkX find_cliques plus RC2 weighted MaxSAT",
        "checked_minimizer": {
            "id": chosen["id"],
            "parameters": parameters,
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "degree": next(iter(dict(graph.degree()).values())),
            "alpha": exact_alpha(graph),
            "beta_checker_a": minimum_beta,
            "beta_checker_a_witness": chosen["last_witness"],
            "beta_checker_b": beta_b,
            "beta_checker_b_witness": witness_b,
            "maximal_clique_count": len(cliques_b),
            "maximal_clique_size_distribution": dict(
                sorted(Counter(str(len(clique)) for clique in cliques_b).items())
            ),
            "spectrum": spectral_profile(graph, cliques_b),
        },
    }


def main() -> int:
    started = time.time()
    specifications = {
        "cyclic_50": (HERE / "scan_circulants_n50.result.json", 11),
        "abelian_50": (HERE / "scan_abelian_n50.result.json", 11),
        "cyclic_59": (HERE / "scan_circulants_n59.result.json", 12),
    }
    families = {
        family: audit_family(family, path, base_size)
        for family, (path, base_size) in specifications.items()
    }
    result = {
        "schema": SCHEMA,
        "families": families,
        "runtime_seconds": time.time() - started,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output = HERE / "audit_family_minima.result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                family: {
                    "minimum_beta_among_alpha_threshold_survivors": data[
                        "minimum_beta_among_alpha_threshold_survivors"
                    ],
                    "minimum_record_count_at_that_value": data[
                        "minimum_record_count_at_that_value"
                    ],
                    "tested_levels": data["tested_levels"],
                }
                for family, data in families.items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
