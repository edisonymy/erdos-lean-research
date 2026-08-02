#!/usr/bin/env python3
"""Verify small graph6 catalogues and summarize graph invariants."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from catalog_lib import (
    independence_number,
    is_minimal_ramsey_33,
    iter_graph6,
    sha256_decompressed,
    sha256_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--expected-order", type=int)
    parser.add_argument("--expected-alpha", type=int)
    parser.add_argument("--verify-minimal", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records: set[bytes] = set()
    count = 0
    duplicate_count = 0
    orders: Counter[int] = Counter()
    alphas: Counter[int] = Counter()
    edge_counts: Counter[int] = Counter()
    maximum_degrees: Counter[int] = Counter()
    nonminimal: list[int] = []
    for index, record, adjacency in iter_graph6(args.input):
        count += 1
        if record in records:
            duplicate_count += 1
        records.add(record)
        orders[len(adjacency)] += 1
        alpha = independence_number(adjacency)
        alphas[alpha] += 1
        edge_counts[sum(mask.bit_count() for mask in adjacency) // 2] += 1
        maximum_degrees[max((mask.bit_count() for mask in adjacency), default=0)] += 1
        if args.verify_minimal and not is_minimal_ramsey_33(adjacency):
            nonminimal.append(index)

    if args.expected_count is not None and count != args.expected_count:
        raise ValueError(f"count {count} != expected {args.expected_count}")
    if args.expected_order is not None and set(orders) != {args.expected_order}:
        raise ValueError(f"orders {dict(orders)} != expected {args.expected_order}")
    if args.expected_alpha is not None and set(alphas) != {args.expected_alpha}:
        raise ValueError(f"alpha distribution {dict(alphas)} != {args.expected_alpha}")
    if duplicate_count:
        raise ValueError(f"found {duplicate_count} duplicate graph6 records")
    if nonminimal:
        raise ValueError(f"nonminimal records: {nonminimal[:20]}")

    summary = {
        "input": str(args.input.resolve()),
        "bytes": args.input.stat().st_size,
        "sha256": sha256_path(args.input),
        "decompressed_sha256": sha256_decompressed(args.input),
        "count": count,
        "duplicate_graph6_records": duplicate_count,
        "orders": dict(sorted(orders.items())),
        "independence_numbers": dict(sorted(alphas.items())),
        "edge_counts": dict(sorted(edge_counts.items())),
        "maximum_degrees": dict(sorted(maximum_degrees.items())),
        "minimal_ramsey_verified": args.verify_minimal,
        "nonminimal_indices": nonminimal,
    }
    output = args.output or args.input.with_suffix(args.input.suffix + ".verification.json")
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
