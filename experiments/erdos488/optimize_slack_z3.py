#!/usr/bin/env python3
"""Exact Z3 optimization of Chojecki's incidence slack at a fixed n.

This searches all primitive sets A contained in [2,n].  Generators a>n/2
can be omitted without changing the slack (they cover only themselves), so
the encoded search uses 2 <= a <= n/2.  A negative optimum disproves the
proposed universal incidence inequality I_A(n)+|A| <= 2 F_A(n).
"""

from __future__ import annotations

import argparse

import z3

from search488 import prefix_counts, sparse_slack


def optimize(n: int, timeout_ms: int, require_sparse: bool,
             minimum_excess: int) -> tuple[str, tuple[int, ...] | None, int | None]:
    generators = range(2, n // 2 + 1)
    x = {a: z3.Bool(f"x_{a}") for a in generators}
    y = {t: z3.Bool(f"y_{t}") for t in range(2, n + 1)}
    opt = z3.Optimize()
    opt.set(timeout=timeout_ms)
    opt.add(z3.Or(*x.values()))

    for a in generators:
        for b in range(2 * a, n // 2 + 1, a):
            opt.add(z3.Or(z3.Not(x[a]), z3.Not(x[b])))

    for t in range(2, n + 1):
        divisors = [x[a] for a in generators if t % a == 0]
        opt.add(y[t] == (z3.Or(*divisors) if divisors else z3.BoolVal(False)))

    covered = z3.Sum([z3.If(y[t], 1, 0) for t in range(2, n + 1)])
    cardinality = z3.Sum([z3.If(x[a], 1, 0) for a in generators])
    weighted_generators = z3.Sum([
        (n // a + 1) * z3.If(x[a], 1, 0) for a in generators
    ])
    if require_sparse:
        opt.add(2 * covered < n)
    opt.add(covered - cardinality >= minimum_excess)
    slack = 2 * covered - weighted_generators
    opt.minimize(slack)
    result = opt.check()
    if result == z3.unknown:
        return "unknown", None, None
    if result != z3.sat:
        return str(result), None, None
    model = opt.model()
    values = tuple(a for a in generators if z3.is_true(model.eval(x[a])))
    optimum = model.eval(slack).as_long()
    direct = sparse_slack(values, n)
    assert optimum == direct[3], (optimum, direct)
    counts = prefix_counts(values, n)
    assert int(counts[n]) == direct[0]
    return "sat", values, optimum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=10)
    parser.add_argument("--stop", type=int, default=200)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--sparse", action="store_true")
    parser.add_argument("--minimum-excess", type=int, default=0)
    args = parser.parse_args()
    for n in range(args.start, args.stop + 1, args.step):
        status, values, slack = optimize(n, args.timeout_ms, args.sparse, args.minimum_excess)
        print(f"n={n} status={status} optimum={slack} A={values}", flush=True)
        if slack is not None and slack < 0:
            break


if __name__ == "__main__":
    main()
