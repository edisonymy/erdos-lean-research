#!/usr/bin/env python3
"""Native DRAT-to-LRAT conversion and LRAT replay for all three formulas."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def checked(command: list[str], log: Path) -> dict:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log.write_text(result.stdout, encoding="utf-8", newline="\n")
    if result.returncode != 0 or ("s VERIFIED" not in result.stdout and "c VERIFIED" not in result.stdout):
        raise RuntimeError(f"checker failure {result.returncode}: {result.stdout[-2000:]}")
    return {"checker": Path(command[0]).name, "exit_code": result.returncode,
            "verified_marker": True, "log": log.name}


def main(certdir: Path, drat_trim: Path, lrat_check: Path) -> None:
    rows = []
    for type_id in range(1, 4):
        stem = f"type_{type_id:02d}"
        cnf = certdir / f"{stem}.cnf"
        drat = certdir / f"{stem}.drat"
        lrat = certdir / f"{stem}.lrat"
        print(f"{stem}: DRAT -> LRAT", flush=True)
        drat_status = checked(
            [str(drat_trim), str(cnf), str(drat), "-L", str(lrat)],
            certdir / f"{stem}.drat-trim.log",
        )
        print(f"{stem}: LRAT replay", flush=True)
        lrat_status = checked(
            [str(lrat_check), str(cnf), str(lrat)],
            certdir / f"{stem}.lrat-check.log",
        )
        row = {"type": type_id}
        for kind, path in (("cnf", cnf), ("drat", drat), ("lrat", lrat)):
            row[kind] = path.name
            row[f"{kind}_bytes"] = path.stat().st_size
            row[f"{kind}_sha256"] = sha256(path)
        row["drat_check"] = drat_status
        row["lrat_check"] = lrat_status
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    manifest = {
        "status": "ALL_THREE_EXACT61_INDEPENDENT_CERTIFICATES_NATIVE_VERIFIED",
        "claim_scope": "fixed-core exact23/maximal-core/q<=14 formulas only",
        "drat_trim": {"binary": drat_trim.name, "sha256": sha256(drat_trim)},
        "lrat_check": {"binary": lrat_check.name, "sha256": sha256(lrat_check)},
        "entries": rows,
    }
    path = certdir / "manifest.verified.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(path, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--certdir", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--lrat-check", type=Path, required=True)
    args = parser.parse_args()
    main(args.certdir.resolve(), args.drat_trim.resolve(), args.lrat_check.resolve())
