#!/usr/bin/env python3
"""Independently check a JSON (K_6, K_6)-Ramsey graph certificate."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.certificate.read_text())
    n = payload["n"]
    raw_edges = payload["edges"]
    edges = {tuple(sorted(edge)) for edge in raw_edges}
    assert len(edges) == len(raw_edges), "duplicate edge"
    assert all(0 <= u < v < n for u, v in edges), "invalid edge"

    checked = 0
    for vertices in itertools.combinations(range(n), 6):
        pairs = list(itertools.combinations(vertices, 2))
        count = sum(pair in edges for pair in pairs)
        assert count != 0, f"independent six-set: {vertices}"
        assert count != 15, f"six-clique: {vertices}"
        checked += 1

    degrees = [sum(v in edge for edge in edges) for v in range(n)]
    print(
        f"PASS n={n} edges={len(edges)} six_sets_checked={checked} "
        f"degree_sequence={sorted(degrees)}"
    )


if __name__ == "__main__":
    main()
