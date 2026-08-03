#!/usr/bin/env python3
"""Exact SAT gate for the only possible n=11, Delta=4 counterexample shape.

If a 4-regular 11-vertex graph G needs more than 20 strong colours, the
compatibility graph J on its 22 edges (pairs that form an induced matching)
has neither a triangle nor a matching of size two.  Once J is known nonempty,
it is a star.  Relabel its centre edge as 01 and one leaf edge as 23.

This script asks exactly whether such a labelled graph exists.  The implication
clauses say that any two G-edges other than 01 cannot form an induced matching.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


N = 11
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
VAR = {e: i + 1 for i, e in enumerate(PAIRS)}


def ve(a: int, b: int) -> int:
    return VAR[(a, b) if a < b else (b, a)]


def build_cnf() -> CNF:
    cnf = CNF()
    pool = IDPool(start_from=len(PAIRS) + 1)
    # Simple 4-regular graph.
    for v in range(N):
        incident = [ve(v, w) for w in range(N) if w != v]
        enc = CardEnc.equals(
            lits=incident, bound=4, vpool=pool, encoding=EncType.seqcounter
        )
        cnf.extend(enc.clauses)

    centre = (0, 1)
    leaf = (2, 3)
    cnf.append([ve(*centre)])
    cnf.append([ve(*leaf)])
    # 01 and 23 form an induced matching.
    for cross in ((0, 2), (0, 3), (1, 2), (1, 3)):
        cnf.append([-ve(*cross)])

    # Every compatible pair of present G-edges must involve the centre 01.
    for i, (a, b) in enumerate(PAIRS):
        if (a, b) == centre:
            continue
        for c, d in PAIRS[i + 1 :]:
            if (c, d) == centre or len({a, b, c, d}) != 4:
                continue
            crosses = [ve(a, c), ve(a, d), ve(b, c), ve(b, d)]
            cnf.append([-ve(a, b), -ve(c, d), *crosses])
    return cnf


def dimacs_bytes(cnf: CNF) -> bytes:
    lines = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in cnf.clauses)
    return ("\n".join(lines) + "\n").encode()


def solve(cnf: CNF, name: str, proof: bool = False) -> tuple[bool, list[int] | None, list[str] | None, float]:
    before = time.time()
    with Solver(name=name, bootstrap_with=cnf.clauses, with_proof=proof) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
        trace = solver.get_proof() if proof and not sat else None
    return sat, model, trace, time.time() - before


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("exact_149_n11_star_sat.json"))
    ap.add_argument("--cnf", type=Path, default=Path("exact_149_n11_star.cnf"))
    ap.add_argument("--proof", type=Path, default=Path("exact_149_n11_star_glucose.drup"))
    args = ap.parse_args()

    cnf = build_cnf()
    db = dimacs_bytes(cnf)
    args.cnf.write_bytes(db)
    primary = solve(cnf, "g4", proof=True)
    secondary_name = None
    secondary = None
    for candidate in ("cadical195", "cadical153", "m22", "g3"):
        try:
            secondary = solve(cnf, candidate, proof=False)
            secondary_name = candidate
            break
        except Exception:
            continue
    if secondary is None:
        raise RuntimeError("no independent second PySAT backend available")

    sat, model, trace, elapsed = primary
    if trace is not None:
        args.proof.write_text("\n".join(trace) + "\n", encoding="ascii", newline="\n")
    edges = None
    if sat and model is not None:
        positive = set(x for x in model if x > 0)
        edges = [list(e) for e in PAIRS if ve(*e) in positive]
    result = {
        "schema": "erdos149-n11-star-sat-v1",
        "claim_scope": "exact labelled existence after symmetry fixing 01 centre, 23 leaf",
        "encoding": {
            "vertices": N,
            "graph_edge_variables": len(PAIRS),
            "cnf_variables": cnf.nv,
            "clauses": len(cnf.clauses),
            "cnf_path": str(args.cnf),
            "cnf_sha256": hashlib.sha256(db).hexdigest(),
        },
        "primary": {
            "solver": "glucose4",
            "sat": sat,
            "elapsed_seconds": elapsed,
            "proof_path": str(args.proof) if trace is not None else None,
            "proof_lines": len(trace) if trace is not None else None,
        },
        "secondary": {
            "solver": secondary_name,
            "sat": secondary[0],
            "elapsed_seconds": secondary[3],
        },
        "solvers_agree": sat == secondary[0],
        "sat_edges": edges,
        "certification_warning": (
            "A raw DRUP trace is recorded if UNSAT, but no independent proof checker "
            "was run in this pulse; solver agreement is computational evidence, not certification."
        ),
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
