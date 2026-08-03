#!/usr/bin/env python3
"""Candidate-first exact search for a counterexample to Erdős problem 583.

For each connected graph emitted by nauty ``geng``, enumerate the edge sets of
all nonempty *simple* paths and solve the resulting bounded exact-cover problem
by backtracking.  A graph is a counterexample exactly when its edge set cannot
be partitioned into ``ceil(n/2)`` of those path masks.

This intentionally does not use the public 2024 implementation: its displayed
greedy walk can revisit vertices, and its displayed ILP does not impose
connectedness of an alleged path.  Here simplicity is enforced directly by the
DFS visited-vertex mask.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path


def parse_graph6(line: bytes) -> tuple[int, list[tuple[int, int]]]:
    data = line.strip()
    if not data or data.startswith(b">"):
        raise ValueError("empty/header graph6 line")
    if data[0] > 126 or data[0] < 63:
        raise ValueError("invalid graph6 byte")
    if data[0] == 126:
        raise ValueError("only n <= 62 is supported")
    n = data[0] - 63
    bits: list[int] = []
    for byte in data[1:]:
        value = byte - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges: list[tuple[int, int]] = []
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                edges.append((i, j))
            pos += 1
    return n, edges


def simple_path_masks(n: int, edges: list[tuple[int, int]]) -> list[int]:
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        bit = 1 << index
        adjacency[u].append((v, bit))
        adjacency[v].append((u, bit))

    masks: set[int] = set()

    def dfs(vertex: int, visited: int, edge_mask: int) -> None:
        if edge_mask:
            masks.add(edge_mask)
        for neighbor, edge_bit in adjacency[vertex]:
            neighbor_bit = 1 << neighbor
            if not visited & neighbor_bit:
                dfs(neighbor, visited | neighbor_bit, edge_mask | edge_bit)

    for start in range(n):
        dfs(start, 1 << start, 0)
    return sorted(masks, key=lambda mask: (-mask.bit_count(), mask))


def path_partition(
    n: int, edges: list[tuple[int, int]], limit: int
) -> tuple[list[int] | None, dict[str, int]]:
    paths = simple_path_masks(n, edges)
    by_edge: list[list[int]] = [[] for _ in edges]
    for path in paths:
        value = path
        while value:
            low = value & -value
            by_edge[low.bit_length() - 1].append(path)
            value ^= low

    full = (1 << len(edges)) - 1
    failed: set[tuple[int, int]] = set()
    nodes = 0

    def solve(remaining: int, slots: int) -> list[int] | None:
        nonlocal nodes
        nodes += 1
        if remaining == 0:
            return []
        if slots == 0 or math.ceil(remaining.bit_count() / max(1, n - 1)) > slots:
            return None
        key = (remaining, slots)
        if key in failed:
            return None

        value = remaining
        chosen: list[int] | None = None
        while value:
            low = value & -value
            edge_index = low.bit_length() - 1
            compatible = [p for p in by_edge[edge_index] if p & remaining == p]
            if not compatible:
                failed.add(key)
                return None
            if chosen is None or len(compatible) < len(chosen):
                chosen = compatible
            value ^= low
        assert chosen is not None
        for path in chosen:
            tail = solve(remaining ^ path, slots - 1)
            if tail is not None:
                return [path, *tail]
        failed.add(key)
        return None

    result = solve(full, limit)
    return result, {"simple_path_masks": len(paths), "search_nodes": nodes,
                    "failed_states": len(failed)}


def decode_path_mask(mask: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    return [list(edge) for i, edge in enumerate(edges) if mask & (1 << i)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=3600.0)
    parser.add_argument("--max-graphs", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    command = [str(args.geng), "-cq", str(args.n)]
    started = time.time()
    checked = 0
    decomposed = 0
    counterexample = None
    digest = hashlib.sha256()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    try:
        for raw in proc.stdout:
            if time.time() - started >= args.seconds:
                break
            if args.max_graphs and checked >= args.max_graphs:
                break
            raw = raw.strip()
            if not raw or raw.startswith(b">"):
                continue
            digest.update(raw + b"\n")
            n, edges = parse_graph6(raw)
            limit = (n + 1) // 2
            solution, stats = path_partition(n, edges, limit)
            checked += 1
            if solution is None:
                counterexample = {
                    "graph6": raw.decode("ascii"),
                    "n": n,
                    "edges": [list(edge) for edge in edges],
                    "bound": limit,
                    "search": stats,
                }
                break
            decomposed += 1
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            stderr = proc.communicate(timeout=5)[1].decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            proc.kill()
            stderr = proc.communicate()[1].decode("utf-8", "replace")

    payload = {
        "schema": "erdos583-simple-path-search-v1",
        "command": command,
        "n": args.n,
        "bound": (args.n + 1) // 2,
        "elapsed_seconds": time.time() - started,
        "checked_graphs": checked,
        "decomposed_graphs": decomposed,
        "graph6_stream_prefix_sha256": digest.hexdigest(),
        "complete": proc.returncode == 0 and counterexample is None,
        "counterexample": counterexample,
        "geng_stderr": stderr,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
