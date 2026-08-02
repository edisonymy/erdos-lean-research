"""Independent audits for search.py's centralizer and fixed=10 quotient scope."""

from __future__ import annotations

import itertools
import json
import math
import random
import sys
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
FIXED5 = HERE.parent / "order5_fixed5"
sys.path.insert(0, str(FIXED5))

from audit_small_quotient import (  # noqa: E402
    build_semantic_quotient,
    is_diameter2_critical,
)
from generate_cases import (  # noqa: E402
    N,
    TARGET_EDGES,
    add_weighted_exact,
    canonical_permutation,
    edge_orbits,
)
from search import centralizer_generators  # noqa: E402


def general_permutation(fixed: int, cycles: int) -> list[int]:
    n = fixed + 5 * cycles
    permutation = list(range(n))
    for cycle in range(cycles):
        start = fixed + 5 * cycle
        for offset in range(5):
            permutation[start + offset] = start + (offset + 1) % 5
    return permutation


def audit_centralizer() -> list[dict]:
    rows = []
    for fixed in (10, 15, 20):
        sigma = canonical_permutation(fixed)
        orbits = edge_orbits(fixed)
        edge_for_pair = {
            pair: variable
            for variable, orbit in enumerate(orbits, start=1)
            for pair in orbit
        }
        generators = centralizer_generators(fixed)
        for name, permutation in generators:
            if sorted(permutation) != list(range(N)):
                raise AssertionError((fixed, name, "not a permutation"))
            if any(
                permutation[sigma[v]] != sigma[permutation[v]] for v in range(N)
            ):
                raise AssertionError((fixed, name, "does not centralize sigma"))
            induced = []
            for orbit in orbits:
                image_variables = {
                    edge_for_pair[
                        tuple(sorted((permutation[u], permutation[v])))
                    ]
                    for u, v in orbit
                }
                if len(image_variables) != 1:
                    raise AssertionError((fixed, name, orbit, image_variables))
                induced.append(next(iter(image_variables)))
            if sorted(induced) != list(range(1, len(orbits) + 1)):
                raise AssertionError((fixed, name, "edge action is not bijective"))

        cycles = (N - fixed) // 5
        expected_generators = (fixed - 1) + (cycles - 1) + cycles
        if len(generators) != expected_generators:
            raise AssertionError((fixed, len(generators), expected_generators))
        histogram = {
            size: sum(len(orbit) == size for orbit in orbits)
            for size in sorted({len(orbit) for orbit in orbits})
        }
        expected_singletons = fixed * (fixed - 1) // 2
        expected_five = fixed * cycles + 2 * cycles + 5 * cycles * (cycles - 1) // 2
        if histogram != {1: expected_singletons, 5: expected_five}:
            raise AssertionError((fixed, histogram, expected_singletons, expected_five))
        rows.append(
            {
                "fixed": fixed,
                "cycles": cycles,
                "edge_orbits": len(orbits),
                "orbit_histogram": {str(k): v for k, v in histogram.items()},
                "generators": len(generators),
                "centralizer_order": math.factorial(fixed)
                * (5**cycles)
                * math.factorial(cycles),
            }
        )
    return rows


def audit_weighted_scope() -> list[dict]:
    rows = []
    for fixed in (10, 15, 20):
        orbits = edge_orbits(fixed)
        weights = [len(orbit) for orbit in orbits]
        variables = list(range(1, len(weights) + 1))
        singleton = [var for var, weight in zip(variables, weights) if weight == 1]
        five = [var for var, weight in zip(variables, weights) if weight == 5]
        formula = CNF()
        formula.nv = len(weights)
        add_weighted_exact(formula, variables, weights, TARGET_EDGES)
        checked = 0
        feasible = []
        with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
            for singleton_count in range(len(singleton) + 1):
                for five_count in range(len(five) + 1):
                    selected = set(singleton[:singleton_count] + five[:five_count])
                    assumptions = [
                        variable if variable in selected else -variable
                        for variable in variables
                    ]
                    encoded = solver.solve(assumptions=assumptions)
                    expected = singleton_count + 5 * five_count == TARGET_EDGES
                    if encoded != expected:
                        raise AssertionError(
                            (fixed, singleton_count, five_count, encoded, expected)
                        )
                    checked += 1
                    if expected:
                        feasible.append([singleton_count, five_count])
        rows.append(
            {
                "fixed": fixed,
                "count_pairs_checked": checked,
                "feasible_singleton_five_counts": feasible,
            }
        )
    return rows


def edge_assignment(
    orbits: list[list[tuple[int, int]]], selected: set[int]
) -> set[tuple[int, int]]:
    return {
        edge
        for variable, orbit in enumerate(orbits, start=1)
        if variable in selected
        for edge in orbit
    }


