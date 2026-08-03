#!/usr/bin/env python3
"""Generate flushed Glucose4 DRAT certificates excluding exact61/nu<=2."""

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


def representatives() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    # Two four-sets are classified up to S9 by intersection size.  Packing
    # compatibility allows exactly 0, 1, or 2.
    reps = {}
    for i, j in itertools.combinations(range(126), 2):
        a, b = BLOCKS[i], BLOCKS[j]
        s = len(set(a) & set(b))
        if s <= 2:
            reps.setdefault(s, (a, b))
    assert sorted(reps) == [0, 1, 2]
    return [reps[s] for s in sorted(reps)]


def build_cnf(core: tuple[tuple[int, ...], tuple[int, ...]]) -> tuple[CNF, dict]:
    cnf = CNF()
    zvars = tuple(range(1, 85))
    cvars = tuple(range(85, 211))
    exact = CardEnc.equals(zvars, bound=23, top_id=210, encoding=EncType.totalizer)
    cnf.extend(exact.clauses)
    top = exact.nv
    core_edges = frozenset().union(*(
        frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in core
    ))
    assert len(core_edges) == 8
    for e in sorted(core_edges):
        cnf.append([-(e + 1)])
    local = 0
    for bi, (b, be) in enumerate(zip(BLOCKS, BEDGES)):
        c = cvars[bi]
        for e in sorted(be):
            cnf.append([-c, -(e + 1)])
        cnf.append([c] + [e + 1 for e in sorted(be)])
        if all(compatible(b, p) for p in core):
            assert be.isdisjoint(core_edges)
            cnf.append([e + 1 for e in sorted(be)])
            local += 1
    atmost = CardEnc.atmost(cvars, bound=14, top_id=top, encoding=EncType.totalizer)
    cnf.extend(atmost.clauses)
    cnf.nv = max(cnf.nv, atmost.nv)
    return cnf, {
        "core": [list(b) for b in core],
        "intersection_size": len(set(core[0]) & set(core[1])),
        "core_edges": [list(TRIPLES[e]) for e in sorted(core_edges)],
        "compatible_blocks": local,
        "variables": cnf.nv,
        "clauses": len(cnf.clauses),
        "encoding": "PySAT totalizer: exactly23 z; c_B iff clean; maximal 2-core; atmost14 c",
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"status": "GENERATED_UNCHECKED_DRAT", "core_type_count": 3, "entries": []}
    for i, core in enumerate(representatives(), 1):
        cnf, meta = build_cnf(core)
        stem = f"type_{i:02d}"
        cp, pp = outdir / f"{stem}.cnf", outdir / f"{stem}.drat"
        cnf.to_file(str(cp))
        with Solver(name="glucose4", bootstrap_with=cnf.clauses, with_proof=True) as solver:
            assert solver.solve() is False
            flushed = ctypes.CDLL("ucrtbase")._flushall()
            proof = solver.get_proof()
            assert proof and proof[-1].strip() == "0", proof[-3:]
        pp.write_text("\n".join(line.strip() for line in proof) + "\n", encoding="ascii", newline="\n")
        entry = {
            "type": i,
            **meta,
            "solver": "PySAT glucose4 with_proof=True",
            "solver_status": "UNSAT",
            "ucrt_flushall_return": flushed,
            "cnf": cp.name,
            "cnf_sha256": sha256(cp),
            "cnf_bytes": cp.stat().st_size,
            "drat": pp.name,
            "drat_sha256": sha256(pp),
            "drat_bytes": pp.stat().st_size,
        }
        manifest["entries"].append(entry)
        print(f"{stem}: UNSAT, drat={pp.stat().st_size}", flush=True)
    mp = outdir / "manifest.generated.json"
    mp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(mp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=Path(__file__).with_name("certificates_exact61_glucose4"))
    args = parser.parse_args()
    run(args.outdir)
