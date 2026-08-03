#!/usr/bin/env python3
"""Independent verifier for enumerate_probe.py's #561 null/candidate result.

Independence points:
* connected graphs are generated as adjacency bitmasks, not edge combinations;
* canonical labels are maximum adjacency words, not minimum edge tuples;
* F is detected by injective maps of its five labelled vertices, not by
  intersecting triples of host edges;
* the expected disconnected catalogue is reconstructed separately.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "probe_result.json"
OUT = HERE / "independent_verification.json"
MAX_EDGES = 5


def edge_universe(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


def bit_edges(n: int, mask: int) -> tuple[tuple[int, int], ...]:
    u = edge_universe(n)
    return tuple(u[i] for i in range(len(u)) if mask >> i & 1)


def is_connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    reach = 1
    while True:
        old = reach
        for a, b in edges:
            if reach >> a & 1:
                reach |= 1 << b
            if reach >> b & 1:
                reach |= 1 << a
        if reach == old:
            return reach == (1 << n) - 1


def adjacency_word(n: int, edges: tuple[tuple[int, int], ...], order: tuple[int, ...]) -> str:
    eset = {tuple(sorted(e)) for e in edges}
    return "".join(
        "1" if tuple(sorted((order[i], order[j]))) in eset else "0"
        for i in range(n)
        for j in range(i + 1, n)
    )


def canon(n: int, edges: tuple[tuple[int, int], ...]) -> str:
    return max(adjacency_word(n, edges, p) for p in itertools.permutations(range(n)))


def independent_connected_types() -> dict[int, set[tuple[int, str]]]:
    answer: dict[int, set[tuple[int, str]]] = defaultdict(set)
    for n in range(2, MAX_EDGES + 2):
        width = n * (n - 1) // 2
        for mask in range(1 << width):
            m = mask.bit_count()
            if not 1 <= m <= MAX_EDGES or n > m + 1:
                continue
            edges = bit_edges(n, mask)
            if is_connected(n, edges):
                answer[m].add((n, canon(n, edges)))
    return answer


def components(n: int, edges: tuple[tuple[int, int], ...]) -> list[tuple[int, tuple[tuple[int, int], ...]]]:
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    unseen = set(range(n))
    out = []
    while unseen:
        seed = min(unseen)
        block = {seed}
        todo = [seed]
        unseen.remove(seed)
        while todo:
            v = todo.pop()
            for w in adj[v]:
                if w in unseen:
                    unseen.remove(w)
                    block.add(w)
                    todo.append(w)
        local = {v: i for i, v in enumerate(sorted(block))}
        local_edges = tuple(sorted((local[a], local[b]) for a, b in edges if a in block and b in block))
        out.append((len(block), local_edges))
    return out


def graph_key(n: int, edges: tuple[tuple[int, int], ...]) -> tuple[tuple[int, int, str], ...]:
    bits = []
    for cn, ce in components(n, edges):
        bits.append((len(ce), cn, canon(cn, ce)))
    return tuple(sorted(bits))


def expected_graph_keys(conn: dict[int, set[tuple[int, str]]]) -> dict[int, set[tuple]]:
    types = sorted((m, n, word) for m, vals in conn.items() for n, word in vals)
    expected: dict[int, set[tuple]] = defaultdict(set)

    def rec(start: int, remaining: int, acc: list[tuple[int, int, str]]):
        if remaining == 0:
            expected[sum(x[0] for x in acc)].add(tuple(sorted(acc)))
            return
        for i in range(start, len(types)):
            item = types[i]
            if item[0] > remaining:
                break
            acc.append(item)
            rec(i, remaining - item[0], acc)
            acc.pop()

    for m in range(1, MAX_EDGES + 1):
        rec(0, m, [])
    return expected


def contains_F_by_injection(
    n: int, colored_edges: set[tuple[int, int]]
) -> bool:
    # Labelled F edges: center 0 to leaves 1,2; independent edge 3--4.
    for image in itertools.permutations(range(n), 5):
        required = (
            tuple(sorted((image[0], image[1]))),
            tuple(sorted((image[0], image[2]))),
            tuple(sorted((image[3], image[4]))),
        )
        if all(e in colored_edges for e in required):
            return True
    return False


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    conn = independent_connected_types()
    expected = expected_graph_keys(conn)
    actual: dict[int, set[tuple]] = defaultdict(set)
    coloring_failures = []

    for index, row in enumerate(payload["catalogue"]):
        n = int(row["n"])
        m = int(row["m"])
        edges = tuple(tuple(e) for e in row["edges"])
        key = graph_key(n, edges)
        if key in actual[m]:
            raise AssertionError(f"duplicate graph type at catalogue row {index}")
        actual[m].add(key)
        red_mask = row["avoiding_red_mask"]
        if red_mask is None:
            continue
        red = {edges[i] for i in range(m) if red_mask >> i & 1}
        blue = set(edges) - red
        if contains_F_by_injection(n, red) or contains_F_by_injection(n, blue):
            coloring_failures.append(index)

    completeness = {
        str(m): {
            "expected": len(expected[m]),
            "actual": len(actual[m]),
            "missing": len(expected[m] - actual[m]),
            "extra": len(actual[m] - expected[m]),
        }
        for m in range(1, MAX_EDGES + 1)
    }
    verified = (
        all(v["missing"] == 0 and v["extra"] == 0 for v in completeness.values())
        and not coloring_failures
        and not payload["arrowing_hosts_at_most_five_edges"]
    )
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "scope": "null bounded probe for the (2,1) vs (2,1) tuple only",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "independent_connected_type_counts_by_edges": {
            str(m): len(conn[m]) for m in range(1, MAX_EDGES + 1)
        },
        "catalogue_completeness": completeness,
        "avoiding_coloring_embedding_check_failures": coloring_failures,
        "full_problem_resolved": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
