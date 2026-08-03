#!/usr/bin/env python3
"""Run the three remaining label-safe m=2 replay jobs concurrently."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "marked_factor_gluing_search.py"
JOBS = (
    ("c2-cadical195", "2", "cadical195", "marked_candidate2_corrected_cadical195.json"),
    ("c1-glucose42", "1", "glucose42", "marked_candidate1_corrected_glucose42.json"),
    ("c2-glucose42", "2", "glucose42", "marked_candidate2_corrected_glucose42.json"),
)


def main() -> None:
    running = []
    for label, candidate, solver, output_name in JOBS:
        stdout_path = HERE / f"{label}.stdout.log"
        stderr_path = HERE / f"{label}.stderr.log"
        stdout = stdout_path.open("w", encoding="utf-8")
        stderr = stderr_path.open("w", encoding="utf-8")
        process = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--candidate",
                candidate,
                "--solver",
                solver,
                "--quiet",
                "--output",
                str(HERE / output_name),
            ],
            stdout=stdout,
            stderr=stderr,
        )
        running.append((label, process, stdout, stderr, stdout_path, stderr_path))

    while any(process.poll() is None for _, process, *_ in running):
        time.sleep(1)

    failed = False
    for label, process, stdout, stderr, stdout_path, stderr_path in running:
        stdout.close()
        stderr.close()
        print(label, stdout_path.read_text(encoding="utf-8").strip(), flush=True)
        if process.returncode:
            failed = True
            print(stderr_path.read_text(encoding="utf-8"), file=sys.stderr, flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
