#!/usr/bin/env python3
"""Determine the true minimum beta over each fully scanned Cayley family.

The main scans stop as soon as an independent set already rejects a graph.
Consequently, the deeper 16/20/25 values in audit_family_minima.py concern
only the alpha-threshold survivors.  This audit restores *all* connected orbit
representatives and raises the tested admissible-set cardinality one level at
a time until the first exact beta value is reached.

Checker A is the bitset/SAT implementation used by the scans. On the
deterministically selected minimum-hash minimizer, Checker B reconstructs the
graph with NetworkX, enumerates maximal cliques with NetworkX.find_cliques,
and maximizes an admissible set with RC2 weighted MaxSAT.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scan_abelian_n50 as a50  # noqa: E402
import scan_circulants_n50 as c50  # noqa: E402
import scan_circulants_n59 as c59  # noqa: E402
from audit_family_minima import spectral_profile  # noqa: E402


OUT = HERE / "audit_global_near_miss.result.json"


def edges_from_adj(adj: list[int]):
    for u in range(len(adj)):
        mask = adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            bit = mask & -mask
            mask ^= bit
            yield u, bit.bit_length() - 1


def exact_size_model(n: int, forbidden: list[int], size: int) -> list[int] | None:
    clauses = [
        [-(v + 1) for v in range(n) if mask >> v & 1]
        for mask in forbidden
    ]
    clauses.append([1])
    pool = IDPool(start_from=n + 1)
    clauses.extend(
        CardEnc.equals(
            lits=list(range(1, n + 1)),
            bound=size,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        positive = {literal for literal in solver.get_model() if 1 <= literal <= n}
    witness = [v for v in range(n) if v + 1 in positive]
    assert len(witness) == size and 0 in witness
    return witness


def independent_model(adj: list[int], size: int) -> list[int] | None:
    forbidden = [(1 << u) | (1 << v) for u, v in edges_from_adj(adj)]
    return exact_size_model(len(adj), forbidden, size)


def graph_from_adj(adj: list[int]):
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(range(len(adj)))
    graph.add_edges_from(edges_from_adj(adj))
    return graph


def beta_networkx_rc2(adj: list[int]) -> tuple[int, list[int], list[list[int]]]:
    import networkx as nx

    graph = graph_from_adj(adj)
    cliques = [sorted(clique) for clique in nx.find_cliques(graph) if len(clique) >= 2]
    formula = WCNF()
    for clique in cliques:
        formula.append([-(v + 1) for v in clique])
    for v in range(len(adj)):
        formula.append([v + 1], weight=1)
    with RC2(formula) as solver:
        model = solver.compute()
        positive = {literal for literal in model if 1 <= literal <= len(adj)}
    witness = [v for v in range(len(adj)) if v + 1 in positive]
    return len(witness), witness, cliques


def edge_hash(adj: list[int]) -> str:
    payload = ";".join(f"{u}-{v}" for u, v in edges_from_adj(adj)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def cyclic_50_states():
    for steps in c50.all_orbit_representatives():
        yield {"parameters": {"steps": list(steps)}, "adj": c50.adjacency(steps)}


def abelian_50_states():
    for involution, pairs in a50.all_orbit_representatives():
        adj = a50.adjacency(involution, pairs)
        if not a50.connected(adj):
            continue
        yield {
            "parameters": a50.label_record(involution, pairs),
            "adj": adj,
        }


def cyclic_59_states():
    for steps in c59.all_orbit_representatives():
        yield {"parameters": {"steps": list(steps)}, "adj": c59.adjacency(steps)}


def audit_family(name: str, state_iter, target_beta_upper: int, clique_function) -> dict:
    states = list(state_iter())
    for state in states:
        state["id"] = edge_hash(state["adj"])
        state["cliques"] = None

    tested_levels = []
    level = target_beta_upper + 2
    while True:
        counts = Counter()
        failures = []
        for state in states:
            if independent_model(state["adj"], level) is not None:
                counts["certified_by_independent_set"] += 1
                continue
            if state["cliques"] is None:
                state["cliques"] = clique_function(state["adj"])
            if exact_size_model(len(state["adj"]), state["cliques"], level) is not None:
                counts["certified_by_general_admissible_set"] += 1
                continue
            failures.append(state)

        tested_levels.append(
            {
                "size": level,
                "sat_count": len(states) - len(failures),
                "unsat_count": len(failures),
                **dict(sorted(counts.items())),
            }
        )
        if failures:
            minimum_beta = level - 1
            break
        level += 1
        if level > len(states[0]["adj"]):
            raise AssertionError("failed to encounter a beta ceiling")

    chosen = min(failures, key=lambda state: state["id"])
    witness_a = exact_size_model(
        len(chosen["adj"]), chosen["cliques"], minimum_beta
    )
    if witness_a is None:
        raise AssertionError("lower cardinality should be satisfiable at the first failing level")

    beta_b, witness_b, cliques_b = beta_networkx_rc2(chosen["adj"])
    if beta_b != minimum_beta:
        raise AssertionError(f"checker disagreement for {name}: {minimum_beta} versus {beta_b}")
    clique_masks_b = {sum(1 << v for v in clique) for clique in cliques_b}
    if clique_masks_b != set(chosen["cliques"]):
        raise AssertionError(f"maximal-clique disagreement for {name}")

    graph = graph_from_adj(chosen["adj"])
    profile = spectral_profile(graph, cliques_b)
    return {
        "family_orbit_count": len(states),
        "target_beta_upper": target_beta_upper,
        "tested_levels": tested_levels,
        "minimum_beta_entire_scanned_family": minimum_beta,
        "gap_above_counterexample_target": minimum_beta - target_beta_upper,
        "minimum_record_count": len(failures),
        "checker_a": "bitset maximal cliques plus CaDiCaL exact-cardinality SAT",
        "checker_b": "NetworkX find_cliques plus RC2 weighted MaxSAT",
        "checked_minimizer": {
            "id": chosen["id"],
            "parameters": chosen["parameters"],
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "degree": next(iter(dict(graph.degree()).values())),
            "beta_checker_a": minimum_beta,
            "beta_checker_a_witness": witness_a,
            "beta_checker_b": beta_b,
            "beta_checker_b_witness": witness_b,
            "maximal_clique_count": len(cliques_b),
            "maximal_clique_size_distribution": dict(
                sorted(Counter(str(len(clique)) for clique in cliques_b).items())
            ),
            "spectrum": profile,
        },
    }


def main() -> int:
    started = time.time()
    families = {
        "cyclic_50": audit_family("cyclic_50", cyclic_50_states, 10, c50.maximal_cliques),
        "abelian_50": audit_family("abelian_50", abelian_50_states, 10, c50.maximal_cliques),
        "cyclic_59": audit_family("cyclic_59", cyclic_59_states, 11, c59.maximal_cliques),
    }
    result = {
        "schema": "erdos151-global-cayley-near-miss-audit-v1",
        "families": families,
        "runtime_seconds": time.time() - started,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "claim_boundary": "Minima are exact only for the three stated connected Cayley families and their stated degree bounds.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                name: {
                    "minimum_beta": data["minimum_beta_entire_scanned_family"],
                    "gap": data["gap_above_counterexample_target"],
                    "minimum_record_count": data["minimum_record_count"],
                    "tested_levels": data["tested_levels"],
                }
                for name, data in families.items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
