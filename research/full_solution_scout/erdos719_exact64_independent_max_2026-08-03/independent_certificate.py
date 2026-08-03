#!/usr/bin/env python3
"""Independent certificate generator for the provisional exact-64 obstruction.

This file deliberately does not import either exact-64 search implementation.
It reconstructs triples, tetrahedra, packing cores, and the CNF from first
principles.  The cardinality constraints use a local Sinz-style sequential
counter rather than PySAT's totalizer used in the first certificate attempt.

Variables have these meanings:
  z_e: triple e is missing (exactly 20 true);
  c_B: tetrahedron B is clean/present;
  auxiliary sequential-counter variables have no mathematical meaning.

For a fixed three-tetrahedron edge-disjoint core P, the CNF asserts that P is
present and maximal, and that at most 21 tetrahedra are present.  Its UNSAT is
the finite obstruction required for that core type.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Solver


VERTICES = tuple(range(9))
TRIPLES = tuple(itertools.combinations(VERTICES, 3))
TRIPLE_ID = {t: i for i, t in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(VERTICES, 4))
BLOCK_EDGES = tuple(
    frozenset(TRIPLE_ID[t] for t in itertools.combinations(block, 3))
    for block in BLOCKS
)


def disjoint_as_hypergraphs(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    """Two tetrahedra share no triple iff their vertex intersection is <= 2."""
    return len(set(a).intersection(b)) <= 2


def membership_signature(core: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    """Canonical cell-size signature for an unlabeled three-block family.

    For labeled blocks, the sizes of the eight Venn cells classify the family
    up to a ground-set permutation.  Minimizing over the six block labelings
    therefore gives a complete isomorphism invariant, including isolated
    vertices through the 000 cell.
    """
    signatures = []
    for order in itertools.permutations(range(3)):
        cells = []
        for pattern in range(8):
            cells.append(sum(
                all((v in core[order[j]]) == bool(pattern & (1 << j)) for j in range(3))
                for v in VERTICES
            ))
        signatures.append(tuple(cells))
    return min(signatures)


def core_representatives() -> list[tuple[tuple[int, ...], ...]]:
    representatives: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    for core in itertools.combinations(BLOCKS, 3):
        if all(disjoint_as_hypergraphs(a, b) for a, b in itertools.combinations(core, 2)):
            representatives.setdefault(membership_signature(core), core)
    return [representatives[key] for key in sorted(representatives)]


@dataclass
class Builder:
    clauses: list[list[int]]
    top: int

    def fresh(self) -> int:
        self.top += 1
        return self.top

    def add(self, *literals: int) -> None:
        self.clauses.append(list(literals))

    def at_most(self, literals: tuple[int, ...], bound: int) -> None:
        """Sinz sequential counter, valid for signed input literals.

        s[i,j] means at least j+1 of literals[0:i+1] are true.  Only the
        forward implications needed for an at-most constraint are encoded.
        Boundary cases are handled explicitly.
        """
        n = len(literals)
        if bound < 0:
            self.add()
            return
        if bound >= n:
            return
        if bound == 0:
            for lit in literals:
                self.add(-lit)
            return
        # Rows exist for prefixes ending at positions 0,...,n-2.
        s = [[self.fresh() for _ in range(bound)] for _ in range(n - 1)]
        self.add(-literals[0], s[0][0])
        for j in range(1, bound):
            # The first one-element prefix cannot contain j+1 >= 2 trues.
            self.add(-s[0][j])
        for i in range(1, n - 1):
            self.add(-literals[i], s[i][0])
            self.add(-s[i - 1][0], s[i][0])
            for j in range(1, bound):
                self.add(-literals[i], -s[i - 1][j - 1], s[i][j])
                self.add(-s[i - 1][j], s[i][j])
            self.add(-literals[i], -s[i - 1][bound - 1])
        self.add(-literals[-1], -s[-1][bound - 1])

    def exactly(self, literals: tuple[int, ...], target: int) -> None:
        self.at_most(literals, target)
        # At least target true is at most n-target false.
        self.at_most(tuple(-lit for lit in literals), len(literals) - target)


def build_formula(core: tuple[tuple[int, ...], ...]) -> tuple[CNF, dict]:
    assert len(core) == 3
    assert all(disjoint_as_hypergraphs(a, b) for a, b in itertools.combinations(core, 2))
    zvars = tuple(range(1, 85))
    cvars = tuple(range(85, 211))
    b = Builder([], 210)
    b.exactly(zvars, 20)

    core_edge_ids = frozenset().union(*(
        frozenset(TRIPLE_ID[t] for t in itertools.combinations(block, 3))
        for block in core
    ))
    assert len(core_edge_ids) == 12
    for edge_id in sorted(core_edge_ids):
        b.add(-(edge_id + 1))

    compatible_count = 0
    for block_id, (block, edge_ids) in enumerate(zip(BLOCKS, BLOCK_EDGES)):
        c = cvars[block_id]
        # c is true iff all four z variables are false.
        for edge_id in sorted(edge_ids):
            b.add(-c, -(edge_id + 1))
        b.add(c, *(edge_id + 1 for edge_id in sorted(edge_ids)))
        # Maximality of the chosen packing core: every block edge-disjoint
        # from it must be dirty (contain a missing triple).
        if all(disjoint_as_hypergraphs(block, member) for member in core):
            assert edge_ids.isdisjoint(core_edge_ids)
            b.add(*(edge_id + 1 for edge_id in sorted(edge_ids)))
            compatible_count += 1

    b.at_most(cvars, 21)
    cnf = CNF(from_clauses=b.clauses)
    cnf.nv = b.top
    return cnf, {
        "core": [list(block) for block in core],
        "signature": list(membership_signature(core)),
        "core_edges": [list(TRIPLES[i]) for i in sorted(core_edge_ids)],
        "compatible_blocks": compatible_count,
        "variables": b.top,
        "clauses": len(b.clauses),
        "cardinality_encoding": "independent signed Sinz sequential counters",
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_glucose_proof(lines: list[str]) -> list[str]:
    out = []
    for raw in lines:
        line = raw.strip()
        if line.startswith("a "):
            line = line[2:]
        if line:
            out.append(line)
    if not out or out[-1] != "0":
        raise RuntimeError(f"proof lacks final empty clause; tail={out[-3:]}")
    return out


def self_test_counter() -> None:
    """Exhaustively test the local counter for all assignments through n=7."""
    for n in range(1, 8):
        for k in range(n + 1):
            b = Builder([], n)
            inputs = tuple(range(1, n + 1))
            b.at_most(inputs, k)
            for mask in range(1 << n):
                assumptions = [i + 1 if mask & (1 << i) else -(i + 1) for i in range(n)]
                with Solver(name="glucose4", bootstrap_with=b.clauses) as solver:
                    got = solver.solve(assumptions=assumptions)
                assert got == (mask.bit_count() <= k), (n, k, mask, got)


def generate(outdir: Path, first_type: int, last_type: int, solver_name: str) -> None:
    self_test_counter()
    reps = core_representatives()
    assert len(reps) == 10, len(reps)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "GENERATED_UNCHECKED_SOLVER_PROOFS",
        "independent_core_type_count": len(reps),
        "entries": [],
    }
    for type_id in range(first_type, last_type + 1):
        core = reps[type_id - 1]
        cnf, metadata = build_formula(core)
        stem = f"type_{type_id:02d}"
        cnf_path = outdir / f"{stem}.cnf"
        drat_path = outdir / f"{stem}.drat"
        cnf.to_file(str(cnf_path))
        with Solver(name=solver_name, bootstrap_with=cnf.clauses, with_proof=True) as solver:
            sat = solver.solve()
            if sat:
                model = solver.get_model()
                raise RuntimeError(f"unexpected SAT for {stem}: model prefix={model[:20]}")
            flush_return = ctypes.CDLL("ucrtbase")._flushall()
            proof = normalized_glucose_proof(solver.get_proof())
        drat_path.write_text("\n".join(proof) + "\n", encoding="ascii", newline="\n")
        entry = {
            "type": type_id,
            **metadata,
            "solver": solver_name,
            "solver_status": "UNSAT_UNCHECKED",
            "ucrt_flushall_return": flush_return,
            "cnf": cnf_path.name,
            "cnf_sha256": sha256(cnf_path),
            "cnf_bytes": cnf_path.stat().st_size,
            "drat": drat_path.name,
            "drat_sha256": sha256(drat_path),
            "drat_bytes": drat_path.stat().st_size,
        }
        manifest["entries"].append(entry)
        print(json.dumps(entry, sort_keys=True), flush=True)
    manifest_path = outdir / "manifest.generated.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(manifest_path, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--first-type", type=int, default=1)
    parser.add_argument("--last-type", type=int, default=10)
    parser.add_argument("--solver", default="glucose4")
    args = parser.parse_args()
    if not 1 <= args.first_type <= args.last_type <= 10:
        parser.error("require 1 <= first-type <= last-type <= 10")
    generate(args.outdir, args.first_type, args.last_type, args.solver)
