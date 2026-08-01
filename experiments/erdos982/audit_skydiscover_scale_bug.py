#!/usr/bin/env python3
"""Reproduce the scale bug in the public SkyDiscover Erdős-982 evaluators.

The script imports and calls the evaluator's own ``verify_solution`` function;
it does not reimplement the acceptance logic.  The public repository is
expected at the pinned commit recorded in the result file.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np


CASES = (
    ("erdos_982_convex_distances", 10, 2.3e-5),
    ("erdos_982_convex_n12", 12, 2.9e-5),
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repository = args.repository.resolve()
    math_root = repository / "skydiscover" / "benchmarks" / "math"
    commit = subprocess.check_output(
        ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True
    ).strip()

    records = []
    for benchmark, n, scale in CASES:
        evaluator_path = math_root / benchmark / "evaluator" / "evaluator.py"
        evaluator = load(evaluator_path, f"audit_{benchmark}")
        angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        points = scale * np.stack([np.cos(angles), np.sin(angles)], axis=1)
        reported = evaluator._max_vertex_distinct(points)
        accepted = evaluator.verify_solution(points, reported, n)
        pairwise = [
            float(np.linalg.norm(points[i] - points[j]))
            for i in range(n) for j in range(i)
        ]
        crosses = []
        for i in range(n):
            u = points[(i + 1) % n] - points[i]
            v = points[(i + 2) % n] - points[(i + 1) % n]
            crosses.append(float(abs(u[0] * v[1] - u[1] * v[0])))
        records.append({
            "benchmark": benchmark,
            "n": n,
            "scale": scale,
            "evaluator_sha256": sha256(evaluator_path),
            "evaluator_accepted": True,
            "evaluator_metric": int(accepted),
            "mathematical_regular_polygon_metric": n // 2,
            "minimum_pairwise_distance": min(pairwise),
            "minimum_consecutive_cross_product": min(crosses),
        })
        assert accepted == 1

    payload = {
        "public_repository": "https://github.com/Open-Galapagos/evolution-fine-tuning",
        "commit": commit,
        "finding": "scale-dependent false positive; not a counterexample to Erdős 982",
        "cause": "distance gaps are divided by max(|d1|,|d2|,1), while convexity and coincidence use fixed absolute thresholds",
        "records": records,
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
