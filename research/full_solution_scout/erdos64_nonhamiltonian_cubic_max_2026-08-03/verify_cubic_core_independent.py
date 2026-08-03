#!/usr/bin/env python3
"""Independent full replay of cubic-census dyadic edge cores.

This checker imports no producer code.  It uses a separately written graph6
decoder and computes the literal intersection of enumerated dyadic-cycle edge
masks.  Enumeration stops only after that intersection becomes empty, since
subsequent intersections cannot restore an edge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path


Edge = tuple[int, int]

KNOWN_COUNTS = {4: 1, 6: 2, 8: 5, 10: 19, 12: 85, 14: 509, 16: 4060, 18: 41301, 20: 510489}


def file_digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(262144)
            if not block:
                break
            state.update(block)
    return state.hexdigest().upper()


def decode_graph6_separately(record: bytes) -> tuple[list[set[int]], list[Edge]]:
    text = record.strip().decode("ascii")
    if text.startswith(">>graph6<<"):
        text = text[10:]
    if not text:
        raise ValueError("blank graph6 line")
    order = ord(text[0]) - 63
    if not 0 <= order <= 62:
        raise ValueError("unsupported extended graph6 order")
    bits = "".join(f"{ord(character) - 63:06b}" for character in text[1:])
    required_bits = order * (order - 1) // 2
    required_chars = (required_bits + 5) // 6
    if len(text) - 1 != required_chars:
        raise ValueError("noncanonical graph6 record length")

    neighbours = [set() for _ in range(order)]
    edges: list[Edge] = []
    position = 0
    for right in range(1, order):
        for left in range(right):
            if bits[position] == "1":
                neighbours[left].add(right)
                neighbours[right].add(left)
                edges.append((left, right))
            position += 1
    return neighbours, edges


def connected_sets(neighbours: list[set[int]]) -> bool:
    reached = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for other in neighbours[vertex]:
            if other not in reached:
                reached.add(other)
                stack.append(other)
    return len(reached) == len(neighbours)


def literal_dyadic_intersection(
    neighbours: list[set[int]], edges: list[Edge]
) -> tuple[int, int, bool]:
    """Return (intersection mask, enumerated cycles, saw any dyadic cycle)."""
    n = len(neighbours)
    edge_number: dict[Edge, int] = {edge: index for index, edge in enumerate(edges)}
    full_intersection = (1 << len(edges)) - 1
    cycles_seen = 0
    saw_cycle = False

    for length in (4, 8, 16, 32):
        if length > n:
            continue
        for root in range(n):
            permitted = set(range(root + 1, n))
            for first in sorted(neighbours[root] & permitted):
                path = [root, first]
                used = {root, first}
                first_edge = 1 << edge_number[(root, first)]

                def extend(vertex: int, mask: int) -> bool:
                    nonlocal full_intersection, cycles_seen, saw_cycle
                    if len(path) == length:
                        if root not in neighbours[vertex]:
                            return False
                        # Opposite orientations have identical edge masks.  The
                        # inequality removes the duplicate without affecting
                        # the literal intersection.
                        if path[1] > path[-1]:
                            return False
                        closing = tuple(sorted((vertex, root)))
                        cycle_mask = mask | (1 << edge_number[closing])
                        saw_cycle = True
                        cycles_seen += 1
                        full_intersection &= cycle_mask
                        return full_intersection == 0

                    for nxt in sorted(neighbours[vertex] & permitted - used):
                        used.add(nxt)
                        path.append(nxt)
                        edge = tuple(sorted((vertex, nxt)))
                        if extend(nxt, mask | (1 << edge_number[edge])):
                            return True
                        path.pop()
                        used.remove(nxt)
                    return False

                if extend(first, first_edge):
                    return 0, cycles_seen, True
    return full_intersection, cycles_seen, saw_cycle


def edge_list_from_mask(edges: list[Edge], mask: int) -> list[list[int]]:
    return [list(edge) for index, edge in enumerate(edges) if mask & (1 << index)]


def audit_file(
    path: Path,
    expected_order: int | None,
    expected_count: int | None,
    progress_every: int,
) -> dict[str, object]:
    begun = time.monotonic()
    stats: Counter[str] = Counter()
    certificate_histogram: Counter[str] = Counter()
    first_survivor: dict[str, object] | None = None
    largest_greedy_certificate: dict[str, object] | None = None
    actual_order: int | None = None

    with path.open("rb") as source:
        for physical_line, record in enumerate(source, start=1):
            if not record.strip() or record.startswith(b">>"):
                continue
            neighbours, edges = decode_graph6_separately(record)
            order = len(neighbours)
            actual_order = order if actual_order is None else actual_order
            if order != actual_order:
                raise ValueError("mixed graph orders")
            if expected_order is not None and order != expected_order:
                raise ValueError(f"expected order {expected_order}, saw {order}")
            if len(set(edges)) != len(edges) or any(u == v for u, v in edges):
                raise ValueError(f"line {physical_line}: not simple")
            if len(edges) != 3 * order // 2 or any(len(row) != 3 for row in neighbours):
                raise ValueError(f"line {physical_line}: not cubic")
            if not connected_sets(neighbours):
                raise ValueError(f"line {physical_line}: disconnected")
            stats["validated_connected_simple_cubic"] += 1

            core, enumerated, saw_cycle = literal_dyadic_intersection(neighbours, edges)
            stats["dyadic_cycles_enumerated_until_decision"] += enumerated
            if not saw_cycle:
                stats["no_dyadic_cycle"] += 1
            if core:
                stats["nonempty_dyadic_core"] += 1
                if first_survivor is None:
                    first_survivor = {
                        "physical_line": physical_line,
                        "graph6": record.strip().decode("ascii"),
                        "core_edges": edge_list_from_mask(edges, core),
                        "saw_dyadic_cycle": saw_cycle,
                    }
            else:
                stats["empty_dyadic_core"] += 1
                certificate_histogram[str(enumerated)] += 1
                if (
                    largest_greedy_certificate is None
                    or enumerated > largest_greedy_certificate["cycles"]
                ):
                    largest_greedy_certificate = {
                        "cycles": enumerated,
                        "physical_line": physical_line,
                        "graph6": record.strip().decode("ascii"),
                    }

            done = stats["validated_connected_simple_cubic"]
            if progress_every and done % progress_every == 0:
                print(
                    json.dumps(
                        {
                            "path": str(path),
                            "processed": done,
                            "seconds": round(time.monotonic() - begun, 3),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

    count = stats["validated_connected_simple_cubic"]
    expected = expected_count
    if expected is None and actual_order is not None:
        expected = KNOWN_COUNTS.get(actual_order)
    complete = expected == count and stats["nonempty_dyadic_core"] == 0
    return {
        "path": str(path),
        "sha256": file_digest(path),
        "bytes": path.stat().st_size,
        "order": actual_order,
        "expected_count": expected,
        "count_matches_expected": count == expected,
        "stats": dict(stats),
        "greedy_empty_intersection_certificate_histogram": dict(
            sorted(certificate_histogram.items(), key=lambda item: int(item[0]))
        ),
        "largest_greedy_certificate": largest_greedy_certificate,
        "first_survivor": first_survivor,
        "complete_empty_core_replay": complete,
        "seconds": round(time.monotonic() - begun, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--expected-order", type=int)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=25000)
    args = parser.parse_args()
    if len(args.inputs) != 1 and (args.expected_order is not None or args.expected_count is not None):
        parser.error("explicit expected order/count is supported only with one input")

    begun = time.monotonic()
    audits: list[dict[str, object]] = []
    for path in args.inputs:
        audits.append(
            audit_file(path, args.expected_order, args.expected_count, args.progress_every)
        )
    summary = {
        "schema": "erdos64-independent-literal-core-replay-v1",
        "independence": (
            "no import from producer; separate graph6 decoder; literal cycle-edge-mask "
            "intersection rather than per-edge avoiding-cycle searches"
        ),
        "inputs": audits,
        "complete": all(audit["complete_empty_core_replay"] for audit in audits),
        "seconds": round(time.monotonic() - begun, 6),
    }
    args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
