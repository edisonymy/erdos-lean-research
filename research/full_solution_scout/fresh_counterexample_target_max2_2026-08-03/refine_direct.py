#!/usr/bin/env python3
"""Warm-start and cross-validate the direct-m #203 phase assignment.

This is a bounded optimizer, not an exact cover checker.  It deliberately uses
the already serialized order-1000/legacy union rather than expanding the pool.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np


def make_labels(maps: list[dict], ks: np.ndarray, ells: np.ndarray) -> np.ndarray:
    max_r = max(int(pm["group_size"]) for pm in maps)
    dtype = np.uint16 if max_r < 2**16 else np.uint32
    labels = np.empty((len(maps), len(ks)), dtype=dtype)
    for i, pm in enumerate(maps):
        r = int(pm["group_size"])
        a = int(pm["a"])
        b = int(pm["b"])
        labels[i] = ((a * (ks % r) + b * (ells % r)) % r).astype(dtype)
    return labels


def counts_for(labels: np.ndarray, phases: list[int]) -> np.ndarray:
    counts = np.zeros(labels.shape[1], dtype=np.int16)
    for i, phase in enumerate(phases):
        counts += labels[i] == phase
    return counts


def coordinate_descent(
    maps: list[dict],
    labels: np.ndarray,
    phases: list[int],
    rng: np.random.Generator,
    sweeps: int,
) -> tuple[list[int], np.ndarray, list[int]]:
    phases = phases.copy()
    counts = counts_for(labels, phases)
    history = [int(np.count_nonzero(counts == 0))]
    for _ in range(sweeps):
        changed = False
        for i0 in rng.permutation(len(maps)):
            i = int(i0)
            old = phases[i]
            counts -= labels[i] == old
            needs = counts == 0
            r = int(maps[i]["group_size"])
            freq = np.bincount(labels[i, needs].astype(np.int64), minlength=r)
            new = int(np.argmax(freq))
            phases[i] = new
            counts += labels[i] == new
            if new != old:
                changed = True
        now = int(np.count_nonzero(counts == 0))
        if now > history[-1]:
            raise AssertionError("coordinate sweep increased objective")
        history.append(now)
        if not changed or now == 0:
            break
    return phases, counts, history


def pair_descent(
    maps: list[dict],
    labels: np.ndarray,
    phases: list[int],
    counts: np.ndarray,
    rng: np.random.Generator,
    attempts: int,
    product_cap: int,
) -> tuple[list[int], np.ndarray, list[dict]]:
    phases = phases.copy()
    trace: list[dict] = []
    eligible = [
        (i, j)
        for i in range(len(maps))
        for j in range(i + 1, len(maps))
        if int(maps[i]["group_size"]) * int(maps[j]["group_size"]) <= product_cap
    ]
    rng.shuffle(eligible)
    for i, j in eligible[:attempts]:
        old_i, old_j = phases[i], phases[j]
        before = int(np.count_nonzero(counts == 0))
        counts -= labels[i] == old_i
        counts -= labels[j] == old_j
        needs = counts == 0
        ri = int(maps[i]["group_size"])
        rj = int(maps[j]["group_size"])
        li = labels[i, needs].astype(np.int64)
        lj = labels[j, needs].astype(np.int64)
        fi = np.bincount(li, minlength=ri)
        fj = np.bincount(lj, minlength=rj)
        joint = np.bincount(li * rj + lj, minlength=ri * rj).reshape(ri, rj)
        score = fi[:, None] + fj[None, :] - joint
        flat = int(np.argmax(score))
        new_i, new_j = divmod(flat, rj)
        phases[i], phases[j] = new_i, new_j
        counts += labels[i] == new_i
        counts += labels[j] == new_j
        after = int(np.count_nonzero(counts == 0))
        if after > before:
            raise AssertionError("pair step increased objective")
        if after < before:
            trace.append(
                {"i": i, "j": j, "before": before, "after": after,
                 "old": [old_i, old_j], "new": [new_i, new_j]}
            )
    return phases, counts, trace


def evaluate_seed(maps: list[dict], phases: list[int], samples: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    ks = rng.integers(0, 2**61, size=samples, dtype=np.int64)
    ells = rng.integers(0, 2**61, size=samples, dtype=np.int64)
    uncovered = np.ones(samples, dtype=bool)
    for pm, phase in zip(maps, phases, strict=True):
        r = int(pm["group_size"])
        label = (
            int(pm["a"]) * (ks % r) + int(pm["b"]) * (ells % r)
        ) % r
        uncovered &= label != phase
    return {
        "seed": seed,
        "samples": samples,
        "uncovered": int(np.count_nonzero(uncovered)),
        "uncovered_fraction": float(np.count_nonzero(uncovered) / samples),
    }


def residual_profiles(
    maps: list[dict], phases: list[int], samples: int, seed: int, moduli: list[int]
) -> dict:
    rng = np.random.default_rng(seed)
    ks = rng.integers(0, 2**61, size=samples, dtype=np.int64)
    ells = rng.integers(0, 2**61, size=samples, dtype=np.int64)
    uncovered = np.ones(samples, dtype=bool)
    for pm, phase in zip(maps, phases, strict=True):
        r = int(pm["group_size"])
        label = (
            int(pm["a"]) * (ks % r) + int(pm["b"]) * (ells % r)
        ) % r
        uncovered &= label != phase
    profiles: dict[str, object] = {}
    for modulus in moduli:
        cells = np.bincount(
            ((ks[uncovered] % modulus) * modulus + (ells[uncovered] % modulus)).astype(np.int64),
            minlength=modulus * modulus,
        ).reshape(modulus, modulus)
        expected = max(1.0, float(np.count_nonzero(uncovered)) / (modulus * modulus))
        profiles[str(modulus)] = {
            "counts": cells.tolist(),
            "max_over_uniform_mean": float(cells.max() / expected),
            "nonzero_cells": int(np.count_nonzero(cells)),
        }
    coords = np.column_stack((ks[uncovered][:5000], ells[uncovered][:5000]))
    return {
        "seed": seed,
        "uncovered_count": int(np.count_nonzero(uncovered)),
        "modular_profiles": profiles,
        "first_residual_coordinates": coords.tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--search-index", type=int, default=0)
    parser.add_argument("--samples", type=int, default=250_000)
    parser.add_argument("--train-seed", type=int, default=203_202_608_04)
    parser.add_argument("--validation-seeds", default="20320260805,20320260806,20320260807")
    parser.add_argument("--perturbations", type=int, default=20)
    parser.add_argument("--perturb-fraction", type=float, default=0.08)
    parser.add_argument("--sweeps", type=int, default=30)
    parser.add_argument("--pair-attempts", type=int, default=120)
    parser.add_argument("--pair-product-cap", type=int, default=200_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    maps = source["prime_maps"]
    initial = [int(x) for x in source["searches"][args.search_index]["best_phases"]]
    if len(initial) != len(maps):
        raise AssertionError("phase/map length mismatch")
    rng = np.random.default_rng(args.train_seed)
    ks = rng.integers(0, 2**61, size=args.samples, dtype=np.int64)
    ells = rng.integers(0, 2**61, size=args.samples, dtype=np.int64)
    labels = make_labels(maps, ks, ells)

    initial_count = int(np.count_nonzero(counts_for(labels, initial) == 0))
    best, best_counts, warm_history = coordinate_descent(
        maps, labels, initial, rng, args.sweeps
    )
    perturb_trace: list[dict] = []
    perturb_size = max(1, round(args.perturb_fraction * len(maps)))
    for run in range(args.perturbations):
        candidate = best.copy()
        for i0 in rng.choice(len(maps), size=perturb_size, replace=False):
            i = int(i0)
            candidate[i] = int(rng.integers(int(maps[i]["group_size"])))
        candidate, candidate_counts, history = coordinate_descent(
            maps, labels, candidate, rng, args.sweeps
        )
        value = int(np.count_nonzero(candidate_counts == 0))
        old_best = int(np.count_nonzero(best_counts == 0))
        accepted = value < old_best
        if accepted:
            best, best_counts = candidate, candidate_counts
        perturb_trace.append(
            {"run": run, "value": value, "accepted": accepted, "history": history}
        )

    best, best_counts, pair_trace = pair_descent(
        maps, labels, best, best_counts, rng,
        args.pair_attempts, args.pair_product_cap,
    )
    best, best_counts, final_history = coordinate_descent(
        maps, labels, best, rng, args.sweeps
    )
    train_uncovered = int(np.count_nonzero(best_counts == 0))
    validation = [
        evaluate_seed(maps, best, args.samples, int(seed))
        for seed in args.validation_seeds.split(",") if seed.strip()
    ]
    profiles = residual_profiles(
        maps, best, args.samples, int(args.validation_seeds.split(",")[0]),
        [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],
    )
    result = {
        "problem": "Erdos #203 direct-m warm refinement",
        "status": "heuristic_sample_only",
        "parameters": vars(args) | {"input": str(args.input), "output": str(args.output)},
        "map_count": len(maps),
        "initial_train_uncovered": initial_count,
        "initial_train_uncovered_fraction": initial_count / args.samples,
        "warm_history": warm_history,
        "perturb_trace": perturb_trace,
        "pair_improvements": pair_trace,
        "final_history": final_history,
        "train_uncovered": train_uncovered,
        "train_uncovered_fraction": train_uncovered / args.samples,
        "best_phases": best,
        "validation": validation,
        "residual_profiles": profiles,
        "cross_seed_below_five_percent": all(
            x["uncovered_fraction"] < 0.05 for x in validation
        ),
        "elapsed_seconds": time.monotonic() - started,
        "claim_boundary": "Heuristic sampled optimization; not a cover or theorem.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "initial": result["initial_train_uncovered_fraction"],
        "train": result["train_uncovered_fraction"],
        "validation": validation,
        "cross_seed_below_five_percent": result["cross_seed_below_five_percent"],
        "pair_improvements": len(pair_trace),
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
