"""Exact V1/TCG-3 triangle-free two-partition separator.

This module is standalone and future-successor-only.  It does not modify the
two live CEGAR runs.  A returned partition is a positive certificate that the
model graph is not edge-arrowing (3,3).  Failure to find one is exact because
the oracle solves the triangle hypergraph's two-colorability CNF.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable

from pysat.solvers import Cadical195


def graph_triangles(adj: list[int]) -> list[tuple[int, int, int]]:
    n = len(adj)
    return [
        triple
        for triple in itertools.combinations(range(n), 3)
        if all((adj[u] >> v) & 1 for u, v in itertools.combinations(triple, 2))
    ]


def find_triangle_free_two_partition(
    adj: list[int],
) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    """Return an exact triangle-free bipartition, or ``None`` if none exists."""

    n = len(adj)
    triangles = graph_triangles(adj)
    with Cadical195() as solver:
        # Variable v+1 is the side of vertex v.  Fix vertex zero to break
        # global color-complement symmetry when the graph is nonempty.
        if n:
            solver.add_clause([-1])
        for a, b, c in triangles:
            variables = (a + 1, b + 1, c + 1)
            solver.add_clause(list(variables))
            solver.add_clause([-variable for variable in variables])
        if not solver.solve():
            return None
        positive = {literal for literal in solver.get_model() if literal > 0}
    side_one = tuple(v for v in range(n) if v + 1 in positive)
    side_zero = tuple(v for v in range(n) if v + 1 not in positive)
    assert partition_is_triangle_free(adj, side_zero, side_one)
    return side_zero, side_one


def partition_is_triangle_free(
    adj: list[int], side_zero: tuple[int, ...], side_one: tuple[int, ...]
) -> bool:
    for side in (side_zero, side_one):
        for a, b, c in itertools.combinations(side, 3):
            if all(
                (adj[u] >> v) & 1
                for u, v in itertools.combinations((a, b, c), 2)
            ):
                return False
    return True


def internal_triples(
    side_zero: tuple[int, ...], side_one: tuple[int, ...]
) -> list[tuple[int, int, int]]:
    """All triples that could become monochromatic for this fixed partition."""

    return list(itertools.combinations(side_zero, 3)) + list(
        itertools.combinations(side_one, 3)
    )


def tcg3_cut(
    side_zero: tuple[int, ...],
    side_one: tuple[int, ...],
    triangle_var: Callable[[tuple[int, int, int]], int],
) -> list[int]:
    """Return ``OR y_t`` over all triples internal to either fixed side."""

    triples = internal_triples(side_zero, side_one)
    if not triples:
        raise ValueError("partition has no internal triple")
    return [triangle_var(triple) for triple in triples]


def separator_stats(
    side_zero: tuple[int, ...], side_one: tuple[int, ...]
) -> dict[str, int]:
    length = len(internal_triples(side_zero, side_one))
    return {
        "side_zero": len(side_zero),
        "side_one": len(side_one),
        "cut_literals": length,
        "maximum_new_triangle_definition_clauses": 3 * length,
    }
