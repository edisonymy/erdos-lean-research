#!/usr/bin/env python3
"""Finite independent audit of the adjacent-terminal triangle cycle map."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


Edge = tuple[int, int]


def parse_small_g6(raw: bytes) -> tuple[int, set[Edge]]:
    data = raw.strip()
    n = data[0] - 63
    values = [value - 63 for value in data[1:]]
    edges: set[Edge] = set()
    position = 0
    for v in range(1, n):
        for u in range(v):
            if values[position // 6] & (1 << (5 - position % 6)):
                edges.add((u, v))
            position += 1
    return n, edges


def adjacency(n: int, edges: set[Edge]) -> list[set[int]]:
    rows = [set() for _ in range(n)]
    for u, v in edges:
        rows[u].add(v)
        rows[v].add(u)
    return rows


def simple_cycle_records(n: int, edges: set[Edge]) -> list[tuple[int, frozenset[Edge]]]:
    rows = adjacency(n, edges)
    result: list[tuple[int, frozenset[Edge]]] = []
    for root in range(n):
        allowed = set(range(root + 1, n))
        for first in sorted(rows[root] & allowed):
            path = [root, first]
            used = {root, first}

            def visit(vertex: int) -> None:
                if root in rows[vertex] and len(path) >= 3 and path[1] < path[-1]:
                    closed = path[1:] + path[:1]
                    cycle_edges = frozenset(
                        tuple(sorted((x, y))) for x, y in zip(path, closed)
                    )
                    result.append((len(path), cycle_edges))
                for nxt in sorted((rows[vertex] & allowed) - used):
                    used.add(nxt)
                    path.append(nxt)
                    visit(nxt)
                    path.pop()
                    used.remove(nxt)

            visit(first)
    return result


def expand_triangle(n: int, edges: set[Edge], marked: Edge) -> tuple[int, set[Edge]]:
    a, b = marked
    u, v, terminal = n, n + 1, n + 2
    expanded = set(edges)
    expanded.remove(marked)
    expanded.update({(a, u), (u, v), (b, v), (u, terminal), (v, terminal)})
    return n + 3, {tuple(sorted(edge)) for edge in expanded}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    graphs = 0
    marked_edges = 0
    cycle_instances_compared = 0
    inputs: list[dict[str, object]] = []
    for path in args.inputs:
        local_graphs = 0
        with path.open("rb") as source:
            for raw in source:
                if not raw.strip() or raw.startswith(b">"):
                    continue
                n, edges = parse_small_g6(raw)
                base_cycles = simple_cycle_records(n, edges)
                graphs += 1
                local_graphs += 1
                for marked in sorted(edges):
                    block_n, block_edges = expand_triangle(n, edges, marked)
                    observed = Counter(length for length, _ in simple_cycle_records(block_n, block_edges))
                    expected: Counter[int] = Counter({3: 1})
                    for length, cycle_edges in base_cycles:
                        if marked in cycle_edges:
                            expected[length + 2] += 1
                            expected[length + 3] += 1
                        else:
                            expected[length] += 1
                    if observed != expected:
                        raise AssertionError(
                            f"cycle-map mismatch in {path}, graph {local_graphs}, edge {marked}: "
                            f"observed={observed}, expected={expected}"
                        )
                    marked_edges += 1
                    cycle_instances_compared += sum(observed.values())
        inputs.append({"path": str(path), "sha256": digest(path), "graphs": local_graphs})

    payload = {
        "schema": "erdos64-triangle-reduction-audit-v1",
        "inputs": inputs,
        "graphs": graphs,
        "marked_edges": marked_edges,
        "expanded_cycle_instances_compared": cycle_instances_compared,
        "all_cycle_length_multisets_match": True,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
