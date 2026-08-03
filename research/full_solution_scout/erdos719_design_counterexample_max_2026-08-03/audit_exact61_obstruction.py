#!/usr/bin/env python3
"""Independent orbit/semantic/DRAT audit for the exact-61 obstruction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path

from pysat.formula import CNF

V = tuple(range(9))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {e: i for i, e in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))
BEDGES = tuple(frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in BLOCKS)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compatible(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return len(set(a) & set(b)) <= 2


def orbit_replay(entries: list[dict]) -> dict:
    counts = Counter()
    for a, b in itertools.combinations(BLOCKS, 2):
        s = len(set(a) & set(b))
        if s <= 2:
            counts[s] += 1
    assert set(counts) == {0, 1, 2}
    assert {e["intersection_size"] for e in entries} == {0, 1, 2}
    return {"orbit_count": 3, "orbit_sizes_by_intersection": dict(sorted(counts.items())), "packing_cores": sum(counts.values())}


def semantic_audit(entry: dict, cnf: CNF) -> dict:
    clauses = Counter(tuple(c) for c in cnf.clauses)
    core = tuple(tuple(b) for b in entry["core"])
    assert len(core) == 2
    assert len(set(core[0]) & set(core[1])) == entry["intersection_size"] <= 2
    core_edges = frozenset().union(*(
        frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in core
    ))
    assert len(core_edges) == 8
    for e in core_edges:
        assert clauses[-(e + 1),] >= 1
    local = 0
    for bi, (b, be) in enumerate(zip(BLOCKS, BEDGES)):
        c = 85 + bi
        for e in be:
            assert clauses[-c, -(e + 1)] >= 1
        assert clauses[tuple([c] + [e + 1 for e in sorted(be)])] >= 1
        if all(compatible(b, p) for p in core):
            assert be.isdisjoint(core_edges)
            assert clauses[tuple(e + 1 for e in sorted(be))] >= 1
            local += 1
    assert local == entry["compatible_blocks"]
    return {"core_edges": 8, "all_clean_equivalences": 126, "compatible_block_hitting_clauses": local, "variables": cnf.nv, "clauses": len(cnf.clauses)}


def run(certdir: Path, checker: Path, output: Path) -> None:
    mp = certdir / "manifest.generated.json"
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    assert len(entries) == 3
    report = {
        "status": "CHECKING",
        "manifest_sha256": sha256(mp),
        "drat_trim_sha256": sha256(checker),
        "orbit_replay": orbit_replay(entries),
        "entries": [],
    }
    for entry in entries:
        cp, pp = certdir / entry["cnf"], certdir / entry["drat"]
        assert sha256(cp) == entry["cnf_sha256"]
        assert sha256(pp) == entry["drat_sha256"]
        semantics = semantic_audit(entry, CNF(from_file=str(cp)))
        proc = subprocess.run([str(checker), str(cp), str(pp), "-I"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        ok = proc.returncode == 0 and "s VERIFIED" in proc.stdout
        report["entries"].append({
            "type": entry["type"], "intersection_size": entry["intersection_size"],
            "cnf_sha256": entry["cnf_sha256"], "drat_sha256": entry["drat_sha256"],
            "semantics": semantics, "checker_returncode": proc.returncode,
            "checker_verified": ok, "checker_output": proc.stdout,
        })
        print(f"type_{entry['type']:02d}: {'VERIFIED' if ok else 'FAILED'}", flush=True)
        if not ok:
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(1)
    report["status"] = "ALL_3_DRAT_VERIFIED_AND_ORBITS_REPLAYED"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(report["status"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--certdir", type=Path, required=True)
    p.add_argument("--checker", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    run(a.certdir, a.checker, a.output)
