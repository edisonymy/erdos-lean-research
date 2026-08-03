#!/usr/bin/env python3
"""Independent finite-base audit for the d=2a+6 kernel gate.

The only base cases needed by the deletion induction are

    (n,q,e)=(9,5,13) and (11,6,16),  q=2n-e.

This auditor deliberately does not import the exploratory scanner.  It uses
its own graph6 parser, explicit four-cycle enumeration, degeneracy peeling,
and a subset dynamic program for eight-cycles.  Python standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from pathlib import Path


def decode_graph6(record: bytes) -> list[list[bool]]:
    raw = record.strip()
    prefix = b">>graph6<<"
    if raw.startswith(prefix):
        raw = raw[len(prefix) :]
    if not raw:
        raise ValueError("empty graph6 record")
    n = raw[0] - 63
    if not 0 <= n < 63:
        raise ValueError("auditor supports short graph6 only")
    payload = []
    for byte in raw[1:]:
        value = byte - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 byte")
        payload.extend(bool(value & (1 << shift)) for shift in range(5, -1, -1))
    matrix = [[False] * n for _ in range(n)]
    cursor = 0
    for upper in range(1, n):
        for lower in range(upper):
            if cursor >= len(payload):
                raise ValueError("truncated graph6 record")
            matrix[lower][upper] = matrix[upper][lower] = payload[cursor]
            cursor += 1
    return matrix


def contains_c4(matrix: list[list[bool]]) -> bool:
    for vertices in itertools.combinations(range(len(matrix)), 4):
        a, b, c, d = vertices
        for cycle in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
            if all(matrix[cycle[i]][cycle[(i + 1) % 4]] for i in range(4)):
                return True
    return False


def is_two_degenerate(matrix: list[list[bool]]) -> bool:
    n = len(matrix)
    alive = set(range(n))
    while alive:
        removable = next(
            (
                vertex
                for vertex in alive
                if sum(matrix[vertex][other] for other in alive) <= 2
            ),
            None,
        )
        if removable is None:
            return False
        alive.remove(removable)
    return True


def contains_c8(matrix: list[list[bool]]) -> bool:
    """Held--Karp path DP, with the least cycle vertex fixed as its start."""
    n = len(matrix)
    if n < 8:
        return False
    for start in range(n):
        states: set[tuple[int, int]] = {(1 << start, start)}
        for size in range(1, 8):
            next_states: set[tuple[int, int]] = set()
            for mask, last in states:
                for vertex in range(start + 1, n):
                    if not (mask & (1 << vertex)) and matrix[last][vertex]:
                        next_states.add((mask | (1 << vertex), vertex))
            states = next_states
            if not states:
                break
        if any(matrix[last][start] for mask, last in states if mask.bit_count() == 8):
            return True
    return False


def audit_case(geng: Path, n: int, q: int) -> dict[str, object]:
    edges = 2 * n - q
    command = [str(geng), "-q", "-c", "-d2", str(n), str(edges)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    assert process.stdout is not None
    counts = {
        "geng_records": 0,
        "c4_free": 0,
        "c4_free_2_degenerate": 0,
        "c4_c8_free_2_degenerate": 0,
    }
    survivors: list[str] = []
    for record in process.stdout:
        counts["geng_records"] += 1
        matrix = decode_graph6(record)
        if contains_c4(matrix):
            continue
        counts["c4_free"] += 1
        if not is_two_degenerate(matrix):
            continue
        counts["c4_free_2_degenerate"] += 1
        if contains_c8(matrix):
            continue
        counts["c4_c8_free_2_degenerate"] += 1
        survivors.append(record.decode("ascii").strip())
    if process.wait():
        raise RuntimeError("geng failed")
    return {"n": n, "q": q, "edges": edges, **counts, "survivors": survivors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geng", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "geng": str(args.geng),
        "geng_sha256": hashlib.sha256(args.geng.read_bytes()).hexdigest(),
        "cases": [audit_case(args.geng, 9, 5), audit_case(args.geng, 11, 6)],
        "dependencies": "Python standard library only; independent parser and cycle DP",
    }
    result["verified"] = all(
        case["c4_c8_free_2_degenerate"] == 0 for case in result["cases"]
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
