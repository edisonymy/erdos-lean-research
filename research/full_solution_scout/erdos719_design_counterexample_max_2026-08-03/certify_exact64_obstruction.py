#!/usr/bin/env python3
"""Generate checkable CNF/DRAT certificates excluding the exact-64 window.

For each isomorphism type of a three-tetrahedron packing core P, encode:

* exactly 20 missing triples;
* the 12 triples of P are present;
* every tetrahedron edge-disjoint from all of P is dirty (P is maximal);
* at most 21 tetrahedra are clean.

Every formula is UNSAT.  The last bound is forced in a genuine nu=3 graph by
the explicit 18-block SQS(10) averaging argument q <= 7 nu = 21.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

V = tuple(range(9))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {e: i for i, e in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))
BEDGES = tuple(frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in BLOCKS)


def compatible(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return len(set(a) & set(b)) <= 2


def core_key(core: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    keys = []
    for perm in itertools.permutations(range(3)):
        keys.append(tuple(
            sum(
                all(((v in core[perm[j]]) == bool(pat & (1 << j))) for j in range(3))
                for v in V
            )
            for pat in range(8)
        ))
    return min(keys)


def representatives() -> dict[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    reps = {}
    for ids in itertools.combinations(range(len(BLOCKS)), 3):
        core = tuple(BLOCKS[i] for i in ids)
        if all(compatible(core[i], core[j]) for i, j in itertools.combinations(range(3), 2)):
            reps.setdefault(core_key(core), core)
    return reps


def build_cnf(core: tuple[tuple[int, ...], ...]) -> tuple[CNF, dict]:
    # z_e = e is missing, variables 1..84.
    # c_B = B is clean, variables 85..210.
    cnf = CNF()
    zvars = tuple(range(1, 85))
    cvars = tuple(range(85, 211))
    top = 210

    exact = CardEnc.equals(zvars, bound=20, top_id=top, encoding=EncType.totalizer)
    cnf.extend(exact.clauses)
    top = exact.nv

    core_edges = frozenset().union(*(
        frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in core
    ))
    assert len(core_edges) == 12
    for e in sorted(core_edges):
        cnf.append([-(e + 1)])

    compatible_blocks = []
    for bi, (b, be) in enumerate(zip(BLOCKS, BEDGES)):
        c = cvars[bi]
        # c_B iff all four triples are present.
        for e in sorted(be):
            cnf.append([-c, -(e + 1)])
        cnf.append([c] + [e + 1 for e in sorted(be)])
        if all(compatible(b, p) for p in core):
            assert be.isdisjoint(core_edges)
            cnf.append([e + 1 for e in sorted(be)])
            compatible_blocks.append(bi)

    atmost = CardEnc.atmost(cvars, bound=21, top_id=top, encoding=EncType.totalizer)
    cnf.extend(atmost.clauses)
    cnf.nv = max(cnf.nv, atmost.nv)
    meta = {
        "core": [list(b) for b in core],
        "core_key": list(core_key(core)),
        "core_edges": [list(TRIPLES[e]) for e in sorted(core_edges)],
        "compatible_blocks": len(compatible_blocks),
        "variables": cnf.nv,
        "clauses": len(cnf.clauses),
        "encoding": "PySAT totalizer: exactly20 z; c_B iff clean; maximal core; atmost21 c",
    }
    return cnf, meta


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_proof(lines: list[str]) -> list[str]:
    out = []
    for raw in lines:
        line = raw.strip()
        if line.startswith("a "):
            line = line[2:]
        # CaDiCaL deletion lines already have the standard leading d.
        out.append(line)
    if not out or out[-1] != "0":
        raise RuntimeError(f"proof export is incomplete; no terminal empty clause: tail={out[-3:]}")
    return out


def run(outdir: Path, solver_name: str, limit_types: int | None) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    reps = representatives()
    manifest = {
        "status": "GENERATED_UNCHECKED_DRAT",
        "core_type_count": len(reps),
        "entries": [],
    }
    assert len(reps) == 10
    keys = sorted(reps)
    if limit_types is not None:
        keys = keys[:limit_types]
    for i, key in enumerate(keys, 1):
        cnf, meta = build_cnf(reps[key])
        stem = f"type_{i:02d}"
        cnf_path = outdir / f"{stem}.cnf"
        proof_path = outdir / f"{stem}.drat"
        cnf.to_file(str(cnf_path))
        with Solver(name=solver_name, bootstrap_with=cnf.clauses, with_proof=True) as solver:
            sat = solver.solve()
            if sat:
                raise RuntimeError(f"unexpected SAT for {stem}")
            # On Windows the native solver writes through UCRT stdio while
            # PySAT reads the underlying temporary file directly.  Without
            # this flush, get_proof() silently returns a buffer-aligned prefix
            # (the source of the preserved failed CaDiCaL traces).
            flush_count = ctypes.CDLL("ucrtbase")._flushall()
            proof = normalize_proof(solver.get_proof())
        proof_path.write_text("\n".join(proof) + "\n", encoding="ascii", newline="\n")
        entry = {
            "type": i,
            **meta,
            "solver": f"PySAT {solver_name} with_proof=True",
            "solver_status": "UNSAT",
            "ucrt_flushall_return": flush_count,
            "cnf": cnf_path.name,
            "cnf_sha256": sha256(cnf_path),
            "cnf_bytes": cnf_path.stat().st_size,
            "drat": proof_path.name,
            "drat_sha256": sha256(proof_path),
            "drat_bytes": proof_path.stat().st_size,
        }
        manifest["entries"].append(entry)
        print(f"{stem}: UNSAT, cnf={entry['cnf_bytes']}, drat={entry['drat_bytes']}", flush=True)
    manifest_path = outdir / "manifest.generated.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(manifest_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=Path(__file__).with_name("certificates"))
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--limit-types", type=int)
    args = parser.parse_args()
    run(args.outdir, args.solver, args.limit_types)
