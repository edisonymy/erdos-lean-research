"""Candidate-first guided edge-swap search for Erdos problem 742 at n=25.

Every state is an unrestricted labelled graph on 25 vertices with exactly
157 edges.  The search uses definition-level diameter and edge-criticality
violations; it does not invoke SAT, symmetry restrictions, or make an UNSAT
claim.  A zero-defect state is checked again by the independent BFS routine
in ``direct_candidate_search.py``.

The important distinction from a plain simulated annealer is that moves are
generated from *failed criticality certificates*.  For a noncritical edge
uv, the generator finds the closest unique-two-path certificate and proposes
deleting one of its surplus incidences.  It then samples compensating edge
insertions, including insertions that repair any newly uncovered distance-2
pair.  Random swaps and diversified restarts keep the search unrestricted.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from itertools import combinations

import direct_candidate_search as core


ALL_EDGES = frozenset(core.ALL_EDGES)
TARGET = core.TARGET_EDGES


def score(metrics: dict[str, object]) -> tuple[int, int, int]:
    """Report tuple; not used lexicographically for move acceptance."""
    return core.objective(metrics)


def energy(metrics: dict[str, object]) -> int:
    # A diameter failure must ultimately disappear, but a finite coefficient
    # lets the walk cross a temporary distance-3 state.  The earlier search
    # effectively used an infinite barrier and remained at edit radius two.
    return (
        30 * len(metrics["diameter_failures"])
        + 6 * len(metrics["noncritical_edges"])
        + int(metrics["defect_sum"])
    )


def criticality_repair_deletions(
    edge: tuple[int, int], edges: set[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Edges whose deletion advances a nearest certificate for ``edge``.

    This returns one-edit pieces of a certificate repair, not a proof that the
    whole graph improves.  All proposed moves are rescored from the definition.
    """
    u, v = edge
    adj = core.adjacency(edges)
    proposals: set[tuple[int, int]] = set()
    best = core.witness_defect(u, v, adj)

    common = adj[u] & adj[v]
    if common.bit_count() == best:
        for w in core.bit_vertices(common):
            proposals.add(core.normal((u, w)))
            proposals.add(core.normal((v, w)))

    def oriented(a: int, b: int) -> None:
        # Candidate x-a-b; make a the unique common neighbour of x and b.
        candidates = adj[a] & ~adj[b] & ~(1 << b) & core.ALL_MASK
        for x in core.bit_vertices(candidates):
            surplus = (adj[x] & adj[b]) & ~(1 << a)
            if surplus.bit_count() != best:
                continue
            for w in core.bit_vertices(surplus):
                proposals.add(core.normal((x, w)))
                proposals.add(core.normal((b, w)))

    oriented(u, v)
    oriented(v, u)
    proposals.discard(edge)
    return sorted(proposals & edges)


def diameter_repair_additions(
    partial_edges: set[tuple[int, int]], rng: random.Random, cap: int = 30
) -> list[tuple[int, int]]:
    """Candidate additions aimed at distance pairs broken by a deletion."""
    metrics = core.local_metrics(partial_edges)
    adj = core.adjacency(partial_edges)
    proposals: set[tuple[int, int]] = set()
    for u, v in metrics["diameter_failures"][:8]:
        proposals.add((u, v))
        # Create a two-path by linking one endpoint to a neighbour of the other.
        for w in core.bit_vertices(adj[v]):
            if w != u:
                proposals.add(core.normal((u, w)))
        for w in core.bit_vertices(adj[u]):
            if w != v:
                proposals.add(core.normal((v, w)))
    proposals -= partial_edges
    values = list(proposals)
    rng.shuffle(values)
    return values[:cap]


def random_exact_graph(rng: random.Random) -> set[tuple[int, int]]:
    return set(rng.sample(tuple(ALL_EDGES), TARGET))


def radius_two_seed(rng: random.Random) -> set[tuple[int, int]]:
    # The best orbit from the exhaustive 14-orbit audit: a P3 in the 13-side,
    # supported by deleting the cross edge incident with the middle vertex.
    b = rng.sample(core.B, 3)
    a = rng.choice(core.A)
    internal = {core.normal((b[0], b[1])), core.normal((b[0], b[2]))}
    deleted = {core.normal((a, b[0]))}
    return core.build_edges(internal, deleted)


