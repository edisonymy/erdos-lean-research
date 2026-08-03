#!/usr/bin/env python3
"""Candidate-first stochastic search for an Erdős--Gyárfás counterexample.

The state space fixes a Carr-shaped degree sequence: ``high`` independent
vertices have degree four and all remaining vertices have degree three.
Degree-preserving two-switches explore the labelled state space.  The score
uses exact counts of simple 4- and 8-cycles.  Whenever those counts vanish,
the retained definition-level cycle finder supplies an actual 16- or
32-cycle; its complete edge set becomes a lazy learned penalty.  A candidate
is written only after exact searches find no cycle of any target length.

This is a witness generator, not an exhaustive computation.  Failure has no
mathematical force.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "erdos64"))
from verify_graph import find_simple_cycle, target_lengths, verify_cycle  # noqa: E402


Edge = tuple[int, int]


def edge(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def adjacency(n: int, edges: set[Edge]) -> list[set[int]]:
    result = [set() for _ in range(n)]
    for u, v in edges:
        result[u].add(v)
        result[v].add(u)
    return result


def cycle_count(adj: list[set[int]], length: int) -> int:
    """Count undirected simple cycles exactly, once per orientation."""

    n = len(adj)
    total = 0
    for root in range(n):
        path = [root]
        used = 1 << root

        def visit(vertex: int, depth: int, mask: int) -> None:
            nonlocal total
            if depth == length:
                if root in adj[vertex] and path[1] < path[-1]:
                    total += 1
                return
            for nxt in adj[vertex]:
                if nxt <= root or mask & (1 << nxt):
                    continue
                path.append(nxt)
                visit(nxt, depth + 1, mask | (1 << nxt))
                path.pop()

        for first in adj[root]:
            if first <= root:
                continue
            path.append(first)
            visit(first, 2, used | (1 << first))
            path.pop()
    return total


def cycle_edges(witness: list[int]) -> frozenset[Edge]:
    return frozenset(edge(u, v) for u, v in zip(witness, witness[1:]))


def collect_cycles_limited(
    adj: list[set[int]], length: int, limit: int, rng: random.Random
) -> list[list[int]]:
    """Return up to ``limit`` exact simple-cycle witnesses.

    Randomized neighbour order diversifies batches.  The root-minimum and
    orientation checks still ensure each undirected cycle is emitted once.
    """

    n = len(adj)
    roots = list(range(n))
    rng.shuffle(roots)
    found: list[list[int]] = []
    for root in roots:
        path = [root]

        def visit(vertex: int, depth: int, mask: int) -> bool:
            if depth == length:
                if root in adj[vertex] and path[1] < path[-1]:
                    found.append(path[:] + [root])
                return len(found) < limit
            candidates = [
                nxt for nxt in adj[vertex]
                if nxt > root and not (mask & (1 << nxt))
            ]
            rng.shuffle(candidates)
            for nxt in candidates:
                path.append(nxt)
                keep_going = visit(nxt, depth + 1, mask | (1 << nxt))
                path.pop()
                if not keep_going:
                    return False
            return True

        starts = [first for first in adj[root] if first > root]
        rng.shuffle(starts)
        for first in starts:
            path.append(first)
            keep_going = visit(first, 2, (1 << root) | (1 << first))
            path.pop()
            if not keep_going:
                return found
    return found


def validate_shape(n: int, high: int, edges: set[Edge]) -> None:
    adj = adjacency(n, edges)
    expected = [4 if v < high else 3 for v in range(n)]
    if [len(row) for row in adj] != expected:
        raise ValueError("wrong degree sequence")
    if any(edge(u, v) in edges for u in range(high) for v in range(u + 1, high)):
        raise ValueError("degree-four vertices are not independent")


def score(
    adj: list[set[int]],
    edges: set[Edge],
    learned: list[frozenset[Edge]],
) -> tuple[int, int, int, int]:
    c4 = cycle_count(adj, 4)
    c8 = cycle_count(adj, 8)
    live_learned = sum(block <= edges for block in learned)
    scalar = 1_000_000 * c4 + 1_000 * c8 + live_learned
    return scalar, c4, c8, live_learned


def propose_switch(
    edges: set[Edge], high: int, rng: random.Random
) -> tuple[tuple[Edge, Edge], tuple[Edge, Edge]] | None:
    first, second = rng.sample(tuple(edges), 2)
    a, b = first
    c, d = second
    if len({a, b, c, d}) != 4:
        return None
    if rng.randrange(2):
        added = (edge(a, c), edge(b, d))
    else:
        added = (edge(a, d), edge(b, c))
    if added[0] == added[1] or any(value in edges for value in added):
        return None
    if any(u < high and v < high for u, v in added):
        return None
    return (first, second), added


def exact_target_check(n: int, edges: set[Edge]) -> tuple[int | None, list[int] | None]:
    bit_adj = [0] * n
    for u, v in edges:
        bit_adj[u] |= 1 << v
        bit_adj[v] |= 1 << u
    for length in target_lengths(n):
        witness = find_simple_cycle(bit_adj, length)
        if witness is not None:
            verify_cycle(bit_adj, witness, length)
            return length, witness
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-graph", type=Path, required=True)
    parser.add_argument("--high", type=int, required=True)
    parser.add_argument("--rng-seed", type=int, default=640064)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--steps", type=int, default=1_000_000)
    parser.add_argument("--long-batch", type=int, default=64)
    parser.add_argument("--candidate-out", type=Path, required=True)
    parser.add_argument("--best-out", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.seed_graph.read_text(encoding="utf-8"))
    n = int(data["n"])
    edges = {edge(int(u), int(v)) for u, v in data["edges"]}
    validate_shape(n, args.high, edges)
    rng = random.Random(args.rng_seed)
    learned: list[frozenset[Edge]] = []
    learned_seen: set[frozenset[Edge]] = set()
    adj = adjacency(n, edges)
    current = score(adj, edges, learned)
    best = current
    best_edges = set(edges)
    started = time.monotonic()
    deadline = started + args.seconds
    accepted = 0
    checks = 0

    for step in range(1, args.steps + 1):
        if time.monotonic() >= deadline:
            break
        proposal = propose_switch(edges, args.high, rng)
        if proposal is None:
            continue
        removed, added = proposal
        trial = set(edges)
        trial.difference_update(removed)
        trial.update(added)
        trial_adj = adjacency(n, trial)
        candidate_score = score(trial_adj, trial, learned)

        progress = min(1.0, (time.monotonic() - started) / args.seconds)
        temperature = max(0.05, 2000.0 * (1.0 - progress) ** 3)
        delta = candidate_score[0] - current[0]
        if delta <= 0 or rng.random() < math.exp(-min(delta / temperature, 700.0)):
            edges, adj, current = trial, trial_adj, candidate_score
            accepted += 1
            if current < best:
                best = current
                best_edges = set(edges)
                print(json.dumps({
                    "status": "BEST",
                    "step": step,
                    "score": current,
                    "learned": len(learned),
                    "seconds": time.monotonic() - started,
                }, sort_keys=True), flush=True)

        if current[1] == 0 and current[2] == 0 and current[3] == 0:
            checks += 1
            batch = collect_cycles_limited(adj, 16, args.long_batch, rng)
            if batch:
                added_blocks = 0
                for cycle in batch:
                    block = cycle_edges(cycle)
                    if block not in learned_seen:
                        learned_seen.add(block)
                        learned.append(block)
                        added_blocks += 1
                if added_blocks:
                    current = score(adj, edges, learned)
                    best = current
                    best_edges = set(edges)
                    print(json.dumps({
                        "status": "LEARNED_C16_BATCH",
                        "batch": added_blocks,
                        "learned": len(learned),
                        "step": step,
                        "seconds": time.monotonic() - started,
                    }, sort_keys=True), flush=True)
                    continue
            length, witness = exact_target_check(n, edges)
            if witness is None:
                payload = {
                    "schema": "erdos64-candidate-v1",
                    "n": n,
                    "edges": [list(value) for value in sorted(edges)],
                    "high": args.high,
                    "rng_seed": args.rng_seed,
                    "steps": step,
                    "exact_target_lengths": target_lengths(n),
                }
                args.candidate_out.write_text(
                    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
                )
                print(json.dumps({
                    "status": "CANDIDATE",
                    "path": str(args.candidate_out),
                    "step": step,
                    "seconds": time.monotonic() - started,
                }, sort_keys=True), flush=True)
                return 10
            block = cycle_edges(witness)
            if block not in learned_seen:
                learned_seen.add(block)
                learned.append(block)
                current = score(adj, edges, learned)
                # The objective changes when a new long-cycle cut is learned.
                # Reset the comparison baseline so ``best_out`` remains
                # meaningful for the current learned-cut family.
                best = current
                best_edges = set(edges)
                print(json.dumps({
                    "status": "LEARNED_LONG_CYCLE",
                    "length": length,
                    "learned": len(learned),
                    "step": step,
                    "seconds": time.monotonic() - started,
                }, sort_keys=True), flush=True)

    best_adj = adjacency(n, best_edges)
    best_score = score(best_adj, best_edges, learned)
    payload = {
        "schema": "erdos64-anneal-best-v1",
        "n": n,
        "high": args.high,
        "edges": [list(value) for value in sorted(best_edges)],
        "score": list(best_score),
        "learned_cycles": len(learned),
        "accepted_switches": accepted,
        "exact_checks": checks,
        "rng_seed": args.rng_seed,
        "seconds": time.monotonic() - started,
        "meaning": "heuristic best state; not a counterexample unless separately verified",
    }
    args.best_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "TIMEOUT_NO_CANDIDATE",
        "best_score": best_score,
        "learned": len(learned),
        "accepted": accepted,
        "checks": checks,
        "seconds": time.monotonic() - started,
    }, sort_keys=True), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
