"""Independent finite audits for the order-five symmetry reduction."""

from __future__ import annotations

import itertools
import json

from pysat.formula import CNF
from pysat.solvers import Solver

from generate_cases import (
    N,
    add_lex_leader,
    add_weighted_atmost,
    add_weighted_exact,
    canonical_permutation,
    edge_orbits,
    edge_pairs,
)


def relabel(
    edges: frozenset[tuple[int, int]], permutation: tuple[int, ...]
) -> frozenset[tuple[int, int]]:
    return frozenset(
        tuple(sorted((permutation[u], permutation[v]))) for u, v in edges
    )


def canonical(edges: frozenset[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return min(
        tuple(sorted(relabel(edges, permutation)))
        for permutation in itertools.permutations(range(5))
    )


def audit_fixed_graph_classification() -> dict:
    pairs = [pair for _, pair in edge_pairs(5)]
    all_pairs = frozenset(pairs)
    representatives = {
        2: {
            canonical(frozenset({(0, 1), (1, 2)})),
            canonical(frozenset({(0, 1), (2, 3)})),
        },
        7: {
            canonical(all_pairs - frozenset({(0, 1), (0, 2), (1, 2)})),
            canonical(all_pairs - frozenset({(0, 1), (0, 2), (0, 3)})),
            canonical(all_pairs - frozenset({(0, 1), (1, 2), (2, 3)})),
            canonical(all_pairs - frozenset({(0, 1), (1, 2), (3, 4)})),
        },
    }
    counts = {}
    for edge_count, expected in representatives.items():
        observed = {
            canonical(frozenset(subset))
            for subset in itertools.combinations(pairs, edge_count)
        }
        if observed != expected:
            raise AssertionError((edge_count, observed, expected))
        counts[str(edge_count)] = {
            "labelled_graphs": len(list(itertools.combinations(pairs, edge_count))),
            "isomorphism_classes": len(observed),
        }
    return counts


def audit_edge_orbits() -> dict:
    permutation = canonical_permutation(5)
    orbits = edge_orbits(5)
    flattened = [pair for orbit in orbits for pair in orbit]
    expected = [pair for _, pair in edge_pairs(N)]
    if sorted(flattened) != expected or len(flattened) != len(set(flattened)):
        raise AssertionError("edge orbits do not partition all unordered pairs")
    for orbit in orbits:
        image = {
            tuple(sorted((permutation[u], permutation[v]))) for u, v in orbit
        }
        if image != set(orbit):
            raise AssertionError((orbit, image))
    histogram = {
        size: sum(len(orbit) == size for orbit in orbits)
        for size in sorted({len(orbit) for orbit in orbits})
    }
    if histogram != {1: 10, 5: 58}:
        raise AssertionError(histogram)
    return {
        "orbits": len(orbits),
        "histogram": {str(key): value for key, value in histogram.items()},
        "covered_edges": len(flattened),
    }


def assumptions(bits: tuple[int, ...], offset: int = 0) -> list[int]:
    return [offset + index + 1 if bit else -(offset + index + 1) for index, bit in enumerate(bits)]


def audit_lex_encoder() -> dict:
    assignments = 0
    for width in range(1, 5):
        formula = CNF()
        formula.nv = 2 * width
        left = list(range(1, width + 1))
        right = list(range(width + 1, 2 * width + 1))
        add_lex_leader(formula, left, right)
        with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
            for left_bits in itertools.product((0, 1), repeat=width):
                for right_bits in itertools.product((0, 1), repeat=width):
                    result = solver.solve(
                        assumptions=assumptions(left_bits)
                        + assumptions(right_bits, offset=width)
                    )
                    expected = left_bits <= right_bits
                    if result != expected:
                        raise AssertionError((width, left_bits, right_bits, result))
                    assignments += 1
    return {"widths": [1, 2, 3, 4], "assignments": assignments}


def audit_weighted_encoders() -> dict:
    weights = [1, 2, 3, 5]
    equality_checks = 0
    atmost_checks = 0
    for bound in range(sum(weights) + 1):
        for mode in ("equals", "atmost"):
            formula = CNF()
            formula.nv = len(weights)
            if mode == "equals":
                add_weighted_exact(formula, list(range(1, 5)), weights, bound)
            else:
                add_weighted_atmost(formula, list(range(1, 5)), weights, bound)
            with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
                for bits in itertools.product((0, 1), repeat=len(weights)):
                    total = sum(weight * bit for weight, bit in zip(weights, bits))
                    result = solver.solve(assumptions=assumptions(bits))
                    expected = total == bound if mode == "equals" else total <= bound
                    if result != expected:
                        raise AssertionError((mode, bound, bits, total, result))
                    if mode == "equals":
                        equality_checks += 1
                    else:
                        atmost_checks += 1
    return {
        "weights": weights,
        "equality_assignments": equality_checks,
        "atmost_assignments": atmost_checks,
    }


def main() -> None:
    result = {
        "status": "PASS",
        "edge_orbits": audit_edge_orbits(),
        "fixed_graph_classification": audit_fixed_graph_classification(),
        "lex_encoder": audit_lex_encoder(),
        "weighted_encoders": audit_weighted_encoders(),
        "claim_scope": (
            "finite audits of orbit arithmetic, the six fixed-graph classes, "
            "and custom CNF helpers; semantic D2C witness equivalence is audited "
            "separately by ../audit_witness_counts.py"
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
