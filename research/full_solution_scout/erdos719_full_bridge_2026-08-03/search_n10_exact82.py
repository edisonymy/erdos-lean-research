#!/usr/bin/env python3
"""Counterexample-first CEGAR for Erdős #719 at (r,n,m,nu)=(3,10,82,2).

The exact Turán input is ex_3(10,K4^3)=75 (Stanton--Bate).  A model with 82
edges and packing number two has decomposition number 82-3*2=76, hence is a
full counterexample to the universal conjecture.

The three runs fix the complete isomorphism types of a clean two-tetrahedron
core, indexed by core intersection 0,1,2.  Static clauses make the core
maximal; the separator then blocks arbitrary three-packings anywhere.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

V = tuple(range(10))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {e: i for i, e in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))
BEDGES = tuple(frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in BLOCKS)
CORE_REPS = {
    0: ((0, 1, 2, 3), (4, 5, 6, 7)),
    1: ((0, 1, 2, 3), (3, 4, 5, 6)),
    2: ((0, 1, 2, 3), (2, 3, 4, 5)),
}


def compatible(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return len(set(a) & set(b)) <= 2


def source_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def packing_batch(clean: list[int], limit: int) -> list[tuple[int, int, int]]:
    """Return up to limit distinct three-packings of clean tetrahedra."""
    clean_set = set(clean)
    after = {}
    for i in clean:
        after[i] = [j for j in clean if j > i and BEDGES[i].isdisjoint(BEDGES[j])]
    out = []
    for i in clean:
        ai = after[i]
        for j in ai:
            for k in after[j]:
                if k in clean_set and BEDGES[i].isdisjoint(BEDGES[k]):
                    out.append((i, j, k))
                    if len(out) >= limit:
                        return out
    return out


def exact_packing_number(clean: list[int]) -> tuple[int, list[int]]:
    order = sorted(clean, key=lambda i: sum(not BEDGES[i].isdisjoint(BEDGES[j]) for j in clean))
    best: list[int] = []

    def dfs(pos: int, used: frozenset[int], chosen: list[int]) -> None:
        nonlocal best
        if len(chosen) + len(order) - pos <= len(best):
            return
        if len(chosen) > len(best):
            best = chosen.copy()
        for z in range(pos, len(order)):
            i = order[z]
            if BEDGES[i].isdisjoint(used):
                dfs(z + 1, used | BEDGES[i], chosen + [i])

    dfs(0, frozenset(), [])
    return len(best), best


def run(core_intersection: int, outdir: Path, max_iterations: int, seconds: float, batch_size: int, conflict_budget: int) -> None:
    core = CORE_REPS[core_intersection]
    core_edges = frozenset().union(*(
        frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in core
    ))
    assert len(core_edges) == 8
    zvars = list(range(1, len(TRIPLES) + 1))
    card = CardEnc.equals(zvars, bound=38, top_id=len(TRIPLES), encoding=EncType.totalizer)
    clauses = list(card.clauses)
    clauses.extend([[-(e + 1)] for e in sorted(core_edges)])
    local = 0
    for b, be in zip(BLOCKS, BEDGES):
        if all(compatible(b, p) for p in core):
            assert be.isdisjoint(core_edges)
            clauses.append([e + 1 for e in sorted(be)])
            local += 1

    outdir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    cuts = 0
    models = 0
    status = "RUNNING"
    with Solver(name="glucose4", bootstrap_with=clauses) as solver:
        for iteration in range(1, max_iterations + 1):
            if time.time() - started >= seconds:
                status = "TIME_LIMIT"
                break
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(expect_interrupt=True)
            if answer is None:
                status = "UNKNOWN_CONFLICT_BUDGET"
                break
            if not answer:
                status = "UNSAT_NO_CERTIFICATE"
                break
            models += 1
            model = solver.get_model()
            # Parse by literal identity, not by the solver's model-list order.
            # PySAT's bundled solvers normally return an ordered full model, but
            # the DIMACS contract does not require clients to rely on that.
            missing = {lit - 1 for lit in model if 1 <= lit <= len(TRIPLES)}
            assert len(missing) == 38 and core_edges.isdisjoint(missing)
            clean = [i for i, be in enumerate(BEDGES) if be.isdisjoint(missing)]
            bad = packing_batch(clean, batch_size)
            if not bad:
                nu, witness = exact_packing_number(clean)
                if nu <= 2:
                    status = "CANDIDATE_EXACT82_NU2"
                    payload = {
                        "status": status,
                        "vertices": 10,
                        "present_edge_count": 82,
                        "missing_edge_count": 38,
                        "packing_number": nu,
                        "decomposition_number": 82 - 3 * nu,
                        "turan_input": 75,
                        "core_intersection": core_intersection,
                        "core": [list(x) for x in core],
                        "missing_triples": [list(TRIPLES[i]) for i in sorted(missing)],
                        "present_triples": [list(e) for i, e in enumerate(TRIPLES) if i not in missing],
                        "maximum_packing": [list(BLOCKS[i]) for i in witness],
                        "source_sha256": source_sha256(),
                    }
                    (outdir / "candidate.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                    break
                raise AssertionError("separator missed a three-packing")
            for pack in bad:
                union = sorted(frozenset().union(*(BEDGES[i] for i in pack)))
                assert len(union) == 12
                solver.add_clause([e + 1 for e in union])
                cuts += 1
        else:
            status = "ITERATION_LIMIT"

    summary = {
        "status": status,
        "core_intersection": core_intersection,
        "models": models,
        "packing_cuts": cuts,
        "elapsed_seconds": time.time() - started,
        "static_clauses": len(clauses),
        "local_maximality_clauses": local,
        "max_iterations": max_iterations,
        "time_limit_seconds": seconds,
        "batch_size": batch_size,
        "per_solve_conflict_budget": conflict_budget,
        "source_sha256": source_sha256(),
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--core-intersection", type=int, choices=(0, 1, 2), required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--max-iterations", type=int, default=100000)
    p.add_argument("--seconds", type=float, default=1200)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--conflict-budget", type=int, default=1000000)
    a = p.parse_args()
    run(a.core_intersection, a.outdir, a.max_iterations, a.seconds, a.batch_size, a.conflict_budget)
