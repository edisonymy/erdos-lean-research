#!/usr/bin/env python3
"""Independent audits of the order-16 t=2 and t=4 core enumerations."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx


X8 = tuple(range(8, 16))
X8_PAIRS = tuple(itertools.combinations(range(8), 2))
X8_PAIR_INDEX = {pair: index for index, pair in enumerate(X8_PAIRS)}


def fixed_u_groups(r):
    if r == 1:
        return ({0, 1}, {2, 3, 4}, {5, 6, 7})
    if r == 2:
        return ({0, 1}, {2, 3}, {4, 5, 6})
    return ({0, 1}, {2, 3}, {4, 5})


def incidence_words(r):
    sizes = {group: (2 if group < r else 3) for group in range(3)}
    missing = r - 1
    labels = (-1, 0, 1, 2) if missing else (0, 1, 2)
    required = {**sizes, **({-1: missing} if missing else {})}
    u_groups = fixed_u_groups(r)
    for word in itertools.product(labels, repeat=8):
        if any(word.count(label) != count for label, count in required.items()):
            continue
        if any(index in u_groups[label] for index, label in enumerate(word) if 0 <= label < r):
            continue
        w_groups = tuple({index for index, label in enumerate(word) if label == group} for group in range(3))
        yield u_groups, w_groups, word


def edge_mask_and_degrees(indices):
    degrees = [0] * 8
    mask = 0
    for index in indices:
        a, b = X8_PAIRS[index]
        degrees[a] += 1
        degrees[b] += 1
        mask |= 1 << index
    return mask, tuple(degrees)


def forbidden_mask(*groups):
    mask = 0
    for group in groups:
        for pair in itertools.combinations(sorted(group), 2):
            mask |= 1 << X8_PAIR_INDEX[pair]
    return mask


def build_t2(r, u_groups, w_groups, internal_mask):
    a, b = 0, 1
    u_vertices, w_vertices = (2, 3, 4), (5, 6, 7)
    edges = [(a, u) for u in u_vertices] + [(b, w) for w in w_vertices]
    edges += [(u_vertices[i], w_vertices[i]) for i in range(r)]
    for vertex, group in zip(u_vertices, u_groups):
        edges += [(vertex, X8[index]) for index in group]
    for vertex, group in zip(w_vertices, w_groups):
        edges += [(vertex, X8[index]) for index in group]
    for index, (left, right) in enumerate(X8_PAIRS):
        if internal_mask & (1 << index):
            edges.append((X8[left], X8[right]))
    edges = sorted(tuple(sorted(edge)) for edge in edges)
    neighbours = [set() for _ in range(16)]
    for left, right in edges:
        neighbours[left].add(right)
        neighbours[right].add(left)
    assert len(edges) == 31 and sorted(map(len, neighbours)) == [3, 3] + [4] * 14
    return edges, neighbours


def compatible(edge, other, neighbours):
    return not (set(edge) & set(other)) and all(y not in neighbours[x] for x in edge for y in other)


def reverse_matching(edges, neighbours, target):
    available = list(range(len(edges) - 1, -1, -1))
    chosen = []
    while available and len(chosen) < target:
        index = available.pop(0)
        position = next(
            (position for position, other in enumerate(available) if compatible(edges[index], edges[other], neighbours)),
            None,
        )
        if position is not None:
            chosen.append((index, available.pop(position)))
    return chosen if len(chosen) == target else None


def audit_t2(primary):
    patterns = {1: [], 2: [], 3: []}
    needed = {1: set(), 2: set(), 3: set()}
    for r in (1, 2, 3):
        u_incidence = [1 if any(index in group for group in fixed_u_groups(r)) else 0 for index in range(8)]
        for u_groups, w_groups, word in incidence_words(r):
            w_incidence = [0 if label == -1 else 1 for label in word]
            degree = tuple(4 - u_incidence[index] - w_incidence[index] for index in range(8))
            forbidden = forbidden_mask(*u_groups, *w_groups)
            patterns[r].append((u_groups, w_groups, degree, forbidden))
            needed[r].add(degree)

    internal = {1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list)}
    for r in (1, 2, 3):
        for indices in itertools.combinations(range(28), 7 + r):
            mask, degrees = edge_mask_and_degrees(indices)
            if degrees in needed[r]:
                internal[r][degrees].append(mask)

    counts = Counter()
    failures = []
    for r in (1, 2, 3):
        counts[f"r{r}_w_partitions"] = len(patterns[r])
        for u_groups, w_groups, degree, forbidden in patterns[r]:
            for mask in internal[r][degree]:
                if mask & forbidden:
                    continue
                counts[f"r{r}_internal_completions"] += 1
                edges, neighbours = build_t2(r, u_groups, w_groups, mask)
                if reverse_matching(edges, neighbours, 11) is None:
                    failures.append({"r": r, "u_groups": [sorted(x) for x in u_groups], "w_groups": [sorted(x) for x in w_groups], "internal_mask": mask})
    keys = [
        "r1_w_partitions", "r1_internal_completions",
        "r2_w_partitions", "r2_internal_completions",
        "r3_w_partitions", "r3_internal_completions",
    ]
    return {
        "counts": dict(sorted(counts.items())),
        "precomputed_degree_vectors": {str(r): {str(key): len(value) for key, value in internal[r].items()} for r in (1, 2, 3)},
        "failures": failures,
        "assertions": {
            "counts_match_primary": all(counts[key] == primary["counts"][key] for key in keys),
            "fresh_failures_empty": not failures,
        },
    }


def canonical_h2_partitions(square):
    def rec(remaining, blocks):
        if not remaining:
            yield tuple(blocks)
            return
        first = min(remaining)
        for pair in itertools.combinations(sorted(remaining - {first}), 2):
            block = (first, *pair)
            if any(square.has_edge(a, b) for a, b in itertools.combinations(block, 2)):
                continue
            yield from rec(remaining - set(block), blocks + [block])
    yield from rec(set(range(12)), [])


def audit_t4(primary, catalogue):
    counts = Counter()
    failures = []
    raw = catalogue.read_bytes()
    for index, record in enumerate(raw.splitlines()):
        graph = nx.from_graph6_bytes(record)
        assert len(graph) == 12 and set(dict(graph.degree()).values()) == {3}
        if any(nx.triangles(graph).values()):
            counts["cores_rejected_with_triangle"] += 1
            continue
        counts["triangle_free_cubic_cores"] += 1
        square = nx.power(graph, 2)
        partitions = list(canonical_h2_partitions(square))
        counts["separated_partitions"] += len(partitions)
        if partitions:
            counts["cores_with_partition"] += 1
        for partition in partitions:
            edges = [(left + 4, right + 4) for left, right in graph.edges()]
            for defect, block in enumerate(partition):
                edges += [(defect, vertex + 4) for vertex in block]
            edges = sorted(tuple(sorted(edge)) for edge in edges)
            neighbours = [set() for _ in range(16)]
            for left, right in edges:
                neighbours[left].add(right)
                neighbours[right].add(left)
            if reverse_matching(edges, neighbours, 10) is None:
                failures.append({"core_index": index, "graph6": record.decode("ascii"), "partition": partition})
    keys = ["cores_rejected_with_triangle", "triangle_free_cubic_cores", "separated_partitions", "cores_with_partition"]
    return {
        "catalogue": {"records": len(raw.splitlines()), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        "counts": dict(sorted(counts.items())),
        "failures": failures,
        "assertions": {
            "counts_match_primary": all(counts[key] == primary["counts"][key] for key in keys),
            "fresh_failures_empty": not failures,
        },
    }


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    t2_primary_path = here / "n16_t2_core_result.json"
    t4_primary_path = here / "n16_t4_core_result.json"
    t2_primary = json.loads(t2_primary_path.read_text(encoding="utf-8"))
    t4_primary = json.loads(t4_primary_path.read_text(encoding="utf-8"))
    t2 = audit_t2(t2_primary)
    t4 = audit_t4(t4_primary, here / "n16_t4_cubic_cores.g6")
    assertions = {
        "t2_primary_verified": t2_primary["status"] == "VERIFIED" and not t2_primary["failures"],
        "t4_primary_verified": t4_primary["status"] == "VERIFIED" and not t4_primary["failures"],
        "t2_fresh_verified": all(t2["assertions"].values()),
        "t4_fresh_verified": all(t4["assertions"].values()),
    }
    result = {
        "schema": "erdos149-n16-core-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "t2": t2,
        "t4": t4,
        "primary_hashes": {
            "t2": hashlib.sha256(t2_primary_path.read_bytes()).hexdigest(),
            "t4": hashlib.sha256(t4_primary_path.read_bytes()).hexdigest(),
        },
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This independently audits only the nonregular order-16 core slices.",
    }
    (here / "n16_cores_fresh_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "t2_counts": t2["counts"], "t4_counts": t4["counts"], "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
