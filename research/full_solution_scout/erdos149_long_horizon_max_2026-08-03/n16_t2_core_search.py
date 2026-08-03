#!/usr/bin/env python3
"""Exhaust the order-16, t=2 generalized theta-core completions."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx


A, B = 0, 1
U, W = (2, 3, 4), (5, 6, 7)
X = tuple(range(8, 16))
TARGET = 11


def norm(a, b):
    return (a, b) if a < b else (b, a)


def fixed_u_blocks(r):
    if r == 1:
        return ((8, 9), (10, 11, 12), (13, 14, 15))
    if r == 2:
        return ((8, 9), (10, 11), (12, 13, 14))
    return ((8, 9), (10, 11), (12, 13))


def w_partitions(r, u_blocks):
    sizes = tuple(2 if i < r else 3 for i in range(3))
    for missing in itertools.combinations(X, r - 1):
        remaining0 = tuple(x for x in X if x not in missing)

        def rec(index, remaining, blocks):
            if index == 2:
                block = tuple(remaining)
                if len(block) == sizes[index] and not (index < r and set(block) & set(u_blocks[index])):
                    yield tuple(blocks + [block])
                return
            for block in itertools.combinations(remaining, sizes[index]):
                if index < r and set(block) & set(u_blocks[index]):
                    continue
                rest = tuple(x for x in remaining if x not in block)
                yield from rec(index + 1, rest, blocks + [tuple(block)])

        yield from rec(0, remaining0, [])


def completions(target, forbidden):
    residual = list(target)
    chosen = []

    def rec(vertex):
        while vertex < 8 and residual[vertex] == 0:
            vertex += 1
        if vertex == 8:
            if all(value == 0 for value in residual):
                yield tuple(chosen)
            return
        candidates = [
            other
            for other in range(vertex + 1, 8)
            if residual[other] > 0 and (vertex, other) not in forbidden
        ]
        need = residual[vertex]
        if len(candidates) < need:
            return
        for neighbours in itertools.combinations(candidates, need):
            residual[vertex] = 0
            for other in neighbours:
                residual[other] -= 1
                chosen.append((vertex, other))
            if all(value >= 0 for value in residual) and sum(residual) % 2 == 0:
                yield from rec(vertex + 1)
            for _ in neighbours:
                chosen.pop()
            for other in neighbours:
                residual[other] += 1
            residual[vertex] = need

    yield from rec(0)


def build(r, u_blocks, w_blocks, internal):
    edges = [norm(A, u) for u in U] + [norm(B, w) for w in W]
    edges += [norm(U[i], W[i]) for i in range(r)]
    for i, block in enumerate(u_blocks):
        edges += [norm(U[i], x) for x in block]
    for i, block in enumerate(w_blocks):
        edges += [norm(W[i], x) for x in block]
    edges += [norm(X[a], X[b]) for a, b in internal]
    edges = sorted(edges)
    adjacency = [0] * 16
    for a, b in edges:
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    assert len(edges) == 31 and sorted(value.bit_count() for value in adjacency) == [3, 3] + [4] * 14
    return edges, adjacency


def compatibility(edges, adjacency):
    comp = [0] * len(edges)
    masks = [(1 << a) | (1 << b) for a, b in edges]
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | masks[i]
        for j in range(i + 1, len(edges)):
            if not forbidden & masks[j]:
                comp[i] |= 1 << j
                comp[j] |= 1 << i
    return comp


def greedy(comp, reverse=False):
    unused = (1 << len(comp)) - 1
    chosen = []
    while unused and len(chosen) < TARGET:
        i = unused.bit_length() - 1 if reverse else (unused & -unused).bit_length() - 1
        neighbours = comp[i] & unused
        if neighbours:
            j = neighbours.bit_length() - 1 if reverse else (neighbours & -neighbours).bit_length() - 1
            chosen.append((i, j))
            unused &= ~((1 << i) | (1 << j))
        else:
            unused &= ~(1 << i)
    return chosen if len(chosen) == TARGET else None


def blossom(comp):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(comp)))
    for i, neighbours in enumerate(comp):
        remaining = neighbours & ~((1 << (i + 1)) - 1)
        while remaining:
            low = remaining & -remaining
            graph.add_edge(i, low.bit_length() - 1)
            remaining ^= low
    matching = nx.max_weight_matching(graph, maxcardinality=True)
    normalized = sorted(tuple(sorted(pair)) for pair in matching)
    return (normalized[:TARGET] if len(normalized) >= TARGET else None), len(normalized)


def main() -> None:
    started = time.perf_counter()
    counts = Counter()
    failures = []
    first_witness = None
    for r in (1, 2, 3):
        u_blocks = fixed_u_blocks(r)
        for w_blocks in w_partitions(r, u_blocks):
            counts[f"r{r}_w_partitions"] += 1
            u_incidence = {x: 0 for x in X}
            w_incidence = {x: 0 for x in X}
            for block in u_blocks:
                for x in block:
                    u_incidence[x] += 1
            for block in w_blocks:
                for x in block:
                    w_incidence[x] += 1
            target = tuple(4 - u_incidence[x] - w_incidence[x] for x in X)
            forbidden = set()
            for block in (*u_blocks, *w_blocks):
                forbidden.update(norm(X.index(a), X.index(b)) for a, b in itertools.combinations(block, 2))
            for internal in completions(target, frozenset(forbidden)):
                counts[f"r{r}_internal_completions"] += 1
                edges, adjacency = build(r, u_blocks, w_blocks, internal)
                comp = compatibility(edges, adjacency)
                chosen = greedy(comp)
                method = "low"
                exact_size = None
                if chosen is None:
                    chosen = greedy(comp, reverse=True)
                    method = "high"
                if chosen is None:
                    chosen, exact_size = blossom(comp)
                    method = "blossom"
                    counts["blossom_fallbacks"] += 1
                if chosen is None:
                    failures.append(
                        {
                            "r": r,
                            "u_blocks": u_blocks,
                            "w_blocks": w_blocks,
                            "internal": internal,
                            "edges": edges,
                            "matching_number": exact_size,
                        }
                    )
                else:
                    counts[f"{method}_matching_success"] += 1
                    if first_witness is None:
                        first_witness = {
                            "r": r,
                            "u_blocks": u_blocks,
                            "w_blocks": w_blocks,
                            "internal": internal,
                            "edges": edges,
                            "matching": chosen,
                            "method": method,
                        }
    script = Path(__file__).resolve()
    result = {
        "schema": "erdos149-n16-t2-theta-core-v1",
        "status": "VERIFIED" if not failures else "RESIDUAL_FOUND",
        "scope": "All r=1,2,3 generalized theta-core completions forced by an order-16 m=31 smallest counterexample.",
        "counts": dict(sorted(counts.items())),
        "required_compatibility_matching": TARGET,
        "failures": failures,
        "first_witness": first_witness,
        "script": {"bytes": script.stat().st_size, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()},
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This checks the forced t=2 core family only; eleven compatibility pairs save eleven colours from 31.",
    }
    (script.with_name("n16_t2_core_result.json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "counts", "failures", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
