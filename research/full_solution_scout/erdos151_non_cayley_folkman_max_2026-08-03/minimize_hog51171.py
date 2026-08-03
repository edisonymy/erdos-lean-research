#!/usr/bin/env python3
"""Bounded non-Cayley attack on Erdos #151 from HoG graph 51171.

The published 43-vertex graph is edge-Ramsey for triangles.  This script
greedily removes edges while preserving that property, using several fixed
edge orders.  It then computes campaign beta exactly by weighted MaxSAT.

This is a discovery script.  Any putative beta <= 9 output must be checked by
the separate verifier before it can be treated as a candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import time
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "HoG_51171.g6"
OUT = HERE / "minimize_hog51171.result.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def edge_key(edge: tuple[int, int]) -> tuple[int, int]:
    u, v = edge
    return (u, v) if u < v else (v, u)


def triangles(graph: nx.Graph) -> list[tuple[int, int, int]]:
    found: list[tuple[int, int, int]] = []
    for a in sorted(graph):
        for b in sorted(v for v in graph[a] if v > a):
            for c in sorted(v for v in set(graph[a]).intersection(graph[b]) if v > b):
                found.append((a, b, c))
    return found


def arrowing_cnf(graph: nx.Graph) -> tuple[list[list[int]], list[tuple[int, int]]]:
    edges = sorted(edge_key(edge) for edge in graph.edges())
    index = {edge: i + 1 for i, edge in enumerate(edges)}
    clauses: list[list[int]] = []
    for a, b, c in triangles(graph):
        variables = [
            index[edge_key((a, b))],
            index[edge_key((a, c))],
            index[edge_key((b, c))],
        ]
        clauses.append(variables)
        clauses.append([-x for x in variables])
    return clauses, edges


def arrows(graph: nx.Graph, solver_name: str = "cadical195") -> bool:
    clauses, _ = arrowing_cnf(graph)
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        return not solver.solve()


def triangle_unsat_core(source: nx.Graph, seed: int) -> tuple[nx.Graph, dict]:
    """Extract one solver-level UNSAT core of triangle constraints.

    Each activation literal enables both clauses forbidding the two
    monochromatic colors of one triangle.  The union of the edges in any
    UNSAT activation core is therefore itself an arrowing subgraph.
    """
    edges = sorted(edge_key(edge) for edge in source.edges())
    edge_index = {edge: i + 1 for i, edge in enumerate(edges)}
    ordered_triangles = triangles(source)
    random.Random(seed).shuffle(ordered_triangles)
    first_activation = len(edges) + 1
    clauses: list[list[int]] = []
    activations: list[int] = []
    triangle_by_activation: dict[int, tuple[int, int, int]] = {}
    for index, (a, b, c) in enumerate(ordered_triangles):
        activation = first_activation + index
        variables = [
            edge_index[edge_key((a, b))],
            edge_index[edge_key((a, c))],
            edge_index[edge_key((b, c))],
        ]
        clauses.append([-activation, *variables])
        clauses.append([-activation, *[-x for x in variables]])
        activations.append(activation)
        triangle_by_activation[activation] = (a, b, c)
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        assert not solver.solve(assumptions=activations)
        core = solver.get_core()
        assert core
        # Re-solving is cheap and occasionally lets CaDiCaL trim its own core.
        previous = None
        while previous != len(core):
            previous = len(core)
            assert not solver.solve(assumptions=core)
            core = solver.get_core()
    used_edges: set[tuple[int, int]] = set()
    for activation in core:
        a, b, c = triangle_by_activation[abs(activation)]
        used_edges.update((edge_key((a, b)), edge_key((a, c)), edge_key((b, c))))
    graph = nx.Graph()
    graph.add_nodes_from(source.nodes())
    graph.add_edges_from(sorted(used_edges))
    assert arrows(graph)
    return graph, {
        "source_triangle_count": len(ordered_triangles),
        "unsat_core_triangle_count": len(core),
        "unsat_core_edge_union_size": len(used_edges),
    }


def maximal_cliques(graph: nx.Graph) -> list[list[int]]:
    return sorted(
        (sorted(clique) for clique in nx.find_cliques(graph) if len(clique) >= 2),
        key=lambda clique: (len(clique), clique),
    )


def exact_beta(graph: nx.Graph) -> tuple[int, list[int], list[list[int]]]:
    cliques = maximal_cliques(graph)
    formula = WCNF()
    for clique in cliques:
        formula.append([-(v + 1) for v in clique])
    for v in sorted(graph):
        formula.append([v + 1], weight=1)
    with RC2(formula, solver="cadical195") as rc2:
        model = rc2.compute()
        cost = rc2.cost
    positive = set(lit for lit in model if 1 <= lit <= graph.number_of_nodes())
    witness = [v for v in sorted(graph) if v + 1 in positive]
    assert len(witness) == graph.number_of_nodes() - cost
    for clique in cliques:
        assert not set(clique).issubset(witness)
    return len(witness), witness, cliques


def graph_record(graph: nx.Graph, beta: bool = True) -> dict:
    ts = triangles(graph)
    degree_values = [degree for _, degree in graph.degree()]
    record: dict = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "minimum_degree": min(degree_values),
        "maximum_degree": max(degree_values),
        "degree_distribution": dict(sorted(Counter(map(str, degree_values)).items())),
        "triangle_count": len(ts),
        "edge_list": [list(edge_key(edge)) for edge in sorted(graph.edges())],
        "graph6": nx.to_graph6_bytes(graph, header=False).decode("ascii").strip(),
    }
    if beta:
        value, witness, cliques = exact_beta(graph)
        record.update(
            {
                "beta": value,
                "beta_witness": witness,
                "gap_above_counterexample_target_beta_9": value - 9,
                "maximal_clique_count": len(cliques),
                "maximal_clique_size_distribution": dict(
                    sorted(Counter(map(str, map(len, cliques))).items())
                ),
            }
        )
    return record


def choose_edge(
    graph: nx.Graph,
    remaining: set[tuple[int, int]],
    strategy: str,
    rng: random.Random,
) -> tuple[int, int]:
    if strategy == "random":
        return rng.choice(sorted(remaining))
    tri_count = Counter()
    for a, b, c in triangles(graph):
        tri_count[edge_key((a, b))] += 1
        tri_count[edge_key((a, c))] += 1
        tri_count[edge_key((b, c))] += 1
    if strategy == "high_degree":
        score = lambda e: (graph.degree(e[0]) + graph.degree(e[1]), tri_count[e], e)
    elif strategy == "low_triangle":
        score = lambda e: (-tri_count[e], graph.degree(e[0]) + graph.degree(e[1]), e)
    elif strategy == "balanced":
        score = lambda e: (
            max(graph.degree(e[0]), graph.degree(e[1])),
            graph.degree(e[0]) + graph.degree(e[1]),
            -tri_count[e],
            e,
        )
    else:
        raise ValueError(strategy)
    return max(remaining, key=score)


def minimize(source: nx.Graph, strategy: str, seed: int) -> tuple[nx.Graph, dict]:
    graph, core_audit = triangle_unsat_core(source, seed)
    rng = random.Random(seed)
    remaining = {edge_key(edge) for edge in graph.edges()}
    tested = deleted = 0
    while remaining:
        edge = choose_edge(graph, remaining, strategy, rng)
        remaining.remove(edge)
        graph.remove_edge(*edge)
        tested += 1
        if arrows(graph):
            deleted += 1
        else:
            graph.add_edge(*edge)
    assert arrows(graph)
    # A one-pass minimization is exact because non-arrowing is inherited by
    # subgraphs: an edge that failed its deletion test can never become
    # deletable after more edges are removed.
    return graph, {
        **core_audit,
        "tested_edges": tested,
        "deleted_edges_after_core_extraction": deleted,
        "edge_minimal": True,
        "edge_minimality_basis": "one-pass monotonicity plus an exact SAT decision for every tested deletion",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--random-seeds", type=int, default=8)
    args = parser.parse_args()
    started = time.time()
    source = nx.from_graph6_bytes(SOURCE.read_bytes().strip())
    source = nx.convert_node_labels_to_integers(source, ordering="sorted")
    assert source.number_of_nodes() == 43
    assert arrows(source, "cadical195")
    assert arrows(source, "glucose4")

    jobs = [("high_degree", 0), ("low_triangle", 0), ("balanced", 0)]
    jobs.extend(("random", seed) for seed in range(args.random_seeds))
    cores = []
    seen: dict[str, int] = {}
    for strategy, seed in jobs:
        tick = time.time()
        core, audit = minimize(source, strategy, seed)
        encoded = nx.to_graph6_bytes(core, header=False).decode("ascii").strip()
        duplicate_of = seen.get(encoded)
        if duplicate_of is None:
            duplicate_of = len(cores)
            seen[encoded] = duplicate_of
        record = {
            "strategy": strategy,
            "seed": seed,
            "duplicate_of_core_index": duplicate_of,
            **audit,
            **graph_record(core),
            "runtime_seconds": time.time() - tick,
        }
        cores.append(record)
        print(
            json.dumps(
                {
                    "strategy": strategy,
                    "seed": seed,
                    "m": record["m"],
                    "Delta": record["maximum_degree"],
                    "beta": record["beta"],
                    "gap": record["gap_above_counterexample_target_beta_9"],
                    "runtime_seconds": record["runtime_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    result = {
        "schema": "erdos151-noncayley-hog51171-edge-minimization-v1",
        "source": {
            "name": "House of Graphs 51171",
            "url": "https://houseofgraphs.org/graphs/51171",
            "paper": "https://arxiv.org/abs/2605.16542",
            "graph6_sha256": sha256(SOURCE),
            "paper_claim": "43 vertices, 440 edges, edge-arrows (3,3)",
            **graph_record(source, beta=False),
            "arrowing_cadical195": True,
            "arrowing_glucose4": True,
        },
        "target": {
            "n": 43,
            "H_n": 10,
            "counterexample_requires_beta_at_most": 9,
            "ramsey_basis": "R(3,10)<=41<43<R(3,11), using the published lower bound R(3,11)>=47",
        },
        "jobs": len(jobs),
        "distinct_labelled_cores": len(seen),
        "cores": cores,
        "best_beta": min(core["beta"] for core in cores),
        "best_maximum_degree": min(core["maximum_degree"] for core in cores),
        "runtime_seconds": time.time() - started,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "claim_boundary": "Exact only for the source and the listed deterministic greedy edge-minimal cores; this is not an exhaustive search of subgraphs.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