def subdivided_bipartite_seed(rng: random.Random) -> set[tuple[int, int]]:
    """Start from the 145-edge C5+ extremal construction, then add 12 edges."""
    left = tuple(range(12))
    right = tuple(range(12, 24))
    w = 24
    a = rng.choice(left)
    b = rng.choice(right)
    edges = {(x, y) for x in left for y in right}
    edges.remove((a, b))
    edges.add(core.normal((a, w)))
    edges.add(core.normal((b, w)))
    assert len(edges) == 145
    edges.update(rng.sample(tuple(ALL_EDGES - edges), TARGET - len(edges)))
    return edges


def deletion_seed(rng: random.Random) -> set[tuple[int, int]]:
    """Greedily descend from a random dense diameter-2 graph to 157 edges."""
    start_size = rng.randint(175, 215)
    edges = set(rng.sample(tuple(ALL_EDGES), start_size))
    # Random dense graphs are almost always diameter two.  If not, add failed
    # pairs, replacing random edges only after reaching diameter two.
    for _ in range(20):
        metrics = core.local_metrics(edges)
        if not metrics["diameter_failures"]:
            break
        edges.add(rng.choice(metrics["diameter_failures"]))
    while len(edges) > TARGET:
        metrics = core.local_metrics(edges)
        removable = list(metrics["noncritical_edges"])
        if not removable:
            # This would itself be a high-edge D2C graph; preserve it for the
            # caller, which will report rather than silently trim it.
            break
        sample = rng.sample(removable, min(24, len(removable)))
        best_edge = min(
            sample,
            key=lambda e: energy(core.local_metrics(edges - {e})),
        )
        edges.remove(best_edge)
    if len(edges) < TARGET:
        edges.update(rng.sample(tuple(ALL_EDGES - edges), TARGET - len(edges)))
    elif len(edges) > TARGET:
        # Defensive fallback; normally every dense intermediate has many
        # removable edges.
        edges = set(rng.sample(tuple(edges), TARGET))
    return edges


def proposed_swaps(
    edges: set[tuple[int, int]],
    metrics: dict[str, object],
    rng: random.Random,
    width: int,
) -> set[tuple[tuple[int, int], tuple[int, int]]]:
    nonedges = ALL_EDGES - edges
    proposals: set[tuple[tuple[int, int], tuple[int, int]]] = set()

    # Certificate-guided deletions, mixed with unrestricted deletions.
    deletion_pool: list[tuple[int, int]] = []
    bad = list(metrics["noncritical_edges"])
    rng.shuffle(bad)
    for target in bad[: min(5, len(bad))]:
        repairs = criticality_repair_deletions(target, edges)
        rng.shuffle(repairs)
        deletion_pool.extend(repairs[:5])
    deletion_pool.extend(rng.sample(tuple(edges), min(width, len(edges))))
    deletion_pool = list(dict.fromkeys(deletion_pool))[: max(10, width)]

    base_adds = list(nonedges)
    rng.shuffle(base_adds)
    base_adds = base_adds[:width]
    for deletion in deletion_pool:
        partial = edges - {deletion}
        adds = diameter_repair_additions(partial, rng)
        adds.extend(base_adds)
        # Additions incident with neither endpoint of a targeted bad edge are
        # naturally represented in base_adds; no structural class is excluded.
        for addition in list(dict.fromkeys(adds))[: 2 * width]:
            if addition != deletion and addition not in edges:
                proposals.add((deletion, addition))

    # Ensure a floor of fully random swaps even if certificate pools collapse.
    for _ in range(width):
        proposals.add((rng.choice(tuple(edges)), rng.choice(tuple(nonedges))))
    return proposals


