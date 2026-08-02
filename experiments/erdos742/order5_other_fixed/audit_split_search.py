"""Independent audit of the order-25 split cardinality search.

It checks the split arithmetic, the unchanged non-cardinality prefix, the two
competing cardinality projections, centralizer lex semantics, and production
CNF semantics under fully fixed random primary assignments.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[3]
OTHER = ROOT / "experiments" / "erdos742" / "order5_other_fixed"
FIXED5 = ROOT / "experiments" / "erdos742" / "order5_fixed5"
sys.path.insert(0, str(OTHER))
sys.path.insert(0, str(FIXED5))

from audit_small_quotient import is_diameter2_critical  # noqa: E402
from generate_cases import (  # noqa: E402
    N,
    TARGET_EDGES,
    add_weighted_exact,
    build_formula,
    edge_orbits,
)
from search import add_centralizer_lex, centralizer_generators  # noqa: E402
from search_split_case import feasible_fixed_edge_counts  # noqa: E402


def digest_clauses(clauses: list[list[int]]) -> str:
    h = hashlib.sha256()
    for clause in clauses:
        h.update(" ".join(map(str, clause)).encode("ascii"))
        h.update(b" 0\n")
    return h.hexdigest()


def orbit_data(fixed: int):
    orbits = edge_orbits(fixed)
    fixed_vars = [i for i, orbit in enumerate(orbits, 1) if len(orbit) == 1]
    moving_vars = [i for i, orbit in enumerate(orbits, 1) if len(orbit) == 5]
    return orbits, fixed_vars, moving_vars


def assumptions(primary_count: int, selected: set[int]) -> list[int]:
    return [i if i in selected else -i for i in range(1, primary_count + 1)]


def direct_edges(orbits, selected: set[int]) -> set[tuple[int, int]]:
    return {
        pair
        for variable, orbit in enumerate(orbits, 1)
        if variable in selected
        for pair in orbit
    }


def direct_no_dominating_edge(edges: set[tuple[int, int]]) -> bool:
    adjacency = [set() for _ in range(N)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return all(
        any(w not in adjacency[u] and w not in adjacency[v]
            for w in range(N) if w not in (u, v))
        for u, v in edges
    )


def direct_max_degree(edges: set[tuple[int, int]], bound: int = 17) -> bool:
    degrees = [0] * N
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
    return max(degrees, default=0) <= bound


def induced_primary_image(fixed: int, permutation: list[int]) -> list[int]:
    orbits = edge_orbits(fixed)
    edge_for_pair = {
        pair: variable
        for variable, orbit in enumerate(orbits, 1)
        for pair in orbit
    }
    image = []
    for orbit in orbits:
        u, v = orbit[0]
        image.append(edge_for_pair[tuple(sorted((permutation[u], permutation[v])))])
    return image


def direct_lex_ok(fixed: int, selected: set[int]) -> bool:
    primary = tuple(i in selected for i in range(1, len(edge_orbits(fixed)) + 1))
    for _, permutation in centralizer_generators(fixed):
        image_map = induced_primary_image(fixed, permutation)
        image = tuple(i in selected for i in image_map)
        if primary > image:
            return False
    return True


def audit_partition(fixed: int) -> dict:
    _, fixed_vars, moving_vars = orbit_data(fixed)
    expected_pairs = [
        [t, q]
        for t in range(len(fixed_vars) + 1)
        for q in range(len(moving_vars) + 1)
        if t + 5 * q == TARGET_EDGES
    ]
    actual = feasible_fixed_edge_counts(fixed)
    actual_pairs = [[t, (TARGET_EDGES - t) // 5] for t in actual]
    if actual_pairs != expected_pairs:
        raise AssertionError((fixed, actual_pairs, expected_pairs))
    return {
        "fixed": fixed,
        "singleton_orbits": len(fixed_vars),
        "moving_orbits": len(moving_vars),
        "feasible_fixed_edge_counts": actual,
        "feasible_pairs": actual_pairs,
        "cases": len(actual),
    }


def audit_unchanged_prefix(fixed: int, split_t: int) -> dict:
    mono, mono_meta = build_formula(
        fixed,
        quotient=True,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )
    split, split_meta = build_formula(
        fixed,
        quotient=True,
        fixed_edge_count=split_t,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )
    mono_prefix = mono.clauses[: -mono_meta["cardinality_clauses"]]
    split_prefix = split.clauses[: -split_meta["cardinality_clauses"]]
    if mono_prefix != split_prefix:
        raise AssertionError((fixed, "non-cardinality prefixes differ"))
    mono_prefix_nv = mono.nv - mono_meta["cardinality_variables"]
    split_prefix_nv = split.nv - split_meta["cardinality_variables"]
    if mono_prefix_nv != split_prefix_nv:
        raise AssertionError((fixed, mono_prefix_nv, split_prefix_nv))
    return {
        "fixed": fixed,
        "selected_t": split_t,
        "prefix_variables": mono_prefix_nv,
        "prefix_clauses": len(mono_prefix),
        "prefix_sha256": digest_clauses(mono_prefix),
        "monolithic_cardinality": {
            "variables": mono_meta["cardinality_variables"],
            "clauses": mono_meta["cardinality_clauses"],
        },
        "split_cardinality": {
            "variables": split_meta["cardinality_variables"],
            "clauses": split_meta["cardinality_clauses"],
            "case": split_meta["cardinality_case"],
        },
    }


def audit_cardinality_projection(fixed: int, split_t: int) -> dict:
    orbits, fixed_vars, moving_vars = orbit_data(fixed)
    primary = list(range(1, len(orbits) + 1))
    weights = [len(orbit) for orbit in orbits]
    split_q = (TARGET_EDGES - split_t) // 5

    mono = CNF()
    mono.nv = len(primary)
    add_weighted_exact(mono, primary, weights, TARGET_EDGES)

    split = CNF()
    split.nv = len(primary)
    for lits, bound in ((fixed_vars, split_t), (moving_vars, split_q)):
        encoded = CardEnc.equals(
            lits=lits,
            bound=bound,
            top_id=split.nv,
            encoding=EncType.seqcounter,
        )
        split.extend(encoded.clauses)

    checked = 0
    mono_true = 0
    split_true = 0
    with Solver(name="cadical195", bootstrap_with=mono.clauses) as mono_solver, Solver(
        name="cadical195", bootstrap_with=split.clauses
    ) as split_solver:
        for t in range(len(fixed_vars) + 1):
            for q in range(len(moving_vars) + 1):
                selected = set(fixed_vars[:t] + moving_vars[:q])
                assumps = assumptions(len(primary), selected)
                mono_sat = mono_solver.solve(assumptions=assumps)
                split_sat = split_solver.solve(assumptions=assumps)
                expected_mono = t + 5 * q == TARGET_EDGES
                expected_split = expected_mono and t == split_t
                if mono_sat != expected_mono or split_sat != expected_split:
                    raise AssertionError(
                        (fixed, t, q, mono_sat, split_sat, expected_mono, expected_split)
                    )
                checked += 1
                mono_true += int(mono_sat)
                split_true += int(split_sat)
    return {
        "fixed": fixed,
        "selected_t": split_t,
        "selected_q": split_q,
        "count_pairs_checked": checked,
        "monolithic_true_pairs": mono_true,
        "split_true_pairs": split_true,
        "mismatches": 0,
    }


def audit_centralizer_lex(fixed: int, checks: int = 500) -> dict:
    orbits, fixed_vars, moving_vars = orbit_data(fixed)
    primary_count = len(orbits)
    formula = CNF()
    formula.nv = primary_count
    add_centralizer_lex(formula, fixed)

    # Every generator must preserve both cardinality blocks, or per-slice lex
    # leaders would not be a sound symmetry restriction.
    fixed_set, moving_set = set(fixed_vars), set(moving_vars)
    for name, permutation in centralizer_generators(fixed):
        image = induced_primary_image(fixed, permutation)
        if {image[i - 1] for i in fixed_vars} != fixed_set:
            raise AssertionError((fixed, name, "does not preserve singleton block"))
        if {image[i - 1] for i in moving_vars} != moving_set:
            raise AssertionError((fixed, name, "does not preserve moving block"))

    rng = random.Random(742_9000 + fixed)
    accepted = 0
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for _ in range(checks):
            selected = {i for i in range(1, primary_count + 1) if rng.getrandbits(1)}
            encoded = solver.solve(assumptions=assumptions(primary_count, selected))
            direct = direct_lex_ok(fixed, selected)
            if encoded != direct:
                raise AssertionError((fixed, sorted(selected), encoded, direct))
            accepted += int(encoded)
    return {
        "fixed": fixed,
        "generators": len(centralizer_generators(fixed)),
        "random_assignments": checks,
        "lex_accepted": accepted,
        "mismatches": 0,
    }


def audit_production_assignments(fixed: int, split_t: int, checks: int = 30) -> dict:
    orbits, fixed_vars, moving_vars = orbit_data(fixed)
    primary_count = len(orbits)
    split_q = (TARGET_EDGES - split_t) // 5
    mono, _ = build_formula(
        fixed,
        quotient=True,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )
    split, _ = build_formula(
        fixed,
        quotient=True,
        fixed_edge_count=split_t,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )

    rng = random.Random(742_10000 + fixed)
    assignments_to_check: list[set[int]] = []
    for index in range(checks):
        if index < checks // 2:
            t, q = split_t, split_q
        elif index < 3 * checks // 4:
            t = max(0, min(len(fixed_vars), split_t + rng.choice((-2, -1, 1, 2))))
            q = split_q
        else:
            t = rng.randrange(len(fixed_vars) + 1)
            q = rng.randrange(len(moving_vars) + 1)
        assignments_to_check.append(
            set(rng.sample(fixed_vars, t) + rng.sample(moving_vars, q))
        )

    mono_true = split_true = direct_critical = 0
    with Solver(name="cadical195", bootstrap_with=mono.clauses) as mono_solver, Solver(
        name="cadical195", bootstrap_with=split.clauses
    ) as split_solver:
        for selected in assignments_to_check:
            assumps = assumptions(primary_count, selected)
            mono_sat = mono_solver.solve(assumptions=assumps)
            split_sat = split_solver.solve(assumptions=assumps)
            edges = direct_edges(orbits, selected)
            core = (
                is_diameter2_critical(N, edges)
                and direct_max_degree(edges)
                and direct_no_dominating_edge(edges)
            )
            t = len(selected & set(fixed_vars))
            q = len(selected & set(moving_vars))
            expected_mono = core and t + 5 * q == TARGET_EDGES
            expected_split = expected_mono and t == split_t
            if mono_sat != expected_mono or split_sat != expected_split:
                raise AssertionError(
                    {
                        "fixed": fixed,
                        "t": t,
                        "q": q,
                        "mono": mono_sat,
                        "split": split_sat,
                        "expected_mono": expected_mono,
                        "expected_split": expected_split,
                    }
                )
            mono_true += int(mono_sat)
            split_true += int(split_sat)
            direct_critical += int(core)
    return {
        "fixed": fixed,
        "selected_t": split_t,
        "selected_q": split_q,
        "fully_fixed_assignments": checks,
        "direct_core_true": direct_critical,
        "monolithic_true": mono_true,
        "split_true": split_true,
        "mismatches": 0,
    }


def main() -> None:
    cases = ((15, 57), (20, 97))
    result = {
        "schema": "erdos742-split-independent-audit-v1",
        "status": "PASS",
        "partition": [audit_partition(fixed) for fixed, _ in cases],
        "unchanged_prefix": [
            audit_unchanged_prefix(fixed, split_t) for fixed, split_t in cases
        ],
        "cardinality_projection": [
            audit_cardinality_projection(fixed, split_t) for fixed, split_t in cases
        ],
        "centralizer_lex": [audit_centralizer_lex(fixed) for fixed, _ in cases],
        "production_assignment_semantics": [
            audit_production_assignments(fixed, split_t) for fixed, split_t in cases
        ],
        "claim_scope": (
            "Independent arithmetic and implementation-semantic audit; random "
            "assignment tests are falsification tests, not a formal proof of the "
            "entire production encoding."
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
