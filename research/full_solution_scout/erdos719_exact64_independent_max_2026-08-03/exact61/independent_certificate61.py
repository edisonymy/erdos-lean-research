#!/usr/bin/env python3
"""Independent signed-Sinz certificates for the exact-61, nu=2 window.

This does not import any design-agent or totalizer CNF.  For each of the three
isomorphism types of a two-tetrahedron edge-disjoint packing core, it asserts:
exactly 23 missing triples, the core is present and maximal, and at most 14
tetrahedra are present.  The last bound is q <= 7*nu from the explicit
18-block packing.
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


V = tuple(range(9))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {t: i for i, t in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))
BEDGES = tuple(frozenset(TID[t] for t in itertools.combinations(b, 3)) for b in BLOCKS)


def edge_disjoint(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return len(set(a).intersection(b)) <= 2


CORES = (
    ((0, 1, 2, 3), (4, 5, 6, 7)),       # intersection 0
    ((0, 1, 2, 3), (0, 4, 5, 6)),       # intersection 1
    ((0, 1, 2, 3), (0, 1, 4, 5)),       # intersection 2
)


@dataclass
class Builder:
    clauses: list[list[int]]
    top: int

    def fresh(self) -> int:
        self.top += 1
        return self.top

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def at_most(self, literals: tuple[int, ...], bound: int) -> None:
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
        s = [[self.fresh() for _ in range(bound)] for _ in range(n - 1)]
        self.add(-literals[0], s[0][0])
        for j in range(1, bound):
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
        self.at_most(tuple(-lit for lit in literals), len(literals) - target)


def build_formula(core: tuple[tuple[int, ...], tuple[int, ...]]) -> tuple[CNF, dict]:
    assert edge_disjoint(*core)
    zvars = tuple(range(1, 85))
    cvars = tuple(range(85, 211))
    builder = Builder([], 210)
    builder.exactly(zvars, 23)
    core_edges = frozenset().union(*(BEDGES[BLOCKS.index(b)] for b in core))
    assert len(core_edges) == 8
    for e in sorted(core_edges):
        builder.add(-(e + 1))
    compatible = 0
    for block_id, (block, edges) in enumerate(zip(BLOCKS, BEDGES)):
        c = cvars[block_id]
        for e in sorted(edges):
            builder.add(-c, -(e + 1))
        builder.add(c, *(e + 1 for e in sorted(edges)))
        if all(edge_disjoint(block, member) for member in core):
            assert edges.isdisjoint(core_edges)
            builder.add(*(e + 1 for e in sorted(edges)))
            compatible += 1
    builder.at_most(cvars, 14)
    cnf = CNF(from_clauses=builder.clauses)
    cnf.nv = builder.top
    return cnf, {
        "core": [list(b) for b in core],
        "core_intersection": len(set(core[0]).intersection(core[1])),
        "core_edges": [list(TRIPLES[e]) for e in sorted(core_edges)],
        "compatible_blocks": compatible,
        "variables": builder.top,
        "clauses": len(builder.clauses),
        "encoding": "independent signed Sinz counters; exact23 z; c iff clean; maximal core; atmost14 c",
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(lines: list[str]) -> list[str]:
    out = []
    for raw in lines:
        line = raw.strip()
        if line.startswith("a "):
            line = line[2:]
        if line:
            out.append(line)
    if not out or out[-1] != "0":
        raise RuntimeError(f"incomplete proof: {out[-3:]}")
    return out


def counter_self_test() -> None:
    for n in range(1, 8):
        for k in range(n + 1):
            builder = Builder([], n)
            inputs = tuple(range(1, n + 1))
            builder.at_most(inputs, k)
            for mask in range(1 << n):
                assumptions = [i + 1 if mask & (1 << i) else -(i + 1) for i in range(n)]
                with Solver(name="glucose4", bootstrap_with=builder.clauses) as solver:
                    got = solver.solve(assumptions=assumptions)
                assert got == (mask.bit_count() <= k), (n, k, mask)


def generate(outdir: Path) -> None:
    counter_self_test()
    outdir.mkdir(parents=True, exist_ok=True)
    entries = []
    for type_id, core in enumerate(CORES, 1):
        cnf, meta = build_formula(core)
        stem = f"type_{type_id:02d}"
        cnf_path = outdir / f"{stem}.cnf"
        drat_path = outdir / f"{stem}.drat"
        cnf.to_file(str(cnf_path))
        with Solver(name="glucose4", bootstrap_with=cnf.clauses, with_proof=True) as solver:
            if solver.solve():
                raise RuntimeError(f"unexpected SAT: {stem}")
            flush_return = ctypes.CDLL("ucrtbase")._flushall()
            proof = normalize(solver.get_proof())
        drat_path.write_text("\n".join(proof) + "\n", encoding="ascii", newline="\n")
        row = {
            "type": type_id,
            **meta,
            "solver": "PySAT glucose4",
            "solver_status": "UNSAT_UNCHECKED",
            "ucrt_flushall_return": flush_return,
            "cnf": cnf_path.name,
            "cnf_bytes": cnf_path.stat().st_size,
            "cnf_sha256": sha256(cnf_path),
            "drat": drat_path.name,
            "drat_bytes": drat_path.stat().st_size,
            "drat_sha256": sha256(drat_path),
        }
        entries.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    manifest = {"status": "THREE_EXACT61_SOLVER_PROOFS_UNCHECKED", "entries": entries}
    (outdir / "manifest.generated.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    generate(args.outdir)
