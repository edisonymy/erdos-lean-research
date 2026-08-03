#!/usr/bin/env python3
"""Verify the only nonregular order-13 residual: degree sequence 4^11 3^2.

The input is the complete connected geng catalogue produced by

    geng -q -c -d3 -D4 13 25 13_m25_min3.g6

For every graph we build its compatibility graph J on E(G): two G-edges are
adjacent in J iff together they induce 2K2.  Five disjoint J-edges save five
colours from 25, so a matching of size at least five is sufficient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx


N = 13


def decode_graph6(raw: bytes) -> tuple[list[tuple[int, int]], list[int]]:
    data = raw.strip()
    if not data or data[0] != N + 63:
        raise ValueError("expected an unheaded graph6 record on 13 vertices")
    bits: list[int] = []
    for byte in data[1:]:
        value = byte - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges: list[tuple[int, int]] = []
    adjacency = [0] * N
    cursor = 0
    for upper in range(1, N):
        for lower in range(upper):
            if bits[cursor]:
                edges.append((lower, upper))
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
            cursor += 1
    return edges, adjacency


def compatibility_adjacency(
    edges: list[tuple[int, int]], adjacency: list[int]
) -> tuple[list[int], int]:
    comp = [0] * len(edges)
    count = 0
    masks = [(1 << a) | (1 << b) for a, b in edges]
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | masks[i]
        for j in range(i + 1, len(edges)):
            if not (forbidden & masks[j]):
                comp[i] |= 1 << j
                comp[j] |= 1 << i
                count += 1
    return comp, count


def greedy_five(comp: list[int]) -> list[tuple[int, int]] | None:
    """Return five disjoint compatibility edges when first-fit finds them."""
    unused = (1 << len(comp)) - 1
    chosen: list[tuple[int, int]] = []
    while unused and len(chosen) < 5:
        low = unused & -unused
        i = low.bit_length() - 1
        neighbours = comp[i] & unused
        if neighbours:
            jlow = neighbours & -neighbours
            j = jlow.bit_length() - 1
            chosen.append((i, j))
            unused &= ~((1 << i) | (1 << j))
        else:
            unused &= ~(1 << i)
    return chosen if len(chosen) == 5 else None


def exact_five(comp: list[int]) -> tuple[list[tuple[int, int]] | None, int]:
    """Use blossom only when the allocation-free first-fit misses."""
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
    return (normalized[:5] if len(normalized) >= 5 else None), len(normalized)


def validate_graph(edges: list[tuple[int, int]]) -> list[int]:
    degree = [0] * N
    graph = nx.Graph()
    graph.add_nodes_from(range(N))
    graph.add_edges_from(edges)
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    assert len(edges) == 25
    assert sorted(degree) == [3, 3] + [4] * 11
    assert nx.is_connected(graph)
    return degree


def verify_catalogue(path: Path) -> dict:
    started = time.perf_counter()
    raw_catalogue = path.read_bytes()
    records = raw_catalogue.splitlines()
    lower_bound_distribution: Counter[int] = Counter()
    failures: list[dict] = []
    first_witness: dict | None = None
    blossom_fallbacks = 0

    for index, raw in enumerate(records):
        edges, adjacency = decode_graph6(raw)
        degree = validate_graph(edges)
        comp, compatibility_edges = compatibility_adjacency(edges, adjacency)
        chosen = greedy_five(comp)
        exact_size = None
        if chosen is None:
            blossom_fallbacks += 1
            chosen, exact_size = exact_five(comp)
        lower_bound = 5 if chosen is not None else (exact_size or 0)
        lower_bound_distribution[lower_bound] += 1
        if chosen is None:
            failures.append(
                {
                    "index": index,
                    "graph6": raw.decode("ascii"),
                    "edges": [list(edge) for edge in edges],
                    "degrees": degree,
                    "compatibility_edges": compatibility_edges,
                    "matching_number": exact_size,
                }
            )
        elif first_witness is None:
            first_witness = {
                "index": index,
                "graph6": raw.decode("ascii"),
                "matching_of_five": [list(pair) for pair in chosen],
            }

    return {
        "schema": "erdos149-n13-almost-regular-catalogue-v1",
        "status": "VERIFIED" if not failures else "FAILURES_FOUND",
        "scope": (
            "All connected simple graphs on 13 vertices with minimum degree 3, "
            "maximum degree 4, and 25 edges (equivalently degree sequence 4^11 3^2)."
        ),
        "catalogue": {
            "path": str(path),
            "generator": "nauty geng -q -c -d3 -D4 13 25",
            "records": len(records),
            "bytes": len(raw_catalogue),
            "sha256": hashlib.sha256(raw_catalogue).hexdigest(),
        },
        "backend": {
            "compatibility": "direct induced-2K2 test",
            "matching": (
                "deterministic first-fit matching, with NetworkX 3.5 "
                "max_weight_matching(maxcardinality=True) fallback"
            ),
        },
        "certified_matching_lower_bound_distribution": dict(sorted(lower_bound_distribution.items())),
        "minimum_certified_matching_size": min(lower_bound_distribution) if lower_bound_distribution else None,
        "blossom_fallbacks": blossom_fallbacks,
        "failures": failures,
        "first_witness": first_witness,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "Five disjoint compatibility pairs yield a strong 20-edge-colouring. "
            "This checks only the stated catalogue slice."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("catalogue", type=Path, nargs="?", default=here / "13_m25_min3.g6")
    parser.add_argument("--out", type=Path, default=here / "n13_almost_regular_result.json")
    args = parser.parse_args()
    result = verify_catalogue(args.catalogue.resolve())
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "minimum_certified_matching_size", "certified_matching_lower_bound_distribution", "blossom_fallbacks", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
