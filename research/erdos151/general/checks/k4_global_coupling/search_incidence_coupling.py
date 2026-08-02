"""Search a strict alpha-level joint completion of four K4 residuals.

This freezes only the U graph and the four within-fan graphs of the audited
local abstraction.  It re-chooses all U--fan incidences and all cross-fan
edges.  It encodes exactly the following *pre-beta* package:

* the rigid ledger profile |U|=13 and four singleton fans of order six;
* degree interval [5,9] and all four saturated-clique cut bounds >=20;
* each W_c=U union A_c is triangle-free with alpha(W_c)<=6;
* every exact singleton fibre has size at most one and its edge is ambient
  maximal;
* omega<=4 and global alpha<=9.

No global bad-ten-set/maximal-clique condition is encoded.  A SAT model is
therefore an adversarial witness about the theory boundary, never a
counterexample to Erdos #151.  The script prints canonical JSON and does not
write files.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
import argparse
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[5]
BASE_CHECKER = (
    ROOT / "research" / "erdos151" / "general" / "checks"
    / "k4_fibre_attack" / "check_k4_fibre_attack.py"
)


def load_base():
    spec = importlib.util.spec_from_file_location("k4_fibre_base", BASE_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def edge(x, y):
    return (x, y) if x < y else (y, x)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-iterations", type=int)
    args = parser.parse_args()

    module = load_base()
    original_edges, _ = module.make_graph()
    fan_of = {v: c for c, fan in enumerate(module.FANS) for v in fan}

    # Retain U--U, within-fan, M, and M--own-fan edges.  Re-choose exactly
    # U--fan and different-fan pairs.
    fixed_edges = set()
    for pair in original_edges:
        x, y = pair
        if x in module.U and y in module.U:
            fixed_edges.add(pair)
        elif x in fan_of and y in fan_of and fan_of[x] == fan_of[y]:
            fixed_edges.add(pair)
        elif x in module.M or y in module.M:
            fixed_edges.add(pair)

    variable_pairs = []
    for u in module.U:
        for fan in module.FANS:
            for a in fan:
                variable_pairs.append(edge(u, a))
    for i, j in itertools.combinations(range(4), 2):
        for a in module.FANS[i]:
            for b in module.FANS[j]:
                variable_pairs.append(edge(a, b))
    variable_pairs = tuple(sorted(set(variable_pairs)))

    pool = IDPool()
    variable = {pair: pool.id(("edge",) + pair) for pair in variable_pairs}
    clauses = []

    def fixed_degree(v):
        return sum(v in pair for pair in fixed_edges)

    # Full degree interval.
    for v in range(module.N):
        incident = [lit for pair, lit in variable.items() if v in pair]
        low = max(0, 5 - fixed_degree(v))
        high = 9 - fixed_degree(v)
        assert high >= 0
        if low:
            clauses.extend(CardEnc.atleast(
                incident, bound=low, vpool=pool, encoding=EncType.seqcounter
            ).clauses)
        if len(incident) > high:
            clauses.extend(CardEnc.atmost(
                incident, bound=high, vpool=pool, encoding=EncType.seqcounter
            ).clauses)

    # Domination of U by each fan, plus the sharp saturated cut >=20.
    for fan in module.FANS:
        cut = []
        for u in module.U:
            row = [variable[edge(u, a)] for a in fan]
            clauses.append(row)
            cut.extend(row)
        clauses.extend(CardEnc.atleast(
            cut, bound=20, vpool=pool, encoding=EncType.seqcounter
        ).clauses)

    # Each residual is triangle-free.  The two fixed parts are already
    # triangle-free; only triangles using incidence variables are possible.
    for fan in module.FANS:
        for u, v in itertools.combinations(module.U, 2):
            if edge(u, v) in fixed_edges:
                for a in fan:
                    clauses.append([-variable[edge(u, a)], -variable[edge(v, a)]])
        for a, b in itertools.combinations(fan, 2):
            if edge(a, b) in fixed_edges:
                for u in module.U:
                    clauses.append([-variable[edge(u, a)], -variable[edge(u, b)]])

    # Exact singleton fibres: cap one per fan vertex, and require every such
    # U--fan edge to remain ambient-maximal.  Since each row is dominated,
    # 'u is singleton at a' is e(ua) and all five alternatives absent.
    for fan in module.FANS:
        for a in fan:
            for u, v in itertools.combinations(module.U, 2):
                clause = [-variable[edge(u, a)], -variable[edge(v, a)]]
                clause.extend(variable[edge(u, b)] for b in fan if b != a)
                clause.extend(variable[edge(v, b)] for b in fan if b != a)
                clauses.append(clause)

            for u in module.U:
                singleton_relax = [-variable[edge(u, a)]]
                singleton_relax.extend(variable[edge(u, b)] for b in fan if b != a)
                for w in range(module.N):
                    if w in (u, a):
                        continue
                    condition = list(singleton_relax)
                    possible = True
                    for pair in (edge(u, w), edge(a, w)):
                        if pair in fixed_edges:
                            continue
                        lit = variable.get(pair)
                        if lit is None:
                            possible = False
                            break
                        condition.append(-lit)
                    if possible:
                        clauses.append(condition)

    # Complete K5 clauses over fixed/variable edge semantics.
    k5_clauses = 0
    for vertices in itertools.combinations(range(module.N), 5):
        missing = []
        possible = True
        for x, y in itertools.combinations(vertices, 2):
            pair = edge(x, y)
            if pair in fixed_edges:
                continue
            lit = variable.get(pair)
            if lit is None:
                possible = False
                break
            missing.append(lit)
        if possible:
            assert missing
            clauses.append([-lit for lit in missing])
            k5_clauses += 1

    def adjacency_from_model(model):
        chosen = {pair for pair, lit in variable.items() if lit in model}
        edges = fixed_edges | chosen
        adjacency = [set() for _ in range(module.N)]
        for x, y in edges:
            adjacency[x].add(y)
            adjacency[y].add(x)
        return chosen, edges, adjacency

    def render_output(payload):
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        print(rendered, end="", flush=True)
        if args.output is not None:
            args.output.write_text(rendered, encoding="utf-8")

    def checkpoint_payload(chosen, edges, adjacency):
        canonical_edges = ";".join(f"{x}-{y}" for x, y in sorted(edges))
        incidence = sorted(
            pair for pair in chosen
            if (pair[0] in module.U) != (pair[1] in module.U)
        )
        cross = sorted(pair for pair in chosen if pair not in incidence)
        residual_witnesses = [
            module.max_independent_set(tuple(module.U) + tuple(fan), adjacency)
            for fan in module.FANS
        ]
        global_witness = module.max_independent_set(range(module.N), adjacency)
        return {
            "schema": "erdos151-order41-k4-incidence-coupling-status-v1",
            "status": "NO_CONCLUSION_ITERATION_LIMIT",
            "claim_boundary": (
                "No SAT or UNSAT conclusion. Every observed outer model was "
                "separated by an exact residual-7-set or global-10-set cut."
            ),
            "base_checker": str(BASE_CHECKER.relative_to(ROOT)).replace("\\", "/"),
            "base_checker_sha256": hashlib.sha256(BASE_CHECKER.read_bytes()).hexdigest(),
            "static_variables": pool.top,
            "static_clauses": len(clauses),
            "k5_static_clauses": k5_clauses,
            "sat_iterations": iterations,
            "residual_alpha_cuts": residual_cuts,
            "global_alpha_cuts": global_cuts,
            "last_model_edge_sha256": hashlib.sha256(canonical_edges.encode()).hexdigest(),
            "last_model_variable_edges": len(chosen),
            "last_model_incidence_edges": [list(pair) for pair in incidence],
            "last_model_cross_fan_edges": [list(pair) for pair in cross],
            "last_model_residual_alphas": [len(w) for w in residual_witnesses],
            "last_model_residual_alpha_witnesses": [list(w) for w in residual_witnesses],
            "last_model_global_alpha": len(global_witness),
            "last_model_global_alpha_witness": list(global_witness),
        }

    seen_residual_seeds = set()
    seen_global_tens = set()
    residual_cuts = 0
    global_cuts = 0
    iterations = 0
    print(
        f"static_ready clauses={len(clauses)} variables={pool.top} "
        f"k5={k5_clauses}",
        file=sys.stderr,
        flush=True,
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        # Start from the audited local abstraction.  This is only a polarity
        # hint; all constraints remain exact and every later model is checked.
        solver.set_phases([
            lit if pair in original_edges else -lit
            for pair, lit in variable.items()
        ])
        frozen_assignment = [
            lit if pair in original_edges else -lit
            for pair, lit in variable.items()
        ]
        if not solver.solve(assumptions=frozen_assignment):
            raise AssertionError("the audited frozen abstraction fails the static CNF")
        first_model = solver.get_model()
        while True:
            if first_model is not None:
                raw_model = first_model
                first_model = None
            else:
                if not solver.solve():
                    break
                raw_model = solver.get_model()
            iterations += 1
            if iterations == 1 or iterations % 1000 == 0:
                print(
                    f"iteration={iterations} residual_cuts={residual_cuts} "
                    f"global_cuts={global_cuts}",
                    file=sys.stderr,
                    flush=True,
                )
            model = {lit for lit in raw_model if lit > 0}
            chosen, edges, adjacency = adjacency_from_model(model)
            new_cuts = 0

            # Exact alpha(W_c)<=6 separation.
            for c, fan in enumerate(module.FANS):
                residual = tuple(module.U) + tuple(fan)
                independent = module.max_independent_set(residual, adjacency)
                if len(independent) <= 6:
                    continue
                for seven in itertools.combinations(independent, 7):
                    key = (c, tuple(seven))
                    if key in seen_residual_seeds:
                        continue
                    seen_residual_seeds.add(key)
                    cut = [
                        variable[pair]
                        for pair in map(lambda xy: edge(*xy), itertools.combinations(seven, 2))
                        if pair in variable
                    ]
                    if not cut:
                        print("UNSAT: frozen residual has an immutable independent 7-set", key)
                        return 1
                    solver.add_clause(cut)
                    residual_cuts += 1
                    new_cuts += 1

            if new_cuts:
                if args.max_iterations is not None and iterations >= args.max_iterations:
                    render_output(checkpoint_payload(chosen, edges, adjacency))
                    return 2
                continue

            # Exact global alpha<=9 separation.
            independent = module.max_independent_set(range(module.N), adjacency)
            if len(independent) > 9:
                for ten in itertools.combinations(independent, 10):
                    ten = tuple(ten)
                    if ten in seen_global_tens:
                        continue
                    seen_global_tens.add(ten)
                    cut = [
                        variable[pair]
                        for pair in map(lambda xy: edge(*xy), itertools.combinations(ten, 2))
                        if pair in variable
                    ]
                    if not cut:
                        print("UNSAT: immutable global independent 10-set", ten)
                        return 1
                    solver.add_clause(cut)
                    global_cuts += 1
                    new_cuts += 1
                assert new_cuts
                if args.max_iterations is not None and iterations >= args.max_iterations:
                    render_output(checkpoint_payload(chosen, edges, adjacency))
                    return 2
                continue

            incidence = sorted(
                pair for pair in chosen
                if (pair[0] in module.U) != (pair[1] in module.U)
            )
            cross = sorted(pair for pair in chosen if pair not in incidence)
            output = {
                "schema": "erdos151-order41-k4-incidence-coupling-v1",
                "claim_boundary": (
                    "four exact triangle-free residuals plus global alpha; "
                    "global beta<=9 is not encoded"
                ),
                "base_checker": str(BASE_CHECKER.relative_to(ROOT)).replace("\\", "/"),
                "base_checker_sha256": hashlib.sha256(BASE_CHECKER.read_bytes()).hexdigest(),
                "sat_iterations": iterations,
                "residual_alpha_cuts": residual_cuts,
                "global_alpha_cuts": global_cuts,
                "k5_static_clauses": k5_clauses,
                "incidence_edges": [list(pair) for pair in incidence],
                "cross_fan_edges": [list(pair) for pair in cross],
            }
            render_output(output)
            return 0

    print("UNSAT for the fixed U/fan incidence-coupling abstraction")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
