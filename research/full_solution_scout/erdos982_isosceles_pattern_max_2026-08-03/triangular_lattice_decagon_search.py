#!/usr/bin/env python3
"""Exact candidate-first search for a locally-four-distance convex decagon.

Points are represented in axial coordinates (x,y) of the triangular lattice,
embedded as (x+y/2, sqrt(3)y/2).  Squared Euclidean distances are therefore
the exact integers dx^2+dx*dy+dy^2, while orientation signs are unchanged by
the positive-determinant axial-to-Cartesian linear map.

This is a bounded heuristic, not an exclusion.  It complements rather than
duplicates the continuous inverse-design search because every accepted score,
convexity test, and distance collision is exact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from pathlib import Path


Point = tuple[int, int]
Polygon = tuple[Point, ...]


def cross(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def strict_hull(points) -> Polygon:
    pts = sorted(set(points))
    if len(pts) < 3:
        return ()
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return tuple(lower[:-1] + upper[:-1])


def squared_distance(a: Point, b: Point) -> int:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx * dx + dx * dy + dy * dy


def profile(poly: Polygon) -> tuple[int, ...]:
    return tuple(
        len({squared_distance(p, q) for j, q in enumerate(poly) if i != j})
        for i, p in enumerate(poly)
    )


def rank(poly: Polygon):
    values = profile(poly)
    return max(values), sum(values), tuple(sorted(values, reverse=True)), poly


def canonical(points) -> Polygon | None:
    pts = tuple(points)
    hull = strict_hull(pts)
    if len(hull) != 10 or len(set(pts)) != 10:
        return None
    return hull


def random_seeds(lattice: list[Point], attempts: int, rng: random.Random) -> set[Polygon]:
    seeds = set()
    for _ in range(attempts):
        size = rng.randint(10, min(55, len(lattice)))
        hull = strict_hull(rng.sample(lattice, size))
        if len(hull) == 10:
            seeds.add(hull)
    return seeds


def quadratic_seeds(lattice: list[Point], coefficient_bound: int) -> set[Polygon]:
    seeds = set()
    for a in range(1, coefficient_bound + 1):
        for c in range(1, coefficient_bound + 1):
            for b in range(-coefficient_bound, coefficient_bound + 1):
                if b * b >= 4 * a * c:
                    continue
                levels = {}
                for x, y in lattice:
                    levels.setdefault(a * x * x + b * x * y + c * y * y, []).append((x, y))
                inside = []
                for value in sorted(levels):
                    inside.extend(levels[value])
                    hull = strict_hull(inside)
                    if len(hull) == 10:
                        seeds.add(hull)
    return seeds


def mutate(parent: Polygon, lattice: list[Point], rng: random.Random) -> Polygon | None:
    child = list(parent)
    count = 1 if rng.random() < 0.9 else 2
    indices = rng.sample(range(10), count)
    occupied = set(child) - {child[i] for i in indices}
    for i in indices:
        # Half local steps, half global replacements.  Locality preserves the
        # equality-rich hull while global jumps avoid a trapped beam.
        if rng.random() < 0.5:
            x, y = child[i]
            candidates = [
                (x + dx, y + dy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))
            ]
            candidates = [p for p in candidates if p in LATTICE_SET and p not in occupied]
            if not candidates:
                return None
            child[i] = rng.choice(candidates)
        else:
            for _ in range(20):
                p = rng.choice(lattice)
                if p not in occupied:
                    child[i] = p
                    break
            else:
                return None
        occupied.add(child[i])
    return canonical(child)


LATTICE_SET: set[Point] = set()


def run(bound: int, random_attempts: int, coefficient_bound: int, beam_width: int,
        generations: int, mutations: int, seed: int, seconds: float) -> dict:
    global LATTICE_SET
    rng = random.Random(seed)
    lattice = [(x, y) for x in range(-bound, bound + 1) for y in range(-bound, bound + 1)]
    LATTICE_SET = set(lattice)
    started = time.monotonic()
    qseeds = quadratic_seeds(lattice, coefficient_bound)
    rseeds = random_seeds(lattice, random_attempts, rng)
    pool = qseeds | rseeds
    if not pool:
        raise RuntimeError("no ten-vertex convex-hull seeds")
    beam = sorted(pool, key=rank)[:beam_width]
    best = beam[0]
    trace = []
    evaluated = len(pool)

    for generation in range(generations + 1):
        if rank(beam[0]) < rank(best):
            best = beam[0]
        values = profile(best)
        trace.append({
            "generation": generation,
            "maximum_local_distances": max(values),
            "sum_local_distances": sum(values),
            "profile": list(values),
            "elapsed_seconds": time.monotonic() - started,
        })
        print(
            f"generation={generation} max={max(values)} sum={sum(values)} "
            f"profile={values}",
            flush=True,
        )
        if max(values) <= 4 or generation == generations or time.monotonic() - started >= seconds:
            break
        children = set(beam)
        each = max(1, mutations // len(beam))
        for parent in beam:
            for _ in range(each):
                child = mutate(parent, lattice, rng)
                if child is not None:
                    children.add(child)
        evaluated += len(children)
        beam = sorted(children, key=rank)[:beam_width]

    values = profile(best)
    return {
        "status": "COUNTEREXAMPLE_CANDIDATE" if max(values) <= 4 else "NO_CANDIDATE_BOUNDED_HEURISTIC",
        "problem": 982,
        "target": "strictly convex n=10 with at most four local distances",
        "lattice": "triangular axial; squared distance dx^2+dx*dy+dy^2",
        "parameters": {
            "bound": bound,
            "random_attempts": random_attempts,
            "coefficient_bound": coefficient_bound,
            "beam_width": beam_width,
            "generations": generations,
            "mutations_per_generation": mutations,
            "seed": seed,
            "seconds": seconds,
        },
        "quadratic_seed_count": len(qseeds),
        "random_seed_count": len(rseeds),
        "unique_seed_count": len(pool),
        "states_ranked_approximately": evaluated,
        "elapsed_seconds": time.monotonic() - started,
        "best": {
            "axial_points_counterclockwise": [list(p) for p in best],
            "cartesian_points_approx": [[x + y / 2, math.sqrt(3) * y / 2] for x, y in best],
            "local_distance_counts": list(values),
            "maximum": max(values),
            "counterexample": max(values) <= 4,
            "squared_distance_sets": [
                sorted({squared_distance(p, q) for j, q in enumerate(best) if i != j})
                for i, p in enumerate(best)
            ],
            "turn_determinants": [cross(best[i], best[(i + 1) % 10], best[(i + 2) % 10]) for i in range(10)],
        },
        "trace": trace,
        "claim_scope": "exact candidate search only; absence is not an exclusion",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=10)
    parser.add_argument("--random-attempts", type=int, default=30000)
    parser.add_argument("--coefficient-bound", type=int, default=7)
    parser.add_argument("--beam", type=int, default=100)
    parser.add_argument("--generations", type=int, default=50)
    parser.add_argument("--mutations", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=982_620_026)
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("triangular_lattice_n10.json"))
    args = parser.parse_args()
    payload = run(args.bound, args.random_attempts, args.coefficient_bound, args.beam,
                  args.generations, args.mutations, args.seed, args.seconds)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("trace", "best")}, sort_keys=True))
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
