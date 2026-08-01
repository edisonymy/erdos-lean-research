#!/usr/bin/env python3
"""Test the upper-half incidence inequality for primitive sets.

The candidate lemma is
  sum_a (floor(n/a)-floor((n/2)/a)) <= F_A(n).
It would imply n*sum_a(1/a) <= 2F_A(n), and hence settle EP488.
"""

from __future__ import annotations

import argparse
import z3

from search488 import prefix_counts, primitive_reduce


def optimize(n: int, timeout_ms: int, sparse: bool = False, decision: bool = False):
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
    top_incidence = z3.Sum([(n // a - (n // 2) // a) * z3.If(x[a], 1, 0)
                            for a in range(2, n + 1)])
    slack = covered - top_incidence
    if sparse:
        opt.add(2 * covered < n)
    if decision:
        opt.add(slack < 0)
    else:
        opt.minimize(slack)
    result = opt.check()
    if result == z3.unknown:
        return "unknown", None, None
    if result == z3.unsat:
        return "unsat", None, None
    model = opt.model()
    values = primitive_reduce(tuple(a for a in range(2, n + 1)
                                    if z3.is_true(model.eval(x[a]))))
    f = int(prefix_counts(values, n)[n])
    exact = f - sum(n // a - (n // 2) // a for a in values)
    assert model.eval(slack).as_long() == exact
    return "sat", values, exact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=10)
    parser.add_argument("--stop", type=int, default=200)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--sparse", action="store_true")
    parser.add_argument("--decision", action="store_true")
    args = parser.parse_args()
    for n in range(args.start, args.stop + 1, args.step):
        status, values, slack = optimize(n, args.timeout_ms, args.sparse, args.decision)
        print(f"n={n} status={status} slack={slack} A={values}", flush=True)
        if slack is not None and slack < 0:
            break


if __name__ == "__main__":
    main()
