"""Adversarial search for a four-residual alpha-coupling.

This is deliberately *not* the whole-graph beta<=9 search.  It freezes the
41-vertex local abstraction from check_k4_fibre_attack.py and varies only the
216 possible edges between different singleton fans.  Every singleton-fibre
edge used in Lemma 2.2 must remain ambient-maximal.  Other initially maximal
U--fan edges may be destroyed, but the complete seeded-anchor property is
checked on a returned model and can then be promoted to a SAT constraint if
needed.

The SAT layer enforces the degree ceiling and omega<=4.  Exact independent
10-sets are separated lazily.  On success the script prints a canonical JSON
object; it does not write any file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import argparse
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[5]
BASE_CHECKER = (
    ROOT
    / "research"
    / "erdos151"
    / "general"
    / "checks"
    / "k4_fibre_attack"
    / "check_k4_fibre_attack.py"
)


def load_base():
    spec = importlib.util.spec_from_file_location("k4_fibre_base", BASE_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def edge(x, y):
    return (x, y) if x < y else (y, x)


def build_adjacency(base, chosen):
    adjacency = [set(neighbours) for neighbours in base]
    for x, y in chosen:
        adjacency[x].add(y)
        adjacency[y].add(x)
    return adjacency


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-degree", action="store_true")
    parser.add_argument("--no-k5", action="store_true")
    parser.add_argument("--allow-destroy-singletons", action="store_true")
    args = parser.parse_args()

    module = load_base()
    base_edges, base_adjacency = module.make_graph()
    core = set(module.U)

    protected_singletons = set()
    for fan in module.FANS:
        fan_set = set(fan)
        for u in module.U:
            neighbours = base_adjacency[u] & fan_set
            if len(neighbours) == 1:
                protected_singletons.add(edge(u, next(iter(neighbours))))

    all_cross_pairs = []
    allowed_pairs = []
    for i, j in itertools.combinations(range(4), 2):
        for x in module.FANS[i]:
            for y in module.FANS[j]:
                pair = edge(x, y)
                all_cross_pairs.append(pair)
                common_core = base_adjacency[x] & base_adjacency[y] & core
                destroys_singleton = any(
                    edge(u, x) in protected_singletons
                    or edge(u, y) in protected_singletons
                    for u in common_core
                )
                if args.allow_destroy_singletons or not destroys_singleton:
                    allowed_pairs.append(pair)

    pool = IDPool()
    variable = {pair: pool.id(("edge",) + pair) for pair in allowed_pairs}
    clauses = []

    # Each fan vertex may use only its remaining degree capacity.
    if not args.no_degree:
        for vertex in itertools.chain.from_iterable(module.FANS):
            incident = [lit for pair, lit in variable.items() if vertex in pair]
            capacity = 9 - len(base_adjacency[vertex])
            if len(incident) > capacity:
                clauses.extend(
                    CardEnc.atmost(
                        incident,
                        bound=capacity,
                        vpool=pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )

    # Complete K5 separation is small enough to generate up front.
    k5_clauses = 0
    if not args.no_k5:
        for vertices in itertools.combinations(range(module.N), 5):
            missing = []
            possible = True
            for x, y in itertools.combinations(vertices, 2):
                pair = edge(x, y)
                if pair in base_edges:
                    continue
                lit = variable.get(pair)
                if lit is None:
                    possible = False
                    break
                missing.append(lit)
            if possible:
                assert missing, "the frozen base unexpectedly contains a K5"
                clauses.append([-lit for lit in missing])
                k5_clauses += 1

    seen_independent_tens = set()
    iterations = 0
    alpha_cuts = 0
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        while solver.solve():
            iterations += 1
            model = set(lit for lit in solver.get_model() if lit > 0)
            chosen = tuple(sorted(pair for pair, lit in variable.items() if lit in model))
            adjacency = build_adjacency(base_adjacency, chosen)
            independent = module.max_independent_set(range(module.N), adjacency)
            if len(independent) <= 9:
                output = {
                    "schema": "erdos151-order41-k4-global-coupling-v1",
                    "claim_boundary": (
                        "fixed local abstraction plus cross-fan edges; alpha<=9, "
                        "not beta<=9 and not a counterexample"
                    ),
                    "search_flags": vars(args),
                    "base_checker": str(BASE_CHECKER.relative_to(ROOT)).replace("\\", "/"),
                    "base_checker_sha256": hashlib.sha256(BASE_CHECKER.read_bytes()).hexdigest(),
                    "allowed_cross_pair_rule": (
                        "different singleton fans and preserves every frozen "
                        "singleton-fibre ambient-maximal edge"
                    ),
                    "protected_singleton_edges": [
                        list(pair) for pair in sorted(protected_singletons)
                    ],
                    "all_cross_pairs": len(all_cross_pairs),
                    "allowed_cross_pairs": len(allowed_pairs),
                    "k5_static_clauses": k5_clauses,
                    "sat_iterations": iterations,
                    "independent_ten_cuts": alpha_cuts,
                    "cross_edges": [list(pair) for pair in chosen],
                }
                print(json.dumps(output, indent=2, sort_keys=True))
                return 0

            # Every ten-subset of the exact independent set needs a cross edge.
            new_cuts = 0
            for ten in itertools.combinations(independent, 10):
                ten = tuple(ten)
                if ten in seen_independent_tens:
                    continue
                seen_independent_tens.add(ten)
                cut = [
                    variable[pair]
                    for pair in map(lambda xy: edge(*xy), itertools.combinations(ten, 2))
                    if pair in variable
                ]
                if not cut:
                    print("UNSAT: a frozen independent ten-set has no allowed cross pair")
                    print(ten)
                    return 1
                solver.add_clause(cut)
                alpha_cuts += 1
                new_cuts += 1
            assert new_cuts

    print("UNSAT under the singleton-fibre-edge preservation abstraction")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