def compare_assignment(
    solver: Solver,
    n: int,
    orbits: list[list[tuple[int, int]]],
    selected: set[int],
) -> bool:
    assumptions = [
        variable if variable in selected else -variable
        for variable in range(1, len(orbits) + 1)
    ]
    encoded = solver.solve(assumptions=assumptions)
    direct = is_diameter2_critical(n, edge_assignment(orbits, selected))
    if encoded != direct:
        raise AssertionError(
            {
                "n": n,
                "selected_orbits": sorted(selected),
                "encoded": encoded,
                "direct": direct,
            }
        )
    return direct


def audit_two_cycle_quotients() -> list[dict]:
    rows = []
    for fixed in range(3):
        cycles = 2
        n = fixed + 5 * cycles
        permutation = general_permutation(fixed, cycles)
        formula, orbits = build_semantic_quotient(n, permutation)
        critical = 0
        with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
            for mask in range(1 << len(orbits)):
                selected = {
                    variable
                    for variable in range(1, len(orbits) + 1)
                    if mask >> (variable - 1) & 1
                }
                critical += int(compare_assignment(solver, n, orbits, selected))
        rows.append(
            {
                "n": n,
                "cycle_type": f"1^{fixed} 5^2",
                "edge_orbits": len(orbits),
                "invariant_graphs": 1 << len(orbits),
                "diameter2_critical_graphs": critical,
                "mismatches": 0,
            }
        )
    return rows


def audit_fixed10_three_cycles() -> dict:
    fixed, cycles = 10, 3
    n = fixed + 5 * cycles
    permutation = general_permutation(fixed, cycles)
    formula, orbits = build_semantic_quotient(n, permutation)
    edge_for_pair = {
        pair: variable
        for variable, orbit in enumerate(orbits, start=1)
        for pair in orbit
    }
    rng = random.Random(742_10_3)
    random_checks = 5000
    random_critical = 0
    bipartite_checks = 0
    direct_bipartition_sizes = set()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for _ in range(random_checks):
            selected = {
                variable
                for variable in range(1, len(orbits) + 1)
                if rng.getrandbits(1)
            }
            random_critical += int(compare_assignment(solver, n, orbits, selected))

        # Each of the 13 vertex orbits must lie wholly in one bipartition side.
        vertex_orbits = [[vertex] for vertex in range(fixed)] + [
            list(range(fixed + 5 * cycle, fixed + 5 * (cycle + 1)))
            for cycle in range(cycles)
        ]
        # Fix the first atom on side zero to remove complementary duplicates.
        for side_mask in range(1 << (len(vertex_orbits) - 1)):
            side = {vertex_orbits[0][0]}
            for index, orbit in enumerate(vertex_orbits[1:]):
                if side_mask >> index & 1:
                    side.update(orbit)
            if len(side) == n:
                continue
            selected = set()
            for u, v in itertools.combinations(range(n), 2):
                if (u in side) != (v in side):
                    selected.add(edge_for_pair[(u, v)])
            assumptions = [
                variable if variable in selected else -variable
                for variable in range(1, len(orbits) + 1)
            ]
            if not solver.solve(assumptions=assumptions):
                raise AssertionError(("complete bipartite rejected", sorted(side)))
            part_size = min(len(side), n - len(side))
            if part_size not in direct_bipartition_sizes:
                if not is_diameter2_critical(n, edge_assignment(orbits, selected)):
                    raise AssertionError(("direct bipartite check failed", sorted(side)))
                direct_bipartition_sizes.add(part_size)
            bipartite_checks += 1
    return {
        "n": n,
        "cycle_type": "1^10 5^3",
        "edge_orbits": len(orbits),
        "random_graphs": random_checks,
        "random_diameter2_critical_graphs": random_critical,
        "complete_bipartite_graphs": bipartite_checks,
        "direct_bipartite_part_sizes": sorted(direct_bipartition_sizes),
        "mismatches": 0,
    }


def main() -> None:
    result = {
        "status": "PASS",
        "centralizer": audit_centralizer(),
        "weighted_157_scope": audit_weighted_scope(),
        "exhaustive_two_cycle_quotients": audit_two_cycle_quotients(),
        "fixed10_three_cycle_quotient": audit_fixed10_three_cycles(),
        "fixed0_scope": (
            "cycle type 5^5 has only size-five edge orbits, so 157 edges is "
            "impossible modulo five"
        ),
        "claim_scope": (
            "implementation audit and finite falsification tests; not an UNSAT "
            "certificate and not a formal proof of the order-25 quotient encoder"
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
