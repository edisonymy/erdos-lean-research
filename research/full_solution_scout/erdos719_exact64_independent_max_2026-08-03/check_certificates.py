#!/usr/bin/env python3
"""Convert and check all ten independent DRAT certificates with native tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_checked(command: list[str], log_path: Path) -> dict:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_path.write_text(result.stdout, encoding="utf-8", newline="\n")
    if result.returncode != 0 or "s VERIFIED" not in result.stdout and "c VERIFIED" not in result.stdout:
        raise RuntimeError(
            f"checker failed ({result.returncode}): {' '.join(command)}\n"
            f"tail={result.stdout[-2000:]}"
        )
    return {
        "checker": Path(command[0]).name,
        "exit_code": result.returncode,
        "verified_marker": True,
        "log": log_path.name,
    }


def main(certdir: Path, drat_trim: Path, lrat_check: Path) -> None:
    entries = []
    for type_id in range(1, 11):
        stem = f"type_{type_id:02d}"
        cnf = certdir / f"{stem}.cnf"
        drat = certdir / f"{stem}.drat"
        lrat = certdir / f"{stem}.lrat"
        if not cnf.is_file() or not drat.is_file():
            raise FileNotFoundError(stem)
        print(f"{stem}: DRAT -> LRAT", flush=True)
        drat_result = run_checked(
            [str(drat_trim), str(cnf), str(drat), "-L", str(lrat)],
            certdir / f"{stem}.drat-trim.log",
        )
        print(f"{stem}: LRAT replay", flush=True)
        lrat_result = run_checked(
            [str(lrat_check), str(cnf), str(lrat)],
            certdir / f"{stem}.lrat-check.log",
        )
        entry = {
            "type": type_id,
            "cnf": cnf.name,
            "cnf_bytes": cnf.stat().st_size,
            "cnf_sha256": sha256(cnf),
            "drat": drat.name,
            "drat_bytes": drat.stat().st_size,
            "drat_sha256": sha256(drat),
            "lrat": lrat.name,
            "lrat_bytes": lrat.stat().st_size,
            "lrat_sha256": sha256(lrat),
            "drat_check": drat_result,
            "lrat_check": lrat_result,
        }
        entries.append(entry)
        print(json.dumps(entry, sort_keys=True), flush=True)
    manifest = {
        "status": "ALL_TEN_INDEPENDENT_CERTIFICATES_NATIVE_VERIFIED",
        "claim_scope": "fixed-core exact20/maximal-core/q<=21 formulas only",
        "drat_trim": {"binary": drat_trim.name, "sha256": sha256(drat_trim)},
        "lrat_check": {"binary": lrat_check.name, "sha256": sha256(lrat_check)},
        "entries": entries,
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
