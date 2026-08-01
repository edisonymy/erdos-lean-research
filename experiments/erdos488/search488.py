#!/usr/bin/env python3
"""Exact finite searches for the corrected multiples version of Erdos #488.

All theorem checks use cross-multiplied Python integers.  Floating point is
used only to rank subcritical examples during randomized exploration.
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
from dataclasses import dataclass

import numpy as np


def primitive_reduce(values: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    vals = sorted(set(values))
    return tuple(a for a in vals if not any(a != b and a % b == 0 for b in vals))


def is_primitive(values: tuple[int, ...]) -> bool:
    return primitive_reduce(values) == values


def prefix_counts(values: tuple[int, ...], horizon: int) -> np.ndarray:
    covered = np.zeros(horizon + 1, dtype=np.int8)
    for a in values:
        covered[a::a] = 1
    return np.cumsum(covered, dtype=np.int64)


def count_ie(values: tuple[int, ...], x: int) -> int:
    """Independent inclusion-exclusion evaluator for small generator sets."""
    total = 0
    for size in range(1, len(values) + 1):
        sign = 1 if size % 2 else -1
        for subset in itertools.combinations(values, size):
            modulus = 1
            for a in subset:
                modulus = math.lcm(modulus, a)
                if modulus > x:
                    break
            total += sign * (x // modulus)
    return total


@dataclass(frozen=True)
class Witness:
    values: tuple[int, ...]
    n: int
    m: int
    fn: int
    fm: int

    @property
    def numerator(self) -> int:
        return self.n * self.fm

    @property
    def denominator(self) -> int:
        return self.m * self.fn

    @property
    def ratio(self) -> float:
        return self.numerator / self.denominator

    @property
    def refutes(self) -> bool:
        return self.numerator >= 2 * self.denominator


def worst_pair(values: tuple[int, ...], horizon: int, n_limit: int | None = None) -> Witness:
    """Find max (F(m)/m)/(F(n)/n) over M <= n < m <= horizon."""
    values = primitive_reduce(values)
    maximum = max(values)
    counts = prefix_counts(values, horizon)
    if n_limit is None:
        n_limit = horizon - 1

    # best_m[n] is an exact maximizer of F(m)/m over m>n.
    best_m = np.empty(horizon + 1, dtype=np.int64)
    best = horizon
    best_m[horizon - 1] = horizon
    for n in range(horizon - 2, maximum - 1, -1):
        candidate = n + 1
        if int(counts[candidate]) * best > int(counts[best]) * candidate:
            best = candidate
        best_m[n] = best

    winner: Witness | None = None
    for n in range(maximum, min(n_limit, horizon - 1) + 1):
        m = int(best_m[n])
        w = Witness(values, n, m, int(counts[n]), int(counts[m]))
        if winner is None or w.numerator * winner.denominator > winner.numerator * w.denominator:
            winner = w
    assert winner is not None
    return winner


def worst_uncovered_pair(values: tuple[int, ...], horizon: int,
                         n_limit: int | None = None) -> Witness | None:
    """Maximize the ratio only on layers not covered by Chojecki's criteria.

    We require the sparse regime, excess at least six, and negative union-bound
    slack.  These conditions exclude the dense, small-excess, and exact sparse
    bottleneck cases already proved in the March 2026 note.
    """
    values = primitive_reduce(values)
    maximum = max(values)
    counts = prefix_counts(values, horizon)
    if n_limit is None:
        n_limit = horizon - 1
    best_m = np.empty(horizon + 1, dtype=np.int64)
    best = horizon
    best_m[horizon - 1] = horizon
    for n in range(horizon - 2, maximum - 1, -1):
        candidate = n + 1
        if int(counts[candidate]) * best > int(counts[best]) * candidate:
            best = candidate
        best_m[n] = best
    incidence = sum((np.arange(horizon + 1, dtype=np.int64) // a for a in values),
                    start=np.zeros(horizon + 1, dtype=np.int64))
    winner: Witness | None = None
    r = len(values)
    for n in range(maximum, min(n_limit, horizon - 1) + 1):
        fn = int(counts[n])
        if fn - r <= 5 or 2 * fn >= n or 2 * fn - int(incidence[n]) - r >= 0:
            continue
        m = int(best_m[n])
        w = Witness(values, n, m, fn, int(counts[m]))
        if winner is None or w.numerator * winner.denominator > winner.numerator * w.denominator:
            winner = w
    return winner


def sparse_slack(values: tuple[int, ...], n: int) -> tuple[int, int, int, int]:
    """Return F(n), incidence I(n), excess, and 2F-I-r slack."""
    counts = prefix_counts(values, n)
    f = int(counts[n])
    incidence = sum(n // a for a in values)
    return f, incidence, f - len(values), 2 * f - incidence - len(values)


def verify_witness(w: Witness) -> None:
    assert is_primitive(w.values)
    assert w.n >= max(w.values) and w.m > w.n
    assert w.fn == count_ie(w.values, w.n)
    assert w.fm == count_ie(w.values, w.m)


def exhaustive(max_generator: int, size: int, horizon: int, n_factor: float) -> None:
    best: Witness | None = None
    checked = 0
    for values in itertools.combinations(range(2, max_generator + 1), size):
        if max(values) != max_generator or not is_primitive(values):
            continue
        checked += 1
        w = worst_pair(values, horizon, max(max_generator, int(n_factor * max_generator)))
        if best is None or w.numerator * best.denominator > best.numerator * w.denominator:
            best = w
        if w.refutes:
            verify_witness(w)
            print(f"COUNTEREXAMPLE {w}")
            return
    assert best is not None
    verify_witness(best)
    print(f"checked={checked} best={best} ratio={best.ratio:.12f} "
          f"slack={sparse_slack(best.values, best.n)}")


def random_primitive(rng: random.Random, maximum: int, size: int) -> tuple[int, ...]:
    # Sample near the top often (where generators have few early multiples),
    # but retain a logarithmic component to create nontrivial overlaps.
    for _ in range(2000):
        vals = {maximum}
        candidates = list(range(2, maximum))
        rng.shuffle(candidates)
        # Occasionally pull small candidates to the front; these are needed
        # to create true overlap layers rather than only near-singleton sets.
        if rng.random() < 0.65:
            candidates.sort(key=lambda a: rng.random() * (a ** rng.uniform(0.0, 1.5)))
        for a in candidates:
            if all(a % b != 0 and b % a != 0 for b in vals):
                vals.add(a)
                if len(vals) == size:
                    return tuple(sorted(vals))
    raise RuntimeError("failed to sample a primitive set")


def randomized(seed: int, trials: int, min_maximum: int, max_maximum: int,
               min_size: int, max_size: int, horizon_factor: int, n_factor: float) -> None:
    rng = random.Random(seed)
    best: Witness | None = None
    best_uncovered: Witness | None = None
    worst_sparse: tuple[int, tuple[int, ...], int, tuple[int, int, int, int]] | None = None
    for trial in range(1, trials + 1):
        maximum = rng.randint(min_maximum, max_maximum)
        size = rng.randint(min_size, min(max_size, (maximum + 1) // 2))
        values = random_primitive(rng, maximum, size)
        horizon = horizon_factor * maximum
        w = worst_pair(values, horizon, max(maximum, int(n_factor * maximum)))
        if best is None or w.numerator * best.denominator > best.numerator * w.denominator:
            best = w
            verify_witness(best)
            print(f"trial={trial} NEW_BEST {best} ratio={best.ratio:.12f} "
                  f"slack={sparse_slack(best.values, best.n)}", flush=True)
        unknown = worst_uncovered_pair(values, horizon, max(maximum, int(n_factor * maximum)))
        if unknown is not None and (best_uncovered is None or
                unknown.numerator * best_uncovered.denominator >
                best_uncovered.numerator * unknown.denominator):
            best_uncovered = unknown
            verify_witness(best_uncovered)
            print(f"trial={trial} NEW_UNCOVERED {best_uncovered} "
                  f"ratio={best_uncovered.ratio:.12f} "
                  f"slack={sparse_slack(best_uncovered.values, best_uncovered.n)}", flush=True)
        counts = prefix_counts(values, max(maximum, int(n_factor * maximum)))
        for n in range(maximum, len(counts)):
            f = int(counts[n])
            if 2 * f >= n:
                continue
            data = sparse_slack(values, n)
            if worst_sparse is None or data[3] < worst_sparse[0]:
                worst_sparse = (data[3], values, n, data)
    assert best is not None
    print(f"FINAL best={best} ratio={best.ratio:.12f}")
    print(f"FINAL_UNCOVERED={best_uncovered}")
    print(f"WORST_SPARSE_SLACK={worst_sparse}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    ex = sub.add_parser("exhaustive")
    ex.add_argument("--maximum", type=int, required=True)
    ex.add_argument("--size", type=int, required=True)
    ex.add_argument("--horizon", type=int, required=True)
    ex.add_argument("--n-factor", type=float, default=4.0)
    rnd = sub.add_parser("random")
    rnd.add_argument("--seed", type=int, default=488)
    rnd.add_argument("--trials", type=int, default=10000)
    rnd.add_argument("--min-maximum", type=int, default=12)
    rnd.add_argument("--max-maximum", type=int, default=200)
    rnd.add_argument("--min-size", type=int, default=4)
    rnd.add_argument("--max-size", type=int, default=20)
    rnd.add_argument("--horizon-factor", type=int, default=30)
    rnd.add_argument("--n-factor", type=float, default=4.0)
    args = parser.parse_args()
    if args.mode == "exhaustive":
        exhaustive(args.maximum, args.size, args.horizon, args.n_factor)
    else:
        randomized(args.seed, args.trials, args.min_maximum, args.max_maximum,
                   args.min_size, args.max_size, args.horizon_factor, args.n_factor)


if __name__ == "__main__":
    main()
