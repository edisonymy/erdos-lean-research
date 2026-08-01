#!/usr/bin/env python3
"""Small-model and model-lifting audit for the order-16 cross search.

This is not an order-16 UNSAT proof.  It exhaustively checks the logical
building blocks on small graphs, checks every maximum independent set of the
three Ramsey(3,4,8) catalogue graphs, and normalizes a deterministic order-16
maximal triangle-free graph with alpha=6 as a concrete symmetry-lifting test.
"""

from __future__ import annotations

import itertools
import json
import random

import z3
from pysat.formula import CNFPlus, IDPool
from pysat.solvers import Solver

from check_g6_family import decode_graph6


Edge = tuple[int, int]


def pairs(n: int) -> list[Edge]:
    return list(itertools.combinations(range(n), 2))


def has_edge(edges: set[Edge], i: int, j: int) -> bool:
    return tuple(sorted((i, j))) in edges


def triangle_free(n: int, edges: set[Edge]) -> bool:
    return not any(
        all(has_edge(edges, i, j) for i, j in itertools.combinations(triple, 2))
        for triple in itertools.combinations(range(n), 3)
    )


def maximal_triangle_free(n: int, edges: set[Edge]) -> bool:
    return triangle_free(n, edges) and all(
        has_edge(edges, i, j)
        or any(
            has_edge(edges, i, k) and has_edge(edges, j, k)
            for k in range(n)
            if k not in (i, j)
        )
        for i, j in pairs(n)
    )


def greedy_maximal_extension(n: int, edges: set[Edge]) -> set[Edge]:
    result = set(edges)
    for i, j in pairs(n):
        if (i, j) in result:
            continue
        if not any(
            has_edge(result, i, k) and has_edge(result, j, k)
            for k in range(n)
            if k not in (i, j)
        ):
            result.add((i, j))
    return result


def independent_sets_of_maximum_size(n: int, edges: set[Edge]) -> list[tuple[int, ...]]:
    for size in range(n, -1, -1):
        found = [
            subset
            for subset in itertools.combinations(range(n), size)
            if not any(has_edge(edges, i, j) for i, j in itertools.combinations(subset, 2))
        ]
        if found:
            return found
    raise AssertionError("the empty set always exists")


def induced_edge_count(edges: set[Edge], subset: tuple[int, ...]) -> int:
    return sum(has_edge(edges, i, j) for i, j in itertools.combinations(subset, 2))


def normalize_cross_symmetry(
    n: int, edges: set[Edge], independent: tuple[int, ...]
) -> tuple[set[Edge], dict[str, object]]:
    """Relabel one maximum independent set exactly as z3_cross_search does."""
    independent_set = set(independent)
    outside = [v for v in range(n) if v not in independent_set]
    s = len(independent)
    if not outside:
        return set(edges), {"permutation": list(range(n)), "cross_degree": None, "codes": []}

    cross_degree = {
        v: sum(has_edge(edges, i, v) for i in independent)
        for v in outside
    }
    chosen = min(outside, key=lambda v: (cross_degree[v], v))
    ordered_i = sorted(i for i in independent if has_edge(edges, i, chosen))
    ordered_i += sorted(i for i in independent if not has_edge(edges, i, chosen))
    old_to_new = {old: new for new, old in enumerate(ordered_i)}
    old_to_new[chosen] = s

    def code(v: int) -> int:
        return sum(
            (1 << old_to_new[i])
            for i in independent
            if has_edge(edges, i, v)
        )

    remaining = sorted((v for v in outside if v != chosen), key=lambda v: (code(v), v))
    for new, old in enumerate(remaining, start=s + 1):
        old_to_new[old] = new
    assert set(old_to_new) == set(range(n))
    transformed = {
        tuple(sorted((old_to_new[i], old_to_new[j])))
        for i, j in edges
    }

    d = cross_degree[chosen]
    new_i = range(s)
    assert all(not has_edge(transformed, i, j) for i, j in itertools.combinations(new_i, 2))
    assert [has_edge(transformed, i, s) for i in new_i] == [i < d for i in new_i]
    assert all(
        sum(has_edge(transformed, i, v) for i in new_i) >= d
        for v in range(s, n)
    )
    codes = [
        sum((1 << i) for i in new_i if has_edge(transformed, i, v))
        for v in range(s + 1, n)
    ]
    assert codes == sorted(codes)
    # The relabelling is a literal graph isomorphism, not just an invariant
    # comparison.
    assert transformed == {
        tuple(sorted((old_to_new[i], old_to_new[j]))) for i, j in edges
    }
    return transformed, {
        "permutation": [old_to_new[i] for i in range(n)],
        "cross_degree": d,
        "codes": codes,
    }


def audit_native_cardinality() -> int:
    checks = 0
    for width in range(1, 7):
        for bound in range(width + 1):
            zvars = [z3.Bool(f"audit_{width}_{bound}_{i}") for i in range(width)]
            zformula = z3.PbGe([(var, 1) for var in zvars], bound)
            cnf = CNFPlus()
            cnf.append([[-(i + 1) for i in range(width)], width - bound], is_atmost=True)
            with Solver(name="minicard", bootstrap_with=cnf) as solver:
                for assignment in itertools.product((False, True), repeat=width):
                    expected = sum(assignment) >= bound
                    substituted = z3.simplify(
                        z3.substitute(
                            zformula,
                            *((var, z3.BoolVal(value)) for var, value in zip(zvars, assignment)),
                        )
                    )
                    assert z3.is_true(substituted) == expected
                    assumptions = [i + 1 if value else -(i + 1) for i, value in enumerate(assignment)]
                    assert solver.solve(assumptions=assumptions) == expected
                    checks += 2
    return checks


