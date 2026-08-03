#!/usr/bin/env python3
"""Asymmetric inverse-design search for a convex locally-4-distance decagon.

This is a candidate generator, never a verifier.  It alternates between the
optimal four-clustering of the nine squared distances at each vertex and a
continuous least-squares solve for the corresponding equality system.  Strict
convexity and point separation are included as strong hinge residuals.

The parameterization uses positive polar radii and positive angular gaps, with
rotation and scale normalized away.  It explores no preselected global edge
coloring and is independent of the H8-relaxation lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.optimize import least_squares


N = 10
K = 4
DIMENSION = 2 * (N - 1)


def decode(parameters: np.ndarray) -> np.ndarray:
    logs = np.concatenate(([0.0], parameters[: N - 1]))
    radii = np.exp(logs)
    radii /= np.mean(radii)
    logits = np.concatenate(([0.0], parameters[N - 1 :]))
    weights = np.exp(logits)
    gaps = 2.0 * math.pi * weights / np.sum(weights)
    angles = np.concatenate(([0.0], np.cumsum(gaps[:-1])))
    return np.column_stack((radii * np.cos(angles), radii * np.sin(angles)))


def geometry(parameters: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    points = decode(parameters)
    differences = points[:, None, :] - points[None, :, :]
    squared = np.sum(differences * differences, axis=2)
    diameter2 = float(np.max(squared))
    squared /= diameter2
    crosses = []
    for i in range(N):
        first = points[(i + 1) % N] - points[i]
        second = points[(i + 2) % N] - points[(i + 1) % N]
        crosses.append((first[0] * second[1] - first[1] * second[0]) / diameter2)
    separation = float(np.min(squared[np.triu_indices(N, 1)]))
    return squared, np.asarray(crosses), separation


def optimal_groups(values: np.ndarray) -> list[list[int]]:
    """Exact 1D least-squares four-clustering of nine labelled values."""
    order = np.argsort(values)
    sorted_values = values[order]
    count = len(values)
    prefix = np.concatenate(([0.0], np.cumsum(sorted_values)))
    prefix2 = np.concatenate(([0.0], np.cumsum(sorted_values * sorted_values)))

    def interval_cost(lo: int, hi: int) -> float:
        size = hi - lo
        total = prefix[hi] - prefix[lo]
        return float(prefix2[hi] - prefix2[lo] - total * total / size)

    dp = np.full((K + 1, count + 1), np.inf)
    parent = np.full((K + 1, count + 1), -1, dtype=int)
    dp[0, 0] = 0.0
    for groups in range(1, K + 1):
        for hi in range(groups, count + 1):
            for lo in range(groups - 1, hi):
                candidate = dp[groups - 1, lo] + interval_cost(lo, hi)
                if candidate < dp[groups, hi]:
                    dp[groups, hi] = candidate
                    parent[groups, hi] = lo
    answer: list[list[int]] = []
    hi = count
    for groups in range(K, 0, -1):
        lo = int(parent[groups, hi])
        answer.append([int(index) for index in order[lo:hi]])
        hi = lo
    answer.reverse()
    return answer


def choose_partitions(parameters: np.ndarray) -> list[list[list[int]]]:
    squared, _crosses, _separation = geometry(parameters)
    return [optimal_groups(np.delete(squared[i], i)) for i in range(N)]


def equality_vector(
    parameters: np.ndarray,
    partitions: list[list[list[int]]],
    convex_margin: float,
    separation_margin: float,
    penalty_scale: float,
) -> np.ndarray:
    squared, crosses, separation = geometry(parameters)
    residuals: list[float] = []
    for i, groups in enumerate(partitions):
        row = np.delete(squared[i], i)
        for group in groups:
            anchor = row[group[0]]
            residuals.extend(float(row[index] - anchor) for index in group[1:])
    hinge = math.sqrt(penalty_scale)
    residuals.extend(hinge * np.maximum(0.0, convex_margin - crosses))
    residuals.append(hinge * max(0.0, separation_margin - separation))
    return np.asarray(residuals)


def metrics(parameters: np.ndarray) -> dict[str, object]:
    squared, crosses, separation = geometry(parameters)
    partitions = choose_partitions(parameters)
    row_sse: list[float] = []
    row_span: list[float] = []
    for i, groups in enumerate(partitions):
        row = np.delete(squared[i], i)
        sse = 0.0
        largest_span = 0.0
        for group in groups:
            values = row[group]
            sse += float(np.sum((values - np.mean(values)) ** 2))
            largest_span = max(largest_span, float(np.max(values) - np.min(values)))
        row_sse.append(sse)
        row_span.append(largest_span)
    return {
        "sum_row_sse": sum(row_sse),
        "maximum_row_sse": max(row_sse),
        "maximum_within_cluster_span": max(row_span),
        "minimum_normalized_turn_cross": float(np.min(crosses)),
        "minimum_normalized_pair_distance_squared": separation,
        "convex": bool(np.min(crosses) > 0.0),
        "parameters": parameters.tolist(),
        "points": decode(parameters).tolist(),
        "partitions": partitions,
        "row_sse": row_sse,
        "row_maximum_span": row_span,
    }


def rank(record: dict[str, object], convex_margin: float, separation_margin: float) -> tuple[float, ...]:
    cross_shortfall = max(0.0, convex_margin - float(record["minimum_normalized_turn_cross"]))
    separation_shortfall = max(
        0.0, separation_margin - float(record["minimum_normalized_pair_distance_squared"])
    )
    return (
        1.0 if cross_shortfall > 0.0 or separation_shortfall > 0.0 else 0.0,
        cross_shortfall + separation_shortfall,
        float(record["maximum_within_cluster_span"]),
        float(record["sum_row_sse"]),
    )


def random_start(rng: np.random.Generator, index: int) -> np.ndarray:
    # Interleave near-regular and strongly asymmetric initial conditions.
    scales = (0.04, 0.10, 0.22, 0.45, 0.75)
    scale = scales[index % len(scales)]
    start = rng.normal(0.0, scale, size=DIMENSION)
    return np.clip(start, -1.45, 1.45)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--starts", type=int, default=120)
    parser.add_argument("--rounds", type=int, default=7)
    parser.add_argument("--max-nfev", type=int, default=1400)
    parser.add_argument("--seed", type=int, default=982_410_2026)
    parser.add_argument("--convex-margin", type=float, default=5e-4)
    parser.add_argument("--separation-margin", type=float, default=2e-3)
    parser.add_argument("--penalty-scale", type=float, default=1e7)
    parser.add_argument("--retain", type=int, default=25)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    lower = np.full(DIMENSION, -1.5)
    upper = np.full(DIMENSION, 1.5)
    retained: list[dict[str, object]] = []
    started = time.time()

    for start_index in range(args.starts):
        parameters = random_start(rng, start_index)
        previous_signature: tuple[tuple[tuple[int, ...], ...], ...] | None = None
        for _round in range(args.rounds):
            partitions = choose_partitions(parameters)
            signature = tuple(tuple(tuple(group) for group in row) for row in partitions)
            result = least_squares(
                equality_vector,
                parameters,
                bounds=(lower, upper),
                args=(
                    partitions,
                    args.convex_margin,
                    args.separation_margin,
                    args.penalty_scale,
                ),
                max_nfev=args.max_nfev,
                ftol=1e-13,
                xtol=1e-13,
                gtol=1e-13,
            )
            parameters = result.x
            if signature == previous_signature:
                break
            previous_signature = signature

        record = metrics(parameters)
        record.update({
            "start_index": start_index,
            "initial_scale_class": (0.04, 0.10, 0.22, 0.45, 0.75)[start_index % 5],
        })
        retained.append(record)
        retained.sort(key=lambda item: rank(item, args.convex_margin, args.separation_margin))
        retained = retained[: args.retain]

        if (start_index + 1) % 10 == 0 or start_index + 1 == args.starts:
            best = retained[0]
            print(
                f"starts={start_index + 1}/{args.starts} "
                f"span={best['maximum_within_cluster_span']:.6g} "
                f"sum_sse={best['sum_row_sse']:.6g} "
                f"cross={best['minimum_normalized_turn_cross']:.6g}",
                flush=True,
            )

    payload = {
        "problem": 982,
        "target": "strictly convex 10-point locally 4-distance set",
        "status": "exploratory numerical inverse design; not a proof or witness",
        "method": "alternate exact 1D local four-clustering with nonlinear equality fitting",
        "h8_relaxation_used": False,
        "raw_K10_coloring_enumeration_used": False,
        "seed": args.seed,
        "starts": args.starts,
        "rounds": args.rounds,
        "max_nfev": args.max_nfev,
        "convex_margin": args.convex_margin,
        "separation_margin": args.separation_margin,
        "penalty_scale": args.penalty_scale,
        "elapsed_seconds": time.time() - started,
        "retained": retained,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print("sha256", digest)


if __name__ == "__main__":
    main()
