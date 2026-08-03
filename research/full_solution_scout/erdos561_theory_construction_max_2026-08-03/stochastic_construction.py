#!/usr/bin/env python3
"""Stochastic fixed-edge host design for the first uncovered #561 tuples.

This complements, rather than duplicates, an exhaustive unlabelled-host
search: it performs edge swaps at the conjectured bound minus one and scores a
host by the exact number of target-avoiding 2-colourings.  Zero is a complete
counterexample candidate.  The exact embedding generator comes from
construction_sweep.py; no heuristic is used in the score itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import networkx as nx

from construction_sweep import canon_edges, embedding_masks, formula


HERE = Path(__file__).resolve().parent
OUT = HERE / "stochastic_construction_result.json"

TARGETS = [
    ((3, 2), (2, 1)),
    ((1, 1, 1), (2, 2, 1)),
    ((2, 1), (2, 2, 1)),
    ((2, 1), (3, 2, 1)),
]


def exact_score(g: nx.Graph, a: tuple[int, ...], b: tuple[int, ...]):
    m = g.number_of_edges()
    r_emb = embedding_masks(g, a)
    b_emb = embedding_masks(g, b)
    avoiding = 0
    first = None
    red_hit_count = [False] * (1 << m)
    blue_hit_count = [False] * (1 << m)
    for mask in r_emb:
        free = ((1 << m) - 1) ^ mask
        sub = free
        while True:
            red_hit_count[mask | sub] = True
            if sub == 0:
                break
            sub = (sub - 1) & free
    # blue embedding iff all its edges lie outside the red mask.
    for mask in b_emb:
        free = ((1 << m) - 1) ^ mask
        sub = free
        while True:
            blue_hit_count[sub] = True
            if sub == 0:
                break
            sub = (sub - 1) & free
    for red in range(1 << m):
        if not red_hit_count[red] and not blue_hit_count[red]:
            avoiding += 1
            if first is None:
                first = red
    return avoiding, first, len(r_emb), len(b_emb)


def random_graph_no_isolates(rng: random.Random, n: int, m: int) -> nx.Graph:
    universe = [(u, v) for u in range(n) for v in range(u + 1, n)]
    while True:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(rng.sample(universe, m))
        if min(dict(g.degree()).values()) >= 1:
            return g


def mutate(rng: random.Random, g: nx.Graph) -> nx.Graph:
    h = g.copy()
    edges = list(h.edges())
    nonedges = list(nx.non_edges(h))
    for _ in range(30):
        old = rng.choice(edges)
        new = rng.choice(nonedges)
        h.remove_edge(*old)
        h.add_edge(*new)
        if min(dict(h.degree()).values()) >= 1:
            return h
        h.remove_edge(*new)
        h.add_edge(*old)
    return g.copy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=5610803)
    ap.add_argument("--restarts", type=int, default=100)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--max-targets", type=int, default=len(TARGETS))
    ap.add_argument("--target-index", type=int, default=None)
    ap.add_argument("--n-min", type=int, default=None)
    ap.add_argument("--n-max", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    all_results = []
    candidates = []

    selected = ([(TARGETS[args.target_index])]
                if args.target_index is not None else TARGETS[: args.max_targets])
    for a, b in selected:
        B, ls = formula(a, b)
        m = B - 1
        n_min = max(sum(a) + len(a), sum(b) + len(b))
        n_max = min(2 * m, n_min + 5)
        if args.n_min is not None:
            n_min = max(n_min, args.n_min)
        if args.n_max is not None:
            n_max = min(n_max, args.n_max)
        cache = {}
        best_by_n = []
        for n in range(n_min, n_max + 1):
            best = None
            best_edges = None
            best_witness = None
            best_counts = None
            evals = 0
            for restart in range(args.restarts):
                g = random_graph_no_isolates(rng, n, m)
                key = canon_edges(g)
                if key not in cache:
                    cache[key] = exact_score(g, a, b)
                    evals += 1
                cur = cache[key]
                temperature = 3.0
                for step in range(args.steps):
                    h = mutate(rng, g)
                    hkey = canon_edges(h)
                    if hkey not in cache:
                        cache[hkey] = exact_score(h, a, b)
                        evals += 1
                    nxt = cache[hkey]
                    delta = nxt[0] - cur[0]
                    if delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 0.05)):
                        g, key, cur = h, hkey, nxt
                    temperature *= 0.992
                    if best is None or cur[0] < best:
                        best = cur[0]
                        best_edges = key
                        best_witness = cur[1]
                        best_counts = cur[2:]
                        print(f"{a} vs {b}, n={n}: best avoiding={best}", flush=True)
                        if best == 0:
                            row = {
                                "a": list(a), "b": list(b), "bound": B,
                                "l_values": ls, "n": n, "m": m,
                                "edges": [list(e) for e in best_edges],
                                "red_embeddings": best_counts[0],
                                "blue_embeddings": best_counts[1],
                            }
                            candidates.append(row)
                            print("CANDIDATE " + json.dumps(row, sort_keys=True), flush=True)
                            break
                if best == 0:
                    break
            best_by_n.append({
                "n": n, "m": m, "evaluations": evals,
                "minimum_avoiding_colorings": best,
                "best_edges": [list(e) for e in best_edges] if best_edges else None,
                "avoiding_red_mask": best_witness,
                "red_embeddings": best_counts[0] if best_counts else None,
                "blue_embeddings": best_counts[1] if best_counts else None,
            })
            checkpoint = {
                "scope": "stochastic edge-swap construction at formula bound minus one",
                "seed": args.seed, "restarts": args.restarts, "steps": args.steps,
                "results": all_results + [{
                    "a": list(a), "b": list(b), "bound": B, "l_values": ls,
                    "edge_budget": m, "by_order": best_by_n,
                }],
                "candidates": candidates,
                "outcome": "CANDIDATE_FOUND" if candidates else "RUNNING_CHECKPOINT",
            }
            OUT.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if best == 0:
                break
        all_results.append({
            "a": list(a), "b": list(b), "bound": B, "l_values": ls,
            "edge_budget": m, "by_order": best_by_n,
        })
        if candidates:
            break

    payload = {
        "scope": "stochastic edge-swap construction at formula bound minus one",
        "seed": args.seed, "restarts": args.restarts, "steps": args.steps,
        "results": all_results, "candidates": candidates,
        "outcome": "CANDIDATE_FOUND" if candidates else "NO_CANDIDATE_IN_STOCHASTIC_PULSE",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": payload["outcome"],
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