def audit_maximality_witness_encoding() -> int:
    checks = 0
    for n in range(2, 6):
        pool = IDPool()
        edge_vars = {pair: pool.id(("edge", *pair)) for pair in pairs(n)}
        formula = CNFPlus()
        for i, j in pairs(n):
            witnesses = []
            for k in range(n):
                if k in (i, j):
                    continue
                witness = pool.id(("common", i, j, k))
                witnesses.append(witness)
                formula.append([-witness, edge_vars[tuple(sorted((i, k)))]] )
                formula.append([-witness, edge_vars[tuple(sorted((j, k)))]] )
            formula.append([edge_vars[i, j], *witnesses])
        with Solver(name="minicard", bootstrap_with=formula) as solver:
            edge_list = pairs(n)
            for mask in range(1 << len(edge_list)):
                edges = {edge for bit, edge in enumerate(edge_list) if mask >> bit & 1}
                assumptions = [
                    edge_vars[e] if e in edges else -edge_vars[e]
                    for e in edge_list
                ]
                expected = all(
                    has_edge(edges, i, j)
                    or any(
                        has_edge(edges, i, k) and has_edge(edges, j, k)
                        for k in range(n)
                        if k not in (i, j)
                    )
                    for i, j in edge_list
                )
                assert solver.solve(assumptions=assumptions) == expected
                checks += 1
    return checks


def audit_all_labelled_graphs_through_six() -> dict[str, int]:
    graphs = 0
    triangle_free_graphs = 0
    maximal_extensions = 0
    normalized_maximum_sets = 0
    for n in range(7):
        edge_list = pairs(n)
        for mask in range(1 << len(edge_list)):
            graphs += 1
            edges = {edge for bit, edge in enumerate(edge_list) if mask >> bit & 1}
            if not triangle_free(n, edges):
                continue
            triangle_free_graphs += 1
            extension = greedy_maximal_extension(n, edges)
            assert edges <= extension
            assert maximal_triangle_free(n, extension)
            original_maximum = independent_sets_of_maximum_size(n, edges)[0]
            extension_maximum = independent_sets_of_maximum_size(n, extension)[0]
            assert len(extension_maximum) <= len(original_maximum)
            for size in range(n + 1):
                for subset in itertools.combinations(range(n), size):
                    assert induced_edge_count(extension, subset) >= induced_edge_count(edges, subset)
            maximal_extensions += 1

            maximum_sets = independent_sets_of_maximum_size(n, edges)
            for independent in maximum_sets:
                transformed, _ = normalize_cross_symmetry(n, edges, independent)
                assert triangle_free(n, transformed) == triangle_free(n, edges)
                assert len(independent_sets_of_maximum_size(n, transformed)[0]) == len(independent)
                normalized_maximum_sets += 1
    return {
        "all_labelled_graphs": graphs,
        "triangle_free_graphs": triangle_free_graphs,
        "maximal_extensions": maximal_extensions,
        "normalized_maximum_independent_sets": normalized_maximum_sets,
    }


def audit_ramsey_348() -> dict[str, int]:
    records = [line for line in open("experiments/erdos128/r34_8.g6", "rb").read().splitlines() if line]
    maximum_sets = 0
    for record in records:
        n, edges = decode_graph6(record)
        assert n == 8 and triangle_free(n, edges)
        independent_sets = independent_sets_of_maximum_size(n, edges)
        assert len(independent_sets[0]) == 3
        for independent in independent_sets:
            transformed, metadata = normalize_cross_symmetry(n, edges, independent)
            # Here |O|=5 > alpha=3.  The exact d-bound argument used at n=16
            # gives d <= floor(alpha/2)=1.
            assert metadata["cross_degree"] == 1
            assert len(independent_sets_of_maximum_size(n, transformed)[0]) == 3
            maximum_sets += 1
    return {"records": len(records), "normalized_maximum_independent_sets": maximum_sets}


def order16_fixture() -> dict[str, object]:
    n = 16
    edge_order = pairs(n)
    random.Random(0).shuffle(edge_order)
    edges: set[Edge] = set()
    for i, j in edge_order:
        if not any(
            has_edge(edges, i, k) and has_edge(edges, j, k)
            for k in range(n)
            if k not in (i, j)
        ):
            edges.add((i, j))
    assert maximal_triangle_free(n, edges)
    independent_sets = independent_sets_of_maximum_size(n, edges)
    assert len(independent_sets[0]) == 6
    transformed, metadata = normalize_cross_symmetry(n, edges, independent_sets[0])
    assert maximal_triangle_free(n, transformed)
    assert len(independent_sets_of_maximum_size(n, transformed)[0]) == 6
    d = metadata["cross_degree"]
    assert isinstance(d, int) and 1 <= d <= 3
    minimum_half_edges = min(
        induced_edge_count(transformed, subset)
        for subset in itertools.combinations(range(n), n // 2)
    )
    # The fixture is only a lifting test, not a counterexample.
    assert minimum_half_edges < 6
    return {
        "seed": 0,
        "edges": len(edges),
        "alpha": 6,
        "chosen_independent_set": list(independent_sets[0]),
        "normalized_cross_degree": d,
        "sorted_cross_codes": metadata["codes"],
        "minimum_half_edges": minimum_half_edges,
    }


def main() -> int:
    payload = {
        "result": "pass",
        "native_cardinality_assignment_checks": audit_native_cardinality(),
        "maximality_witness_assignment_checks": audit_maximality_witness_encoding(),
        "small_graphs": audit_all_labelled_graphs_through_six(),
        "ramsey_3_4_8": audit_ramsey_348(),
        "order16_model_lifting_fixture": order16_fixture(),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
