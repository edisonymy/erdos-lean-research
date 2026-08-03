#!/usr/bin/env python3
"""Independent six-pair audit of the connected order-13 4-regular catalogue."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


N = 13


def parse(line: str) -> tuple[list[tuple[int, int]], list[int]]:
    fields = line.split()
    assert fields[0] == "13" and len(fields[1]) == 78
    bits = iter(fields[1])
    edges: list[tuple[int, int]] = []
    adjacency = [0] * N
    for left in range(N):
        for right in range(left + 1, N):
            if next(bits) == "1":
                edges.append((left, right))
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
    assert [x.bit_count() for x in adjacency] == [4] * N
    return edges, adjacency


def reverse_greedy_six(edges: list[tuple[int, int]], adjacency: list[int]):
    masks = [(1 << a) | (1 << b) for a, b in edges]
    candidates: list[tuple[int, int]] = []
    for i in range(len(edges) - 1, -1, -1):
        a, b = edges[i]
        forbidden = adjacency[a] | adjacency[b] | masks[i]
        for j in range(i - 1, -1, -1):
            if not forbidden & masks[j]:
                candidates.append((i, j))
    used = 0
    chosen = []
    for i, j in candidates:
        pair_mask = (1 << i) | (1 << j)
        if not used & pair_mask:
            used |= pair_mask
            chosen.append((i, j))
            if len(chosen) == 6:
                return chosen
    return None


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    catalogue = here / "13_4reg.txt"
    primary_path = here / "n13_4regular_result.json"
    raw = catalogue.read_bytes()
    lines = raw.decode("ascii").splitlines()
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    failures = []
    for index, line in enumerate(lines):
        edges, adjacency = parse(line)
        chosen = reverse_greedy_six(edges, adjacency)
        if chosen is None:
            failures.append({"index": index, "line": line})
    digest = hashlib.sha256(raw).hexdigest()
    assertions = {
        "record_count_is_10778": len(lines) == 10778,
        "records_unique": len(set(lines)) == len(lines),
        "catalogue_hash_matches_primary": digest == primary["catalogue"]["sha256"],
        "primary_verified": primary["status"] == "VERIFIED" and not primary["failures"],
        "fresh_failures_empty": not failures,
    }
    result = {
        "schema": "erdos149-n13-4regular-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "catalogue": {
            "records": len(lines),
            "unique_records": len(set(lines)),
            "bytes": len(raw),
            "sha256": digest,
        },
        "fresh_reverse_greedy_matchings_of_six": len(lines) - len(failures),
        "failures": failures,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This audit covers only the connected order-13 4-regular catalogue slice.",
    }
    out = here / "n13_4regular_fresh_audit.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "records": len(lines), "failures": len(failures), "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
