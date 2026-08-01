#!/usr/bin/env python3
"""Exact counterexample-first search for Erdős problem 982.

All coordinates are integers and every predicate (strict convexity,
cocircularity, and squared-distance equality) is evaluated exactly.  The
search deliberately excludes cocircular point sets: those satisfy the target
bound for the elementary reason that a circle meets a circle centred at a
fixed vertex in at most two points.

The two seed families are genuinely noncyclic:

* hulls of bounded-lattice intersections with sublevel sets
  a*x^2 + b*x*y + c*y^2 <= R;
* hulls of random subsets of a bounded integer lattice.

A beam search then replaces one or two vertices by lattice points, retaining
only strictly convex, noncocircular polygons.  This is a heuristic, not an
exhaustive search.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import random
import time
from typing import Iterable, Sequence

Point = tuple[int, int]
Polygon = tuple[Point, ...]


def cross(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def strict_hull(points: Iterable[Point]) -> Polygon:
    """Andrew hull; collinear boundary points are discarded."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return ()
    lower: list[Point] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return tuple(lower[:-1] + upper[:-1])


def is_cocircular(poly: Sequence[Point]) -> bool:
    """Exact rational circumcentre test using the first three vertices."""
    if len(poly) < 4:
        return True
    (x1, y1), (x2, y2), (x3, y3) = poly[:3]
    den = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if den == 0:
        return False
    s1, s2, s3 = x1 * x1 + y1 * y1, x2 * x2 + y2 * y2, x3 * x3 + y3 * y3
    ux = Fraction(s1 * (y2 - y3) + s2 * (y3 - y1) + s3 * (y1 - y2), den)
    uy = Fraction(s1 * (x3 - x2) + s2 * (x1 - x3) + s3 * (x2 - x1), den)
    radius2 = (Fraction(x1) - ux) ** 2 + (Fraction(y1) - uy) ** 2
    return all((Fraction(x) - ux) ** 2 + (Fraction(y) - uy) ** 2 == radius2 for x, y in poly[3:])


def distance_profile(poly: Sequence[Point]) -> tuple[int, ...]:
    counts: list[int] = []
    for i, (x, y) in enumerate(poly):
        values = {
            (x - u) * (x - u) + (y - v) * (y - v)
            for j, (u, v) in enumerate(poly)
            if i != j
        }
        counts.append(len(values))
    return tuple(counts)


def rank(poly: Polygon) -> tuple[int, int, int, tuple[int, ...]]:
    """Lexicographic minimisation with the conjecture's maximum first."""
    profile = distance_profile(poly)
    ordered = tuple(sorted(profile, reverse=True))
    return (max(profile), sum(profile), len(set(profile)), ordered)


def canonical(points: Iterable[Point]) -> Polygon | None:
    pts = tuple(points)
    h = strict_hull(pts)
    if len(h) != len(set(pts)) or is_cocircular(h):
        return None
    return h


def quadratic_seeds(
    targets: set[int], coefficient_bound: int, coordinate_bound: int
) -> tuple[set[Polygon], int]:
    """Enumerate hulls of a lattice box intersected with quadratic sublevels."""
    seeds: set[Polygon] = set()
    examined = 0
    lattice = [
        (x, y)
        for x in range(-coordinate_bound, coordinate_bound + 1)
        for y in range(-coordinate_bound, coordinate_bound + 1)
    ]
    for a in range(1, coefficient_bound + 1):
        for c in range(a, coefficient_bound + 1):
            for b in range(0, 2 * math.isqrt(a * c) + 1):
                if b * b >= 4 * a * c or math.gcd(math.gcd(a, b), c) != 1:
                    continue
                by_value: dict[int, list[Point]] = {}
                for x, y in lattice:
                    q = a * x * x + b * x * y + c * y * y
                    by_value.setdefault(q, []).append((x, y))
                inside: list[Point] = []
                for q in sorted(by_value):
                    inside.extend(by_value[q])
                    examined += 1
                    h = strict_hull(inside)
                    if len(h) in targets and not is_cocircular(h):
                        seeds.add(h)
    return seeds, examined


def random_hull_seeds(
    targets: set[int], coordinate_bound: int, attempts: int, rng: random.Random
) -> set[Polygon]:
    lattice = [
        (x, y)
        for x in range(-coordinate_bound, coordinate_bound + 1)
        for y in range(-coordinate_bound, coordinate_bound + 1)
    ]
    maximum_sample = min(len(lattice), 8 * max(targets))
    seeds: set[Polygon] = set()
    for _ in range(attempts):
        sample_size = rng.randint(max(targets), maximum_sample)
        h = strict_hull(rng.sample(lattice, sample_size))
        if len(h) in targets and not is_cocircular(h):
            seeds.add(h)
    return seeds


