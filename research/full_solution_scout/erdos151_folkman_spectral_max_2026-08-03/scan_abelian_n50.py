#!/usr/bin/env python3
"""Exact scan of low-degree Cayley graphs on Z_2 x Z_5 x Z_5.

Together with scan_circulants_n50.py this covers the two abelian groups of
order 50.  Inverse pairs contribute degree two and the unique involution
(1,0,0) contributes degree one.  We retain one representative under the
full GL(2,5) action on the 5-primary component.  Every connected inverse-
closed connection set of degree at most ten is therefore covered.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scan_circulants_n50 import (  # noqa: E402
    N,
    TARGET,
    admissible_11,
    edges_from_adj,
    independent_11,
    maximal_cliques,
    validate_witness,
)


SCHEMA = "erdos151-abelian-z2xz5xz5-n50-scan-v1"


def neg_vec(v: tuple[int, int]) -> tuple[int, int]:
    return (-v[0] % 5, -v[1] % 5)


def pair_rep(v: tuple[int, int]) -> tuple[int, int]:
    return min(v, neg_vec(v))


PROJECTIVE_PAIRS = tuple(
    sorted({pair_rep((x, y)) for x in range(5) for y in range(5) if (x, y) != (0, 0)})
)
PAIR_LABELS = tuple((epsilon, v) for epsilon in (0, 1) for v in PROJECTIVE_PAIRS)
PAIR_INDEX = {label: i for i, label in enumerate(PAIR_LABELS)}


def det(matrix: tuple[int, int, int, int]) -> int:
    a, b, c, d = matrix
    return (a * d - b * c) % 5


GL2 = tuple(
    matrix
    for matrix in itertools.product(range(5), repeat=4)
    if det(matrix) != 0
)


def apply_matrix(matrix: tuple[int, int, int, int], v: tuple[int, int]) -> tuple[int, int]:
    a, b, c, d = matrix
    x, y = v
    return ((a * x + b * y) % 5, (c * x + d * y) % 5)


ACTION_PERMS = tuple(
    tuple(
        PAIR_INDEX[(epsilon, pair_rep(apply_matrix(matrix, v)))]
        for epsilon, v in PAIR_LABELS
    )
    for matrix in GL2
)


def orbit_images(pair_indices: tuple[int, ...]):
    for perm in ACTION_PERMS:
        yield tuple(sorted(perm[index] for index in pair_indices))


def all_orbit_representatives():
    seen: set[tuple[bool, tuple[int, ...]]] = set()
    for use_involution in (False, True):
        max_pairs = 5 if not use_involution else 4
        for size in range(max_pairs + 1):
            for pair_indices in itertools.combinations(range(len(PAIR_LABELS)), size):
                if not pair_indices and not use_involution:
                    continue
                key = (use_involution, pair_indices)
                if key in seen:
                    continue
                images = {(use_involution, image) for image in orbit_images(pair_indices)}
                seen.update(images)
                yield min(images)


def vertex_id(epsilon: int, x: int, y: int) -> int:
    return epsilon * 25 + x * 5 + y


def decode_vertex(vertex: int) -> tuple[int, int, int]:
    epsilon, rem = divmod(vertex, 25)
    x, y = divmod(rem, 5)
    return epsilon, x, y


def add_group(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return ((a[0] + b[0]) % 2, (a[1] + b[1]) % 5, (a[2] + b[2]) % 5)


def adjacency(use_involution: bool, pair_indices: tuple[int, ...]) -> list[int]:
    generators: list[tuple[int, int, int]] = []
    if use_involution:
        generators.append((1, 0, 0))
    for index in pair_indices:
        epsilon, v = PAIR_LABELS[index]
        generators.append((epsilon, v[0], v[1]))
        nv = neg_vec(v)
        generators.append((epsilon, nv[0], nv[1]))
    adj = [0] * N
    for u in range(N):
        point = decode_vertex(u)
        for generator in generators:
            target = add_group(point, generator)
            v = vertex_id(*target)
            if u == v:
                raise AssertionError("identity entered the connection set")
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    expected = 2 * len(pair_indices) + int(use_involution)
    if any(mask.bit_count() != expected for mask in adj):
        raise AssertionError("Cayley degree mismatch")
    return adj


def connected(adj: list[int]) -> bool:
    reached = 1
    frontier = 1
    while frontier:
        neighbours = 0
        scan = frontier
        while scan:
            bit = scan & -scan
            v = bit.bit_length() - 1
            scan ^= bit
            neighbours |= adj[v]
        frontier = neighbours & ~reached
        reached |= frontier
    return reached.bit_count() == N


def edge_hash(adj: list[int]) -> str:
    raw = ";".join(f"{u}-{v}" for u, v in edges_from_adj(adj)).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def label_record(use_involution: bool, pair_indices: tuple[int, ...]) -> dict:
    return {
        "involution": use_involution,
        "inverse_pair_generators": [
            [PAIR_LABELS[i][0], PAIR_LABELS[i][1][0], PAIR_LABELS[i][1][1]]
            for i in pair_indices
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".result.json"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    started = time.time()
    counters = Counter()
    degree_orbits = Counter()
    alpha_survivors = Counter()
    candidates: list[dict] = []
    beta_near_misses: list[dict] = []
    samples: list[dict] = []

    for raw_index, (use_involution, pair_indices) in enumerate(all_orbit_representatives()):
        if args.limit is not None and raw_index >= args.limit:
            break
        adj = adjacency(use_involution, pair_indices)
        if not connected(adj):
            counters["disconnected_orbits_skipped"] += 1
            continue
        counters["connected_orbits_tested"] += 1
        degree = 2 * len(pair_indices) + int(use_involution)
        degree_orbits[str(degree)] += 1
        label = label_record(use_involution, pair_indices)

        iw = independent_11(adj)
        if iw is not None:
            counters["killed_by_independent_11"] += 1
            if len(samples) < 12:
                samples.append(label | {"reason": "alpha>=11", "witness": iw})
            continue
        counters["alpha_le_10"] += 1
        alpha_survivors[str(degree)] += 1

        cliques = maximal_cliques(adj)
        aw = admissible_11(cliques)
        if aw is not None:
            validate_witness(aw, cliques)
            counters["killed_by_admissible_11"] += 1
            beta_near_misses.append(
                label
                | {
                    "degree": degree,
                    "witness": aw,
                    "maximal_clique_count": len(cliques),
                    "maximal_clique_size_distribution": dict(
                        sorted(Counter(str(c.bit_count()) for c in cliques).items())
                    ),
                }
            )
            if len(samples) < 24:
                samples.append(
                    label
                    | {
                        "reason": "beta>=11",
                        "witness": aw,
                        "maximal_clique_count": len(cliques),
                        "maximal_clique_size_distribution": dict(
                            sorted(Counter(str(c.bit_count()) for c in cliques).items())
                        ),
                    }
                )
            continue

        counters["beta_le_10_hits"] += 1
        candidates.append(
            label
            | {
                "degree": degree,
                "edge_sha256": edge_hash(adj),
                "edges": [list(edge) for edge in edges_from_adj(adj)],
                "maximal_cliques": [
                    [v for v in range(N) if clique >> v & 1] for clique in cliques
                ],
            }
        )

    complete = args.limit is None
    result = {
        "schema": SCHEMA,
        "complete": complete,
        "family": "all connected undirected Cayley graphs on Z_2 x Z_5 x Z_5 of degree at most 10",
        "quotient": "one representative per full GL(2,5) action",
        "gl2_order": len(GL2),
        "inverse_pair_count": len(PAIR_LABELS),
        "n": N,
        "H_50": 11,
        "target": "beta <= 10",
        "counters": dict(counters),
        "orbit_counts_by_degree": dict(sorted(degree_orbits.items(), key=lambda x: int(x[0]))),
        "alpha_le_10_by_degree": dict(sorted(alpha_survivors.items(), key=lambda x: int(x[0]))),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "beta_near_misses": beta_near_misses,
        "sample_failures": samples,
        "runtime_seconds": time.time() - started,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "solver": "CaDiCaL 1.9.5 through python-sat",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("complete", "counters", "candidate_count", "runtime_seconds")}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
