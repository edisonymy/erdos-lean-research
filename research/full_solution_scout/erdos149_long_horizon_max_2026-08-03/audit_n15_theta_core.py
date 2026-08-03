#!/usr/bin/env python3
"""Independent subset-enumeration audit of the order-15 theta-core search."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter, defaultdict
from pathlib import Path


A, B = 0, 1
U, W = (2, 3, 4), (5, 6, 7)
X = tuple(range(8, 15))
X_PAIRS = tuple(itertools.combinations(range(7), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(X_PAIRS)}
TARGET = 9


def degree_tuple(indices):
    degree = [0] * 7
    for index in indices:
        a, b = X_PAIRS[index]
        degree[a] += 1
        degree[b] += 1
    return tuple(degree)


def candidate_internal_masks():
    r2 = []
    for indices in itertools.combinations(range(21), 7):
        if degree_tuple(indices) == (2,) * 7:
            r2.append(sum(1 << index for index in indices))
    needed_r3 = {(2, 2, 2, 2, 2, 2, 4)}
    for missing in range(6):
        target = [2] * 7
        target[missing] = 3
        target[6] = 3
        needed_r3.add(tuple(target))
    r3 = defaultdict(list)
    for indices in itertools.combinations(range(21), 8):
        degree = degree_tuple(indices)
        if degree in needed_r3:
            r3[degree].append(sum(1 << index for index in indices))
    return r2, r3


def assignments(r):
    u_groups = ({0, 1}, {2, 3}, {4, 5, 6}) if r == 2 else ({0, 1}, {2, 3}, {4, 5})
    labels = (0, 1, 2) if r == 2 else (-1, 0, 1, 2)
    required_counts = {0: 2, 1: 2, 2: 3} if r == 2 else {-1: 1, 0: 2, 1: 2, 2: 2}
    for assignment in itertools.product(labels, repeat=7):
        if any(assignment.count(label) != count for label, count in required_counts.items()):
            continue
        if any(index in u_groups[label] for index, label in enumerate(assignment) if 0 <= label < r):
            continue
        w_groups = tuple(tuple(index for index, label in enumerate(assignment) if label == group) for group in range(3))
        yield u_groups, w_groups, assignment


def forbidden_mask(u_groups, w_groups):
    mask = 0
    for group in (*u_groups, *w_groups):
        for pair in itertools.combinations(sorted(group), 2):
            mask |= 1 << PAIR_INDEX[pair]
    return mask


def build(r, u_groups, w_groups, internal_mask):
    edges = [(A, u) for u in U] + [(B, w) for w in W]
    edges += [(U[i], W[i]) for i in range(r)]
    for group, u in zip(u_groups, U):
        edges += [(u, X[index]) for index in group]
    for group, w in zip(w_groups, W):
        edges += [(w, X[index]) for index in group]
    for index, (a, b) in enumerate(X_PAIRS):
        if internal_mask & (1 << index):
            edges.append((X[a], X[b]))
    edges = sorted(tuple(sorted(edge)) for edge in edges)
    neighbours = [set() for _ in range(15)]
    for a, b in edges:
        neighbours[a].add(b)
        neighbours[b].add(a)
    assert len(edges) == 29 and sorted(map(len, neighbours)) == [3, 3] + [4] * 13
    return edges, neighbours


def compatible(e, f, neighbours):
    return not (set(e) & set(f)) and all(y not in neighbours[x] for x in e for y in f)


def reverse_matching(edges, neighbours):
    available = list(range(len(edges) - 1, -1, -1))
    chosen = []
    while available and len(chosen) < TARGET:
        i = available.pop(0)
        position = next(
            (position for position, j in enumerate(available) if compatible(edges[i], edges[j], neighbours)),
            None,
        )
        if position is not None:
            chosen.append((i, available.pop(position)))
    return chosen if len(chosen) == TARGET else None


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    primary_path = here / "n15_theta_core_result.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    r2_internal, r3_internal = candidate_internal_masks()
    counts = Counter()
    failures = []
    for r in (2, 3):
        for u_groups, w_groups, assignment in assignments(r):
            counts[f"r{r}_w_partitions"] += 1
            if r == 2:
                candidates = r2_internal
            else:
                u_incidence = [1, 1, 1, 1, 1, 1, 0]
                w_incidence = [0 if value == -1 else 1 for value in assignment]
                target = tuple(4 - u_incidence[index] - w_incidence[index] for index in range(7))
                candidates = r3_internal[target]
            forbidden = forbidden_mask(u_groups, w_groups)
            for internal_mask in candidates:
                if internal_mask & forbidden:
                    continue
                counts[f"r{r}_internal_completions"] += 1
                edges, neighbours = build(r, u_groups, w_groups, internal_mask)
                matching = reverse_matching(edges, neighbours)
                if matching is None:
                    failures.append(
                        {
                            "r": r,
                            "u_groups": [sorted(group) for group in u_groups],
                            "w_groups": [list(group) for group in w_groups],
                            "internal_mask": internal_mask,
                            "edges": edges,
                        }
                    )
    expected = {
        "r2_w_partitions": 55,
        "r2_internal_completions": 492,
        "r3_w_partitions": 94,
        "r3_internal_completions": 4764,
    }
    assertions = {
        "primary_verified": primary["status"] == "VERIFIED" and not primary["failures"],
        "fresh_counts_match_expected": all(counts[key] == value for key, value in expected.items()),
        "fresh_counts_match_primary": all(primary["counts"][key] == counts[key] for key in expected),
        "fresh_failures_empty": not failures,
    }
    result = {
        "schema": "erdos149-n15-theta-core-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "method": "Enumerate all 7-edge and 8-edge subsets of K7 by degree vector; filter independently enumerated W-incidence words; use reverse on-demand compatibility matching.",
        "precomputed_internal_graphs": {
            "two_regular_on_seven": len(r2_internal),
            "r3_degree_vector_counts": {str(key): len(value) for key, value in sorted(r3_internal.items())},
        },
        "counts": dict(sorted(counts.items())),
        "fresh_reverse_matchings_of_nine": counts["r2_internal_completions"] + counts["r3_internal_completions"] - len(failures),
        "failures": failures,
        "primary": {
            "path": str(primary_path),
            "bytes": primary_path.stat().st_size,
            "sha256": hashlib.sha256(primary_path.read_bytes()).hexdigest(),
        },
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This audit checks the finite theta-core completion space; the separate mathematical reduction establishes why it covers the m=29 residual.",
    }
    (here / "n15_theta_core_fresh_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "counts": result["counts"], "failures": len(failures), "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
