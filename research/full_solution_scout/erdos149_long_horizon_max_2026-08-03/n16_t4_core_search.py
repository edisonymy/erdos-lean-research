#!/usr/bin/env python3
"""Exhaust the order-16, t=4 local-equality cubic cores."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx


D = tuple(range(4))
R = tuple(range(4, 16))
TARGET = 10


def decode_graph6(raw: bytes):
    data = raw.strip()
    assert data[0] - 63 == 12
    bits = "".join(f"{byte - 63:06b}" for byte in data[1:])
    cursor = 0
    edges = []
    adjacency = [0] * 12
    for upper in range(1, 12):
        for lower in range(upper):
            if bits[cursor] == "1":
                edges.append((lower, upper))
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
            cursor += 1
    assert len(edges) == 18 and [x.bit_count() for x in adjacency] == [3] * 12
    return edges, adjacency


def triangle_free(adjacency):
    return all(not (adjacency[u] & adjacency[v]) for u in range(12) for v in range(u + 1, 12) if adjacency[u] & (1 << v))


def separated_triple(triple, adjacency):
    return all(
        not (adjacency[u] & (1 << v)) and not (adjacency[u] & adjacency[v])
        for u, v in itertools.combinations(triple, 2)
    )


def canonical_partitions(adjacency):
    def rec(remaining, blocks):
        if not remaining:
            yield tuple(blocks)
            return
        first = min(remaining)
        rest = sorted(remaining - {first})
        for pair in itertools.combinations(rest, 2):
            block = (first, *pair)
            if not separated_triple(block, adjacency):
                continue
            yield from rec(remaining - set(block), blocks + [block])

    yield from rec(set(range(12)), [])


def build(core_edges, partition):
    edges = [(a + 4, b + 4) for a, b in core_edges]
    for defect, block in zip(D, partition):
        edges.extend((defect, vertex + 4) for vertex in block)
    edges = sorted(tuple(sorted(edge)) for edge in edges)
    adjacency = [0] * 16
    for a, b in edges:
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    assert len(edges) == 30
    assert sorted(value.bit_count() for value in adjacency) == [3] * 4 + [4] * 12
    return edges, adjacency


def comp_adjacency(edges, adjacency):
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
    return normalized[:TARGET] if len(normalized) >= TARGET else None, len(normalized)


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    catalogue = here / "n16_t4_cubic_cores.g6"
    raw = catalogue.read_bytes()
    records = raw.splitlines()
    counts = Counter()
    failures = []
    first_witness = None
    for index, record in enumerate(records):
        core_edges, core_adjacency = decode_graph6(record)
        if not triangle_free(core_adjacency):
            counts["cores_rejected_with_triangle"] += 1
            continue
        counts["triangle_free_cubic_cores"] += 1
        partitions = list(canonical_partitions(core_adjacency))
        counts["separated_partitions"] += len(partitions)
        if partitions:
            counts["cores_with_partition"] += 1
        for partition in partitions:
            edges, adjacency = build(core_edges, partition)
            comp = comp_adjacency(edges, adjacency)
            chosen = greedy(comp)
            method = "low"
            exact_size = None
            if chosen is None:
                chosen = greedy(comp, reverse=True)
                method = "high"
            if chosen is None:
                chosen, exact_size = blossom(comp)
                method = "blossom"
            if chosen is None:
                failures.append(
                    {
                        "core_index": index,
                        "graph6": record.decode("ascii"),
                        "partition": partition,
                        "edges": edges,
                        "matching_number": exact_size,
                    }
                )
            else:
                counts[f"{method}_matching_success"] += 1
                if first_witness is None:
                    first_witness = {
                        "core_index": index,
                        "graph6": record.decode("ascii"),
                        "partition": partition,
                        "edges": edges,
                        "matching": chosen,
                        "method": method,
                    }
    script = Path(__file__).resolve()
    result = {
        "schema": "erdos149-n16-t4-cubic-core-v1",
        "status": "VERIFIED" if not failures else "RESIDUAL_FOUND",
        "scope": "All cubic 12-vertex cores and separated four-triple partitions forced by an order-16 smallest counterexample with four degree-three vertices.",
        "catalogue": {"records": len(records), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        "counts": dict(sorted(counts.items())),
        "required_compatibility_matching": TARGET,
        "failures": failures,
        "first_witness": first_witness,
        "script": {"bytes": script.stat().st_size, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()},
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This checks the forced t=4 core family only; ten compatibility pairs save ten colours from 30.",
    }
    (here / "n16_t4_core_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "counts", "failures", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
