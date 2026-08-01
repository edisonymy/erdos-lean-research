#!/usr/bin/env python3
"""Search for failure of n * sum(1/a) <= 2 F_A(n) for primitive A.

If this reciprocal majorant held universally, Erdos #488 would follow at
once from D_A(m) < sum(1/a) (apart from the elementary singleton case).
The optimizer uses exact rational arithmetic.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import math

import z3

from search488 import prefix_counts, primitive_reduce


def optimize(n: int, timeout_ms: int, decision: bool = False, sparse: bool = False):
    x = {a: z3.Bool(f"x_{a}") for a in range(2, n + 1)}
    y = {t: z3.Bool(f"y_{t}") for t in range(2, n + 1)}
    opt = z3.Solver() if decision else z3.Optimize()
    opt.set(timeout=timeout_ms)
    opt.add(z3.Or(*x.values()))
    for a in range(2, n + 1):
        for b in range(2 * a, n + 1, a):
            opt.add(z3.Or(z3.Not(x[a]), z3.Not(x[b])))
    for t in range(2, n + 1):
        divisors = [x[a] for a in range(2, t + 1) if t % a == 0]
        opt.add(y[t] == z3.Or(*divisors))
    covered = z3.Sum([z3.If(y[t], 1, 0) for t in range(2, n + 1)])
    scale = math.lcm(*range(2, n + 1))
    reciprocal_scaled = z3.Sum([z3.If(x[a], n * (scale // a), 0)
                                for a in range(2, n + 1)])
    slack_scaled = 2 * scale * covered - reciprocal_scaled
    if sparse:
        opt.add(2 * covered < n)
    if decision:
        opt.add(slack_scaled < 0)
    else:
        opt.minimize(slack_scaled)
    result = opt.check()
    if result == z3.unknown:
        return "unknown", None, None
    if result == z3.unsat:
        return "unsat", None, None
    model = opt.model()
    values = primitive_reduce(tuple(a for a in range(2, n + 1)
                                    if z3.is_true(model.eval(x[a]))))
    f = int(prefix_counts(values, n)[n])
    exact = 2 * f - n * sum((Fraction(1, a) for a in values), Fraction())
    claimed = model.eval(slack_scaled).as_long()
    assert Fraction(claimed, scale) == exact
    return "sat", values, exact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=10)
    parser.add_argument("--stop", type=int, default=200)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--decision", action="store_true")
    parser.add_argument("--sparse", action="store_true")
    args = parser.parse_args()
    for n in range(args.start, args.stop + 1, args.step):
        status, values, slack = optimize(n, args.timeout_ms, args.decision, args.sparse)
        print(f"n={n} status={status} slack={slack} A={values}", flush=True)
        if slack is not None and slack < 0:
            break


if __name__ == "__main__":
    main()
