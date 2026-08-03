#!/usr/bin/env python3
"""One-command replay of both independently certified n=9 windows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(path: Path) -> None:
    command = [sys.executable, "-B", str(path)]
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run(HERE / "replay_all.py")
    run(HERE / "exact61/replay_all61.py")
    print("ALL_ERDOS719_N9_INDEPENDENT_AUDITS_PASS", flush=True)


if __name__ == "__main__":
    main()
