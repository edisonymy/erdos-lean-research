#!/usr/bin/env python3
"""Exact lazy-SMT probe of the finite d=2a+4 incidence skeletons.

This is exploratory computation.  A UNSAT result is not promoted to a mathematical
proof; it is intended to expose the short dyadic obstruction in each finite case.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import z3


Edge = tuple[int, int]


@dataclass(frozen=True)
class Case:
    name: str
    a: int
    j_edges: tuple[Edge, ...]
    d0: int


CASES = (
    Case("a1_empty_d0_2", 1, (), 2),
    Case("a2_empty_d0_0", 2, (), 0),
    Case("a2_edge_d0_1", 2, ((0, 1),), 1),
    Case("a3_path_d0_0", 3, ((0, 1), (1, 2)), 0),
    Case("a3_triangle_d0_1", 3, ((0, 1), (1, 2), (0, 2)), 1),
    Case("a4_paw_d0_0", 4, ((0, 1), (0, 2), (1, 2), (0, 3)), 0),
    Case(
        "a5_friendship_d0_0",
        5,
        ((0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)),
        0,
    ),
)


def find_cycle(adjacency: list[set[int]], length: int) -> list[int] | None:
    n = len(adjacency)
    if length > n:
        return None
    for root in range(n):
        allowed = set(range(root + 1, n))
        for first in sorted(adjacency[root] & allowed):
            path = [root, first]
            used = {root, first}

            def visit(vertex: int) -> list[int] | None:
                if len(path) == length:
                    if root in adjacency[vertex] and path[1] < path[-1]:
                        return list(path)
                    return None
                for nxt in sorted((adjacency[vertex] & allowed) - used):
                    used.add(nxt)
                    path.append(nxt)
                    result = visit(nxt)
                    if result is not None:
                        return result
                    path.pop()
                    used.remove(nxt)
                return None

            result = visit(first)
            if result is not None:
                return result
    return None


def solve(case: Case, lengths: tuple[int, ...] = (4, 8, 16)) -> dict[str, object]:
    a = case.a
    d = 2 * a + 4
    d2 = len(case.j_edges)
    j_degree = [0] * a
    for left, right in case.j_edges:
        j_degree[left] += 1
        j_degree[right] += 1
    attachments = [4 - degree for degree in j_degree]
    d1 = sum(attachments)
    if case.d0 + d1 + d2 != d:
        raise AssertionError(f"bad skeleton arithmetic in {case.name}")

    # Global vertex labels: A first, then D2, D1 grouped by its A-neighbor, then D0.
    d_labels = list(range(a, a + d))
    d2_labels = d_labels[:d2]
    cursor = d2
    d1_by_a: list[list[int]] = []
    for count in attachments:
        d1_by_a.append(d_labels[cursor : cursor + count])
        cursor += count
    d0_labels = d_labels[cursor:]
    if len(d0_labels) != case.d0:
        raise AssertionError("D partition mismatch")

    fixed_edges: set[Edge] = set()
    for label, (left, right) in zip(d2_labels, case.j_edges):
        fixed_edges.add(tuple(sorted((left, label))))
        fixed_edges.add(tuple(sorted((right, label))))
    for high, group in enumerate(d1_by_a):
        for label in group:
            fixed_edges.add((high, label))

    variables: dict[Edge, z3.BoolRef] = {}
    for pos, left in enumerate(d_labels):
        for right in d_labels[pos + 1 :]:
            variables[(left, right)] = z3.Bool(f"e_{left}_{right}")

    solver = z3.Solver()
    required_d_degree: dict[int, int] = {}
    for label in d2_labels:
        required_d_degree[label] = 1
    for group in d1_by_a:
        for label in group:
            required_d_degree[label] = 2
    for label in d0_labels:
        required_d_degree[label] = 3
    for vertex in d_labels:
        incident = [var for edge, var in variables.items() if vertex in edge]
        solver.add(z3.Sum([z3.If(var, 1, 0) for var in incident]) == required_d_degree[vertex])

    iterations = 0
    blocks = {4: 0, 8: 0, 16: 0}
    fixed_obstruction: dict[str, object] | None = None
    while solver.check() == z3.sat:
        iterations += 1
        model = solver.model()
        variable_edges = {
            item for item, var in variables.items() if z3.is_true(model.evaluate(var))
        }
        all_edges = fixed_edges | variable_edges
        adjacency = [set() for _ in range(a + d)]
        for left, right in all_edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        if min(map(len, adjacency)) != 3 or any(len(adjacency[v]) != 4 for v in range(a)):
            raise AssertionError("model does not realize the promised degree sequence")

        obstruction = None
        for length in lengths:
            cycle = find_cycle(adjacency, length)
            if cycle is not None:
                obstruction = (length, cycle)
                break
        if obstruction is None:
            first_c8 = find_cycle(adjacency, 8)
            return {
                "case": case.name,
                "status": "SAT_AVOIDING_" + "_".join(map(str, lengths)),
                "order": a + d,
                "iterations": iterations,
                "blocks": blocks,
                "edges": sorted([list(item) for item in all_edges]),
                "first_c8": first_c8,
            }

        length, cycle = obstruction
        cycle_edges = [
            tuple(sorted((cycle[index], cycle[(index + 1) % length])))
            for index in range(length)
        ]
        variable_cycle_edges = [variables[item] for item in cycle_edges if item in variables]
        if not variable_cycle_edges:
            fixed_obstruction = {"length": length, "cycle": cycle}
            break
        solver.add(z3.Or([z3.Not(var) for var in variable_cycle_edges]))
        blocks[length] += 1

    return {
        "case": case.name,
        "status": "UNSAT",
        "order": a + d,
        "iterations": iterations,
        "blocks": blocks,
        "fixed_obstruction": fixed_obstruction,
        "skeleton": {
            "a": a,
            "d": d,
            "d0": case.d0,
            "d1": d1,
            "d2": d2,
            "j_edges": [list(item) for item in case.j_edges],
            "d1_attachments_per_A": attachments,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c4-only", action="store_true")
    args = parser.parse_args()
    lengths = (4,) if args.c4_only else (4, 8, 16)
    results = [solve(case, lengths) for case in CASES]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
