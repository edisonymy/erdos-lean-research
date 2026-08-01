"""Exhaustively compare a small public CNF with the graph definition.

For every assignment of the first C(n, 2) variables, solve only for the
auxiliary variables and compare satisfiability with the independent checker.
This is practical for n <= 6 and catches variable-order or encoding mistakes.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

from candidate_search import add_degree_order, fresh_variable
from verify_graph import edge_variables, verify_diameter2_critical


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("n", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--degree-order", action="store_true")
    parser.add_argument("--fix-triangle", action="store_true")
    parser.add_argument("--result", type=Path)
    parser.add_argument("--no-dominating-edge", action="store_true")
    parser.add_argument("--min-edges", type=int)
    parser.add_argument("--max-edges", type=int)
    args = parser.parse_args()
    if args.n > 6:
        raise SystemExit("exhaustive audit is intentionally limited to n <= 6")

    formula = CNF(from_file=str(args.cnf))
    variables = list(edge_variables(args.n))
    edge_map = {edge: var for var, edge in variables}
    if args.min_edges is not None and not 0 <= args.min_edges <= len(variables):
        raise SystemExit("invalid edge lower bound")
    if args.max_edges is not None and not 0 <= args.max_edges <= len(variables):
        raise SystemExit("invalid edge upper bound")
    if (
        args.min_edges is not None
        and args.max_edges is not None
        and args.min_edges > args.max_edges
    ):
        raise SystemExit("edge lower bound exceeds edge upper bound")
    if args.min_edges is not None:
        lower = CardEnc.atleast(
            lits=[var for var, _ in variables],
            bound=args.min_edges,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(lower.clauses)
    if args.max_edges is not None:
        upper = CardEnc.atmost(
            lits=[var for var, _ in variables],
            bound=args.max_edges,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(upper.clauses)
    if args.fix_triangle:
        for edge in ((0, 1), (0, 2), (1, 2)):
            formula.append([edge_map[edge]])
    if args.degree_order:
        blocks = [[0, 1, 2], list(range(3, args.n))] if args.fix_triangle else None
        add_degree_order(formula, args.n, blocks=blocks)
    if args.no_dominating_edge:
        for u, v in itertools.combinations(range(args.n), 2):
            witnesses = []
            for w in range(args.n):
                if w in (u, v):
                    continue
                witness = fresh_variable(formula)
                witnesses.append(witness)
                formula.append([-witness, -edge_map[(min(u, w), max(u, w))]])
                formula.append([-witness, -edge_map[(min(v, w), max(v, w))]])
            formula.append([-edge_map[(u, v)], *witnesses])
    mismatches = []
    accepted = 0
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        for bits in itertools.product((False, True), repeat=len(variables)):
            assumptions = [var if bit else -var for (var, _), bit in zip(variables, bits)]
            cnf_accepts = solver.solve(assumptions=assumptions)
            edges = {edge for (_, edge), bit in zip(variables, bits) if bit}
            checker_accepts = verify_diameter2_critical(args.n, edges)["valid"]
            if checker_accepts and args.min_edges is not None:
                checker_accepts = len(edges) >= args.min_edges
            if checker_accepts and args.max_edges is not None:
                checker_accepts = len(edges) <= args.max_edges
            if checker_accepts and args.fix_triangle:
                checker_accepts = all(edge in edges for edge in ((0, 1), (0, 2), (1, 2)))
            if checker_accepts and args.degree_order:
                degrees = [sum(vertex in edge for edge in edges) for vertex in range(args.n)]
                blocks = [[0, 1, 2], list(range(3, args.n))] if args.fix_triangle else [list(range(args.n))]
                checker_accepts = all(
                    degrees[left] >= degrees[right]
                    for block in blocks
                    for left, right in zip(block, block[1:])
                )
            if checker_accepts and args.no_dominating_edge:
                neighbours = [set() for _ in range(args.n)]
                for u, v in edges:
                    neighbours[u].add(v)
                    neighbours[v].add(u)
                checker_accepts = all(
                    len(neighbours[u] | neighbours[v] | {u, v}) < args.n
                    for u, v in edges
                )
            accepted += int(cnf_accepts)
            if cnf_accepts != checker_accepts:
                mismatches.append({"bits": bits, "cnf": cnf_accepts, "checker": checker_accepts})
                if len(mismatches) >= 10:
                    break

    digest = hashlib.sha256(args.cnf.read_bytes()).hexdigest()
    result = {
        "n": args.n,
        "source_sha256": digest,
        "assignments": 1 << len(variables),
        "cnf_accepted": accepted,
        "degree_order": args.degree_order,
        "fix_triangle": args.fix_triangle,
        "no_dominating_edge": args.no_dominating_edge,
        "min_edges": args.min_edges,
        "max_edges": args.max_edges,
        "mismatches": mismatches,
        "pass": not mismatches,
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.result:
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(text, encoding="utf-8")
    print(text, end="")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
