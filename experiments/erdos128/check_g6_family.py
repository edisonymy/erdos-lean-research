#!/usr/bin/env python3
"""Check a graph6 family against the exact Erdos-128 half-set property.

The input is expected to be a trusted complete catalogue of the relevant
maximal Ramsey graphs.  The program itself independently decodes graph6,
checks triangle-freeness and the advertised independence-number bound, and
exhaustively finds the minimum number of edges in a floor(n/2)-set.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import hashlib
from pathlib import Path


def decode_graph6(line: bytes) -> tuple[int, set[tuple[int, int]]]:
    data = line.strip()
    if not data or data.startswith(b">>"):
        raise ValueError("only nonempty small graph6 records are supported")
    n = data[0] - 63
    if not 0 <= n <= 62:
        raise ValueError("only graph6 records with n <= 62 are supported")
    bits: list[int] = []
    for char in data[1:]:
        value = char - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    need = n * (n - 1) // 2
    if len(bits) < need:
        raise ValueError("truncated graph6 record")
    edges: set[tuple[int, int]] = set()
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                edges.add((i, j))
            pos += 1
    return n, edges


def edge_count(edges: set[tuple[int, int]], vertices: tuple[int, ...]) -> int:
    return sum((i, j) in edges for i, j in itertools.combinations(vertices, 2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("--alpha-upper", type=int, required=True)
    parser.add_argument("--screen", action="store_true",
                        help="stop each graph at the first half-set below the strict threshold")
    args = parser.parse_args()

    raw = args.catalogue.read_bytes()
    decoded = gzip.decompress(raw) if args.catalogue.suffix == ".gz" else raw
    records = [line for line in decoded.splitlines() if line]
    if not records:
        raise SystemExit("empty catalogue")
    first_n, _ = decode_graph6(records[0])
    edge_position: dict[tuple[int, int], int] = {}
    position = 0
    for j in range(1, first_n):
        for i in range(j):
            edge_position[i, j] = position
            position += 1
    half_masks = []
    for subset in itertools.combinations(range(first_n), first_n // 2):
        mask = sum(1 << edge_position[i, j] for i, j in itertools.combinations(subset, 2))
        half_masks.append((subset, mask))
    independence_masks = []
    for subset in itertools.combinations(range(first_n), args.alpha_upper + 1):
        mask = sum(1 << edge_position[i, j] for i, j in itertools.combinations(subset, 2))
        independence_masks.append((subset, mask))
    outcomes = []
    witness_histogram: dict[int, int] = {}
    for index, record in enumerate(records):
        n, edges = decode_graph6(record)
        if n != first_n:
            raise SystemExit(f"mixed graph orders: {first_n} and {n}")
        adjacency = [0] * n
        edge_mask = 0
        pos = 0
        for j in range(1, n):
            for i in range(j):
                if (i, j) in edges:
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
                    edge_mask |= 1 << pos
                pos += 1
        for i, j in edges:
            if adjacency[i] & adjacency[j]:
                raise SystemExit(f"record {index}: triangle through edge {(i, j)}")
        for subset, subset_edge_mask in independence_masks:
            if edge_mask & subset_edge_mask == 0:
                raise SystemExit(f"record {index}: independent set {subset}")

        k = n // 2
        strict = n * n // 50 + 1
        minimum = None
        witness = None
        for subset, half_mask in half_masks:
            count = (edge_mask & half_mask).bit_count()
            if minimum is None or count < minimum:
                minimum = count
                witness = subset
                if args.screen and count < strict:
                    break
        assert minimum is not None and witness is not None
        witness_histogram[minimum] = witness_histogram.get(minimum, 0) + 1
        count_key = "witness_half_edges" if args.screen else "minimum_half_edges"
        outcomes.append({"index": index, "n": n, "edges": len(edges),
                         count_key: minimum, "witness": witness,
                         "strict_counterexample_threshold": strict})

    payload = {"catalogue": str(args.catalogue),
               "compressed_sha256": hashlib.sha256(raw).hexdigest(),
               "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
               "records": len(records), "screen_mode": args.screen,
               "edge_count_histogram": witness_histogram,
               "all_ruled_out": all(
                   x["witness_half_edges" if args.screen else "minimum_half_edges"]
                   < x["strict_counterexample_threshold"] for x in outcomes)}
    if len(outcomes) <= 20:
        payload["outcomes"] = outcomes
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
