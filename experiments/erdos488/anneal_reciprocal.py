#!/usr/bin/env python3
"""Randomized local search against the sparse reciprocal inequality."""

from __future__ import annotations

import argparse
import math
import random
from fractions import Fraction

from search488 import is_primitive, prefix_counts, primitive_reduce


def metrics(values: tuple[int, ...], n: int):
    f = int(prefix_counts(values, n)[n])
    slack = 2 * f - n * sum((Fraction(1, a) for a in values), Fraction())
    excess = f - len(values)
    return slack, f, excess


def initial(rng: random.Random, n: int, size: int) -> tuple[int, ...]:
    for _ in range(10000):
        vals: set[int] = set()
        candidates = list(range(3, n // 2 + 1))
        rng.shuffle(candidates)
        for a in candidates:
            if all(a % b and b % a for b in vals):
                vals.add(a)
                if len(vals) == size:
                    result = tuple(sorted(vals))
                    slack, f, excess = metrics(result, n)
                    if 2 * f < n and excess >= 6:
                        return result
    raise RuntimeError("initialization failed")


def mutate(rng: random.Random, values: tuple[int, ...], n: int,
           min_size: int, max_size: int) -> tuple[int, ...]:
    vals = set(values)
    action = rng.random()
    if action < 0.25 and len(vals) > min_size:
        vals.remove(rng.choice(tuple(vals)))
    elif action < 0.5 and len(vals) < max_size:
        candidates = [a for a in range(2, n + 1)
                      if a not in vals and all(a % b and b % a for b in vals)]
        if candidates:
            vals.add(rng.choice(candidates))
    else:
        vals.remove(rng.choice(tuple(vals)))
        candidates = [a for a in range(2, n + 1)
                      if a not in vals and all(a % b and b % a for b in vals)]
        if candidates:
            vals.add(rng.choice(candidates))
    result = tuple(sorted(vals))
    assert is_primitive(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--steps", type=int, default=200000)
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--min-size", type=int, default=4)
    parser.add_argument("--max-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=488)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    global_best = None
    for restart in range(args.restarts):
        values = initial(rng, args.n, rng.randint(args.min_size, args.max_size))
        current = metrics(values, args.n)
        for step in range(args.steps // args.restarts):
            proposal = mutate(rng, values, args.n, args.min_size, args.max_size)
            pm = metrics(proposal, args.n)
            if 2 * pm[1] >= args.n or pm[2] < 6:
                continue
            temperature = max(0.001, 2.0 * (1.0 - step / (args.steps / args.restarts)))
            delta = float(pm[0] - current[0])
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                values, current = proposal, pm
            candidate = (current[0], values, current[1], current[2])
            if global_best is None or candidate[0] < global_best[0]:
                global_best = candidate
                print(f"restart={restart} step={step} best={global_best}", flush=True)
                if candidate[0] < 0:
                    return
    print(f"FINAL {global_best}")


if __name__ == "__main__":
    main()
