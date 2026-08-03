#!/usr/bin/env python3
"""Exact order-12, m=23 triangle-free residual for Erdős #149.

The compatibility graph J has vertices E(G), with adjacency meaning that two
G-edges induce 2K2.  A triangle-free 23-edge counterexample has matching
number at most two.  This generator covers matching number one (a star, after
symmetry fixing) and matching number exactly two.

For matching number two, fix a maximum matching M of J.  The four underlying
G-edges have exactly three possible endpoint-overlap types (0, 1, or 2
overlaps); more overlap would place one of the fixed G-edges between the
endpoints of the other compatible pair.  For each type, the CNF forbids every
M-augmenting path of lengths 1, 3, and 5.  Berge's theorem then gives
nu(J)=2.  Compatibility is represented by exact Tseitin indicators, degree
four uses direct 5-subset clauses, and global edge cardinality uses a totalizer
rather than the root sequential-counter encoding.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


N = 12
M = 23
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
VAR = {edge: index + 1 for index, edge in enumerate(PAIRS)}
MATCHING_CASES = {
    # M consists of compatibility edges fixed[0]--fixed[1] and
    # fixed[2]--fixed[3].
    "overlap0": ((0, 1), (2, 3), (4, 5), (6, 7)),
    "overlap1": ((0, 1), (2, 3), (0, 4), (5, 6)),
    "overlap2": ((0, 1), (2, 3), (0, 4), (2, 5)),
}


def norm(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def ve(edge: tuple[int, int]) -> int:
    return VAR[norm(*edge)]


def crosses(e: tuple[int, int], f: tuple[int, int]) -> list[tuple[int, int]]:
    a, b = e
    c, d = f
    return [norm(a, c), norm(a, d), norm(b, c), norm(b, d)]


def qkey(e: tuple[int, int], f: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return (e, f) if VAR[e] < VAR[f] else (f, e)


def build_base() -> tuple[CNF, IDPool, dict[tuple[tuple[int, int], tuple[int, int]], int]]:
    cnf = CNF()
    pool = IDPool(start_from=len(PAIRS) + 1)

    # Maximum degree at most four, by the definition-level 5-subset encoding.
    for vertex in range(N):
        incident = [norm(vertex, other) for other in range(N) if other != vertex]
        for five in itertools.combinations(incident, 5):
            cnf.append([-ve(edge) for edge in five])

    # Exactly 23 edges, using a different cardinality family from the root CNFs.
    cnf.extend(
        CardEnc.equals(
            [ve(edge) for edge in PAIRS],
            bound=M,
            vpool=pool,
            encoding=EncType.totalizer,
        ).clauses
    )

    # Exact indicators q(e,f) <-> (e,f present and their four cross-edges absent).
    compat: dict[tuple[tuple[int, int], tuple[int, int]], int] = {}
    for e, f in itertools.combinations(PAIRS, 2):
        if len(set(e) | set(f)) != 4:
            continue
        q = pool.id(("compat", e, f))
        compat[qkey(e, f)] = q
        cnf.append([-q, ve(e)])
        cnf.append([-q, ve(f)])
        for cross in crosses(e, f):
            cnf.append([-q, -ve(cross)])
        cnf.append([-ve(e), -ve(f), *[ve(cross) for cross in crosses(e, f)], q])
    return cnf, pool, compat


def qvar(compat, e, f) -> int | None:
    return compat.get(qkey(e, f))


def add_triangle_free(cnf: CNF, compat) -> int:
    count = 0
    # Pairwise compatible G-edges are pairwise endpoint-disjoint.  Hence every
    # J-triangle is one of the following triples of independent K_12 edges.
    for a, b, c in itertools.combinations(PAIRS, 3):
        qab, qac, qbc = qvar(compat, a, b), qvar(compat, a, c), qvar(compat, b, c)
        if qab is not None and qac is not None and qbc is not None:
            cnf.append([-qab, -qac, -qbc])
            count += 1
    return count


def add_star_case(cnf: CNF, compat) -> dict:
    centre, leaf = (0, 1), (2, 3)
    fixed = qvar(compat, centre, leaf)
    assert fixed is not None
    cnf.append([fixed])
    forbidden = 0
    for (e, f), q in compat.items():
        if centre not in (e, f):
            cnf.append([-q])
            forbidden += 1
    return {"fixed_matching": [[list(centre), list(leaf)]], "star_forbidden_q": forbidden}


def add_berge_case(cnf: CNF, compat, fixed: tuple[tuple[int, int], ...]) -> dict:
    a, b, c, d = fixed
    matching = ((a, b), (c, d))
    for x, y in matching:
        q = qvar(compat, x, y)
        assert q is not None
        cnf.append([q])

    matched = set(fixed)
    unmatched = [edge for edge in PAIRS if edge not in matched]

    # Length-one augmenting paths: unmatched vertices form an independent set.
    length1 = 0
    for u, v in itertools.combinations(unmatched, 2):
        if (q := qvar(compat, u, v)) is not None:
            cnf.append([-q])
            length1 += 1

    # Length-three augmenting paths u-x-y-v through one edge xy of M.
    length3 = 0
    for x, y in matching:
        for u, v in itertools.permutations(unmatched, 2):
            qux, qyv = qvar(compat, u, x), qvar(compat, y, v)
            if qux is not None and qyv is not None:
                cnf.append([-qux, -qyv])
                length3 += 1

    # Length-five augmenting paths using both matching edges.  Orient and order
    # the two M-edges; reversed paths may duplicate clauses harmlessly.
    length5 = 0
    for first_index, second_index in ((0, 1), (1, 0)):
        for x1, y1 in (matching[first_index], matching[first_index][::-1]):
            for x2, y2 in (matching[second_index], matching[second_index][::-1]):
                bridge = qvar(compat, y1, x2)
                if bridge is None:
                    continue
                for u, v in itertools.permutations(unmatched, 2):
                    qu, qv = qvar(compat, u, x1), qvar(compat, y2, v)
                    if qu is not None and qv is not None:
                        cnf.append([-qu, -bridge, -qv])
                        length5 += 1

    triangle_clauses = add_triangle_free(cnf, compat)
    return {
        "fixed_graph_edges": [list(edge) for edge in fixed],
        "fixed_matching": [[list(a), list(b)], [list(c), list(d)]],
        "augmenting_path_clauses": {"length1": length1, "length3": length3, "length5": length5},
        "triangle_clauses": triangle_clauses,
    }


def build(case: str) -> tuple[CNF, dict]:
    cnf, pool, compat = build_base()
    if case == "star":
        details = add_star_case(cnf, compat)
    else:
        details = add_berge_case(cnf, compat, MATCHING_CASES[case])
    details.update(
        {
            "compatibility_indicators": len(compat),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
            "cardinality": "degree direct 5-subsets; global equality totalizer",
        }
    )
    return cnf, details


def dimacs_bytes(cnf: CNF) -> bytes:
    lines = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in cnf.clauses)
    return ("\n".join(lines) + "\n").encode("ascii")


def compatibility_graph(edges: list[tuple[int, int]]) -> nx.Graph:
    present = set(edges)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(edges)))
    for i, j in itertools.combinations(range(len(edges)), 2):
        e, f = edges[i], edges[j]
        if len(set(e) | set(f)) == 4 and all(x not in present for x in crosses(e, f)):
            graph.add_edge(i, j)
    return graph


def verify_model(model: list[int], case: str) -> dict:
    positive = {lit for lit in model if lit > 0}
    edges = [edge for edge in PAIRS if ve(edge) in positive]
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(N)]
    assert len(edges) == M and max(degrees) <= 4
    jgraph = compatibility_graph(edges)
    triangles = [cycle for cycle in nx.enumerate_all_cliques(jgraph) if len(cycle) == 3]
    matching = nx.max_weight_matching(jgraph, maxcardinality=True)
    if case == "star":
        assert len(matching) == 1 and not triangles
    else:
        assert len(matching) == 2 and not triangles
    return {
        "edges": [list(edge) for edge in edges],
        "degrees": degrees,
        "compatibility_edges": jgraph.number_of_edges(),
        "compatibility_matching_number": len(matching),
        "compatibility_triangles": triangles,
        "strong_chromatic_index": M - len(matching),
    }


def solve(cnf: CNF, solver_name: str) -> tuple[bool, list[int] | None, float]:
    started = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    return sat, model, time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "trianglefree_cnfs")
    parser.add_argument("--cases", nargs="+", choices=["star", *MATCHING_CASES], default=["star", *MATCHING_CASES])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result = {"schema": "erdos149-n12-m23-trianglefree-berge-v1", "cases": {}}
    for case in args.cases:
        cnf, details = build(case)
        raw = dimacs_bytes(cnf)
        cnf_path = args.out_dir / f"{case}.cnf"
        cnf_path.write_bytes(raw)
        primary = solve(cnf, "cadical195")
        secondary = solve(cnf, "g4")
        assert primary[0] == secondary[0]
        candidate = verify_model(primary[1], case) if primary[0] and primary[1] else None
        result["cases"][case] = {
            "encoding": details,
            "cnf": {"path": str(cnf_path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
            "primary": {"solver": "cadical195", "sat": primary[0], "seconds": primary[2]},
            "secondary": {"solver": "glucose4", "sat": secondary[0], "seconds": secondary[2]},
            "candidate": candidate,
        }
        print(case, "SAT" if primary[0] else "UNSAT", f"{primary[2]:.3f}s/{secondary[2]:.3f}s")
    out = args.out_dir / "result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
