#!/usr/bin/env python3
"""Replay every complete pure-sigma CNF/DRAT pair committed in the packet."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(packet: Path, checker: Path, output: Path) -> int:
    records = []
    for sigma in range(5, 19):
        cnf = packet / f"pure_sigma{sigma}.cnf"
        proof = packet / f"pure_sigma{sigma}.drat"
        if not cnf.exists() or not proof.exists():
            records.append({
                "sigma": sigma,
                "cnf_present": cnf.exists(),
                "proof_present": proof.exists(),
                "status": "INCOMPLETE_PAIR",
            })
            continue
        proc = subprocess.run([str(checker), str(cnf), str(proof)],
                              capture_output=True, text=True)
        verified = "s VERIFIED" in proc.stdout
        records.append({
            "sigma": sigma,
            "cnf_present": True,
            "proof_present": True,
            "cnf_sha256_raw_checkout": sha(cnf),
            "proof_sha256_raw_checkout": sha(proof),
            "checker_exit": proc.returncode,
            "verified": verified,
            "status": "VERIFIED" if verified else "NOT_VERIFIED",
        })
    result = {
        "checker": str(checker),
        "records": records,
        "verified_sigmas": [r["sigma"] for r in records if r["status"] == "VERIFIED"],
        "incomplete_sigmas": [r["sigma"] for r in records if r["status"] == "INCOMPLETE_PAIR"],
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("verified_sigmas", "incomplete_sigmas")}, indent=2))
    return int(any(r["status"] == "NOT_VERIFIED" for r in records))


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
