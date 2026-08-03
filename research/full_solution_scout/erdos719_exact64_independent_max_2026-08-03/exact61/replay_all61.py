#!/usr/bin/env python3
"""One-command replay for the exact-61 independent certificate packet."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def run(args: list[str]) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run([
        sys.executable, "-B", str(HERE / "check_certificates61.py"),
        "--certdir", str(HERE / "certificates"),
        "--drat-trim", str(ROOT / "tools/proof_checkers/windows_drat/bin/drat-trim.exe"),
        "--lrat-check", str(ROOT / "tools/proof_checkers/windows_drat/bin/lrat-check.exe"),
    ])
    run([sys.executable, "-B", str(HERE / "structural_audit61.py")])
    print("ALL_EXACT61_INDEPENDENT_AUDITS_PASS", flush=True)


if __name__ == "__main__":
    main()
