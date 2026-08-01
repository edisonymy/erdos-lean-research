#!/usr/bin/env python3
"""CNF encoding of the exact finite Erdos-128 counterexample search."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--dimacs", type=Path)
    parser.add_argument("--build-only", action="store_true",
                        help="write DIMACS and exit without starting a solver")
    parser.add_argument("--alpha-upper", type=int,
                        help="add clauses forbidding independent sets larger than this")
    parser.add_argument("--fix-independent-size", type=int,
                        help="by relabelling, force vertices 0..s-1 to be independent")
    args = parser.parse_args()

    if args.build_only and args.dimacs is None:
        parser.error("--build-only requires --dimacs")

    n = args.n
    if n < 0:
        parser.error("n must be nonnegative")
    if args.alpha_upper is not None and not 0 <= args.alpha_upper <= n:
        parser.error("--alpha-upper must lie between 0 and n")
    if args.fix_independent_size is not None and not 0 <= args.fix_independent_size <= n:
        parser.error("--fix-independent-size must lie between 0 and n")
    if (args.alpha_upper is not None and args.fix_independent_size is not None
            and args.fix_independent_size > args.alpha_upper):
        parser.error("--fix-independent-size cannot exceed --alpha-upper")
    k = n // 2
    threshold = n * n // 50 + 1
    pool = IDPool()
    evar = {(i, j): pool.id(("e", i, j)) for i in range(n) for j in range(i + 1, n)}
    cnf = CNF()

    for i, j, l in itertools.combinations(range(n), 3):
        cnf.append([-evar[i, j], -evar[i, l], -evar[j, l]])

    if args.fix_independent_size is not None:
        s = args.fix_independent_size
        for i, j in itertools.combinations(range(s), 2):
            cnf.append([-evar[i, j]])

    if args.alpha_upper is not None:
        a = args.alpha_upper
        for subset in itertools.combinations(range(n), a + 1):
            cnf.append([evar[i, j] for i, j in itertools.combinations(subset, 2)])

    start = time.monotonic()
    for subset in itertools.combinations(range(n), k):
        lits = [evar[i, j] for i, j in itertools.combinations(subset, 2)]
        enc = CardEnc.atleast(lits=lits, bound=threshold, vpool=pool, encoding=EncType.seqcounter)
        cnf.extend(enc.clauses)
    built = time.monotonic()
    if args.dimacs:
        cnf.to_file(str(args.dimacs))
    print(json.dumps({"n": n, "half_size": k, "threshold": threshold,
                      "alpha_upper": args.alpha_upper,
                      "fixed_independent_size": args.fix_independent_size,
                      "half_sets": math.comb(n, k), "variables": cnf.nv,
                      "clauses": len(cnf.clauses), "build_seconds": built - start}), flush=True)

    if args.build_only:
        return 0

    with Solver(name=args.solver, bootstrap_with=cnf.clauses, with_proof=bool(args.proof)) as solver:
        solve_start = time.monotonic()
        sat = solver.solve()
        solve_end = time.monotonic()
        stats = solver.accum_stats()
        print(json.dumps({"result": "sat" if sat else "unsat",
                          "solve_seconds": solve_end - solve_start, "stats": stats}), flush=True)
        if sat:
            model = set(solver.get_model())
            selected = [[i, j] for (i, j), v in evar.items() if v in model]
            output = args.model or Path(f"counterexample_n{n}.json")
            output.write_text(json.dumps({"n": n, "edges": selected}, indent=2) + "\n",
                              encoding="utf-8")
            print(f"wrote {output}")
        elif args.proof:
            proof = solver.get_proof()
            args.proof.write_text("\n".join(proof) + "\n", encoding="ascii")
            print(f"wrote {args.proof} ({len(proof)} proof lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
