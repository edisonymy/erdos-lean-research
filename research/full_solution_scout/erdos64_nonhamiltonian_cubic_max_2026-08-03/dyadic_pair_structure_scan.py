#!/usr/bin/env python3
"""Structural scan for two edge-disjoint dyadic cycles.

Two edge-disjoint dyadic cycles immediately certify an empty dyadic edge core.
When no such pair exists, this program enumerates every dyadic cycle edge set
and computes the exact minimum size of an empty-intersection subfamily.  This
separates the common local obstruction from genuinely Helly-like exceptions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

from verify_cubic_core_independent import decode_graph6_separately


Edge = tuple[int, int]


def dyadic_masks_until_disjoint(
    neighbours: list[set[int]], edges: list[Edge]
) -> tuple[list[int], tuple[int, int] | None, bool]:
    n = len(neighbours)
    edge_index = {edge: index for index, edge in enumerate(edges)}
    masks: list[int] = []
    known: set[int] = set()
    intersection = (1 << len(edges)) - 1

    for length in (4, 8, 16, 32):
        if length > n:
            continue
        for root in range(n):
            allowed = set(range(root + 1, n))
            for first in sorted(neighbours[root] & allowed):
                path = [root, first]
                used = {root, first}
                initial = 1 << edge_index[(root, first)]

                def visit(vertex: int, mask: int) -> tuple[int, int] | None:
                    nonlocal intersection
                    if len(path) == length:
                        if root not in neighbours[vertex] or path[1] > path[-1]:
                            return None
                        closing = tuple(sorted((vertex, root)))
                        final_mask = mask | (1 << edge_index[closing])
                        if final_mask in known:
                            return None
                        for index, prior in enumerate(masks):
                            if not final_mask & prior:
                                masks.append(final_mask)
                                known.add(final_mask)
                                intersection &= final_mask
                                return index, len(masks) - 1
                        masks.append(final_mask)
                        known.add(final_mask)
                        intersection &= final_mask
                        return None

                    for nxt in sorted((neighbours[vertex] & allowed) - used):
                        used.add(nxt)
                        path.append(nxt)
                        edge = tuple(sorted((vertex, nxt)))
                        pair = visit(nxt, mask | (1 << edge_index[edge]))
                        path.pop()
                        used.remove(nxt)
                        if pair is not None:
                            return pair
                    return None

                pair = visit(first, initial)
                if pair is not None:
                    return masks, pair, intersection == 0
    return masks, None, intersection == 0


def minimum_empty_width(masks: list[int], edge_count: int) -> int | None:
    full = (1 << edge_count) - 1
    frontier = {full}
    visited = {full}
    depth = 0
    while frontier:
        depth += 1
        next_frontier: set[int] = set()
        for state in frontier:
            for cycle in masks:
                reduced = state & cycle
                if reduced == 0:
                    return depth
                if reduced != state and reduced not in visited:
                    next_frontier.add(reduced)
        visited.update(next_frontier)
        frontier = next_frontier
    return None


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--expected-order", type=int, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=25000)
    args = parser.parse_args()

    begun = time.monotonic()
    stats: Counter[str] = Counter()
    width_histogram: Counter[str] = Counter()
    first_no_pair: dict[str, object] | None = None
    largest_no_pair_cycle_family: dict[str, object] | None = None
    no_pair_examples: list[dict[str, object]] = []
    with args.input.open("rb") as source:
        for physical_line, record in enumerate(source, start=1):
            if not record.strip() or record.startswith(b">>"):
                continue
            neighbours, edges = decode_graph6_separately(record)
            if len(neighbours) != args.expected_order:
                raise ValueError("unexpected graph order")
            if len(edges) != 3 * len(neighbours) // 2 or any(len(row) != 3 for row in neighbours):
                raise ValueError("noncubic record")
            stats["graphs"] += 1
            masks, pair, full_intersection_empty = dyadic_masks_until_disjoint(neighbours, edges)
            stats["distinct_cycle_masks_examined"] += len(masks)
            if pair is not None:
                stats["two_edge_disjoint_dyadic_cycles"] += 1
                width_histogram["2"] += 1
            else:
                stats["no_edge_disjoint_dyadic_pair"] += 1
                if not full_intersection_empty:
                    stats["nonempty_dyadic_core"] += 1
                    width = None
                else:
                    width = minimum_empty_width(masks, len(edges))
                    if width is None:
                        raise AssertionError("empty total intersection but BFS found no certificate")
                    width_histogram[str(width)] += 1
                example = {
                    "physical_line": physical_line,
                    "graph6": record.strip().decode("ascii"),
                    "distinct_dyadic_cycle_edge_sets": len(masks),
                    "minimum_empty_intersection_width": width,
                }
                if first_no_pair is None:
                    first_no_pair = example
                no_pair_examples.append(example)
                if (
                    largest_no_pair_cycle_family is None
                    or len(masks) > largest_no_pair_cycle_family["distinct_dyadic_cycle_edge_sets"]
                ):
                    largest_no_pair_cycle_family = example

            if args.progress_every and stats["graphs"] % args.progress_every == 0:
                print(
                    json.dumps(
                        {
                            "processed": stats["graphs"],
                            "no_pair": stats["no_edge_disjoint_dyadic_pair"],
                            "seconds": round(time.monotonic() - begun, 3),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

    complete = stats["graphs"] == args.expected_count and stats["nonempty_dyadic_core"] == 0
    payload = {
        "schema": "erdos64-dyadic-pair-structure-v1",
        "input": str(args.input),
        "sha256": digest(args.input),
        "expected_order": args.expected_order,
        "expected_count": args.expected_count,
        "stats": dict(stats),
        "minimum_empty_intersection_width_histogram": dict(
            sorted(width_histogram.items(), key=lambda item: int(item[0]))
        ),
        "first_no_pair": first_no_pair,
        "no_pair_examples": no_pair_examples,
        "largest_no_pair_cycle_family": largest_no_pair_cycle_family,
        "complete": complete,
        "seconds": round(time.monotonic() - begun, 6),
    }
    args.summary_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