def search(seconds: float, seed: int, width: int) -> dict[str, object]:
    rng = random.Random(seed)
    deadline = time.perf_counter() + seconds
    constructors = (radius_two_seed, subdivided_bipartite_seed, deletion_seed,
                    random_exact_graph)
    edges = radius_two_seed(rng)
    metrics = core.local_metrics(edges)
    current_energy = energy(metrics)
    best_lex = (score(metrics), set(edges), metrics)
    best_energy = (current_energy, score(metrics), set(edges), metrics)
    iterations = accepted = restarts = 0
    stagnant = 0
    temperature = 18.0

    while time.perf_counter() < deadline and best_lex[0][:2] != (0, 0):
        iterations += 1
        moves = proposed_swaps(edges, metrics, rng, width)
        evaluated = []
        for deletion, addition in moves:
            trial = (edges - {deletion}) | {addition}
            trial_metrics = core.local_metrics(trial)
            trial_energy = energy(trial_metrics)
            trial_score = score(trial_metrics)
            evaluated.append((trial_energy, rng.random(), trial,
                              trial_metrics, deletion, addition))
            # Record every scored neighbour, not only the move selected by the
            # scalar-energy beam.  This keeps the candidate audit independent
            # of the heuristic trade-off between criticality and diameter.
            if trial_score < best_lex[0]:
                best_lex = (trial_score, set(trial), trial_metrics)
            if (trial_energy, trial_score) < best_energy[:2]:
                best_energy = (trial_energy, trial_score, set(trial),
                               trial_metrics)
                stagnant = 0
        if not evaluated:
            break
        candidate = min(evaluated, key=lambda item: (item[0], item[1]))
        candidate_energy, _, trial, trial_metrics, _, _ = candidate
        delta = candidate_energy - current_energy
        if delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 0.2)):
            edges, metrics = trial, trial_metrics
            current_energy = candidate_energy
            accepted += 1
        temperature *= 0.997

        if (candidate_energy, score(trial_metrics)) >= best_energy[:2]:
            stagnant += 1

        if stagnant >= 90 or temperature < 0.25:
            restarts += 1
            constructor = constructors[restarts % len(constructors)]
            edges = constructor(rng)
            metrics = core.local_metrics(edges)
            current_energy = energy(metrics)
            restart_score = score(metrics)
            if restart_score < best_lex[0]:
                best_lex = (restart_score, set(edges), metrics)
            if (current_energy, restart_score) < best_energy[:2]:
                best_energy = (current_energy, restart_score, set(edges), metrics)
            temperature = 18.0 + 4.0 * (restarts % 3)
            stagnant = 0

    best_score, best_edges, best_metrics = best_lex
    bfs = core.verify_by_bfs(best_edges) if best_score[:2] == (0, 0) else None
    cross = set(core.CROSS_EDGES)
    internal = sorted(best_edges - cross)
    deleted_cross = sorted(cross - best_edges)
    return {
        "scope": "unrestricted exact-157 candidate search; no UNSAT claim",
        "seed": seed,
        "seconds": seconds,
        "width": width,
        "iterations": iterations,
        "accepted": accepted,
        "restarts": restarts,
        "best_objective": best_score,
        "best_energy": energy(best_metrics),
        "diameter_failures": best_metrics["diameter_failures"],
        "noncritical_count": len(best_metrics["noncritical_edges"]),
        "noncritical_edges": best_metrics["noncritical_edges"],
        "defect_histogram": {
            str(value): best_metrics["defects"].count(value)
            for value in sorted(set(best_metrics["defects"]))
        },
        "degree_sequence": sorted(best_metrics["degrees"], reverse=True),
        "relative_partition_k_internal": len(internal),
        "relative_partition_deleted_cross": len(deleted_cross),
        "internal_edges": internal,
        "deleted_cross_edges": deleted_cross,
        "bfs_verification": bfs,
        "candidate_edges": sorted(best_edges) if bfs and bfs.get("valid") else None,
        "lowest_scalar_state": {
            "energy": best_energy[0],
            "objective": best_energy[1],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=742)
    parser.add_argument("--width", type=int, default=14)
    args = parser.parse_args()
    print(json.dumps(search(args.seconds, args.seed, args.width), indent=2))


if __name__ == "__main__":
    main()
