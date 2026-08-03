#!/usr/bin/env python3
"""Exact low-degree circulant counterexample scan at the R(3,12) upper endpoint.

The published bound R(3,12) <= 59 implies H(59) >= 12.  Hence any graph
with beta <= 11 is a counterexample to Erdos #151.  A circulant on the odd
group Z_59 has even degree, so Delta <= 11 means at most five inverse step
pairs.  This script exhausts that entire connected family modulo unit
multipliers.  Its two SAT stages are the same definition-level tests as in
scan_circulants_n50.py, parameterized here by n=59 and target size 12.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import time
from collections import Counter
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


N = 59
TARGET = 12
UNITS = tuple(range(1, N))
SCHEMA = "erdos151-circulant-n59-scan-v1"


def norm_step(x: int) -> int:
    x %= N
    return min(x, N - x)


def canonical_steps(steps: tuple[int, ...]) -> tuple[int, ...]:
    return min(tuple(sorted({norm_step(a * d) for d in steps})) for a in UNITS)


def all_orbit_representatives():
    seen: set[tuple[int, ...]] = set()
    for size in range(1, 6):
        for steps in itertools.combinations(range(1, (N - 1) // 2 + 1), size):
            canon = canonical_steps(steps)
            if canon in seen:
                continue
            seen.add(canon)
            yield canon


def adjacency(steps: tuple[int, ...]) -> list[int]:
    adj = [0] * N
    for u in range(N):
        for d in steps:
            for sign in (-1, 1):
                v = (u + sign * d) % N
                adj[u] |= 1 << v
    expected = 2 * len(steps)
    if any(mask.bit_count() != expected for mask in adj):
        raise AssertionError("degree mismatch")
    return adj


def edges_from_adj(adj: list[int]):
    for u in range(N):
        mask = adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            bit = mask & -mask
            mask ^= bit
            yield u, bit.bit_length() - 1


def maximal_cliques(adj: list[int]) -> list[int]:
    out: list[int] = []

    def bk(r: int, p: int, x: int) -> None:
        if not p and not x:
            if r.bit_count() >= 2:
                out.append(r)
            return
        px = p | x
        pivot = -1
        score = -1
        scan = px
        while scan:
            bit = scan & -scan
            scan ^= bit
            u = bit.bit_length() - 1
            value = (p & adj[u]).bit_count()
            if value > score:
                pivot, score = u, value
        choices = p if pivot < 0 else p & ~adj[pivot]
        while choices:
            bit = choices & -choices
            choices ^= bit
            v = bit.bit_length() - 1
            bk(r | bit, p & adj[v], x & adj[v])
            p ^= bit
            x |= bit

    bk(0, (1 << N) - 1, 0)
    return out


def target_model(clauses: list[list[int]]) -> list[int] | None:
    pool = IDPool(start_from=N + 1)
    formula = list(clauses)
    formula.append([1])
    formula.extend(
        CardEnc.equals(
            list(range(1, N + 1)),
            TARGET,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=formula) as solver:
        if not solver.solve():
            return None
        positive = {lit for lit in solver.get_model() if 1 <= lit <= N}
    result = [v for v in range(N) if v + 1 in positive]
    if len(result) != TARGET or 0 not in result:
        raise AssertionError("bad model")
    return result


def edge_hash(adj: list[int]) -> str:
    raw = ";".join(f"{u}-{v}" for u, v in edges_from_adj(adj)).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".result.json"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    started = time.time()
    counters = Counter()
    orbit_degrees = Counter()
    survivor_degrees = Counter()
    candidates: list[dict] = []
    beta_near_misses: list[dict] = []
    samples: list[dict] = []

    for index, steps in enumerate(all_orbit_representatives()):
        if args.limit is not None and index >= args.limit:
            break
        counters["orbits_tested"] += 1
        degree = 2 * len(steps)
        orbit_degrees[str(degree)] += 1
        adj = adjacency(steps)
        independent_clauses = [[-(u + 1), -(v + 1)] for u, v in edges_from_adj(adj)]
        iw = target_model(independent_clauses)
        if iw is not None:
            counters["killed_by_independent_12"] += 1
            if len(samples) < 12:
                samples.append({"steps": list(steps), "reason": "alpha>=12", "witness": iw})
            continue
        counters["alpha_le_11"] += 1
        survivor_degrees[str(degree)] += 1
        cliques = maximal_cliques(adj)
        clique_clauses = [
            [-(v + 1) for v in range(N) if clique >> v & 1] for clique in cliques
        ]
        aw = target_model(clique_clauses)
        if aw is not None:
            mask = sum(1 << v for v in aw)
            if any(clique & mask == clique for clique in cliques):
                raise AssertionError("inadmissible witness")
            counters["killed_by_admissible_12"] += 1
            beta_near_misses.append(
                {
                    "steps": list(steps),
                    "degree": degree,
                    "witness": aw,
                    "maximal_clique_count": len(cliques),
                    "maximal_clique_size_distribution": dict(
                        sorted(Counter(str(c.bit_count()) for c in cliques).items())
                    ),
                }
            )
            if len(samples) < 24:
                samples.append(
                    {
                        "steps": list(steps),
                        "reason": "beta>=12",
                        "witness": aw,
                        "maximal_clique_count": len(cliques),
                        "maximal_clique_size_distribution": dict(
                            sorted(Counter(str(c.bit_count()) for c in cliques).items())
                        ),
                    }
                )
            continue
        counters["beta_le_11_hits"] += 1
        candidates.append(
            {
                "steps": list(steps),
                "degree": degree,
                "edge_sha256": edge_hash(adj),
                "edges": [list(edge) for edge in edges_from_adj(adj)],
                "maximal_cliques": [
                    [v for v in range(N) if clique >> v & 1] for clique in cliques
                ],
            }
        )

    complete = args.limit is None
    result = {
        "schema": SCHEMA,
        "complete": complete,
        "family": "all connected undirected circulants Cay(Z_59,+/-D) with degree at most 10",
        "quotient": "one representative per nonzero multiplier action",
        "n": N,
        "published_input": "R(3,12) <= 59, hence H(59) >= 12",
        "target": "beta <= 11",
        "counters": dict(counters),
        "orbit_counts_by_degree": dict(sorted(orbit_degrees.items(), key=lambda x: int(x[0]))),
        "alpha_le_11_by_degree": dict(sorted(survivor_degrees.items(), key=lambda x: int(x[0]))),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "beta_near_misses": beta_near_misses,
        "sample_failures": samples,
        "runtime_seconds": time.time() - started,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "solver": "CaDiCaL 1.9.5 through python-sat",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("complete", "counters", "candidate_count", "runtime_seconds")}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
