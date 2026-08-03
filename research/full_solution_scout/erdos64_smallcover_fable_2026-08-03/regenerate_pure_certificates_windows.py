#!/usr/bin/env python3
"""Rebuild and certify the pure small-side formulas on Windows.

This is a portable successor to ``certify_pure.py``.  It regenerates the
static CNF from ``sat_search.build``, optionally checks its hash against the
packet manifest, obtains a fresh ASCII proof from a proof-logging PySAT
solver, and invokes an external ``drat-trim``.  The result is not labelled
verified unless every requested stage succeeds.

The script deliberately writes generated artifacts beneath ``--out-dir``;
it never replaces the packet's historical certificates.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from pysat.solvers import Solver

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sat_search  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-fA-F]{64})\s+(.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            entries[match.group(2).strip()] = match.group(1).upper()
    return entries


def write_dimacs(path: Path, nvars: int, clauses: list[list[int]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {nvars} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def flush_native_streams() -> None:
    """Make PySAT's native proof tempfile visible before ``get_proof``."""
    for runtime in ("ucrtbase", "msvcrt"):
        try:
            ctypes.CDLL(runtime).fflush(None)
        except OSError:
            pass


def write_proof(path: Path, lines: list[str]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        for line in lines:
            handle.write(line.rstrip("\r\n") + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sigmas", nargs="+", type=int)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parent / "CERT_SHA256SUMS.txt")
    parser.add_argument("--solver", choices=["cd195", "g3", "g4", "g42"], default="cd195")
    parser.add_argument("--drat-trim", type=Path)
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()

    expected = read_manifest(args.manifest)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    overall_start = time.monotonic()

    for sigma in args.sigmas:
        start = time.monotonic()
        pool, _x, _u, m_cap, clauses = sat_search.build(
            sigma, exact3=False, verbose=False
        )
        cnf_name = f"pure_sigma{sigma}.cnf"
        cnf_path = args.out_dir / cnf_name
        write_dimacs(cnf_path, pool.top, clauses)
        cnf_hash = sha256(cnf_path)
        expected_hash = expected.get(cnf_name)
        hash_match = expected_hash is None or cnf_hash == expected_hash
        row: dict[str, object] = {
            "sigma": sigma,
            "line_cap": m_cap,
            "variables": pool.top,
            "clauses": len(clauses),
            "cnf": str(cnf_path),
            "cnf_sha256": cnf_hash,
            "expected_cnf_sha256": expected_hash,
            "manifest_cnf_match": hash_match,
            "status": "CNF_GENERATED",
        }
        if not hash_match:
            row["status"] = "CNF_HASH_MISMATCH"
            rows.append(row)
            break
        if args.generate_only:
            row["seconds"] = round(time.monotonic() - start, 6)
            rows.append(row)
            continue

        proof_path = args.out_dir / f"pure_sigma{sigma}.{args.solver}.ascii.drat"
        with Solver(name=args.solver, bootstrap_with=clauses, with_proof=True) as solver:
            sat = solver.solve()
            flush_native_streams()
            proof = None if sat else solver.get_proof()
        row["sat"] = sat
        if sat or proof is None:
            row["status"] = "SAT_OR_NO_PROOF"
            rows.append(row)
            break
        write_proof(proof_path, proof)
        row.update(
            {
                "proof": str(proof_path),
                "proof_lines": len(proof),
                "proof_sha256": sha256(proof_path),
                "status": "UNSAT_PROOF_EXPORTED_UNCHECKED",
            }
        )
        if args.drat_trim is not None:
            checked = subprocess.run(
                [str(args.drat_trim), str(cnf_path), str(proof_path), "-I"],
                capture_output=True,
                text=True,
                errors="replace",
            )
            transcript = checked.stdout + checked.stderr
            verified = checked.returncode == 0 and "s VERIFIED" in transcript
            row.update(
                {
                    "drat_trim_returncode": checked.returncode,
                    "drat_trim_verified": verified,
                    "drat_trim_transcript_tail": transcript[-2000:],
                    "status": "VERIFIED" if verified else "PROOF_CHECK_FAILED",
                }
            )
        row["seconds"] = round(time.monotonic() - start, 6)
        rows.append(row)
        if row["status"] in {"PROOF_CHECK_FAILED", "SAT_OR_NO_PROOF"}:
            break

    all_expected = len(rows) == len(args.sigmas)
    if args.generate_only:
        good = all_expected and all(row["status"] == "CNF_GENERATED" for row in rows)
        status = "GENERATED" if good else "FAILED"
    elif args.drat_trim is not None:
        good = all_expected and all(row["status"] == "VERIFIED" for row in rows)
        status = "VERIFIED" if good else "FAILED"
    else:
        good = all_expected and all(
            row["status"] == "UNSAT_PROOF_EXPORTED_UNCHECKED" for row in rows
        )
        status = "UNSAT_PROOFS_EXPORTED_UNCHECKED" if good else "FAILED"
    payload = {
        "schema": "erdos64-pure-windows-regeneration-v1",
        "status": status,
        "solver": None if args.generate_only else args.solver,
        "encoder": str(Path(sat_search.__file__).resolve()),
        "manifest": str(args.manifest.resolve()),
        "rows": rows,
        "runtime_seconds": round(time.monotonic() - overall_start, 6),
        "python": sys.version,
    }
    args.result.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
