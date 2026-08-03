#!/usr/bin/env python3
"""Independent verifier 1 for meta_candidate.json: injective embeddings."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "meta_candidate.json"
OUT = HERE / "meta_candidate_injection_verification.json"


def labelled_target_edges(degrees):
    edges = []
    cursor = 0
    for degree in degrees:
        center = cursor
        cursor += 1
        for _ in range(degree):
            edges.append((center, cursor))
            cursor += 1
    return cursor, tuple(edges)


def embedding_masks(n, host_edges, degrees):
    target_n, target_edges = labelled_target_edges(degrees)
    edge_index = {tuple(sorted(edge)): i for i, edge in enumerate(host_edges)}
    masks = set()
    for image in itertools.permutations(range(n), target_n):
        required = [tuple(sorted((image[a], image[b]))) for a, b in target_edges]
        if all(edge in edge_index for edge in required):
            mask = 0
            for edge in required:
                mask |= 1 << edge_index[edge]
            masks.add(mask)
    return tuple(sorted(masks))


def main():
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    n = int(candidate["n"])
    edges = tuple(tuple(sorted(edge)) for edge in candidate["edges"])
    red_patterns = embedding_masks(n, edges, candidate["red_degrees"])
    blue_patterns = embedding_masks(n, edges, candidate["blue_degrees"])
    full = (1 << len(edges)) - 1
    avoiding = []
    for red in range(full + 1):
        blue = full ^ red
        if not any((red & p) == p for p in red_patterns) and not any(
            (blue & p) == p for p in blue_patterns
        ):
            avoiding.append(red)
    arrows = not avoiding
    result = {
        "status": "VERIFIED" if arrows else "FAILED",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "method": "all injective maps of labelled target graphs; all edge colorings",
        "red_embedding_masks": len(red_patterns),
        "blue_embedding_masks": len(blue_patterns),
        "colorings_checked": 1 << len(edges),
        "avoiding_red_masks": avoiding,
        "arrows": arrows,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not arrows:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
