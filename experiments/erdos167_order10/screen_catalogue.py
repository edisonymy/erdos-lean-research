#!/usr/bin/env python3
"""Filter McKay's complete order-10 catalogue to the Puleo residual.

Input lines encode complement graphs C in graph6.  The corresponding dense
graph G=K_10-C can only evade Puleo's mad(G)<7 theorem if at least one holds:

* |E(C)| <= 10 (G itself has at least 35 edges);
* |E(C-v)| <= 4 for some v (some 9-vertex subgraph has >= 32 edges);
* C-{u,v} is empty for some u,v (G contains K_8).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path


N = 10
EDGES = tuple((i, j) for j in range(1, N) for i in range(j))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}


def decode_graph6(line: bytes) -> int:
    line = line.strip()
    if len(line) != 9 or line[0] != 63 + N:
        raise ValueError(f"unexpected order-10 graph6 line: {line!r}")
    mask = 0
    bit_index = 0
    for char in line[1:]:
        value = char - 63
        if not 0 <= value < 64:
            raise ValueError(f"invalid graph6 byte: {char}")
        for shift in range(5, -1, -1):
            if bit_index < len(EDGES) and value & (1 << shift):
                mask |= 1 << bit_index
            bit_index += 1
    return mask


def residual_family(mask: int) -> int:
    """Bit field: 1=global density, 2=dense 9-subgraph, 4=contains K8."""
    edge_count = mask.bit_count()
    if edge_count > 17:
        return 0

    family = int(edge_count <= 10)

    degrees = [0] * N
    for index, (u, v) in enumerate(EDGES):
        if mask & (1 << index):
            degrees[u] += 1
            degrees[v] += 1

    if edge_count <= 13 and any(edge_count - degrees[v] <= 4 for v in range(N)):
        family |= 2

    # C-{u,v} is empty exactly when every complement edge touches u or v.
    for u in range(N):
        for v in range(u + 1, N):
            if edge_count - degrees[u] - degrees[v] + int(
                bool(mask & (1 << EDGE_INDEX[(u, v)]))
            ) == 0:
                family |= 4
                return family
    return family


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()

    total = 0
    selected = 0
    selected_by_family: dict[str, int] = {}
    input_digest = hashlib.sha256()
    output_digest = hashlib.sha256()

    with gzip.open(args.catalogue, "rb") as source, args.output.open("wb") as out:
        for line in source:
            total += 1
            input_digest.update(line)
            mask = decode_graph6(line)
            family = residual_family(mask)
            if not family:
                continue
            selected += 1
            selected_by_family[str(family)] = selected_by_family.get(str(family), 0) + 1
            out.write(line)
            output_digest.update(line)

    summary = {
        "schema": "tuza-order-10-puleo-residual-screen-v1",
        "catalogue_records": total,
        "catalogue_uncompressed_sha256": input_digest.hexdigest(),
        "residual_records": selected,
        "residual_graph6_sha256": output_digest.hexdigest(),
        "family_bit_counts": selected_by_family,
        "family_bits": {
            "1": "complement has at most 10 edges",
            "2": "delete one complement vertex and at most 4 edges remain",
            "4": "two complement vertices cover every complement edge",
        },
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
