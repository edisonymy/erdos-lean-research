"""Exhaustively compare small order-five quotient CNFs with the definition."""

from __future__ import annotations

import itertools
import json
from collections import deque

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


def pairs(n: int) -> list[tuple[int, int]]:
    return list(itertools.combinations(range(n), 2))


def permutation_with_one_five_cycle(fixed: int) -> list[int]:
    n = fixed + 5
    permutation = list(range(n))
    for offset in range(5):
        permutation[fixed + offset] = fixed + (offset + 1) % 5
    return permutation


def pair_orbits(n: int, permutation: list[int]) -> list[list[tuple[int, int]]]:
    unseen = set(pairs(n))
    answer = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current not in orbit:
            orbit.append(current)
            u, v = current
            current = tuple(sorted((permutation[u], permutation[v])))
        for pair in orbit:
            unseen.remove(pair)
        answer.append(sorted(orbit))
    return answer


def build_semantic_quotient(
    n: int, permutation: list[int]
) -> tuple[CNF, list[list[tuple[int, int]]]]:
    orbits = pair_orbits(n, permutation)
    edge_for_pair = {}
    for variable, orbit in enumerate(orbits, start=1):
        for pair in orbit:
            edge_for_pair[pair] = variable
    formula = CNF()
    formula.nv = len(orbits)

    def edge(u: int, v: int) -> int:
        return edge_for_pair[(min(u, v), max(u, v))]

    def fresh() -> int:
        formula.nv += 1
        return formula.nv

    for orbit in orbits:
        u, v = orbit[0]
        common_markers = []
        for w in range(n):
            if w in (u, v):
                continue
            marker = fresh()
            common_markers.append(marker)
            formula.append([-marker, edge(u, w)])
            formula.append([-marker, edge(v, w)])
        formula.append([edge(u, v), *common_markers])
        if common_markers:
            atmost = CardEnc.atmost(
                common_markers,
                bound=1,
                top_id=formula.nv,
                encoding=EncType.seqcounter,
            )
            formula.extend(atmost.clauses)

    for orbit in orbits:
        u, v = orbit[0]
        alternatives = []
        no_common = fresh()
        alternatives.append(no_common)
        for w in range(n):
            if w in (u, v):
                continue
            formula.append([-no_common, -edge(u, w), -edge(v, w)])
        for a, b in ((u, v), (v, u)):
            for x in range(n):
                if x in (a, b):
                    continue
                unique = fresh()
                alternatives.append(unique)
                formula.append([-unique, edge(a, x)])
                formula.append([-unique, -edge(b, x)])
                for w in range(n):
                    if w in (a, b, x):
                        continue
                    formula.append([-unique, -edge(x, w), -edge(b, w)])
        formula.append([-edge(u, v), *alternatives])
        atmost = CardEnc.atmost(
            alternatives,
            bound=1,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(atmost.clauses)
    return formula, orbits


def diameter(n: int, edges: set[tuple[int, int]]) -> int | None:
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    maximum = 0
    for source in range(n):
        distances = [-1] * n
        distances[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if distances[v] == -1:
                    distances[v] = distances[u] + 1
                    queue.append(v)
        if -1 in distances:
            return None
        maximum = max(maximum, max(distances))
    return maximum


def is_diameter2_critical(n: int, edges: set[tuple[int, int]]) -> bool:
    return diameter(n, edges) == 2 and all(
        diameter(n, edges - {edge}) != 2 for edge in edges
    )


def main() -> None:
    rows = []
    total_graphs = 0
    total_critical = 0
    for fixed in range(6):
        n = fixed + 5
        permutation = permutation_with_one_five_cycle(fixed)
        formula, orbits = build_semantic_quotient(n, permutation)
        graph_count = 1 << len(orbits)
        critical_count = 0
        with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
            for mask in range(graph_count):
                selected = {
                    variable
                    for variable in range(1, len(orbits) + 1)
                    if mask >> (variable - 1) & 1
                }
                edges = {
                    edge
                    for variable, orbit in enumerate(orbits, start=1)
                    if variable in selected
                    for edge in orbit
                }
                direct = is_diameter2_critical(n, edges)
                assumptions = [
                    variable if variable in selected else -variable
                    for variable in range(1, len(orbits) + 1)
                ]
                encoded = solver.solve(assumptions=assumptions)
                if direct != encoded:
                    raise AssertionError(
                        {
                            "n": n,
                            "fixed": fixed,
                            "mask": mask,
                            "edges": sorted(edges),
                            "direct": direct,
                            "encoded": encoded,
                        }
                    )
                critical_count += int(direct)
        rows.append(
            {
                "n": n,
                "cycle_type": f"1^{fixed} 5^1",
                "edge_orbits": len(orbits),
                "invariant_graphs": graph_count,
                "diameter2_critical_graphs": critical_count,
                "mismatches": 0,
            }
        )
        total_graphs += graph_count
        total_critical += critical_count
    print(
        json.dumps(
            {
                "status": "PASS",
                "total_invariant_graphs": total_graphs,
                "total_diameter2_critical_graphs": total_critical,
                "mismatches": 0,
                "rows": rows,
                "claim_scope": (
                    "exhaustive quotient-CNF versus direct deletion-definition audit "
                    "for one order-five cycle and zero through five fixed vertices"
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
