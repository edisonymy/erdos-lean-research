"""Direct candidate-first search for an order-25 Murty--Simon counterexample.

The search does not use the existing SAT encoding.  It works on graph edge
sets of exactly 157 edges, represented relative to K_{12,13}: choose k
internal edges and delete k-1 cross edges.  This parametrizes *every* labelled
157-edge graph for the fixed 12+13 vertex partition, not only small
perturbations of the complete bipartite graph.

The objective is computed from the definition-level unique-two-path
criterion.  A candidate is accepted only after a separate BFS edge-deletion
implementation also verifies it.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from collections import deque
from itertools import combinations


N = 25
A = tuple(range(12))
B = tuple(range(12, 25))
ALL_VERTICES = tuple(range(N))
ALL_MASK = (1 << N) - 1
ALL_EDGES = tuple(combinations(range(N), 2))
CROSS_EDGES = tuple((a, b) for a in A for b in B)
INTERNAL_EDGES = tuple(combinations(A, 2)) + tuple(combinations(B, 2))
CROSS_SET = frozenset(CROSS_EDGES)
INTERNAL_SET = frozenset(INTERNAL_EDGES)
TARGET_EDGES = 157


def normal(edge: tuple[int, int]) -> tuple[int, int]:
    u, v = edge
    return (u, v) if u < v else (v, u)


def build_edges(
    internal: set[tuple[int, int]], deleted_cross: set[tuple[int, int]]
) -> set[tuple[int, int]]:
    assert internal <= INTERNAL_SET
    assert deleted_cross <= CROSS_SET
    assert len(internal) == len(deleted_cross) + 1
    edges = (set(CROSS_EDGES) - deleted_cross) | internal
    assert len(edges) == TARGET_EDGES
    return edges


def adjacency(edges: set[tuple[int, int]]) -> list[int]:
    adj = [0] * N
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def bit_vertices(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def edge_is_critical_local(u: int, v: int, adj: list[int]) -> bool:
    """Unique-two-path characterization, independent of BFS verification."""
    if not (adj[u] & adj[v]):
        return True

    # Deleting uv can strand distance x--v, with x-u-v its unique 2-path.
    candidates = adj[u] & ~adj[v] & ~(1 << v) & ALL_MASK
    for x in bit_vertices(candidates):
        if adj[x] & adj[v] == 1 << u:
            return True

    # Symmetric orientation.
    candidates = adj[v] & ~adj[u] & ~(1 << u) & ALL_MASK
    for x in bit_vertices(candidates):
        if adj[x] & adj[u] == 1 << v:
            return True
    return False


def witness_defect(u: int, v: int, adj: list[int]) -> int:
    """A lower-level repair signal for a currently noncritical edge.

    This is not claimed to be an exact edit distance.  It is the least number
    of surplus common-neighbour incidences in the three local witness forms.
    Zero is equivalent to criticality.
    """
    common = (adj[u] & adj[v]).bit_count()
    best = common
    candidates = adj[u] & ~adj[v] & ~(1 << v) & ALL_MASK
    for x in bit_vertices(candidates):
        intersection = adj[x] & adj[v]
        if intersection & (1 << u):
            best = min(best, intersection.bit_count() - 1)
    candidates = adj[v] & ~adj[u] & ~(1 << u) & ALL_MASK
    for x in bit_vertices(candidates):
        intersection = adj[x] & adj[u]
        if intersection & (1 << v):
            best = min(best, intersection.bit_count() - 1)
    return best


def local_metrics(edges: set[tuple[int, int]]) -> dict[str, object]:
    adj = adjacency(edges)
    diameter_failures = []
    for u, v in ALL_EDGES:
        if (u, v) not in edges and not (adj[u] & adj[v]):
            diameter_failures.append((u, v))
    noncritical = []
    defects = []
    for u, v in edges:
        if not edge_is_critical_local(u, v, adj):
            noncritical.append((u, v))
            defects.append(witness_defect(u, v, adj))
    degrees = [mask.bit_count() for mask in adj]
    return {
        "diameter_failures": tuple(sorted(diameter_failures)),
        "noncritical_edges": tuple(sorted(noncritical)),
        "defects": tuple(defects),
        "defect_sum": sum(defects),
        "degrees": tuple(degrees),
    }


def objective(metrics: dict[str, object]) -> tuple[int, int, int]:
    return (
        len(metrics["diameter_failures"]),
        len(metrics["noncritical_edges"]),
        int(metrics["defect_sum"]),
    )


def scalar_energy(value: tuple[int, int, int]) -> int:
    return 100_000 * value[0] + 100 * value[1] + value[2]


def bfs_diameter(edges: set[tuple[int, int]]) -> int | None:
    neighbours = [[] for _ in range(N)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    diameter = 0
    for source in range(N):
        dist = [-1] * N
        dist[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in neighbours[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        if -1 in dist:
            return None
        diameter = max(diameter, max(dist))
    return diameter


def verify_by_bfs(edges: set[tuple[int, int]]) -> dict[str, object]:
    original = bfs_diameter(edges)
    if original != 2:
        return {"valid": False, "original_diameter": original}
    for edge in sorted(edges):
        if bfs_diameter(edges - {edge}) == 2:
            return {"valid": False, "removable_edge": edge}
    return {
        "valid": True,
        "n": N,
        "edge_count": len(edges),
        "counterexample": len(edges) > N * N // 4,
    }


def radius_two_orbit_representatives():
    """The 14 orbits for adding two internal edges and deleting one cross edge."""
    reps = []
    # Both internal edges in A: adjacent P3 or disjoint matching; deleted A
    # endpoint has each possible orbit role.  The B endpoint is outside.
    for name, pair, roles in (
        ("AA_path", {(0, 1), (0, 2)}, (0, 1, 3)),
        ("AA_matching", {(0, 1), (2, 3)}, (0, 4)),
    ):
        for a_endpoint in roles:
            reps.append((f"{name}_role{a_endpoint}", pair, {(a_endpoint, 12)}))
    # Symmetric patterns in the 13-side.
    for name, pair, roles in (
        ("BB_path", {(12, 13), (12, 14)}, (12, 13, 15)),
        ("BB_matching", {(12, 13), (14, 15)}, (12, 16)),
    ):
        for b_endpoint in roles:
            reps.append((f"{name}_role{b_endpoint}", pair, {(0, b_endpoint)}))
    # One internal edge per side; the deleted endpoint can be incident or not
    # to the selected internal edge on each side.
    pair = {(0, 1), (12, 13)}
    for a_endpoint in (0, 2):
        for b_endpoint in (12, 14):
            reps.append((f"AB_roles_{a_endpoint}_{b_endpoint}", pair,
                         {(a_endpoint, b_endpoint)}))
    assert len(reps) == 14
    return reps


def audit_radius_two() -> list[dict[str, object]]:
    records = []
    for name, internal, deleted in radius_two_orbit_representatives():
        edges = build_edges(set(internal), set(deleted))
        metrics = local_metrics(edges)
        records.append({
            "orbit": name,
            "objective": objective(metrics),
            "noncritical_edges": metrics["noncritical_edges"],
        })
    return records


def audit_radius_one() -> list[dict[str, object]]:
    """The two orbits K_12,13 plus one internal edge."""
    records = []
    for name, edge in (("internal_in_12_side", (0, 1)),
                       ("internal_in_13_side", (12, 13))):
        edges = build_edges({edge}, set())
        metrics = local_metrics(edges)
        records.append({
            "orbit": name,
            "objective": objective(metrics),
            "noncritical_edges": metrics["noncritical_edges"],
            "defects": metrics["defects"],
        })
    return records


def random_state(rng: random.Random, k: int | None = None):
    if k is None:
        k = rng.randint(1, 45)
    internal = set(rng.sample(INTERNAL_EDGES, k))
    deleted = set(rng.sample(CROSS_EDGES, k - 1))
    return internal, deleted


def mutate(
    rng: random.Random,
    internal: set[tuple[int, int]],
    deleted: set[tuple[int, int]],
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    new_i = set(internal)
    new_d = set(deleted)
    move = rng.random()
    k = len(new_i)
    if move < 0.38:
        new_i.remove(rng.choice(tuple(new_i)))
        new_i.add(rng.choice(tuple(INTERNAL_SET - new_i)))
    elif move < 0.76 and new_d:
        new_d.remove(rng.choice(tuple(new_d)))
        new_d.add(rng.choice(tuple(CROSS_SET - new_d)))
    elif move < 0.88 and k < min(len(INTERNAL_EDGES), len(CROSS_EDGES) + 1):
        new_i.add(rng.choice(tuple(INTERNAL_SET - new_i)))
        new_d.add(rng.choice(tuple(CROSS_SET - new_d)))
    elif k > 1:
        new_i.remove(rng.choice(tuple(new_i)))
        new_d.remove(rng.choice(tuple(new_d)))
    else:
        new_i.remove(rng.choice(tuple(new_i)))
        new_i.add(rng.choice(tuple(INTERNAL_SET - new_i)))
    return new_i, new_d


def stochastic_search(seconds: float, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    deadline = time.perf_counter() + seconds
    internal, deleted = random_state(rng, k=1)
    edges = build_edges(internal, deleted)
    metrics = local_metrics(edges)
    value = objective(metrics)
    best = (value, set(internal), set(deleted), metrics)
    iterations = 0
    accepted = 0
    restarts = 0
    stagnant = 0
    temperature = 8.0

    while time.perf_counter() < deadline and best[0][:2] != (0, 0):
        iterations += 1
        trial_i, trial_d = mutate(rng, internal, deleted)
        trial_edges = build_edges(trial_i, trial_d)
        trial_metrics = local_metrics(trial_edges)
        trial_value = objective(trial_metrics)
        delta = scalar_energy(trial_value) - scalar_energy(value)
        if delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 0.05)):
            internal, deleted = trial_i, trial_d
            metrics, value = trial_metrics, trial_value
            accepted += 1
        temperature *= 0.9995
        if trial_value < best[0]:
            best = (trial_value, set(trial_i), set(trial_d), trial_metrics)
            stagnant = 0
        else:
            stagnant += 1
        if stagnant >= 4_000:
            restarts += 1
            # Restart partly near the best and partly at a diversified k.
            if restarts % 2:
                internal, deleted = set(best[1]), set(best[2])
                for _ in range(20):
                    internal, deleted = mutate(rng, internal, deleted)
            else:
                internal, deleted = random_state(rng)
            metrics = local_metrics(build_edges(internal, deleted))
            value = objective(metrics)
            temperature = 8.0
            stagnant = 0

    best_value, best_i, best_d, best_metrics = best
    best_edges = build_edges(best_i, best_d)
    bfs = verify_by_bfs(best_edges) if best_value[:2] == (0, 0) else None
    return {
        "seed": seed,
        "seconds": seconds,
        "iterations": iterations,
        "accepted": accepted,
        "restarts": restarts,
        "objective": best_value,
        "k_internal": len(best_i),
        "internal_edges": sorted(best_i),
        "deleted_cross_edges": sorted(best_d),
        "noncritical_edges": best_metrics["noncritical_edges"],
        "diameter_failures": best_metrics["diameter_failures"],
        "defects": best_metrics["defects"],
        "degree_sequence": sorted(best_metrics["degrees"], reverse=True),
        "bfs_verification": bfs,
        "candidate_edges": sorted(best_edges) if bfs and bfs.get("valid") else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=742)
    args = parser.parse_args()
    started = time.perf_counter()
    result = {
        "scope": "direct candidate search; no symmetry-class UNSAT claim",
        "n": N,
        "target_edges": TARGET_EDGES,
        "radius_one_orbit": audit_radius_one(),
        "radius_two_orbits": audit_radius_two(),
        "stochastic": stochastic_search(args.seconds, args.seed),
        "wall_seconds": time.perf_counter() - started,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
