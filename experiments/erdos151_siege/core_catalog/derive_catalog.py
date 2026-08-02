#!/usr/bin/env python3
"""Derive audited minimal-(3,3)-Ramsey subcatalogues from McKay inputs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from catalog_lib import (
    arrows_33,
    complement,
    encode_graph6,
    is_minimal_ramsey_33,
    iter_graph6,
    sha256_decompressed,
    sha256_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--mode",
        choices=("critical6", "minimal", "complement-minimal"),
        required=True,
        help=(
            "critical6: retain arrowing members of an edge-6-critical catalogue; "
            "minimal: independently test each input graph for Ramsey minimality; "
            "complement-minimal: complement each record and test Ramsey minimality"
        ),
    )
    parser.add_argument("--expected-input-count", type=int)
    parser.add_argument("--expected-output-count", type=int)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--progress-every", type=int, default=10_000)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume from the .checkpoint.json and .tmp files after interruption",
    )
    return parser.parse_args()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def main() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output.with_suffix(args.output.suffix + ".checkpoint.json")
    summary_path = args.output.with_suffix(args.output.suffix + ".summary.json")
    started = time.monotonic()
    elapsed_before_resume = 0.0
    seen = 0
    retained = 0
    order: int | None = None
    temporary_output = args.output.with_name(args.output.name + ".tmp")

    if args.resume:
        if not checkpoint_path.exists() or not temporary_output.exists():
            raise ValueError("--resume needs both checkpoint and temporary output files")
        with checkpoint_path.open("r", encoding="utf-8") as stream:
            checkpoint = json.load(stream)
        if checkpoint.get("complete"):
            raise ValueError("checkpoint is already complete")
        if Path(checkpoint["input"]).resolve() != args.input.resolve():
            raise ValueError("checkpoint input does not match command input")
        if checkpoint["mode"] != args.mode:
            raise ValueError("checkpoint mode does not match command mode")
        seen = int(checkpoint["records_seen"])
        retained = int(checkpoint["records_retained"])
        elapsed_before_resume = float(checkpoint.get("elapsed_seconds", 0.0))
        temporary_records = sum(1 for _ in iter_graph6(temporary_output))
        if temporary_records != retained:
            raise ValueError(
                "temporary output has "
                f"{temporary_records} records but checkpoint says {retained}; "
                "restart without --resume"
            )

    with temporary_output.open("ab" if args.resume else "wb") as output:
        for index, _record, input_adjacency in iter_graph6(args.input):
            if index <= seen:
                continue
            if args.limit is not None and index > args.limit:
                break
            seen = index
            if order is None:
                order = len(input_adjacency)
            elif len(input_adjacency) != order:
                raise ValueError("mixed graph orders in one catalogue")

            candidate = (
                complement(input_adjacency)
                if args.mode == "complement-minimal"
                else input_adjacency
            )
            keep = (
                arrows_33(candidate)
                if args.mode == "critical6"
                else is_minimal_ramsey_33(candidate)
            )
            if keep:
                output.write(encode_graph6(candidate) + b"\n")
                retained += 1

            if args.progress_every and seen % args.progress_every == 0:
                output.flush()
                os.fsync(output.fileno())
                checkpoint = {
                    "complete": False,
                    "input": str(args.input.resolve()),
                    "mode": args.mode,
                    "records_seen": seen,
                    "records_retained": retained,
                    "elapsed_seconds": round(
                        elapsed_before_resume + time.monotonic() - started, 3
                    ),
                }
                atomic_json(checkpoint_path, checkpoint)
                print(
                    f"seen={seen} retained={retained} "
                    f"elapsed={checkpoint['elapsed_seconds']}s",
                    file=sys.stderr,
                    flush=True,
                )

    if args.expected_input_count is not None and seen != args.expected_input_count:
        raise ValueError(f"input count {seen} != expected {args.expected_input_count}")
    if args.expected_output_count is not None and retained != args.expected_output_count:
        raise ValueError(f"output count {retained} != expected {args.expected_output_count}")
    os.replace(temporary_output, args.output)

    summary = {
        "complete": True,
        "input": str(args.input.resolve()),
        "input_bytes": args.input.stat().st_size,
        "input_sha256": sha256_path(args.input),
        "input_decompressed_sha256": sha256_decompressed(args.input),
        "source_url": args.source_url,
        "mode": args.mode,
        "mode_soundness": (
            "Every retained graph arrows (3,3). The input graphs are edge-6-critical, "
            "so deleting any edge produces a 5-colorable graph; pulling back a good "
            "two-edge-coloring of K5 proves every edge deletion is non-Ramsey."
            if args.mode == "critical6"
            else (
                "Each input graph is independently tested both for (3,3)-Ramseyness and "
                "for failure after every single-edge deletion."
                if args.mode == "minimal"
                else "Each input graph is complemented, then independently tested both "
                "for (3,3)-Ramseyness and for failure after every single-edge deletion."
            )
        ),
        "order": order,
        "records_seen": seen,
        "records_retained": retained,
        "output": str(args.output.resolve()),
        "output_bytes": args.output.stat().st_size,
        "output_sha256": sha256_path(args.output),
        "elapsed_seconds": round(
            elapsed_before_resume + time.monotonic() - started, 3
        ),
        "expectations": {
            "input": args.expected_input_count,
            "output": args.expected_output_count,
        },
    }
    atomic_json(summary_path, summary)
    atomic_json(checkpoint_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
