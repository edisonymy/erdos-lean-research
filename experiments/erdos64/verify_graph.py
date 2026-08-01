#!/usr/bin/env python3
"""Exact finite-certificate checker for Erdős problem 64.

Input JSON has the form ``{"n": 10, "edges": [[0, 1], ...]}``.  The checker
validates that the graph is finite, simple, and has minimum degree at least 3,
then exhaustively searches for simple cycles of every power-of-two length at
most ``n``.  Exit status 0 means the input is a counterexample certificate;
exit status 1 means it is not; exit status 2 means the input is malformed.

This file is intentionally independent of the SAT search in
``k4_lift_cegar.py``.  It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def adjacency_from_edges(n: int, edges: list[list[int]] | list[tuple[int, int]]) -> list[int]:
    # ``bool`` subclasses ``int`` in Python, but JSON booleans are not valid
    # vertex labels or graph orders for this certificate schema.
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    adjacency = [0] * n
    seen: set[tuple[int, int]] = set()
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError(f"invalid edge: {edge!r}")
        u, v = edge
        if type(u) is not int or type(v) is not int:
            raise ValueError(f"edge endpoints must be integers: {edge!r}")
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"edge endpoint outside 0..{n - 1}: {edge!r}")
        if u == v:
            raise ValueError(f"loop is not allowed: {edge!r}")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise ValueError(f"duplicate edge: {edge!r}")
        seen.add(key)
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    return adjacency


def find_simple_cycle(adjacency: list[int], length: int) -> list[int] | None:
    """Return one simple cycle of exactly ``length``, or ``None``.

    The smallest-labelled vertex is fixed as the root of each search.  All
    other vertices on that branch must have a larger label, so every simple
    cycle is still represented and the search is finite and exhaustive.
    """

    n = len(adjacency)
    if length < 3 or length > n:
        return None

    for root in range(n):
        forbidden_low = (1 << (root + 1)) - 1

        def dfs(vertex: int, depth: int, used: int, path: list[int]) -> list[int] | None:
            if depth == length:
                return path + [root] if adjacency[vertex] & (1 << root) else None
            candidates = adjacency[vertex] & ~used & ~forbidden_low
            while candidates:
                bit = candidates & -candidates
                candidates -= bit
                nxt = bit.bit_length() - 1
                witness = dfs(nxt, depth + 1, used | bit, path + [nxt])
                if witness is not None:
                    return witness
            return None

        candidates = adjacency[root] & ~forbidden_low
        while candidates:
            bit = candidates & -candidates
            candidates -= bit
            nxt = bit.bit_length() - 1
            witness = dfs(nxt, 2, (1 << root) | bit, [root, nxt])
            if witness is not None:
                return witness
    return None


def target_lengths(n: int) -> list[int]:
    lengths: list[int] = []
    value = 4
    while value <= n:
        lengths.append(value)
        value *= 2
    return lengths


def verify_cycle(adjacency: list[int], cycle: list[int], length: int) -> None:
    if len(cycle) != length + 1 or cycle[0] != cycle[-1]:
        raise AssertionError("cycle witness has the wrong shape")
    if len(set(cycle[:-1])) != length:
        raise AssertionError("cycle witness repeats a vertex")
    for u, v in zip(cycle, cycle[1:]):
        if not (adjacency[u] & (1 << v)):
            raise AssertionError(f"cycle witness uses non-edge {(u, v)}")


def inspect(n: int, edges: list[list[int]] | list[tuple[int, int]]) -> dict[str, object]:
    adjacency = adjacency_from_edges(n, edges)
    degrees = [row.bit_count() for row in adjacency]
    witnesses: dict[str, list[int] | None] = {}
    for length in target_lengths(n):
        witness = find_simple_cycle(adjacency, length)
        if witness is not None:
            verify_cycle(adjacency, witness, length)
        witnesses[str(length)] = witness
    minimum_degree = min(degrees, default=0)
    is_counterexample = n > 0 and minimum_degree >= 3 and all(
        witness is None for witness in witnesses.values()
    )
    return {
        "n": n,
        "edge_count": sum(degrees) // 2,
        "minimum_degree": minimum_degree,
        "target_cycle_witnesses": witnesses,
        "is_counterexample": is_counterexample,
    }


def self_test() -> None:
    k4 = [[u, v] for u in range(4) for v in range(u + 1, 4)]
    assert inspect(4, k4)["target_cycle_witnesses"]["4"] is not None

    # Standard Petersen labelling: outer 5-cycle, spokes, inner pentagram.
    petersen: list[list[int]] = []
    for i in range(5):
        petersen.append([i, (i + 1) % 5])
        petersen.append([i, 5 + i])
        petersen.append([5 + i, 5 + ((i + 2) % 5)])
    result = inspect(10, petersen)
    assert result["minimum_degree"] == 3
    assert result["target_cycle_witnesses"]["4"] is None
    assert result["target_cycle_witnesses"]["8"] is not None

    c7 = [[i, (i + 1) % 7] for i in range(7)]
    result = inspect(7, c7)
    assert result["minimum_degree"] == 2
    assert not result["is_counterexample"]
    print("self-test: PASS (K4, Petersen, C7)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.certificate is None:
        parser.error("provide a JSON certificate or --self-test")
    try:
        payload = json.loads(args.certificate.read_text(encoding="utf-8"))
        result = inspect(payload["n"], payload["edges"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"invalid certificate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["is_counterexample"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
