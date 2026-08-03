#!/usr/bin/env python3
"""Partition-safe order-22 replay using the producer's avoiding-cycle method.

This separate successor driver leaves the completed order-20 producer frozen.
Any graph with no dyadic cycle or with a surviving marked edge is written to a
raw candidate directory before the process exits.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from scan_cubic_census import (
    cycle_through_edge,
    dump_candidate,
    dyadic_core,
    is_connected,
    parse_graph6,
    sha256_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--partition", type=int, required=True)
    parser.add_argument("--modulus", type=int, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=100000)
    args = parser.parse_args()

    begun = time.monotonic()
    stats: Counter[str] = Counter()
    candidate = None
    with args.input.open("rb") as source:
        for index, raw in enumerate(source, start=1):
            if not raw.strip() or raw.startswith(b">"):
                continue
            rows, edges = parse_graph6(raw)
            n = len(rows)
            if n != 22:
                raise ValueError(f"record {index}: expected order 22, found {n}")
            if len(edges) != 33 or any(row.bit_count() != 3 for row in rows):
                raise ValueError(f"record {index}: not simple cubic")
            if not is_connected(rows):
                raise ValueError(f"record {index}: disconnected")
            stats["validated_connected_simple_cubic"] += 1

            core, detail = dyadic_core(rows, edges)
            if detail["no_dyadic_cycle"]:
                stats["no_dyadic_cycle"] += 1
                candidate = dump_candidate(
                    args.candidate_dir,
                    n,
                    index,
                    edges,
                    None,
                    f"partition {args.partition}/{args.modulus}: cubic graph has no dyadic cycle",
                    raw.strip().decode("ascii"),
                )
                break
            if not core:
                stats["empty_dyadic_core"] += 1
            else:
                stats["nonempty_dyadic_core"] += 1
                survivors = []
                for edge in core:
                    if not any(
                        cycle_through_edge(rows, edge, length)
                        for length in (3, 7, 15)
                    ):
                        survivors.append(edge)
                stats["core_edges_after_mersenne"] += len(survivors)
                if survivors:
                    candidate = dump_candidate(
                        args.candidate_dir,
                        n,
                        index,
                        edges,
                        survivors[0],
                        f"partition {args.partition}/{args.modulus}: marked edge survives",
                        raw.strip().decode("ascii"),
                    )
                    break

            if args.progress_every and stats["validated_connected_simple_cubic"] % args.progress_every == 0:
                print(
                    json.dumps(
                        {
                            "partition": args.partition,
                            "processed": stats["validated_connected_simple_cubic"],
                            "seconds": round(time.monotonic() - begun, 3),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

    count = stats["validated_connected_simple_cubic"]
    complete = candidate is None and count == args.expected_count
    payload = {
        "schema": "erdos64-order22-partition-avoiding-cycle-replay-v1",
        "input": str(args.input),
        "sha256": sha256_file(args.input),
        "partition": args.partition,
        "modulus": args.modulus,
        "expected_count": args.expected_count,
        "stats": dict(stats),
        "candidate": candidate,
        "complete": complete,
        "seconds": round(time.monotonic() - begun, 6),
    }
    args.summary_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 10 if candidate is not None else 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
