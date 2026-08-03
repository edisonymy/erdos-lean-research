#!/usr/bin/env python3
"""Independent lazy-SMT cross-check of the universal-plus-six finite cases."""

from __future__ import annotations

import json
from dataclasses import dataclass

import z3

from slack4_finite_probe import find_cycle


Edge = tuple[int, int]


@dataclass(frozen=True)
class Case:
    name: str
    a: int
    j_edges: tuple[Edge, ...]
    d0: int
    excess: tuple[int, ...]


CASES = (
    Case("a1_empty_x3", 1, (), 0, (3,)),
    Case("a1_empty_x1_d0_2", 1, (), 2, (1,)),
    Case("a2_empty_high0", 2, (), 0, (1, 0)),
    Case("a2_edge_high0_d0_1", 2, ((0, 1),), 1, (1, 0)),
    Case("a3_path_high_outer", 3, ((0, 1), (1, 2)), 0, (1, 0, 0)),
    Case("a3_path_high_middle", 3, ((0, 1), (1, 2)), 0, (0, 1, 0)),
    Case("a3_triangle_high0_d0_1", 3, ((0, 1), (1, 2), (0, 2)), 1, (1, 0, 0)),
    Case("a4_paw_high_center", 4, ((0, 1), (0, 2), (1, 2), (0, 3)), 0, (1, 0, 0, 0)),
    Case("a4_paw_high_outer", 4, ((0, 1), (0, 2), (1, 2), (0, 3)), 0, (0, 1, 0, 0)),
    Case("a4_paw_high_leaf", 4, ((0, 1), (0, 2), (1, 2), (0, 3)), 0, (0, 0, 0, 1)),
    Case(
        "a5_friendship_high_center",
        5,
        ((0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)),
        0,
        (1, 0, 0, 0, 0),
    ),
    Case(
        "a5_friendship_high_outer",
        5,
        ((0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)),
        0,
        (0, 1, 0, 0, 0),
    ),
)


def solve(case: Case) -> dict[str, object]:
    a = case.a
    d = 2 * a + 5
    d2 = len(case.j_edges)
    j_degree = [0] * a
    for left, right in case.j_edges:
        j_degree[left] += 1
        j_degree[right] += 1
    attachments = [4 + case.excess[i] - j_degree[i] for i in range(a)]
    d1 = sum(attachments)
    if case.d0 + d1 + d2 != d or sum(case.excess) % 2 != 1:
        raise AssertionError(f"bad equality arithmetic in {case.name}")

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

    fixed: set[Edge] = set()
    for label, (left, right) in zip(d2_labels, case.j_edges):
        fixed.add(tuple(sorted((left, label))))
        fixed.add(tuple(sorted((right, label))))
    for high, group in enumerate(d1_by_a):
        fixed.update((high, label) for label in group)

    variables: dict[Edge, z3.BoolRef] = {}
    for position, left in enumerate(d_labels):
        for right in d_labels[position + 1 :]:
            variables[(left, right)] = z3.Bool(f"{case.name}_e_{left}_{right}")

    required = {label: 1 for label in d2_labels}
    required.update(label_and_degree for group in d1_by_a for label_and_degree in ((label, 2) for label in group))
    required.update((label, 3) for label in d0_labels)
    solver = z3.Solver()
    for vertex in d_labels:
        incident = [variable for item, variable in variables.items() if vertex in item]
        solver.add(z3.Sum([z3.If(variable, 1, 0) for variable in incident]) == required[vertex])

    iterations = 0
    blocks = {4: 0, 8: 0, 16: 0}
    while solver.check() == z3.sat:
        iterations += 1
        model = solver.model()
        chosen = {item for item, variable in variables.items() if z3.is_true(model.evaluate(variable))}
        edges = fixed | chosen
        adjacency = [set() for _ in range(a + d)]
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        if any(len(adjacency[i]) != 4 + case.excess[i] for i in range(a)):
            raise AssertionError("bad A degree")
        if any(len(adjacency[i]) != 3 for i in d_labels):
            raise AssertionError("bad D degree")

        obstruction = None
        for length in (4, 8, 16):
            cycle = find_cycle(adjacency, length)
            if cycle is not None:
                obstruction = (length, cycle)
                break
        if obstruction is None:
            return {
                "case": case.name,
                "status": "SAT_DYADIC_FREE_COUNTEREXAMPLE",
                "iterations": iterations,
                "blocks": blocks,
                "edges": sorted(map(list, edges)),
            }
        length, cycle = obstruction
        cycle_edges = [
            tuple(sorted((cycle[i], cycle[(i + 1) % length]))) for i in range(length)
        ]
        literals = [z3.Not(variables[item]) for item in cycle_edges if item in variables]
        if not literals:
            return {
                "case": case.name,
                "status": "FIXED_DYADIC_OBSTRUCTION",
                "length": length,
                "cycle": cycle,
            }
        solver.add(z3.Or(literals))
        blocks[length] += 1

    return {
        "case": case.name,
        "status": "UNSAT",
        "iterations": iterations,
        "blocks": blocks,
        "a": a,
        "d": d,
        "d0": case.d0,
        "d1": d1,
        "d2": d2,
        "attachments": attachments,
    }


def main() -> int:
    results = [solve(case) for case in CASES]
    print(json.dumps(results, indent=2))
    return 10 if any(item["status"] == "SAT_DYADIC_FREE_COUNTEREXAMPLE" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
