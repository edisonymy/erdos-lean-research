#!/usr/bin/env python3
"""Exact SAT gate for the triangle-containing m=23 slice of Erdős #149.

For a 23-edge subquartic graph G, let J(G) be its induced-matching
compatibility graph.  A hypothetical graph needing 21 strong colours has
maximum clique-packing saving two.  This script handles the case in which J
contains a triangle.  Relabel that compatible triple of G-edges as
T={01,23,45}.  It then forbids every way to save a third colour:

* a compatibility edge disjoint from T;
* a K4 of J containing T;
* a triangle using one outside J-vertex plus two vertices of T, together with
  a disjoint compatibility edge; and
* a matching of size three in J.

These are all possible clique-packing patterns with total saving at least
three once J-T is independent.  Thus SAT would produce a genuine 23-edge
counterexample candidate; UNSAT excludes the entire triangle-containing
slice, subject to the audited CNF mapping.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


N = 12
M = 23
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
EDGE_INDEX = {edge: index for index, edge in enumerate(PAIRS)}
VAR = {edge: index + 1 for index, edge in enumerate(PAIRS)}
TRIANGLE = ((0, 1), (2, 3), (4, 5))


def norm(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def ve(a: int, b: int) -> int:
    return VAR[norm(a, b)]


def cross_edges(
    first: tuple[int, int], second: tuple[int, int]
) -> list[tuple[int, int]]:
    a, b = first
    c, d = second
    return [norm(a, c), norm(a, d), norm(b, c), norm(b, d)]


def build_cnf() -> tuple[CNF, dict[tuple[tuple[int, int], int], int]]:
    cnf = CNF()
    pool = IDPool(start_from=len(PAIRS) + 1)

    for vertex in range(N):
        cnf.extend(
            CardEnc.atmost(
                lits=[ve(vertex, other) for other in range(N) if other != vertex],
                bound=4,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    cnf.extend(
        CardEnc.equals(
            lits=[ve(*edge) for edge in PAIRS],
            bound=M,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )

    # Fix a compatibility triangle T in J(G): three present graph edges and
    # no G-cross-edge between any two of them.
    for edge in TRIANGLE:
        cnf.append([ve(*edge)])
    for first, second in itertools.combinations(TRIANGLE, 2):
        for cross in cross_edges(first, second):
            cnf.append([-ve(*cross)])

    outside = [edge for edge in PAIRS if edge not in TRIANGLE]

    # T is a vertex cover of J: no two outside G-edges may be compatible.
    for index, first in enumerate(outside):
        for second in outside[index + 1 :]:
            if len(set(first) | set(second)) != 4:
                continue
            cnf.append(
                [-ve(*first), -ve(*second)]
                + [ve(*edge) for edge in cross_edges(first, second)]
            )

    # Exact compatibility indicators between each outside J-vertex and each
    # member of T.  Pairs sharing a graph endpoint are structurally
    # incompatible and receive no variable.
    compat: dict[tuple[tuple[int, int], int], int] = {}
    for edge in outside:
        for triangle_index, fixed in enumerate(TRIANGLE):
            if len(set(edge) | set(fixed)) != 4:
                continue
            indicator = pool.id(("compat", edge, triangle_index))
            compat[(edge, triangle_index)] = indicator
            crosses = cross_edges(edge, fixed)
            cnf.append([-indicator, ve(*edge)])
            for cross in crosses:
                cnf.append([-indicator, -ve(*cross)])
            cnf.append([-ve(*edge)] + [ve(*cross) for cross in crosses] + [indicator])

    # No K4 containing T.
    for edge in outside:
        indicators = [compat.get((edge, index)) for index in range(3)]
        if all(indicators):
            cnf.append([-int(indicator) for indicator in indicators])

    # No alternate triangle plus a disjoint compatibility edge.  If outside
    # edge u is compatible with T_i and T_j, then no distinct outside edge v
    # may be compatible with the remaining T_k.
    for edge_u in outside:
        for i, j in itertools.combinations(range(3), 2):
            k = 3 - i - j
            c_ui = compat.get((edge_u, i))
            c_uj = compat.get((edge_u, j))
            if c_ui is None or c_uj is None:
                continue
            for edge_v in outside:
                if edge_v == edge_u:
                    continue
                c_vk = compat.get((edge_v, k))
                if c_vk is not None:
                    cnf.append([-c_ui, -c_uj, -c_vk])

    # No matching of size three.  Since T covers J, such a matching consists
    # of three distinct outside vertices matched bijectively to T.
    for edge_a, edge_b, edge_c in itertools.combinations(outside, 3):
        chosen = (edge_a, edge_b, edge_c)
        for assignment in itertools.permutations(range(3)):
            indicators = [
                compat.get((chosen[position], assignment[position]))
                for position in range(3)
            ]
            if all(indicators):
                cnf.append([-int(indicator) for indicator in indicators])

    return cnf, compat


def dimacs_bytes(cnf: CNF) -> bytes:
    lines = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in cnf.clauses)
    return ("\n".join(lines) + "\n").encode("ascii")


def solve(cnf: CNF, name: str) -> tuple[bool, list[int] | None, float]:
    started = time.perf_counter()
    with Solver(name=name, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    return sat, model, time.perf_counter() - started


def reconstruct(model: list[int]) -> dict:
    positive = {literal for literal in model if literal > 0}
    edges = [edge for edge in PAIRS if ve(*edge) in positive]
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(N)]
    if len(edges) != M or max(degrees) > 4:
        raise AssertionError("decoded model violates cardinality")
    return {"edges": [list(edge) for edge in edges], "degrees": degrees}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    args = parser.parse_args()

    cnf, compat = build_cnf()
    raw = dimacs_bytes(cnf)
    args.cnf.parent.mkdir(parents=True, exist_ok=True)
    args.cnf.write_bytes(raw)

    primary = solve(cnf, "cadical195")
    secondary = solve(cnf, "g4")
    if primary[0] != secondary[0]:
        raise AssertionError("independent solvers disagree")

    result = {
        "schema": "erdos149-n12-m23-triangle-sat-v1",
        "scope": (
            "exact existence of an order-12, 23-edge, subquartic graph whose "
            "compatibility graph contains a triangle but has clique-packing "
            "saving at most two"
        ),
        "encoding": {
            "vertices": N,
            "edges_required": M,
            "graph_edge_variables": len(PAIRS),
            "compatibility_indicators": len(compat),
            "cnf_variables": cnf.nv,
            "clauses": len(cnf.clauses),
            "cnf_path": str(args.cnf),
            "cnf_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "primary": {
            "solver": "cadical195",
            "sat": primary[0],
            "elapsed_seconds": primary[2],
        },
        "secondary": {
            "solver": "glucose4",
            "sat": secondary[0],
            "elapsed_seconds": secondary[2],
        },
        "solvers_agree": primary[0] == secondary[0],
        "candidate": reconstruct(primary[1]) if primary[0] and primary[1] else None,
        "certification_boundary": (
            "A SAT graph requires an independent exact strong-colouring audit. "
            "An UNSAT result requires a replayed proof and an independent "
            "definition-level encoding audit before supporting a bounded theorem."
        ),
    }
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
