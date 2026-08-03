#!/usr/bin/env python3
"""Exact labelled SAT gate for the 22-edge, order-12 part of Erdős #149.

Let J(G) be the compatibility graph whose vertices are the edges of G and
whose adjacent pairs form induced matchings in G.  A 22-edge graph has a
strong edge-colouring with at most 20 colours iff J contains either a
triangle or a matching of size two.  If neither exists and J is nonempty,
J is a star.

The Chung--Gyárfás--Tuza--Trotter extremal theorem says that a subquartic
2K2-free graph has at most 20 edges, so J is nonempty here.  Relabel the
centre of its star as edge 01 and one leaf as edge 23.  The CNF below asks
whether the resulting exact obstruction exists on 12 vertices, with exactly
22 edges and maximum degree at most four.

This is a full symmetry reduction of the m=22 slice, not an enumeration
heuristic.  Any SAT model is independently reconstructed and its compatibility
graph is checked from the original definition before being reported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


N = 12
M = 22
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
VAR = {edge: index + 1 for index, edge in enumerate(PAIRS)}


def ve(a: int, b: int) -> int:
    return VAR[(a, b) if a < b else (b, a)]


def build_cnf() -> CNF:
    cnf = CNF()
    pool = IDPool(start_from=len(PAIRS) + 1)

    # Maximum degree four and exactly 22 graph edges.
    for vertex in range(N):
        incident = [ve(vertex, other) for other in range(N) if other != vertex]
        cnf.extend(
            CardEnc.atmost(
                lits=incident,
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

    centre = (0, 1)
    leaf = (2, 3)
    cnf.append([ve(*centre)])
    cnf.append([ve(*leaf)])
    # 01 and 23 must be a compatible pair in J(G).
    for cross in ((0, 2), (0, 3), (1, 2), (1, 3)):
        cnf.append([-ve(*cross)])

    # Every compatible pair of present G-edges must involve the centre 01.
    # Thus J(G) is a subgraph of a star centred at 01; the fixed leaf makes it
    # nonempty.  Each clause is precisely the negation of two present disjoint
    # edges with all four cross-edges absent.
    for i, (a, b) in enumerate(PAIRS):
        if (a, b) == centre:
            continue
        for c, d in PAIRS[i + 1 :]:
            if (c, d) == centre or len({a, b, c, d}) != 4:
                continue
            crosses = [ve(a, c), ve(a, d), ve(b, c), ve(b, d)]
            cnf.append([-ve(a, b), -ve(c, d), *crosses])
    return cnf


def dimacs_bytes(cnf: CNF) -> bytes:
    lines = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in cnf.clauses)
    return ("\n".join(lines) + "\n").encode("ascii")


def solve(
    cnf: CNF, name: str, proof: bool
) -> tuple[bool, list[int] | None, list[str] | None, float]:
    started = time.perf_counter()
    with Solver(name=name, bootstrap_with=cnf.clauses, with_proof=proof) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
        trace = solver.get_proof() if proof and not sat else None
    return sat, model, trace, time.perf_counter() - started


def compatibility_edges(edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    edge_set = set(edges)
    out: list[tuple[int, int]] = []
    for i, (a, b) in enumerate(edges):
        for j in range(i + 1, len(edges)):
            c, d = edges[j]
            if len({a, b, c, d}) != 4:
                continue
            if any(
                (min(x, y), max(x, y)) in edge_set
                for x in (a, b)
                for y in (c, d)
            ):
                continue
            out.append((i, j))
    return out


def audit_sat_model(model: list[int]) -> dict:
    positive = {literal for literal in model if literal > 0}
    edges = [edge for edge in PAIRS if ve(*edge) in positive]
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(N)]
    if len(edges) != M or max(degrees) > 4:
        raise AssertionError("decoded model violates graph cardinality")

    compat = compatibility_edges(edges)
    centre_index = edges.index((0, 1))
    leaf_index = edges.index((2, 3))
    if (min(centre_index, leaf_index), max(centre_index, leaf_index)) not in compat:
        raise AssertionError("fixed centre and leaf are not compatible")
    if any(centre_index not in pair for pair in compat):
        raise AssertionError("decoded compatibility graph is not a star")

    # Directly exclude the two possible ways to save two colours.
    compat_set = {tuple(sorted(pair)) for pair in compat}
    matching_two = None
    for i, first in enumerate(compat):
        for second in compat[i + 1 :]:
            if set(first).isdisjoint(second):
                matching_two = [list(first), list(second)]
                break
        if matching_two is not None:
            break
    triangle = None
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            if (i, j) not in compat_set:
                continue
            for k in range(j + 1, len(edges)):
                if (i, k) in compat_set and (j, k) in compat_set:
                    triangle = [i, j, k]
                    break
            if triangle is not None:
                break
        if triangle is not None:
            break
    if matching_two is not None or triangle is not None:
        raise AssertionError("decoded model admits a 20-colour saving pattern")

    return {
        "edges": [list(edge) for edge in edges],
        "degrees": degrees,
        "compatibility_edges": [list(pair) for pair in compat],
        "compatibility_centre_edge_index": centre_index,
        "compatibility_leaf_edge_index": leaf_index,
        "matching_two": matching_two,
        "triangle": triangle,
        "strong_chromatic_index_from_star": 21,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--primary", default="cadical195")
    args = parser.parse_args()

    cnf = build_cnf()
    raw_cnf = dimacs_bytes(cnf)
    args.cnf.parent.mkdir(parents=True, exist_ok=True)
    args.cnf.write_bytes(raw_cnf)

    primary = solve(cnf, args.primary, proof=args.proof is not None)
    secondary_name = None
    secondary = None
    for candidate in ("g4", "m22", "g3", "cadical153"):
        if candidate == args.primary:
            continue
        try:
            secondary = solve(cnf, candidate, proof=False)
            secondary_name = candidate
            break
        except Exception:
            continue
    if secondary is None:
        raise RuntimeError("no independent second PySAT backend is available")

    sat, model, trace, elapsed = primary
    if sat != secondary[0]:
        raise AssertionError("independent SAT solvers disagree")
    if trace is not None and args.proof is not None:
        args.proof.write_text(
            "\n".join(trace) + "\n", encoding="ascii", newline="\n"
        )

    witness = audit_sat_model(model) if sat and model is not None else None
    result = {
        "schema": "erdos149-n12-m22-star-sat-v1",
        "claim_scope": (
            "exact existence of an order-12, 22-edge, subquartic graph whose "
            "compatibility graph is a nonempty star, after fixing its centre "
            "to edge 01 and a leaf to edge 23"
        ),
        "mathematical_reduction": (
            "CGTT gives J(G) nonempty at 22 edges; failure to save two colours "
            "means J has no triangle and no matching of size two, hence is a star"
        ),
        "encoding": {
            "vertices": N,
            "edges_required": M,
            "graph_edge_variables": len(PAIRS),
            "cnf_variables": cnf.nv,
            "clauses": len(cnf.clauses),
            "cnf_path": str(args.cnf),
            "cnf_sha256": hashlib.sha256(raw_cnf).hexdigest(),
        },
        "primary": {
            "solver": args.primary,
            "sat": sat,
            "elapsed_seconds": elapsed,
            "proof_path": str(args.proof) if trace is not None and args.proof else None,
            "proof_lines": len(trace) if trace is not None else None,
        },
        "secondary": {
            "solver": secondary_name,
            "sat": secondary[0],
            "elapsed_seconds": secondary[3],
        },
        "solvers_agree": sat == secondary[0],
        "witness": witness,
        "certification_boundary": (
            "A SAT witness is checked directly from the graph definition. An "
            "UNSAT result requires an independently replayed proof before it "
            "supports an exhaustive bounded theorem."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
