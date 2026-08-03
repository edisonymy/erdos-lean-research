#!/usr/bin/env python3
"""Trace inverse-design minima as the enforced convexity margin varies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from inverse_design_n10 import DIMENSION, choose_partitions, equality_vector, metrics


def refine(parameters: np.ndarray, margin: float, penalty: float, max_nfev: int) -> np.ndarray:
    lower = np.full(DIMENSION, -1.5)
    upper = np.full(DIMENSION, 1.5)
    previous = None
    for _ in range(9):
        partitions = choose_partitions(parameters)
        signature = tuple(tuple(tuple(group) for group in row) for row in partitions)
        result = least_squares(
            equality_vector,
            parameters,
            bounds=(lower, upper),
            args=(partitions, margin, 2e-3, penalty),
            max_nfev=max_nfev,
            ftol=1e-14,
            xtol=1e-14,
            gtol=1e-14,
        )
        parameters = result.x
        if signature == previous:
            break
        previous = signature
    return parameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--penalty", type=float, default=1e9)
    parser.add_argument("--max-nfev", type=int, default=1200)
    parser.add_argument("--seed-count", type=int, default=1)
    parser.add_argument(
        "--margins", type=float, nargs="+", default=(0.0, 1e-4, 5e-4, 1e-3, 2e-3)
    )
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    seeds = [
        np.asarray(record["parameters"], dtype=float)
        for record in source["records"][: args.seed_count]
    ]
    margins = tuple(args.margins)
    traces = []
    for seed_index, seed in enumerate(seeds):
        for direction, schedule in (("ascending", margins),):
            parameters = seed.copy()
            entries = []
            for margin in schedule:
                parameters = refine(parameters, margin, args.penalty, args.max_nfev)
                record = metrics(parameters)
                entries.append({
                    "requested_margin": margin,
                    "minimum_turn": record["minimum_normalized_turn_cross"],
                    "maximum_span": record["maximum_within_cluster_span"],
                    "sum_sse": record["sum_row_sse"],
                    "parameters": record["parameters"],
                    "partitions": record["partitions"],
                })
                print(
                    f"seed={seed_index} {direction} margin={margin:g} "
                    f"turn={record['minimum_normalized_turn_cross']:.7g} "
                    f"span={record['maximum_within_cluster_span']:.7g} "
                    f"sum_sse={record['sum_row_sse']:.7g}",
                    flush=True,
                )
            traces.append({"seed_index": seed_index, "direction": direction, "entries": entries})
    payload = {
        "status": "numerical diagnostic only",
        "source": str(args.source),
        "penalty": args.penalty,
        "max_nfev": args.max_nfev,
        "traces": traces,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
