#!/usr/bin/env python3
"""Witness-producing checks for the two order-14 minimal-counterexample slices."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import networkx as nx


N = 14


def decode_graph6(raw: bytes) -> tuple[list[tuple[int, int]], list[int]]:
    data = raw.strip()
    if not data or data[0] != N + 63:
        raise ValueError("expected an unheaded graph6 record on 14 vertices")
    bit_buffer = 0
    bit_count = 0
    payload = iter(data[1:])
    edges: list[tuple[int, int]] = []
    adjacency = [0] * N
    for upper in range(1, N):
        for lower in range(upper):
            if bit_count == 0:
                bit_buffer = next(payload) - 63
                bit_count = 6
            bit_count -= 1
            if (bit_buffer >> bit_count) & 1:
                edges.append((lower, upper))
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
    return edges, adjacency


def compatibility_adjacency(
    edges: list[tuple[int, int]], adjacency: list[int]
) -> tuple[list[int], int]:
    comp = [0] * len(edges)
    count = 0
    endpoint_masks = [(1 << a) | (1 << b) for a, b in edges]
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | endpoint_masks[i]
        for j in range(i + 1, len(edges)):
            if not forbidden & endpoint_masks[j]:
                comp[i] |= 1 << j
                comp[j] |= 1 << i
                count += 1
    return comp, count


def first_fit(comp: list[int], target: int, reverse: bool = False):
    unused = (1 << len(comp)) - 1
    chosen = []
    while unused and len(chosen) < target:
        if reverse:
            i = unused.bit_length() - 1
            neighbours = comp[i] & unused
            if neighbours:
                j = neighbours.bit_length() - 1
            else:
                j = -1
        else:
            low = unused & -unused
            i = low.bit_length() - 1
            neighbours = comp[i] & unused
            if neighbours:
                j = (neighbours & -neighbours).bit_length() - 1
            else:
                j = -1
        if j >= 0:
            chosen.append((i, j))
            unused &= ~((1 << i) | (1 << j))
        else:
            unused &= ~(1 << i)
    return chosen if len(chosen) == target else None


def blossom(comp: list[int], target: int):
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
    return (normalized[:target] if len(normalized) >= target else None), len(normalized)


def verify(path: Path, m: int, max_records: int | None) -> dict:
    expected_degrees = [3, 3] + [4] * 12 if m == 27 else [4] * 14
    target = m - 20
    raw_catalogue = path.read_bytes()
    all_records = raw_catalogue.splitlines()
    records = all_records if max_records is None else all_records[:max_records]
    started = time.perf_counter()
    low_success = reverse_success = blossom_success = 0
    failures = []
    first_witness = None
    for index, raw in enumerate(records):
        edges, adjacency = decode_graph6(raw)
        assert len(edges) == m
        assert sorted(x.bit_count() for x in adjacency) == expected_degrees
        comp, compatibility_edges = compatibility_adjacency(edges, adjacency)
        chosen = first_fit(comp, target)
        method = "low-first"
        exact_size = None
        if chosen is not None:
            low_success += 1
        else:
            chosen = first_fit(comp, target, reverse=True)
            method = "high-first"
            if chosen is not None:
                reverse_success += 1
            else:
                chosen, exact_size = blossom(comp, target)
                method = "blossom"
                if chosen is not None:
                    blossom_success += 1
        if chosen is None:
            failures.append(
                {
                    "index": index,
                    "graph6": raw.decode("ascii"),
                    "compatibility_edges": compatibility_edges,
                    "matching_number": exact_size,
                }
            )
        elif first_witness is None:
            first_witness = {
                "index": index,
                "graph6": raw.decode("ascii"),
                "method": method,
                "matching": [list(pair) for pair in chosen],
            }
    complete = max_records is None
    return {
        "schema": "erdos149-n14-slice-v1",
        "status": "VERIFIED" if complete and not failures else ("PREFIX_CHECKED" if not failures else "FAILURES_FOUND"),
        "scope": f"Connected order-14 subquartic graphs with {m} edges.",
        "catalogue": {
            "path": str(path),
            "records": len(all_records),
            "records_checked": len(records),
            "bytes": len(raw_catalogue),
            "sha256": hashlib.sha256(raw_catalogue).hexdigest(),
        },
        "edge_count": m,
        "degree_sequence": expected_degrees,
        "required_compatibility_matching": target,
        "methods": {
            "low_first_success": low_success,
            "high_first_success": reverse_success,
            "blossom_success": blossom_success,
        },
        "failures": failures,
        "first_witness": first_witness,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "A matching of m-20 compatibility edges gives a strong 20-edge-colouring; this result covers only the stated catalogue slice.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("m", type=int, choices=(27, 28))
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify(args.catalogue.resolve(), args.m, args.max_records)
    output = args.out or Path(__file__).resolve().parent / f"n14_m{args.m}_result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "catalogue", "methods", "failures", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
