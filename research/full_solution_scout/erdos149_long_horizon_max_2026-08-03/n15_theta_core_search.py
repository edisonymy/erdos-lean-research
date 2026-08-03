#!/usr/bin/env python3
"""Exhaust the local-equality theta cores for an order-15 m=29 counterexample.

In a smallest counterexample the two degree-three vertices a,b have distance
three.  Their neighbour sets U,W are joined by a matching of size r=2 or 3.
The remaining seven vertices X receive disjoint U- and W-neighbour blocks;
only the graph induced by X remains to be completed to degree four.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx


A, B = 0, 1
U = (2, 3, 4)
W = (5, 6, 7)
X = tuple(range(8, 15))
N = 15
TARGET_MATCHING = 9


def norm(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def w_partitions(r: int, u_blocks: tuple[tuple[int, ...], ...]):
    sizes = (2, 2, 3) if r == 2 else (2, 2, 2)
    missing_choices = (None,) if r == 2 else X
    for missing in missing_choices:
        available = tuple(x for x in X if x != missing)

        def rec(index: int, remaining: tuple[int, ...], blocks: list[tuple[int, ...]]):
            if index == 2:
                block = tuple(remaining)
                if len(block) != sizes[index]:
                    return
                if index < r and set(block) & set(u_blocks[index]):
                    return
                yield tuple(blocks + [block])
                return
            for block in itertools.combinations(remaining, sizes[index]):
                if index < r and set(block) & set(u_blocks[index]):
                    continue
                rest = tuple(x for x in remaining if x not in block)
                yield from rec(index + 1, rest, blocks + [tuple(block)])

        yield from rec(0, available, [])


def internal_completions(
    target_degrees: tuple[int, ...], forbidden: frozenset[tuple[int, int]]
):
    residual = list(target_degrees)
    chosen: list[tuple[int, int]] = []

    def rec(vertex: int):
        while vertex < len(X) and residual[vertex] == 0:
            vertex += 1
        if vertex == len(X):
            if all(value == 0 for value in residual):
                yield tuple(chosen)
            return
        candidates = [
            other
            for other in range(vertex + 1, len(X))
            if residual[other] > 0 and (vertex, other) not in forbidden
        ]
        need = residual[vertex]
        if len(candidates) < need:
            return
        for neighbours in itertools.combinations(candidates, need):
            if any(residual[other] <= 0 for other in neighbours):
                continue
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


def compatibility_adjacency(edges: list[tuple[int, int]], adjacency: list[int]):
    comp = [0] * len(edges)
    masks = [(1 << a) | (1 << b) for a, b in edges]
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | masks[i]
        for j in range(i + 1, len(edges)):
            if not forbidden & masks[j]:
                comp[i] |= 1 << j
                comp[j] |= 1 << i
    return comp


def greedy_matching(comp: list[int], target: int):
    unused = (1 << len(comp)) - 1
    chosen = []
    while unused and len(chosen) < target:
        low = unused & -unused
        i = low.bit_length() - 1
        neighbours = comp[i] & unused
        if neighbours:
            j = (neighbours & -neighbours).bit_length() - 1
            chosen.append((i, j))
            unused &= ~((1 << i) | (1 << j))
        else:
            unused ^= low
    return chosen if len(chosen) == target else None


def exact_matching(comp: list[int]):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(comp)))
    for i, neighbours in enumerate(comp):
        remaining = neighbours & ~((1 << (i + 1)) - 1)
        while remaining:
            low = remaining & -remaining
            graph.add_edge(i, low.bit_length() - 1)
            remaining ^= low
    matching = nx.max_weight_matching(graph, maxcardinality=True)
    return sorted(tuple(sorted(pair)) for pair in matching)


def build_graph(
    r: int,
    u_blocks: tuple[tuple[int, ...], ...],
    w_blocks: tuple[tuple[int, ...], ...],
    internal: tuple[tuple[int, int], ...],
):
    edges = [norm(A, u) for u in U] + [norm(B, w) for w in W]
    edges += [norm(U[i], W[i]) for i in range(r)]
    for i, block in enumerate(u_blocks):
        edges += [norm(U[i], x) for x in block]
    for i, block in enumerate(w_blocks):
        edges += [norm(W[i], x) for x in block]
    edges += [norm(X[i], X[j]) for i, j in internal]
    edges = sorted(edges)
    adjacency = [0] * N
    for a, b in edges:
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    assert len(edges) == 29
    assert sorted(value.bit_count() for value in adjacency) == [3, 3] + [4] * 13
    return edges, adjacency


def main() -> None:
    started = time.perf_counter()
    totals = Counter()
    matching_lower_bounds = Counter()
    failures = []
    first_witness = None
    for r in (2, 3):
        if r == 2:
            u_blocks = ((8, 9), (10, 11), (12, 13, 14))
        else:
            u_blocks = ((8, 9), (10, 11), (12, 13))
        for w_blocks in w_partitions(r, u_blocks):
            totals[f"r{r}_w_partitions"] += 1
            u_incidence = {x: 0 for x in X}
            w_incidence = {x: 0 for x in X}
            for block in u_blocks:
                for x in block:
                    u_incidence[x] += 1
            for block in w_blocks:
                for x in block:
                    w_incidence[x] += 1
            targets = tuple(4 - u_incidence[x] - w_incidence[x] for x in X)
            forbidden = set()
            for block in (*u_blocks, *w_blocks):
                forbidden.update(norm(X.index(a), X.index(b)) for a, b in itertools.combinations(block, 2))
            for internal in internal_completions(targets, frozenset(forbidden)):
                totals[f"r{r}_internal_completions"] += 1
                edges, adjacency = build_graph(r, u_blocks, w_blocks, internal)
                comp = compatibility_adjacency(edges, adjacency)
                chosen = greedy_matching(comp, TARGET_MATCHING)
                exact_size = None
                if chosen is None:
                    exact = exact_matching(comp)
                    exact_size = len(exact)
                    chosen = exact[:TARGET_MATCHING] if exact_size >= TARGET_MATCHING else None
                    totals["blossom_fallbacks"] += 1
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
                    matching_lower_bounds[TARGET_MATCHING] += 1
                    if first_witness is None:
                        first_witness = {
                            "r": r,
                            "u_blocks": u_blocks,
                            "w_blocks": w_blocks,
                            "internal": internal,
                            "edges": edges,
                            "matching": chosen,
                        }

    script_path = Path(__file__).resolve()
    result = {
        "schema": "erdos149-n15-theta-core-search-v1",
        "status": "VERIFIED" if not failures else "RESIDUAL_FOUND",
        "scope": "All labelled completions of the forced r=2 or r=3 theta cores for an order-15 m=29 smallest counterexample.",
        "fixed_core": {
            "degree_three_vertices": [A, B],
            "neighbour_sets": [list(U), list(W)],
            "remaining_vertices": list(X),
            "cross_matching_sizes": [2, 3],
        },
        "counts": dict(sorted(totals.items())),
        "certified_matching_lower_bound_distribution": dict(sorted(matching_lower_bounds.items())),
        "required_compatibility_matching": TARGET_MATCHING,
        "failures": failures,
        "first_witness": first_witness,
        "script": {
            "bytes": script_path.stat().st_size,
            "sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "The core reduction is mathematical; this search covers its finite labelled completion space only. Nine compatibility pairs save nine colours from 29.",
    }
    out = script_path.with_name("n15_theta_core_result.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "counts", "certified_matching_lower_bound_distribution", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
