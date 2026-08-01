"""Candidate-only SAT search for a Murty--Simon counterexample.

The input CNFs are Brian Li's public diameter-2-critical instances.  They are
not trusted as proofs: a SAT model is decoded only through the first C(n, 2)
variables and then checked from the graph definition by verify_graph.py.
An UNSAT answer is exploratory unless accompanied by an independently checked
proof certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

from verify_graph import edge_variables, verify_diameter2_critical


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fresh_variable(formula: CNF) -> int:
    formula.nv += 1
    return formula.nv


def comparator(formula: CNF, a: int, b: int) -> tuple[int, int]:
    """Return exact Boolean outputs (a OR b, a AND b)."""
    high = fresh_variable(formula)
    low = fresh_variable(formula)
    formula.extend(
        [
            [-a, high],
            [-b, high],
            [a, b, -high],
            [a, -low],
            [b, -low],
            [-a, -b, low],
        ]
    )
    return high, low


def sorted_unary_sum(formula: CNF, inputs: list[int]) -> list[int]:
    """Insertion sorting network; output[k] iff at least k+1 inputs are true."""
    outputs: list[int] = []
    for value in inputs:
        carry = value
        new_outputs = []
        for old in outputs:
            high, carry = comparator(formula, old, carry)
            new_outputs.append(high)
        new_outputs.append(carry)
        outputs = new_outputs
    return outputs


def add_degree_order(
    formula: CNF, n: int, blocks: list[list[int]] | None = None
) -> tuple[int, int]:
    """Sort degrees inside each supplied vertex block."""
    before_nv, before_clauses = formula.nv, len(formula.clauses)
    edge_for_pair = {edge: var for var, edge in edge_variables(n)}
    unary_degrees = []
    for vertex in range(n):
        incident = [
            edge_for_pair[(min(vertex, other), max(vertex, other))]
            for other in range(n)
            if other != vertex
        ]
        unary_degrees.append(sorted_unary_sum(formula, incident))
    if blocks is None:
        blocks = [list(range(n))]
    for block in blocks:
        for left, right in zip(block, block[1:]):
            for threshold in range(n - 1):
                formula.append(
                    [-unary_degrees[right][threshold], unary_degrees[left][threshold]]
                )
    return formula.nv - before_nv, len(formula.clauses) - before_clauses


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("n", type=int)
    parser.add_argument("--min-edges", type=int)
    parser.add_argument("--max-edges", type=int)
    parser.add_argument("--solver", default="maplesat")
    parser.add_argument("--result", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--degree-order", action="store_true")
    parser.add_argument("--fix-triangle", action="store_true")
    parser.add_argument("--max-degree", type=int)
    parser.add_argument("--no-dominating-edge", action="store_true")
    args = parser.parse_args()

    if args.n < 3:
        raise SystemExit("n must be at least 3")
    edge_count = args.n * (args.n - 1) // 2
    min_edges = args.min_edges
    if min_edges is None:
        min_edges = args.n * args.n // 4 + 1
    if not 0 <= min_edges <= edge_count:
        raise SystemExit("invalid edge lower bound")
    if args.max_edges is not None and not min_edges <= args.max_edges <= edge_count:
        raise SystemExit("invalid edge upper bound")
    if args.fix_triangle and min_edges <= args.n * args.n // 4:
        raise SystemExit(
            "--fix-triangle is exhaustive only when --min-edges exceeds "
            "the Mantel bound floor(n^2/4)"
        )

    started = time.perf_counter()
    source_sha256 = sha256(args.cnf)
    formula = CNF(from_file=str(args.cnf))
    source_nv, source_clauses = formula.nv, len(formula.clauses)
    cardinality = CardEnc.atleast(
        lits=list(range(1, edge_count + 1)),
        bound=min_edges,
        top_id=formula.nv,
        encoding=EncType.seqcounter,
    )
    formula.extend(cardinality.clauses)
    upper_cardinality_variables = 0
    upper_cardinality_clauses = 0
    if args.max_edges is not None:
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        upper = CardEnc.atmost(
            lits=list(range(1, edge_count + 1)),
            bound=args.max_edges,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(upper.clauses)
        upper_cardinality_variables = formula.nv - before_nv
        upper_cardinality_clauses = len(formula.clauses) - before_clauses
    edge_for_pair = {edge: var for var, edge in edge_variables(args.n)}
    fixed_triangle_clauses = 0
    if args.fix_triangle:
        for edge in ((0, 1), (0, 2), (1, 2)):
            formula.append([edge_for_pair[edge]])
            fixed_triangle_clauses += 1
    degree_order_variables = 0
    degree_order_clauses = 0
    if args.degree_order:
        blocks = None
        if args.fix_triangle:
            blocks = [[0, 1, 2], list(range(3, args.n))]
        degree_order_variables, degree_order_clauses = add_degree_order(
            formula, args.n, blocks=blocks
        )
    max_degree_variables = 0
    max_degree_clauses = 0
    if args.max_degree is not None:
        if not 0 <= args.max_degree < args.n:
            raise SystemExit("invalid maximum degree")
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        if args.degree_order and args.fix_triangle:
            vertices = [0]
            if args.n > 3:
                vertices.append(3)
        elif args.degree_order:
            vertices = [0]
        else:
            vertices = list(range(args.n))
        for vertex in vertices:
            incident = [
                edge_for_pair[(min(vertex, other), max(vertex, other))]
                for other in range(args.n)
                if other != vertex
            ]
            bound = CardEnc.atmost(
                lits=incident,
                bound=args.max_degree,
                top_id=formula.nv,
                encoding=EncType.seqcounter,
            )
            formula.extend(bound.clauses)
        max_degree_variables = formula.nv - before_nv
        max_degree_clauses = len(formula.clauses) - before_clauses
    no_dom_variables = 0
    no_dom_clauses = 0
    if args.no_dominating_edge:
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        for u in range(args.n):
            for v in range(u + 1, args.n):
                witnesses = []
                for w in range(args.n):
                    if w in (u, v):
                        continue
                    witness = fresh_variable(formula)
                    witnesses.append(witness)
                    uw = edge_for_pair[(min(u, w), max(u, w))]
                    vw = edge_for_pair[(min(v, w), max(v, w))]
                    formula.append([-witness, -uw])
                    formula.append([-witness, -vw])
                formula.append([-edge_for_pair[(u, v)], *witnesses])
        no_dom_variables = formula.nv - before_nv
        no_dom_clauses = len(formula.clauses) - before_clauses
    built = time.perf_counter()

    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        sat = solver.solve()
        stats = solver.accum_stats()
        model = solver.get_model() if sat else None
    finished = time.perf_counter()
    if sha256(args.cnf) != source_sha256:
        raise RuntimeError("source CNF changed during the solver run")

    candidate = None
    if model is not None:
        positive = set(lit for lit in model if lit > 0)
        edges = [list(edge) for var, edge in edge_variables(args.n) if var in positive]
        candidate = {"n": args.n, "edges": edges}
        checked = verify_diameter2_critical(args.n, {tuple(edge) for edge in edges})
        candidate["verification"] = checked
        if (
            not checked["valid"]
            or len(edges) < min_edges
            or (args.max_edges is not None and len(edges) > args.max_edges)
        ):
            raise RuntimeError("SAT model failed the independent graph checker")
        edge_set = {tuple(edge) for edge in edges}
        degrees = [
            sum((min(vertex, other), max(vertex, other)) in edge_set
                for other in range(args.n) if other != vertex)
            for vertex in range(args.n)
        ]
        if args.fix_triangle and not all(
            edge in edge_set for edge in ((0, 1), (0, 2), (1, 2))
        ):
            raise RuntimeError("SAT model violates the fixed-triangle restriction")
        if args.degree_order:
            blocks = [list(range(args.n))]
            if args.fix_triangle:
                blocks = [[0, 1, 2], list(range(3, args.n))]
            if any(
                degrees[left] < degrees[right]
                for block in blocks
                for left, right in zip(block, block[1:])
            ):
                raise RuntimeError("SAT model violates the degree-order restriction")
        if args.max_degree is not None and max(degrees) > args.max_degree:
            raise RuntimeError("SAT model violates the maximum-degree restriction")
        if args.no_dominating_edge and any(
            all(
                w in (u, v)
                or (min(u, w), max(u, w)) in edge_set
                or (min(v, w), max(v, w)) in edge_set
                for w in range(args.n)
            )
            for u, v in edge_set
        ):
            raise RuntimeError("SAT model contains a dominating edge")
        if args.candidate:
            args.candidate.parent.mkdir(parents=True, exist_ok=True)
            args.candidate.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    result = {
        "source": str(args.cnf),
        "source_sha256": source_sha256,
        "n": args.n,
        "edge_variables": edge_count,
        "min_edges": min_edges,
        "max_edges": args.max_edges,
        "source_variables": source_nv,
        "source_clauses": source_clauses,
        "cardinality_variables": max(0, cardinality.nv - source_nv),
        "cardinality_clauses": len(cardinality.clauses),
        "upper_cardinality_variables": upper_cardinality_variables,
        "upper_cardinality_clauses": upper_cardinality_clauses,
        "degree_order": args.degree_order,
        "fix_triangle": args.fix_triangle,
        "fixed_triangle_clauses": fixed_triangle_clauses,
        "degree_order_variables": degree_order_variables,
        "degree_order_clauses": degree_order_clauses,
        "max_degree": args.max_degree,
        "max_degree_variables": max_degree_variables,
        "max_degree_clauses": max_degree_clauses,
        "no_dominating_edge": args.no_dominating_edge,
        "no_dominating_edge_variables": no_dom_variables,
        "no_dominating_edge_clauses": no_dom_clauses,
        "total_variables": formula.nv,
        "total_clauses": len(formula.clauses),
        "solver": args.solver,
        "sat": sat,
        "stats": stats,
        "build_seconds": built - started,
        "solve_seconds": finished - built,
        "candidate": candidate,
        "claim_scope": "candidate search only; UNSAT is not a certified theorem",
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.result:
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