def mutations(poly: Polygon, lattice: Sequence[Point], count: int, rng: random.Random) -> Iterable[Polygon]:
    pts = list(poly)
    occupied = set(pts)
    for _ in range(count):
        child = pts.copy()
        if rng.random() < 0.82:
            indices = [rng.randrange(len(pts))]
        else:
            i = rng.randrange(len(pts))
            indices = [i, (i + rng.choice((-1, 1))) % len(pts)]
        unavailable = occupied - {pts[i] for i in indices}
        replacements: list[Point] = []
        for _i in indices:
            for _attempt in range(12):
                p = rng.choice(lattice)
                if p not in unavailable and p not in replacements:
                    replacements.append(p)
                    break
        if len(replacements) != len(indices):
            continue
        for i, p in zip(indices, replacements):
            child[i] = p
        candidate = canonical(child)
        if candidate is not None and len(candidate) == len(poly):
            yield candidate


def beam_search(
    initial: Iterable[Polygon], target: int, coordinate_bound: int,
    beam_width: int, generations: int, mutations_per_parent: int,
    rng: random.Random,
) -> tuple[Polygon, list[dict[str, object]]]:
    lattice = [
        (x, y)
        for x in range(-coordinate_bound, coordinate_bound + 1)
        for y in range(-coordinate_bound, coordinate_bound + 1)
    ]
    pool = {p for p in initial if len(p) == target}
    if not pool:
        raise RuntimeError(f"no initial polygons with n={target}")
    beam = sorted(pool, key=rank)[:beam_width]
    best = beam[0]
    trace: list[dict[str, object]] = []
    for generation in range(generations + 1):
        if rank(beam[0]) < rank(best):
            best = beam[0]
        profile = distance_profile(best)
        trace.append({
            "generation": generation,
            "max_distinct": max(profile),
            "margin": max(profile) - target // 2,
            "profile": list(profile),
        })
        if max(profile) < target // 2 or generation == generations:
            break
        children = set(beam)
        each = max(1, mutations_per_parent // len(beam))
        for parent in beam:
            children.update(mutations(parent, lattice, each, rng))
        beam = sorted(children, key=rank)[:beam_width]
    return best, trace


def record(poly: Polygon, trace: list[dict[str, object]]) -> dict[str, object]:
    profile = distance_profile(poly)
    threshold = len(poly) // 2
    return {
        "n": len(poly),
        "points_counterclockwise": [list(p) for p in poly],
        "distinct_squared_distance_counts": list(profile),
        "maximum": max(profile),
        "threshold": threshold,
        "margin": max(profile) - threshold,
        "counterexample": max(profile) < threshold,
        "cocircular": is_cocircular(poly),
        "trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=int, nargs="+", default=[8, 9, 11, 13, 14])
    parser.add_argument("--box", type=int, default=8)
    parser.add_argument("--quadratic-coefficients", type=int, default=8)
    parser.add_argument("--random-seeds", type=int, default=30_000)
    parser.add_argument("--beam", type=int, default=64)
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--mutations", type=int, default=25_000)
    parser.add_argument("--seed", type=int, default=982_2026)
    parser.add_argument("--output", type=Path, default=Path("noncyclic_exact_run.json"))
    args = parser.parse_args()

    started = time.time()
    targets = set(args.targets)
    rng = random.Random(args.seed)
    qseeds, quadratic_states = quadratic_seeds(targets, args.quadratic_coefficients, args.box)
    rseeds = random_hull_seeds(targets, args.box, args.random_seeds, rng)
    all_seeds = qseeds | rseeds
    results: list[dict[str, object]] = []
    for n in sorted(targets):
        candidates = [p for p in all_seeds if len(p) == n]
        if not candidates:
            results.append({"n": n, "error": "no seeds"})
            continue
        best, trace = beam_search(
            candidates, n, args.box, args.beam, args.generations,
            args.mutations, rng,
        )
        results.append(record(best, trace))
        if results[-1]["counterexample"]:
            break

    payload = {
        "problem": "Erdos 982",
        "method": "exact noncocircular integer-lattice heuristic",
        "parameters": vars(args) | {"output": str(args.output)},
        "quadratic_sublevel_states_examined": quadratic_states,
        "quadratic_seed_polygons": len(qseeds),
        "random_seed_polygons": len(rseeds),
        "unique_seed_polygons": len(all_seeds),
        "elapsed_seconds": time.time() - started,
        "results": results,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
