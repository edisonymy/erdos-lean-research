#!/usr/bin/env python3
"""Exhaustive small-order audit of the standalone V1/TCG-3 separator."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from pysat.formula import IDPool
from pysat.solvers import Cadical195

from tcg3_separator import (
    find_triangle_free_two_partition,
    graph_triangles,
    internal_triples,
    partition_is_triangle_free,
    separator_stats,
    tcg3_cut,
)


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[int]:
    result = [0] * n
    for u, v in edges:
        result[u] |= 1 << v
        result[v] |= 1 << u
    return result


def brute_partition(adj: list[int]):
    n = len(adj)
    for mask in range(1 << max(0, n - 1)):
        side_one = tuple(v for v in range(1, n) if (mask >> (v - 1)) & 1)
        side_zero = tuple(v for v in range(n) if v not in side_one)
        if partition_is_triangle_free(adj, side_zero, side_one):
            return side_zero, side_one
    return None


def audit_v1_triangle_coloring() -> list[dict[str, object]]:
    records = []
    for sides in itertools.product((0, 1), repeat=3):
        edge_colors = [
            "red" if sides[u] != sides[v] else "blue"
            for u, v in itertools.combinations(range(3), 2)
        ]
        internal_triangle = len(set(sides)) == 1
        assert edge_colors.count("red") in (0, 2)
        assert (edge_colors.count("blue") == 3) == internal_triangle
        assert (edge_colors.count("blue") == 1) == (not internal_triangle)
        records.append(
            {
                "vertex_sides": sides,
                "edge_colors": edge_colors,
                "internal_triangle": internal_triangle,
            }
        )
    assert len(records) == 8
    return records


def audit_y_cut_semantics() -> dict[str, int]:
    n = 5
    edges = list(itertools.combinations(range(n), 2))
    checks = 0
    for partition_mask in range(1 << (n - 1)):
        side_one = tuple(v for v in range(1, n) if (partition_mask >> (v - 1)) & 1)
        side_zero = tuple(v for v in range(n) if v not in side_one)
        triples = internal_triples(side_zero, side_one)
        assert triples
        pool = IDPool()
        edge_vars = {edge: pool.id(("edge",) + edge) for edge in edges}
        solver = Cadical195()
        def triangle_var(triple):
            witness = pool.id(("triangle-witness",) + triple)
            for edge in itertools.combinations(triple, 2):
                solver.add_clause([-witness, edge_vars[tuple(sorted(edge))]])
            return witness

        witnesses = tcg3_cut(side_zero, side_one, triangle_var)
        assert len(witnesses) == len(triples)
        solver.add_clause(witnesses)
        for graph_mask in range(1 << len(edges)):
            graph_edges = {
                edge for index, edge in enumerate(edges) if (graph_mask >> index) & 1
            }
            assumptions = [
                edge_vars[edge] if edge in graph_edges else -edge_vars[edge]
                for edge in edges
            ]
            satisfiable = solver.solve(assumptions=assumptions)
            expected = any(
                all(tuple(sorted(edge)) in graph_edges for edge in itertools.combinations(triple, 2))
                for triple in triples
            )
            assert satisfiable == expected
            checks += 1
        solver.delete()
    return {"partitions": 1 << (n - 1), "graphs_per_partition": 1 << len(edges), "checks": checks}


def main() -> None:
    v1_records = audit_v1_triangle_coloring()
    n = 6
    edges = list(itertools.combinations(range(n), 2))
    partitionable = 0
    nonpartitionable = 0
    for graph_mask in range(1 << len(edges)):
        graph_edges = {
            edge for index, edge in enumerate(edges) if (graph_mask >> index) & 1
        }
        adj = adjacency(n, graph_edges)
        exact = find_triangle_free_two_partition(adj)
        brute = brute_partition(adj)
        assert (exact is None) == (brute is None)
        if exact is None:
            nonpartitionable += 1
        else:
            partitionable += 1
            assert partition_is_triangle_free(adj, *exact)

    cut_semantics = audit_y_cut_semantics()
    balanced_stats = separator_stats(tuple(range(25)), tuple(range(25, 50)))
    extreme_stats = separator_stats(tuple(range(50)), tuple())

    successor_path = Path(__file__).with_name("cegar_face_matching3.py")
    successor_source = successor_path.read_text(encoding="utf-8-sig")
    explicit_separator_absent = all(
        token not in successor_source
        for token in ("find_triangle_free_two_partition", "tcg3_cut")
    )
    assert explicit_separator_absent

    payload = {
        "schema": "erdos151-v1-tcg3-separator-audit-v1",
        "status": "PASS",
        "v1_triangle_side_assignments_checked": len(v1_records),
        "exhaustive_n6": {
            "graphs_checked": 1 << len(edges),
            "partitionable": partitionable,
            "nonpartitionable": nonpartitionable,
            "exact_oracle_agrees_with_bruteforce": True,
        },
        "y_witness_cut_semantics": {
            **cut_semantics,
            "result": (
                "with y_t -> all three edges, OR y_t is satisfiable under a "
                "fixed graph iff some internal triple is a triangle"
            ),
        },
        "production_order_cost_bounds": {
            "oracle_variables": 50,
            "oracle_clauses": "twice the actual triangle count, at most 39200",
            "balanced_partition": balanced_stats,
            "extreme_partition": extreme_stats,
            "incremental_cut_clauses": 1,
        },
        "matching3_successor_has_explicit_separator": not explicit_separator_absent,
        "assessment": (
            "sound and cheap enough for a later successor pilot; do not mutate "
            "or restart either live run"
        ),
        "claim_boundary": (
            "a found partition certifies non-arrowing and yields a sound cut; "
            "live order-50 behavior was not tested or inferred"
        ),
    }
    output = Path(__file__).with_name("audit_tcg3_separator.result.json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
