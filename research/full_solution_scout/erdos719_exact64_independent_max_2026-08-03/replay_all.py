#!/usr/bin/env python3
"""One-command native certificate replay plus structural audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    python = sys.executable
    run([
        python, "-B", str(HERE / "check_certificates.py"),
        "--certdir", str(HERE / "certificates"),
        "--drat-trim", str(ROOT / "tools/proof_checkers/windows_drat/bin/drat-trim.exe"),
        "--lrat-check", str(ROOT / "tools/proof_checkers/windows_drat/bin/lrat-check.exe"),
    ])
    run([python, "-B", str(HERE / "structural_audit.py")])
    print("ALL_EXACT64_INDEPENDENT_AUDITS_PASS", flush=True)


if __name__ == "__main__":
    main()
