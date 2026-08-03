#!/usr/bin/env python3
"""Global constrained numerical search for the n=10 locally-4 target.

This companion to inverse_design_n10.py uses differential evolution to cross
partition boundaries.  A large hinge penalty enforces a genuinely positive
convexity margin; the output remains candidate-generation evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import differential_evolution, least_squares

from inverse_design_n10 import (
    DIMENSION,
    choose_partitions,
    equality_vector,
    geometry,
    metrics,
)


def dynamic_objective(
    parameters: np.ndarray,
    convex_margin: float,
    separation_margin: float,
    penalty_scale: float,
) -> float:
    squared, crosses, separation = geometry(parameters)
    partitions = choose_partitions(parameters)
    row_costs: list[float] = []
    for i, groups in enumerate(partitions):
        row = np.delete(squared[i], i)
        cost = 0.0
        for group in groups:
            values = row[group]
            cost += float(np.sum((values - np.mean(values)) ** 2))
        row_costs.append(cost)
    penalty = penalty_scale * float(np.sum(np.maximum(0.0, convex_margin - crosses) ** 2))
    penalty += penalty_scale * max(0.0, separation_margin - separation) ** 2
    return max(row_costs) + 0.3 * sum(row_costs) + penalty


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=4)
    parser.add_argument("--maxiter", type=int, default=220)
    parser.add_argument("--popsize", type=int, default=8)
    parser.add_argument("--seed", type=int, default=982_411_000)
    parser.add_argument("--convex-margin", type=float, default=5e-4)
    parser.add_argument("--separation-margin", type=float, default=2e-3)
    parser.add_argument("--penalty-scale", type=float, default=1e7)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    bounds = [(-1.5, 1.5)] * DIMENSION
    lower = np.full(DIMENSION, -1.5)
    upper = np.full(DIMENSION, 1.5)
    records: list[dict[str, object]] = []
    started = time.time()

    for run in range(args.runs):
        run_started = time.time()
        result = differential_evolution(
            dynamic_objective,
            bounds,
            args=(args.convex_margin, args.separation_margin, args.penalty_scale),
            seed=args.seed + run,
            maxiter=args.maxiter,
            popsize=args.popsize,
            mutation=(0.45, 1.0),
            recombination=0.85,
            tol=1e-10,
            atol=1e-13,
            polish=False,
            updating="immediate",
            workers=1,
            x0=np.zeros(DIMENSION),
        )
        parameters = result.x
        previous = None
        for _round in range(7):
            partitions = choose_partitions(parameters)
            signature = tuple(tuple(tuple(group) for group in row) for row in partitions)
            refined = least_squares(
                equality_vector,
                parameters,
                bounds=(lower, upper),
                args=(
                    partitions,
                    args.convex_margin,
                    args.separation_margin,
                    args.penalty_scale,
                ),
                max_nfev=3000,
                ftol=1e-14,
                xtol=1e-14,
                gtol=1e-14,
            )
            if dynamic_objective(
                refined.x, args.convex_margin, args.separation_margin, args.penalty_scale
            ) <= dynamic_objective(
                parameters, args.convex_margin, args.separation_margin, args.penalty_scale
            ):
                parameters = refined.x
            if signature == previous:
                break
            previous = signature

        record = metrics(parameters)
        record.update({
            "run": run,
            "optimizer_fun": float(result.fun),
            "optimizer_nfev": int(result.nfev),
            "optimizer_success": bool(result.success),
            "elapsed_seconds": time.time() - run_started,
            "penalized_objective": dynamic_objective(
                parameters, args.convex_margin, args.separation_margin, args.penalty_scale
            ),
        })
        records.append(record)
        print(
            f"run={run} span={record['maximum_within_cluster_span']:.6g} "
            f"sum_sse={record['sum_row_sse']:.6g} "
            f"cross={record['minimum_normalized_turn_cross']:.6g} "
            f"seconds={record['elapsed_seconds']:.1f}",
            flush=True,
        )

    records.sort(
        key=lambda record: (
            0 if float(record["minimum_normalized_turn_cross"]) >= args.convex_margin else 1,
            float(record["maximum_within_cluster_span"]),
            float(record["sum_row_sse"]),
        )
    )
    payload = {
        "problem": 982,
        "target": "strictly convex 10-point locally 4-distance set",
        "status": "exploratory numerical inverse design; not a proof or witness",
        "method": "dynamic local clustering plus globally searched equality residual",
        "h8_relaxation_used": False,
        "raw_K10_coloring_enumeration_used": False,
        "runs": args.runs,
        "maxiter": args.maxiter,
        "popsize": args.popsize,
        "seed": args.seed,
        "convex_margin": args.convex_margin,
        "separation_margin": args.separation_margin,
        "penalty_scale": args.penalty_scale,
        "elapsed_seconds": time.time() - started,
        "records": records,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
