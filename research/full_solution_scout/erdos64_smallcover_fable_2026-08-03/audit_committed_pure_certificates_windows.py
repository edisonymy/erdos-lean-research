#!/usr/bin/env python3
"""Replay the committed binary DRAT certificates on Windows.

The repository's Windows drat-trim build misparses Kissat's binary DRAT
stream on some nontrivial proofs.  This auditor decodes the documented
binary integer format to ASCII first, normalizes checked-out CNF line endings
back to their manifest-bound LF form, and then invokes drat-trim in ASCII
mode.  It never imports the SAT encoder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-fA-F]{64})\s+(.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[match.group(2).strip()] = match.group(1).upper()
    return result


def binary_drat_to_ascii(data: bytes) -> tuple[bytes, int, bool]:
    output: list[str] = []
    cursor = 0
    saw_empty = False
    while cursor < len(data):
        opcode = data[cursor]
        cursor += 1
        if opcode not in (ord("a"), ord("d")):
            raise ValueError(f"invalid binary DRAT opcode {opcode} at {cursor - 1}")
        literals: list[int] = []
        while True:
            value = 0
            shift = 0
            while True:
                if cursor >= len(data):
                    raise ValueError("truncated binary DRAT integer")
                byte = data[cursor]
                cursor += 1
                value |= (byte & 0x7F) << shift
                if byte < 0x80:
                    break
                shift += 7
            if value == 0:
                break
            literal = -(value >> 1) if value & 1 else value >> 1
            if literal == 0:
                raise ValueError("nonterminal binary literal decodes to zero")
            literals.append(literal)
        if opcode == ord("a") and not literals:
            saw_empty = True
        prefix = "d " if opcode == ord("d") else ""
        output.append(prefix + " ".join(map(str, literals)) + " 0\n")
    return "".join(output).encode("ascii"), len(output), saw_empty


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path(__file__).parent)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sigmas", type=int, nargs="+", default=list(range(5, 14)))
    args = parser.parse_args()

    expected = manifest(args.packet / "CERT_SHA256SUMS.txt")
    args.scratch.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.monotonic()
    for sigma in args.sigmas:
        cnf_name = f"pure_sigma{sigma}.cnf"
        proof_name = f"pure_sigma{sigma}.drat"
        cnf_source = (args.packet / cnf_name).read_bytes()
        proof_source = (args.packet / proof_name).read_bytes()
        cnf_lf = cnf_source.replace(b"\r\n", b"\n")
        cnf_hash = sha256(cnf_lf)
        proof_hash = sha256(proof_source)
        if cnf_hash != expected[cnf_name]:
            raise AssertionError(f"manifest CNF mismatch at sigma={sigma}")
        if proof_hash != expected[proof_name]:
            raise AssertionError(f"manifest proof mismatch at sigma={sigma}")

        ascii_proof, clauses, saw_empty = binary_drat_to_ascii(proof_source)
        if not saw_empty:
            raise AssertionError(f"proof has no empty addition at sigma={sigma}")
        cnf_path = args.scratch / cnf_name
        proof_path = args.scratch / f"pure_sigma{sigma}.ascii.drat"
        cnf_path.write_bytes(cnf_lf)
        proof_path.write_bytes(ascii_proof)
        checked = subprocess.run(
            [str(args.drat_trim), str(cnf_path), str(proof_path), "-I"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        transcript = checked.stdout + checked.stderr
        verified = checked.returncode == 0 and "s VERIFIED" in transcript
        rows.append(
            {
                "sigma": sigma,
                "cnf_sha256": cnf_hash,
                "binary_drat_sha256": proof_hash,
                "ascii_drat_sha256": sha256(ascii_proof),
                "proof_clauses": clauses,
                "empty_addition_present": saw_empty,
                "drat_trim_returncode": checked.returncode,
                "drat_trim_verified": verified,
                "transcript_tail": transcript[-1000:],
            }
        )
        if not verified:
            break

    payload = {
        "schema": "erdos64-fable-pure-committed-windows-audit-v1",
        "status": "VERIFIED" if len(rows) == len(args.sigmas) and all(
            row["drat_trim_verified"] for row in rows
        ) else "FAILED",
        "scope": "manifest-bound committed pure_sigma CNF/DRAT pairs only",
        "binary_decoder_imports_encoder": False,
        "sigmas_requested": args.sigmas,
        "rows": rows,
        "runtime_seconds": round(time.monotonic() - started, 6),
        "python": sys.version,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
