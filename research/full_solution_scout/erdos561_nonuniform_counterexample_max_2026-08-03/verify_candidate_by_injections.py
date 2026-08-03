#!/usr/bin/env python3
"""Definition-level verifier for any candidate emitted by search_all_hosts.py.

This verifier does not use the search program's adjacent-edge target detector.
It constructs every injective embedding of two fixed labelled target graphs,
then independently enumerates every red/blue edge assignment.  It can also
check a standalone candidate JSON copied into this directory.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEARCH = HERE / "search_result.json"
STANDALONE = HERE / "candidate.json"
OUT = HERE / "candidate_verification_injections.json"

RED_TARGET_N = 5
RED_TARGET_EDGES = ((0, 1), (0, 2), (3, 4))
BLUE_TARGET_N = 6
BLUE_TARGET_EDGES = ((0, 1), (0, 2), (3, 4), (3, 5))


def embedding_masks(n: int, host_edges: tuple[tuple[int, int], ...], target_n: int, target_edges):
    edge_index = {tuple(sorted(edge)): i for i, edge in enumerate(host_edges)}
    masks: set[int] = set()
    for image in itertools.permutations(range(n), target_n):
        required = [tuple(sorted((image[a], image[b]))) for a, b in target_edges]
        if all(edge in edge_index for edge in required):
            mask = 0
            for edge in required:
                mask |= 1 << edge_index[edge]
            masks.add(mask)
    return tuple(sorted(masks))


def verify_one(candidate: dict) -> dict:
    n = int(candidate["n"])
    edges = tuple(tuple(sorted(edge)) for edge in candidate["edges"])
    if len(edges) != len(set(edges)) or any(a == b for a, b in edges):
        raise ValueError("candidate is not a simple graph")
    red_embeddings = embedding_masks(n, edges, RED_TARGET_N, RED_TARGET_EDGES)
    blue_embeddings = embedding_masks(n, edges, BLUE_TARGET_N, BLUE_TARGET_EDGES)
    full = (1 << len(edges)) - 1
    avoiding = []
    for red in range(full + 1):
        blue = full ^ red
        if not any((red & p) == p for p in red_embeddings) and not any(
            (blue & p) == p for p in blue_embeddings
        ):
            avoiding.append(red)
    return {
        "n": n,
        "m": len(edges),
        "edges": [list(edge) for edge in edges],
        "red_injective_embedding_masks": len(red_embeddings),
        "blue_injective_embedding_masks": len(blue_embeddings),
        "colorings_checked": 1 << len(edges),
        "avoiding_red_masks": avoiding,
        "arrows": not avoiding,
    }


def main() -> None:
    if STANDALONE.exists():
        source = STANDALONE
        payload = json.loads(source.read_text(encoding="utf-8"))
        candidates = [payload]
    else:
        source = SEARCH
        payload = json.loads(source.read_text(encoding="utf-8"))
        candidates = payload["arrowing_hosts"]
    checks = [verify_one(candidate) for candidate in candidates]
    status = "VERIFIED" if candidates and all(row["arrows"] for row in checks) else (
        "NO_CANDIDATE" if not candidates else "FAILED"
    )
    result = {
        "status": status,
        "source": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "method": "all injective target embeddings and all edge 2-colorings",
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if status == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
