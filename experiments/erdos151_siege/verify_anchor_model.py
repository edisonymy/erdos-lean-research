#!/usr/bin/env python3
"""Independently verify SAT witnesses emitted by anchor_model.py.

This checker uses only the Python standard library and reconstructs every
asserted graph property from the dumped edge list.  It deliberately shares
no encoding code with the PySAT generator.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


N = 28
R = 7
S = tuple(range(R))
OUTSIDE = tuple(range(R, N))
KNOWN_ADMISSIBLE_8_SETS = {
    1: (0, 1, 3, 4, 5, 6, 7, 8),
    2: (0, 1, 2, 3, 4, 5, 8, 11),
    3: (0, 1, 2, 3, 4, 5, 13, 17),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_set(adj: list[int], size: int) -> list[int] | None:
    """Return an independent set of the requested size, if one exists."""

    def search(candidates: int, chosen: list[int]) -> list[int] | None:
        if len(chosen) == size:
            return chosen
        if candidates.bit_count() < size - len(chosen):
            return None
        bit = candidates & -candidates
        vertex = bit.bit_length() - 1
        found = search(candidates & ~bit & ~adj[vertex], chosen + [vertex])
        if found is not None:
            return found
        return search(candidates & ~bit, chosen)

    return search((1 << N) - 1, [])


def is_clique(vertices: tuple[int, ...], adj: list[int]) -> bool:
    return all((adj[u] >> v) & 1 for u, v in itertools.combinations(vertices, 2))


def is_ambient_maximal_clique(vertices: tuple[int, ...], adj: list[int]) -> bool:
    if len(vertices) < 2 or not is_clique(vertices, adj):
        return False
    members = set(vertices)
    return not any(
        w not in members and all((adj[w] >> v) & 1 for v in vertices)
        for w in range(N)
    )


def verify(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["result"] == "SAT"
    stage = int(data["stage"])
    assert stage in (1, 2, 3, 4)

    adj = [0] * N
    seen: set[tuple[int, int]] = set()
    for raw_u, raw_v in data["edges"]:
        u, v = sorted((int(raw_u), int(raw_v)))
        assert 0 <= u < v < N and (u, v) not in seen
        seen.add((u, v))
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    assert len(seen) == data["edge_count"]

    degrees = [mask.bit_count() for mask in adj]
    assert max(degrees) <= R
    if stage >= 3:
        assert min(degrees) >= 5

    k5 = next(
        (q for q in itertools.combinations(range(N), 5) if is_clique(q, adj)),
        None,
    )
    assert k5 is None, f"omega violation: {k5}"

    alpha_witness = independent_set(adj, R + 1) if stage >= 2 else None
    assert alpha_witness is None, f"alpha violation: {alpha_witness}"

    maximal_inside_s = []
    for size in range(2, 5):
        for clique in itertools.combinations(S, size):
            if is_ambient_maximal_clique(clique, adj):
                maximal_inside_s.append(clique)
    assert not maximal_inside_s, f"S is not admissible: {maximal_inside_s}"

    admissible8 = KNOWN_ADMISSIBLE_8_SETS.get(stage)
    if admissible8 is not None:
        contained_maximal = []
        for size in range(2, 5):
            for clique in itertools.combinations(admissible8, size):
                if is_ambient_maximal_clique(clique, adj):
                    contained_maximal.append(clique)
        assert not contained_maximal, (
            f"recorded admissible 8-set is invalid: {contained_maximal}"
        )

    anchors: dict[int, list[list[int]]] = {}
    for v in OUTSIDE:
        found = []
        neighbors_s = [a for a in S if (adj[v] >> a) & 1]
        for size in range(1, 4):
            for anchor in itertools.combinations(neighbors_s, size):
                clique = (v,) + anchor
                if is_ambient_maximal_clique(clique, adj):
                    found.append(list(anchor))
        assert found, f"outside vertex {v} has no S-anchor"
        anchors[v] = found

    if stage >= 4:
        for removed_size in range(1, R + 1):
            for removed_tuple in itertools.combinations(S, removed_size):
                removed = set(removed_tuple)
                bad = [
                    v for v in OUTSIDE
                    if all(removed.intersection(anchor) for anchor in anchors[v])
                ]
                induced_masks = [adj[v] for v in range(N)]

                def search(candidates: int, needed: int) -> bool:
                    if needed == 0:
                        return True
                    if candidates.bit_count() < needed:
                        return False
                    bit = candidates & -candidates
                    vertex = bit.bit_length() - 1
                    if search(candidates & ~bit & ~induced_masks[vertex], needed - 1):
                        return True
                    return search(candidates & ~bit, needed)

                mask = sum(1 << v for v in bad)
                assert not search(mask, removed_size + 1), (
                    f"anchor-swap shadow violation for R0={removed_tuple}"
                )

    c_values = [sum((adj[v] >> a) & 1 for a in S) for v in OUTSIDE]
    distribution = {
        str(value): c_values.count(value) for value in sorted(set(c_values))
    }
    assert distribution == data["c_distribution"]
    assert degrees[:R] == data["degrees_S"]
    assert [min(degrees[R:]), max(degrees[R:])] == data["degrees_X_minmax"]
    if "anchor_count_minmax" in data:
        assert data["anchor_count_minmax"] == [
            min(map(len, anchors.values())),
            max(map(len, anchors.values())),
        ]

    return {
        "status": "VERIFIED",
        "stage": stage,
        "witness": str(path),
        "witness_sha256": sha256(path),
        "edge_count": len(seen),
        "degree_minmax": [min(degrees), max(degrees)],
        "c_distribution": distribution,
        "anchor_count_minmax": [
            min(map(len, anchors.values())),
            max(map(len, anchors.values())),
        ],
        "admissible_8_set_showing_beta_not_enforced": admissible8,
        "checked": [
            "simple labelled graph",
            "maximum degree at most 7",
            "stage-3 minimum degree at least 5 when applicable",
            "clique number at most 4",
            "independence number at most 7 for stages 2 and 3",
            "S contains no ambient-maximal nontrivial clique",
            "every outside vertex has an ambient-maximal S-anchor",
            *(
                ["explicit admissible 8-set showing beta <= 7 is not encoded"]
                if admissible8 is not None else []
            ),
            *(
                ["all-removal-set anchor-swap shadow constraints"]
                if stage >= 4 else []
            ),
            "recorded summary counts",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", type=Path, nargs="+")
    args = parser.parse_args()
    results = [verify(path) for path in args.witness]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
