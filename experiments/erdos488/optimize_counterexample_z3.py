#!/usr/bin/env python3
"""Exact fixed-(n,m) optimization for counterexamples to Erdos #488.

For every possible generator a in [2,n], x_a says that a is selected and
y_t is the OR of selected divisors of t.  The objective

    n F_A(m) - 2 m F_A(n)

is an integer.  A nonnegative optimum is an exact counterexample.  We may
allow nonprimitive selections because primitive reduction preserves every
y_t and never increases max(A).
"""

from __future__ import annotations

import argparse

import z3

from search488 import Witness, count_ie, prefix_counts, primitive_reduce, verify_witness


def optimize_pair(n: int, m: int, timeout_ms: int) -> tuple[str, Witness | None, int | None]:
    assert 1 < n < m
    x = {a: z3.Bool(f"x_{a}") for a in range(2, n + 1)}
    y = {t: z3.Bool(f"y_{t}") for t in range(2, m + 1)}
    opt = z3.Optimize()
    opt.set(timeout=timeout_ms)
    opt.add(z3.Or(*x.values()))
    for t in range(2, m + 1):
        selected_divisors = [x[a] for a in range(2, min(n, t) + 1) if t % a == 0]
        opt.add(y[t] == z3.Or(*selected_divisors))
    fn = z3.Sum([z3.If(y[t], 1, 0) for t in range(2, n + 1)])
    fm = z3.Sum([z3.If(y[t], 1, 0) for t in range(2, m + 1)])
    margin = n * fm - 2 * m * fn
    opt.maximize(margin)
    result = opt.check()
    if result == z3.unknown:
        return "unknown", None, None
    if result != z3.sat:
        return str(result), None, None
    model = opt.model()
    selected = tuple(a for a in range(2, n + 1) if z3.is_true(model.eval(x[a])))
    values = primitive_reduce(selected)
    counts = prefix_counts(values, m)
    witness = Witness(values, n, m, int(counts[n]), int(counts[m]))
    verify_witness(witness)
    exact_margin = witness.numerator - 2 * witness.denominator
    claimed_margin = model.eval(margin).as_long()
    assert exact_margin == claimed_margin, (exact_margin, claimed_margin, selected, values)
    assert witness.fn == count_ie(values, n) if len(values) <= 20 else True
    return "sat", witness, exact_margin


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, nargs="+", required=True)
    parser.add_argument("--multipliers", type=int, nargs="*", default=[2, 3, 5, 10, 20])
    parser.add_argument("--m", type=int, nargs="*", default=[])
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()
    for n in args.n:
        ms = sorted(set(args.m + [k * n for k in args.multipliers]))
        for m in ms:
            if m <= n:
                continue
            status, witness, margin = optimize_pair(n, m, args.timeout_ms)
            ratio = None if witness is None else witness.ratio
            print(f"n={n} m={m} status={status} margin={margin} ratio={ratio} A={None if witness is None else witness.values}",
                  flush=True)
            if margin is not None and margin >= 0:
                return


if __name__ == "__main__":
    main()
