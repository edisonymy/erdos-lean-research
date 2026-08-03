#!/usr/bin/env python3
"""Exact scan of all undirected circulants on Z_50 with Delta <= 10.

For a step set D subset {1,...,25}, where 25 is self-inverse, the graph has
edges x--(x+d) modulo 50.  Steps 1..24 contribute degree two and step 25
contributes degree one.  We quotient only by the sound multiplier action of
the units of Z_50; every labelled step set is represented by one orbit
minimum, so a zero-hit result covers the full stated family.

The target is beta(G) <= 10.  Since H(50)=11, any hit is a counterexample to
Erdos #151.  Stage 1 checks the necessary alpha(G) <= 10 condition.  Stage 2
enumerates all nontrivial inclusion-maximal cliques and asks whether an
admissible 11-set exists.  Translation symmetry soundly fixes vertex 0 in
both SAT queries.

Dependencies: Python 3.12 and python-sat (already pinned in the workspace).
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


N = 50
TARGET = 11
UNITS = tuple(a for a in range(1, N) if math.gcd(a, N) == 1)
SCHEMA = "erdos151-circulant-n50-scan-v1"


def norm_step(x: int) -> int:
    x %= N
    if x == 0:
        raise ValueError("zero is not a step")
    return min(x, N - x)


def multiplier_images(steps: tuple[int, ...]):
    for a in UNITS:
        yield tuple(sorted({norm_step(a * d) for d in steps}))


def canonical_steps(steps: tuple[int, ...]) -> tuple[int, ...]:
    return min(multiplier_images(steps))


def degree_of_steps(steps: tuple[int, ...]) -> int:
    return 2 * len(steps) - (1 if 25 in steps else 0)


def connected_steps(steps: tuple[int, ...]) -> bool:
    return math.gcd(N, *steps) == 1


def all_orbit_representatives():
    """Yield exactly one multiplier-orbit representative at degree <= 10."""
    seen: set[tuple[int, ...]] = set()
    paired = tuple(range(1, 25))
    for use_opposite in (False, True):
        max_pairs = 5 if not use_opposite else 4
        for size in range(max_pairs + 1):
            for combo in itertools.combinations(paired, size):
                steps = combo + ((25,) if use_opposite else ())
                if not steps or not connected_steps(steps):
                    continue
                canon = canonical_steps(steps)
                if canon in seen:
                    continue
                seen.add(canon)
                yield canon


def adjacency(steps: tuple[int, ...]) -> list[int]:
    adj = [0] * N
    for u in range(N):
        for d in steps:
            v = (u + d) % N
            if u != v:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    expected = degree_of_steps(steps)
    if any(mask.bit_count() != expected for mask in adj):
        raise AssertionError("circulant degree mismatch")
    return adj


def edges_from_adj(adj: list[int]):
    for u in range(N):
        mask = adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            bit = mask & -mask
            v = bit.bit_length() - 1
            mask ^= bit
            yield u, v


def maximal_cliques(adj: list[int]) -> list[int]:
    """Bron--Kerbosch with pivot, returning all maximal cliques of size >=2."""
    out: list[int] = []

    def bk(r: int, p: int, x: int) -> None:
        if not p and not x:
            if r.bit_count() >= 2:
                out.append(r)
            return
        px = p | x
        pivot = -1
        best = -1
        scan = px
        while scan:
            bit = scan & -scan
            u = bit.bit_length() - 1
            scan ^= bit
            score = (p & adj[u]).bit_count()
            if score > best:
                best = score
                pivot = u
        candidates = p if pivot < 0 else p & ~adj[pivot]
        while candidates:
            bit = candidates & -candidates
            v = bit.bit_length() - 1
            candidates ^= bit
            bk(r | bit, p & adj[v], x & adj[v])
            p ^= bit
            x |= bit

    bk(0, (1 << N) - 1, 0)
    if len(out) != len(set(out)):
        raise AssertionError("duplicate maximal clique")
    return out


def selected_model(model: list[int]) -> list[int]:
    positives = {lit for lit in model if 1 <= lit <= N}
    return [v for v in range(N) if v + 1 in positives]


def size_target_model(clauses: list[list[int]]) -> list[int] | None:
    """Return a size-11 model containing vertex 0, or None if UNSAT."""
    pool = IDPool(start_from=N + 1)
    formula = list(clauses)
    formula.append([1])  # translation symmetry: rotate a nonempty set to 0
    formula.extend(
        CardEnc.equals(
            lits=list(range(1, N + 1)),
            bound=TARGET,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=formula) as solver:
        if not solver.solve():
            return None
        chosen = selected_model(solver.get_model())
    if len(chosen) != TARGET or 0 not in chosen:
        raise AssertionError("bad cardinality model")
    return chosen


def independent_11(adj: list[int]) -> list[int] | None:
    return size_target_model([[-(u + 1), -(v + 1)] for u, v in edges_from_adj(adj)])


def admissible_11(cliques: list[int]) -> list[int] | None:
    clauses: list[list[int]] = []
    for clique in cliques:
        clauses.append([-(v + 1) for v in range(N) if clique >> v & 1])
    return size_target_model(clauses)


def edge_hash(adj: list[int]) -> str:
    payload = ";".join(f"{u}-{v}" for u, v in edges_from_adj(adj)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def validate_witness(witness: list[int], forbidden: list[int]) -> None:
    mask = sum(1 << v for v in witness)
    if any(item & mask == item for item in forbidden):
        raise AssertionError("recorded witness violates a forbidden set")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".result.json"))
    parser.add_argument("--limit", type=int, default=None, help="development-only orbit limit")
    args = parser.parse_args()

    started = time.time()
    counters = Counter()
    degree_orbits = Counter()
    alpha_survivors_by_degree = Counter()
    beta_hits: list[dict] = []
    beta_near_misses: list[dict] = []
    sample_failures: list[dict] = []

    reps = all_orbit_representatives()
    for index, steps in enumerate(reps):
        if args.limit is not None and index >= args.limit:
            break
        counters["orbits_tested"] += 1
        degree = degree_of_steps(steps)
        degree_orbits[str(degree)] += 1
        adj = adjacency(steps)

        iw = independent_11(adj)
        if iw is not None:
            counters["killed_by_independent_11"] += 1
            if len(sample_failures) < 12:
                sample_failures.append({"steps": list(steps), "reason": "alpha>=11", "witness": iw})
            continue

        counters["alpha_le_10"] += 1
        alpha_survivors_by_degree[str(degree)] += 1
        cliques = maximal_cliques(adj)
        aw = admissible_11(cliques)
        if aw is not None:
            validate_witness(aw, cliques)
            counters["killed_by_admissible_11"] += 1
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
            if len(sample_failures) < 24:
                sample_failures.append(
                    {
                        "steps": list(steps),
                        "reason": "beta>=11",
                        "witness": aw,
                        "maximal_clique_count": len(cliques),
                        "maximal_clique_size_distribution": dict(
                            sorted(Counter(str(c.bit_count()) for c in cliques).items())
                        ),
                    }
                )
            continue

        counters["beta_le_10_hits"] += 1
        beta_hits.append(
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
        "family": "all connected undirected Cayley graphs Cay(Z_50,D) of degree at most 10",
        "quotient": "one representative per action D -> aD, a a unit modulo 50",
        "n": N,
        "H_50": 11,
        "target": "beta <= 10",
        "counters": dict(counters),
        "orbit_counts_by_degree": dict(sorted(degree_orbits.items(), key=lambda x: int(x[0]))),
        "alpha_le_10_by_degree": dict(
            sorted(alpha_survivors_by_degree.items(), key=lambda x: int(x[0]))
        ),
        "candidate_count": len(beta_hits),
        "candidates": beta_hits,
        "beta_near_misses": beta_near_misses,
        "sample_failures": sample_failures,
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
