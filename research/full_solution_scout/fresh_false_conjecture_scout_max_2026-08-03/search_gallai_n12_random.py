#!/usr/bin/env python3
"""Bounded candidate-first probe at the true small-order frontier of #583.

Botler--Cano--Sambinelli (2019) verified Gallai's conjecture through order 11,
so this deliberately does *not* enumerate smaller graphs.  It samples graphs
of order 12, rejects graphs covered by several published sufficient classes,
and asks an exact Z3 sequence model whether their edges can be partitioned
into six simple paths.

This is a discovery probe, not an exhaustive verification.  SAT models are
checked by independent plain-Python code.  Any UNSAT answer is only a
candidate until a separately implemented certified SAT encoding also proves
UNSAT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import z3


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).strip().decode("ascii")


def outside_easy_classes(G: nx.Graph) -> tuple[bool, str]:
    """Apply only sound, coarse filters; this does not characterize hardness."""
    if not nx.is_connected(G):
        return False, "disconnected"
    if max(nx.core_number(G).values()) <= 3:
        return False, "3-degenerate"
    if max(dict(G.degree()).values()) <= 5:
        return False, "maximum-degree-at-most-5"
    if nx.is_bipartite(G):
        return False, "bipartite-through-order-16"
    if len(set(dict(G.degree()).values())) == 1:
        return False, "regular-through-order-14"
    if nx.check_planarity(G)[0]:
        return False, "planar"

    # Botler--Sambinelli (2021 journal version of arXiv:1911.04546)
    # includes E-subgraphs of maximum degree at most three.  Here the
    # E-subgraph is induced by the even-degree vertices of G.
    even = [v for v, d in G.degree() if d % 2 == 0]
    E = G.subgraph(even)
    if not even or max((d for _, d in E.degree()), default=0) <= 3:
        return False, "even-degree-subgraph-max-degree-at-most-3"
    return True, "accepted"


def solve_six_paths(
    G: nx.Graph, timeout_ms: int
) -> tuple[str, list[list[int]] | None, float, str]:
    """Decide existence of an edge partition into <= 6 simple paths.

    Each path is represented by a length and a vertex sequence.  Active
    sequence vertices are pairwise distinct, consecutive vertices are
    adjacent, and every graph edge occurs as exactly one active step across
    all six sequences.  This is an exact finite formulation.
    """
    n = len(G)
    k = (n + 1) // 2
    edges = [tuple(sorted(e)) for e in G.edges()]
    edge_set = set(edges)
    lengths = [z3.Int(f"length_{p}") for p in range(k)]
    seq = [[z3.Int(f"v_{p}_{i}") for i in range(n)] for p in range(k)]
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)

    # Redundant consequences and symmetry breakers are important here: the six
    # path labels and the two orientations of every path are interchangeable.
    solver.add(z3.Sum(lengths) == len(edges))
    for p in range(k - 1):
        solver.add(lengths[p] >= lengths[p + 1])
        solver.add(
            z3.Implies(lengths[p] == lengths[p + 1], seq[p][0] <= seq[p + 1][0])
        )

    for p in range(k):
        solver.add(lengths[p] >= 0, lengths[p] <= n - 1)
        for i in range(n):
            solver.add(seq[p][i] >= 0, seq[p][i] < n)
        for i in range(n):
            for j in range(i + 1, n):
                solver.add(z3.Implies(j <= lengths[p], seq[p][i] != seq[p][j]))
        solver.add(
            z3.Or(
                lengths[p] == 0,
                *[
                    z3.And(lengths[p] == length, seq[p][0] < seq[p][length])
                    for length in range(1, n)
                ],
            )
        )
        for i in range(n - 1):
            allowed = []
            for u, v in edges:
                allowed.append(z3.And(seq[p][i] == u, seq[p][i + 1] == v))
                allowed.append(z3.And(seq[p][i] == v, seq[p][i + 1] == u))
            solver.add(z3.Implies(i < lengths[p], z3.Or(allowed)))

    for u, v in edges:
        occurrences = []
        for p in range(k):
            for i in range(n - 1):
                occurrences.append(
                    z3.And(
                        i < lengths[p],
                        z3.Or(
                            z3.And(seq[p][i] == u, seq[p][i + 1] == v),
                            z3.And(seq[p][i] == v, seq[p][i + 1] == u),
                        ),
                    )
                )
        solver.add(z3.PbEq([(term, 1) for term in occurrences], 1))

    started = time.perf_counter()
    answer = solver.check()
    elapsed = time.perf_counter() - started
    if answer == z3.sat:
        model = solver.model()
        paths = []
        for p in range(k):
            length = model.eval(lengths[p]).as_long()
            if length:
                paths.append(
                    [model.eval(seq[p][i]).as_long() for i in range(length + 1)]
                )
        return "sat", paths, elapsed, ""
    if answer == z3.unsat:
        return "unsat", None, elapsed, ""
    return "unknown", None, elapsed, solver.reason_unknown()


def check_decomposition(G: nx.Graph, paths: list[list[int]]) -> None:
    """Logically independent, dependency-free check of a SAT witness."""
    seen: Counter[tuple[int, int]] = Counter()
    for path in paths:
        if len(path) != len(set(path)):
            raise AssertionError("model path repeats a vertex")
        for a, b in zip(path, path[1:]):
            edge = tuple(sorted((a, b)))
            if not G.has_edge(*edge):
                raise AssertionError("model uses a non-edge")
            seen[edge] += 1
    expected = Counter(tuple(sorted(e)) for e in G.edges())
    if seen != expected:
        raise AssertionError("model paths do not partition the edge set")
    if len(paths) > (len(G) + 1) // 2:
        raise AssertionError("model uses too many paths")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=58312026)
    parser.add_argument("--accepted", type=int, default=500)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--per-graph-ms", type=int, default=1500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    probabilities = [0.35, 0.425, 0.5, 0.575, 0.65, 0.725, 0.8]
    started = time.time()
    generated = 0
    accepted = 0
    sat = 0
    unknown = 0
    rejected: Counter[str] = Counter()
    by_probability: Counter[str] = Counter()
    slowest: list[dict] = []
    candidate = None
    digest = hashlib.sha256()

    while accepted < args.accepted and time.time() - started < args.seconds:
        p = rng.choice(probabilities)
        seed = rng.getrandbits(64)
        G = nx.gnp_random_graph(12, p, seed=seed)
        generated += 1
        useful, reason = outside_easy_classes(G)
        if not useful:
            rejected[reason] += 1
            continue
        accepted += 1
        code = graph6(G)
        digest.update((code + "\n").encode("ascii"))
        status, paths, elapsed, detail = solve_six_paths(G, args.per_graph_ms)
        by_probability[f"{p:.3f}:{status}"] += 1
        record = {
            "graph6": code,
            "p": p,
            "generator_seed": seed,
            "edges": G.number_of_edges(),
            "even_vertices": sum(d % 2 == 0 for _, d in G.degree()),
            "solve_seconds": elapsed,
            "status": status,
            "detail": detail,
        }
        slowest.append(record)
        slowest = sorted(slowest, key=lambda row: row["solve_seconds"], reverse=True)[:20]
        if status == "sat":
            assert paths is not None
            check_decomposition(G, paths)
            sat += 1
        elif status == "unknown":
            unknown += 1
        else:
            candidate = {
                **record,
                "edges_list": [list(sorted(e)) for e in G.edges()],
                "warning": "UNSAT is an unverified candidate, not yet a result",
            }
            break

    payload = {
        "schema": "erdos583-n12-candidate-first-v1",
        "scope": "non-exhaustive deterministic-seed random sample",
        "seed": args.seed,
        "limits": {
            "accepted": args.accepted,
            "wall_seconds": args.seconds,
            "per_graph_ms": args.per_graph_ms,
        },
        "elapsed_seconds": time.time() - started,
        "generated": generated,
        "accepted": accepted,
        "sat_with_independently_checked_decomposition": sat,
        "unknown": unknown,
        "rejected": dict(sorted(rejected.items())),
        "by_probability_and_status": dict(sorted(by_probability.items())),
        "accepted_graph6_stream_sha256": digest.hexdigest(),
        "candidate": candidate,
        "slowest": slowest,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
