#!/usr/bin/env python3
"""Construct ten compatibility pairs in every connected 4-regular n=15 graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import networkx as nx


N, M, TARGET = 15, 30, 10


def decode(raw: bytes):
    data = raw.strip()
    assert data[0] == N + 63
    bits = []
    for byte in data[1:]:
        value = byte - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges = []
    adjacency = [0] * N
    cursor = 0
    for upper in range(1, N):
        for lower in range(upper):
            if bits[cursor]:
                edges.append((lower, upper))
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
            cursor += 1
    assert len(edges) == M and [x.bit_count() for x in adjacency] == [4] * N
    return edges, adjacency


def compatibility(edges, adjacency):
    comp = [0] * M
    masks = [(1 << a) | (1 << b) for a, b in edges]
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | masks[i]
        for j in range(i + 1, M):
            if not forbidden & masks[j]:
                comp[i] |= 1 << j
                comp[j] |= 1 << i
    return comp


def first_fit(comp, reverse=False):
    unused = (1 << M) - 1
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
    graph.add_nodes_from(range(M))
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
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("catalogue", type=Path, nargs="?", default=here / "15_m30_4regular.g6")
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--out", type=Path, default=here / "n15_regular_result.json")
    args = parser.parse_args()
    raw = args.catalogue.resolve().read_bytes()
    all_records = raw.splitlines()
    records = all_records if args.max_records is None else all_records[: args.max_records]
    started = time.perf_counter()
    methods = {"low_first": 0, "high_first": 0, "blossom": 0}
    failures = []
    first_witness = None
    for index, record in enumerate(records):
        edges, adjacency = decode(record)
        comp = compatibility(edges, adjacency)
        chosen = first_fit(comp)
        method = "low_first"
        exact_size = None
        if chosen is None:
            chosen = first_fit(comp, reverse=True)
            method = "high_first"
        if chosen is None:
            chosen, exact_size = blossom(comp)
            method = "blossom"
        if chosen is None:
            failures.append({"index": index, "graph6": record.decode("ascii"), "matching_number": exact_size})
        else:
            methods[method] += 1
            if first_witness is None:
                first_witness = {"index": index, "graph6": record.decode("ascii"), "method": method, "matching": chosen}
    complete = args.max_records is None
    result = {
        "schema": "erdos149-n15-regular-v1",
        "status": "VERIFIED" if complete and not failures else ("PREFIX_CHECKED" if not failures else "FAILURES_FOUND"),
        "scope": "All connected 4-regular graphs on 15 vertices in the pinned geng catalogue.",
        "catalogue": {
            "path": str(args.catalogue.resolve()),
            "records": len(all_records),
            "records_checked": len(records),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "required_compatibility_matching": TARGET,
        "methods": methods,
        "failures": failures,
        "first_witness": first_witness,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "Ten disjoint compatibility pairs save ten colours from 30; this covers only the connected 4-regular order-15 catalogue.",
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "catalogue", "methods", "failures", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
