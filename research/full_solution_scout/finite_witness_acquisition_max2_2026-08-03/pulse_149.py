#!/usr/bin/env python3
"""Bounded counterexample pulse for Erdos problem 149 at Delta=4, n=11.

We search 4-regular simple graphs.  Such a graph has 22 edges.  Let J have
one vertex per edge of G, with two vertices adjacent exactly when the two G
edges form an induced matching.  A strong 20-edge-colouring exists whenever
J contains either two vertex-disjoint edges or a triangle: these save two
colours from the all-singleton 22-colouring.

This is a discovery pulse, not an exhaustive proof.  It uses degree-preserving
2-switches and records the closest graph and an explicit 20-colouring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from pathlib import Path


N = 11


def norm_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def circulant_graph() -> set[tuple[int, int]]:
    return {
        norm_edge(v, (v + d) % N)
        for v in range(N)
        for d in (1, 2)
    }


def adjacency(edges: set[tuple[int, int]]) -> list[set[int]]:
    out = [set() for _ in range(N)]
    for a, b in edges:
        out[a].add(b)
        out[b].add(a)
    return out


def compatibility_graph(
    edges: set[tuple[int, int]],
) -> tuple[list[tuple[int, int]], list[set[int]]]:
    edge_list = sorted(edges)
    adj = adjacency(edges)
    j = [set() for _ in edge_list]
    for i, (a, b) in enumerate(edge_list):
        for k in range(i + 1, len(edge_list)):
            c, d = edge_list[k]
            if len({a, b, c, d}) != 4:
                continue
            if c in adj[a] or d in adj[a] or c in adj[b] or d in adj[b]:
                continue
            j[i].add(k)
            j[k].add(i)
    return edge_list, j


def savings_witness(j: list[set[int]]) -> dict | None:
    jedges = [(a, b) for a in range(len(j)) for b in j[a] if a < b]
    # A triangle is one colour class of size 3.
    for a, b in jedges:
        common = j[a].intersection(j[b])
        if common:
            c = min(common)
            return {"kind": "triangle", "classes": [[a, b, c]]}
    # Two disjoint J-edges are two colour classes of size 2.
    for x, (a, b) in enumerate(jedges):
        for c, d in jedges[x + 1 :]:
            if len({a, b, c, d}) == 4:
                return {"kind": "matching2", "classes": [[a, b], [c, d]]}
    return None


def violation_score(j: list[set[int]]) -> tuple[int, int, int]:
    jedges = [(a, b) for a in range(len(j)) for b in j[a] if a < b]
    triangles = 0
    for a, b in jedges:
        triangles += sum(1 for c in j[a].intersection(j[b]) if c > b)
    disjoint_pairs = 0
    for x, (a, b) in enumerate(jedges):
        for c, d in jedges[x + 1 :]:
            if len({a, b, c, d}) == 4:
                disjoint_pairs += 1
    # The first coordinate is exactly the decisive gate.
    return (1 if triangles or disjoint_pairs else 0, triangles + disjoint_pairs, len(jedges))


def switched(
    edges: set[tuple[int, int]], rng: random.Random
) -> set[tuple[int, int]] | None:
    e = tuple(edges)
    ab, cd = rng.sample(e, 2)
    a, b = ab
    c, d = cd
    if len({a, b, c, d}) != 4:
        return None
    if rng.randrange(2):
        new1, new2 = norm_edge(a, c), norm_edge(b, d)
    else:
        new1, new2 = norm_edge(a, d), norm_edge(b, c)
    if new1 in edges or new2 in edges or new1 == new2:
        return None
    out = set(edges)
    out.remove(ab)
    out.remove(cd)
    out.add(new1)
    out.add(new2)
    return out


def colouring_from_witness(edge_count: int, witness: dict) -> list[int]:
    colours = list(range(edge_count))
    for cls in witness["classes"]:
        base = min(colours[i] for i in cls)
        for i in cls:
            colours[i] = base
    # Canonicalise to 0..k-1.
    remap: dict[int, int] = {}
    return [remap.setdefault(c, len(remap)) for c in colours]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=400_000)
    parser.add_argument("--restarts", type=int, default=12)
    parser.add_argument("--seed", type=int, default=149_20260803)
    parser.add_argument("--out", type=Path, default=Path("pulse_149_result.json"))
    args = parser.parse_args()

    rng = random.Random(args.seed)
    started = time.time()
    best_edges: set[tuple[int, int]] | None = None
    best_score: tuple[int, int, int] | None = None
    evaluated = 0
    accepted = 0
    hit = None

    for restart in range(args.restarts):
        current = circulant_graph()
        # Randomise each restart before hill-climbing.
        for _ in range(200 + 40 * restart):
            proposal = switched(current, rng)
            if proposal is not None:
                current = proposal
        _, j = compatibility_graph(current)
        current_score = violation_score(j)
        temperature = 3.0
        per_restart = max(1, args.steps // args.restarts)
        for step in range(per_restart):
            proposal = switched(current, rng)
            if proposal is None:
                continue
            evaluated += 1
            _, pj = compatibility_graph(proposal)
            proposal_score = violation_score(pj)
            if best_score is None or proposal_score < best_score:
                best_score = proposal_score
                best_edges = set(proposal)
            if proposal_score[0] == 0:
                hit = set(proposal)
                break
            delta = proposal_score[1] - current_score[1]
            accept = delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 0.05))
            if accept:
                current = proposal
                current_score = proposal_score
                accepted += 1
            temperature *= 0.99997
            if step and step % 5000 == 0:
                temperature = max(temperature, 0.4)
        if hit is not None:
            break

    chosen = hit if hit is not None else best_edges
    assert chosen is not None
    edge_list, j = compatibility_graph(chosen)
    witness = savings_witness(j)
    result = {
        "schema": "erdos149-delta4-n11-pulse-v1",
        "scope": {
            "exhaustive": False,
            "n": N,
            "degree_sequence": [4] * N,
            "edge_count": 22,
            "search": "seeded degree-preserving 2-switch hill-climb",
        },
        "parameters": {
            "seed": args.seed,
            "steps_requested": args.steps,
            "restarts": args.restarts,
        },
        "statistics": {
            "proposals_evaluated": evaluated,
            "proposals_accepted": accepted,
            "elapsed_seconds": time.time() - started,
        },
        "counterexample_candidate": hit is not None,
        "best_score": list(violation_score(j)),
        "edges": [list(e) for e in edge_list],
        "compatibility_edges": sorted(
            [a, b] for a in range(len(j)) for b in j[a] if a < b
        ),
        "twenty_colour_savings_witness": witness,
    }
    if witness is not None:
        result["explicit_strong_colouring"] = colouring_from_witness(len(edge_list), witness)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.write_bytes(payload.encode())
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps({
        "counterexample_candidate": hit is not None,
        "best_score": result["best_score"],
        "evaluated": evaluated,
        "elapsed_seconds": result["statistics"]["elapsed_seconds"],
        "output": str(args.out),
        "sha256": digest,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
