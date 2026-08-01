#!/usr/bin/env python3
"""Proof-producing CNF for the three exhaustive order-16 cross-degree cases.

This translates the native cardinalities in ``minicard_cross_search.py`` to
PySAT's sequential-counter CNF.  It only builds DIMACS; solving and certificate
checking are deliberately separate stages in ``cross_proof_pipeline.ps1``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


N = 16
INDEPENDENT_SIZE = 6
HALF_SIZE = 8
HALF_EDGE_THRESHOLD = 6
GLOBAL_EDGE_THRESHOLD = 26
I = range(INDEPENDENT_SIZE)
O = range(INDEPENDENT_SIZE, N)


def pairs(n: int) -> list[tuple[int, int]]:
    return list(itertools.combinations(range(n), 2))


def append_atleast(
    cnf: CNF, pool: IDPool, literals: Iterable[int], bound: int
) -> tuple[int, int]:
    """Append a sequential-counter encoding of ``sum(literals) >= bound``.

    Return the numbers of new clauses and new variables.  The function is
    intentionally public so the retained semantic audit can exercise the
    exact helper used by the order-16 generator.
    """

    lits = list(literals)
    if len(set(map(abs, lits))) != len(lits) or any(lit == 0 for lit in lits):
        raise ValueError("cardinality literals must be nonzero distinct variables")
    if not 0 <= bound <= len(lits):
        raise ValueError("cardinality bound must lie between zero and its width")
    if any(abs(lit) > pool.top for lit in lits):
        raise ValueError("cardinality literal has not been allocated in the ID pool")

    before_clauses = len(cnf.clauses)
    before_variables = pool.top
    encoded = CardEnc.atleast(
        lits=lits,
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoded.clauses)
    # Trivial bound zero introduces no clauses, so CNF.extend has no literal
    # from which to learn the already allocated input-variable maximum.
    cnf.nv = max(cnf.nv, pool.top)
    if cnf.nv != pool.top:
        raise AssertionError("CNF and ID-pool variable maxima diverged")
    return len(cnf.clauses) - before_clauses, pool.top - before_variables


def append_maximal_triangle_free(
    cnf: CNF,
    pool: IDPool,
    edge_variables: dict[tuple[int, int], int],
    n: int,
) -> tuple[int, int]:
    """Add an existential common-neighbour witness for every absent edge."""

    before_clauses = len(cnf.clauses)
    before_variables = pool.top

    def edge(i: int, j: int) -> int:
        return edge_variables[tuple(sorted((i, j)))]

    for i, j in itertools.combinations(range(n), 2):
        witnesses: list[int] = []
        for k in range(n):
            if k in (i, j):
                continue
            witness = pool.id(("common", i, j, k))
            witnesses.append(witness)
            cnf.append([-witness, edge(i, k)])
            cnf.append([-witness, edge(j, k)])
        cnf.append([edge(i, j), *witnesses])
    return len(cnf.clauses) - before_clauses, pool.top - before_variables


def _record_delta(
    groups: dict[str, dict[str, int]],
    name: str,
    cnf: CNF,
    pool: IDPool,
    before_clauses: int,
    before_variables: int,
    source_constraints: int,
) -> None:
    groups[name] = {
        "source_constraints": source_constraints,
        "cnf_clauses": len(cnf.clauses) - before_clauses,
        "new_variables": pool.top - before_variables,
    }


def build_cross_formula(cross_degree: int) -> tuple[CNF, dict[str, Any]]:
    if cross_degree not in (1, 2, 3):
        raise ValueError("cross degree must be 1, 2, or 3")

    started = time.monotonic()
    pool = IDPool()
    edge_variables = {
        (i, j): pool.id(("edge", i, j))
        for i in range(N)
        for j in range(i + 1, N)
    }
    if list(edge_variables.values()) != list(range(1, 121)):
        raise AssertionError("the 120 edge variables are not the DIMACS prefix 1..120")

    def edge(i: int, j: int) -> int:
        return edge_variables[tuple(sorted((i, j)))]

    cnf = CNF()
    groups: dict[str, dict[str, int]] = {}

    before_c, before_v = len(cnf.clauses), pool.top
    for i, j, k in itertools.combinations(range(N), 3):
        cnf.append([-edge(i, j), -edge(i, k), -edge(j, k)])
    _record_delta(groups, "triangle_free", cnf, pool, before_c, before_v, 560)

    before_c, before_v = len(cnf.clauses), pool.top
    for i, j in itertools.combinations(I, 2):
        cnf.append([-edge(i, j)])
    _record_delta(groups, "fixed_independent_six", cnf, pool, before_c, before_v, 15)

    before_c, before_v = len(cnf.clauses), pool.top
    for subset in itertools.combinations(range(N), 7):
        cnf.append([edge(i, j) for i, j in itertools.combinations(subset, 2)])
    _record_delta(groups, "alpha_at_most_six", cnf, pool, before_c, before_v, 11440)

    before_c, before_v = len(cnf.clauses), pool.top
    for subset in itertools.combinations(range(N), HALF_SIZE):
        append_atleast(
            cnf,
            pool,
            (edge(i, j) for i, j in itertools.combinations(subset, 2)),
            HALF_EDGE_THRESHOLD,
        )
    _record_delta(groups, "dense_halves", cnf, pool, before_c, before_v, 12870)

    before_c, before_v = len(cnf.clauses), pool.top
    appended_c, appended_v = append_maximal_triangle_free(
        cnf, pool, edge_variables, N
    )
    if appended_c != 3480 or appended_v != 1680:
        raise AssertionError("unexpected maximality-witness dimensions")
    _record_delta(groups, "maximal_triangle_free", cnf, pool, before_c, before_v, 120)

    before_c, before_v = len(cnf.clauses), pool.top
    for i in I:
        cnf.append([edge(i, 6) if i < cross_degree else -edge(i, 6)])
    _record_delta(groups, "cross_prefix", cnf, pool, before_c, before_v, 6)

    before_c, before_v = len(cnf.clauses), pool.top
    for vertex in O:
        append_atleast(
            cnf,
            pool,
            (edge(i, vertex) for i in I),
            cross_degree,
        )
    _record_delta(groups, "minimum_cross_degree", cnf, pool, before_c, before_v, 10)

    before_c, before_v = len(cnf.clauses), pool.top
    append_atleast(cnf, pool, edge_variables.values(), GLOBAL_EDGE_THRESHOLD)
    _record_delta(groups, "global_edge_lower_bound", cnf, pool, before_c, before_v, 1)

    expected_sources = {
        "triangle_free": 560,
        "fixed_independent_six": 15,
        "alpha_at_most_six": 11440,
        "dense_halves": 12870,
        "maximal_triangle_free": 120,
        "cross_prefix": 6,
        "minimum_cross_degree": 10,
        "global_edge_lower_bound": 1,
    }
    if {name: record["source_constraints"] for name, record in groups.items()} != expected_sources:
        raise AssertionError("source-constraint group count mismatch")
    if cnf.nv != pool.top:
        raise AssertionError("final CNF and ID-pool variable maxima diverged")
    literal_variables: set[int] = set()
    for clause in cnf.clauses:
        if not clause:
            raise AssertionError("empty clause in satisfiable-source encoding")
        for literal in clause:
            variable = abs(literal)
            if literal == 0 or variable > pool.top:
                raise AssertionError("invalid or unallocated CNF literal")
            literal_variables.add(variable)
    # CardEnc obtains anonymous auxiliaries from IDPool._next(), so they do
    # not occur in IDPool.id2obj.  The literal support is the right integrity
    # check: with all values in 1..top, cardinality top proves gap-freedom.
    if len(literal_variables) != pool.top:
        raise AssertionError("the CNF literal support is not the gap-free interval 1..nv")

    metadata: dict[str, Any] = {
        "schema": "erdos128-cross-proof-cnf-v1",
        "n": N,
        "cross_degree": cross_degree,
        "symmetry": {
            "fixed_independent_set": list(I),
            "chosen_outside_vertex": 6,
            "chosen_neighbourhood": list(range(cross_degree)),
            "outside_neighbourhood_sorting": False,
        },
        "edge_variables": len(edge_variables),
        "edge_variable_interval": [1, 120],
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "constraint_groups": groups,
        "integrity": {
            "cnf_nv_equals_pool_top": True,
            "all_literals_allocated": True,
            "id_pool_gap_free": True,
            "edge_variables_are_prefix_1_to_120": True,
        },
        "build_seconds": time.monotonic() - started,
    }
    return cnf, metadata


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cross_degree", type=int, choices=(1, 2, 3))
    parser.add_argument("--dimacs", type=Path)
    parser.add_argument(
        "--measure-only",
        action="store_true",
        help="construct and audit the CNF in memory without writing DIMACS",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="permit replacement of an existing DIMACS path",
    )
    args = parser.parse_args()
    if not args.measure_only and args.dimacs is None:
        parser.error("provide --dimacs or select --measure-only")
    if args.measure_only and args.dimacs is not None:
        parser.error("--measure-only and --dimacs are mutually exclusive")
    if args.dimacs is not None and args.dimacs.exists() and not args.overwrite:
        parser.error("DIMACS path exists; use a fresh path or pass --overwrite")

    cnf, metadata = build_cross_formula(args.cross_degree)
    if args.dimacs is not None:
        args.dimacs.parent.mkdir(parents=True, exist_ok=True)
        cnf.to_file(str(args.dimacs))
        metadata["dimacs"] = {
            "path": str(args.dimacs),
            "bytes": args.dimacs.stat().st_size,
            "sha256": file_sha256(args.dimacs),
        }
    else:
        metadata["dimacs"] = None
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
