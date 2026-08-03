#!/usr/bin/env python3
"""Exact SAT probe for the 38-block / 14-leave supersaturation claim.

Variables x_T mark 38 missing triples.  A 4-set Q is clean precisely when
none of its four triples is missing.  The target CNF asks for at most 13 clean
4-sets.  UNSAT would prove that every 82-edge 3-graph on ten vertices has at
least fourteen tetrahedra; SAT emits a directly checkable counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def build() -> tuple[CNF, list[tuple[int, ...]], list[tuple[int, ...]], list[int], list[int]]:
    triples = list(itertools.combinations(range(10), 3))
    quads = list(itertools.combinations(range(10), 4))
    tid = {e: i for i, e in enumerate(triples)}
    pool = IDPool()
    xv = [pool.id(("x", e)) for e in triples]
    uv = [pool.id(("u", Q)) for Q in quads]
    cnf = CNF()
    cnf.extend(CardEnc.equals(xv, bound=38, vpool=pool, encoding=EncType.totalizer).clauses)
    for qi, Q in enumerate(quads):
        xs = [xv[tid[e]] for e in itertools.combinations(Q, 3)]
        # u_Q iff every x_T is false.
        for x in xs:
            cnf.append([-uv[qi], -x])
        cnf.append([uv[qi], *xs])
    cnf.extend(CardEnc.atmost(uv, bound=13, vpool=pool, encoding=EncType.totalizer).clauses)
    cnf.nv = pool.top
    return cnf, triples, quads, xv, uv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--cnf", type=Path)
    ap.add_argument("--result", type=Path, default=Path(__file__).with_name("n10_leave_sat_result.json"))
    args = ap.parse_args()
    cnf, triples, quads, xv, uv = build()
    if args.cnf:
        cnf.to_file(args.cnf)
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        stats = solver.accum_stats()
        model = set(solver.get_model() or [])
    payload = {
        "solver": args.solver,
        "sat": sat,
        "variables": cnf.nv,
        "clauses": len(cnf.clauses),
        "stats": stats,
        "missing_triples": [list(e) for e, v in zip(triples, xv) if v in model],
        "clean_quads": [list(Q) for Q, v in zip(quads, uv) if v in model],
    }
    args.result.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("solver", "sat", "variables", "clauses", "stats")}, sort_keys=True))
    if args.cnf:
        print("cnf_sha256=" + hashlib.sha256(args.cnf.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
