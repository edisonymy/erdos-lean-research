"""Independent exhaustive verifier for a JSON K_26 edge-coloring certificate."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    data = json.loads(args.candidate.read_text())
    n = data["n"]
    colors = data["colors"]
    matrix = data["matrix"]
    assert n == 26 and colors == 5 and len(matrix) == n
    counts = [0] * colors
    for u in range(n):
        assert len(matrix[u]) == n and matrix[u][u] == -1
        for v in range(u + 1, n):
            c = matrix[u][v]
            assert matrix[v][u] == c and 0 <= c < colors
            counts[c] += 1
    checked = 0
    for subset in itertools.combinations(range(n), 6):
        seen = {matrix[u][v] for u, v in itertools.combinations(subset, 2)}
        checked += 1
        if len(seen) != colors:
            raise SystemExit(f"FAIL subset={subset} colors_seen={sorted(seen)} checked={checked}")
    print(f"PASS edges_per_color={counts} six_sets_checked={checked}")


if __name__ == "__main__":
    main()
