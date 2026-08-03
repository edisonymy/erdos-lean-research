#!/usr/bin/env python3
"""Independent replay/audit for the exact-64 core-obstruction package."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import sys
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


def independent_key(core: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    """Canonical Venn-cell count vector, independently implemented."""
    candidates = []
    for order in itertools.permutations(core):
        cell_counts = Counter(tuple(i for i, b in enumerate(order) if v in b) for v in V)
        candidates.append(tuple(cell_counts[tuple(i for i in range(3) if mask & (1 << i))] for mask in range(8)))
    return min(candidates)


def audit_orbits(entries: list[dict]) -> dict:
    counts: Counter[tuple[int, ...]] = Counter()
    packing_count = 0
    for ids in itertools.combinations(range(126), 3):
        core = tuple(BLOCKS[i] for i in ids)
        if all(compatible(a, b) for a, b in itertools.combinations(core, 2)):
            counts[independent_key(core)] += 1
            packing_count += 1
    manifest_keys = {tuple(e["core_key"]) for e in entries}
    assert len(counts) == 10
    assert manifest_keys == set(counts)
    assert sum(counts.values()) == packing_count
    return {
        "packing_cores": packing_count,
        "orbit_count": len(counts),
        "orbit_sizes": {"/".join(map(str, k)): counts[k] for k in sorted(counts)},
    }


def audit_semantics(entry: dict, cnf: CNF) -> dict:
    clauses = Counter(tuple(c) for c in cnf.clauses)
    core = tuple(tuple(b) for b in entry["core"])
    assert independent_key(core) == tuple(entry["core_key"])
    assert all(compatible(a, b) for a, b in itertools.combinations(core, 2))
    core_edges = frozenset().union(*(
        frozenset(TID[e] for e in itertools.combinations(b, 3)) for b in core
    ))
    assert len(core_edges) == 12
    for e in core_edges:
        assert clauses[-(e + 1),] >= 1

    local = 0
    for bi, (b, be) in enumerate(zip(BLOCKS, BEDGES)):
        c = 85 + bi
        # These clauses establish c_B iff every edge of B is present, so the
        # at-most constraint counts all 126 clean tetrahedra.
        for e in be:
            assert clauses[-c, -(e + 1)] >= 1
        assert clauses[tuple([c] + [e + 1 for e in sorted(be)])] >= 1
        if all(compatible(b, p) for p in core):
            assert be.isdisjoint(core_edges)
            assert clauses[tuple(e + 1 for e in sorted(be))] >= 1
            local += 1
    assert local == entry["compatible_blocks"]
    return {
        "core_edges": len(core_edges),
        "all_clean_equivalences": 126,
        "compatible_block_hitting_clauses": local,
        "variables": cnf.nv,
        "clauses": len(cnf.clauses),
    }


def run(certdir: Path, checker: Path, output: Path) -> None:
    manifest_path = certdir / "manifest.generated.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    assert len(entries) == 10
    report = {
        "status": "CHECKING",
        "python": sys.version,
        "platform": platform.platform(),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "drat_trim": str(checker),
        "drat_trim_sha256": sha256(checker),
        "orbit_replay": audit_orbits(entries),
        "entries": [],
    }
    for entry in entries:
        cnf_path = certdir / entry["cnf"]
        proof_path = certdir / entry["drat"]
        assert sha256(cnf_path) == entry["cnf_sha256"]
        assert sha256(proof_path) == entry["drat_sha256"]
        cnf = CNF(from_file=str(cnf_path))
        semantics = audit_semantics(entry, cnf)
        proc = subprocess.run(
            [str(checker), str(cnf_path), str(proof_path), "-I"],
            cwd=str(Path.cwd()),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        verified = proc.returncode == 0 and "s VERIFIED" in proc.stdout
        row = {
            "type": entry["type"],
            "cnf_sha256": entry["cnf_sha256"],
            "drat_sha256": entry["drat_sha256"],
            "semantics": semantics,
            "checker_returncode": proc.returncode,
            "checker_verified": verified,
            "checker_output": proc.stdout,
        }
        report["entries"].append(row)
        print(f"type_{entry['type']:02d}: {'VERIFIED' if verified else 'FAILED'}", flush=True)
        if not verified:
            output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(1)
    report["status"] = "ALL_10_DRAT_VERIFIED_AND_ORBITS_REPLAYED"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--certdir", type=Path, required=True)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.certdir, args.checker, args.output)
