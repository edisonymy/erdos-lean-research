"""Exact one-2-switch obstruction for the pinned order-39 Ramsey base.

Let B be the labelled 39-vertex graph in ``source_r3_10_39.matrix``.  This
audit enumerates every valid old-old 2-switch of B.  For every resulting base
B', it proves that adding two new vertices (with arbitrary incident edges)
cannot produce a graph with both maximum degree at most 9 and independence
number at most 9.

The proof is deliberately only about this finite perturbation family.  It
does not claim that all order-41 candidates, or even all perturbations of B,
are impossible.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

from audit_ramsey39_extensions import (
    SOURCE,
    digest_sets,
    enumerate_networkx,
    enumerate_sat,
    load_base,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "one_switch_extension_audit.json"

Edge = tuple[int, int]
EdgePair = tuple[Edge, Edge]
Switch = tuple[EdgePair, EdgePair]


def edge(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def edge_pair(first: Edge, second: Edge) -> EdgePair:
    return tuple(sorted((edge(*first), edge(*second))))  # type: ignore[return-value]


def enumerate_switches_by_edge_pairs(graph: nx.Graph) -> list[Switch]:
    """Enumerate switches by choosing two old edges and a cross matching."""

    old_edges = sorted(edge(u, v) for u, v in graph.edges())
    old_edge_set = set(old_edges)
    result: set[Switch] = set()
    for index, (a, b) in enumerate(old_edges):
        for c, d in old_edges[index + 1 :]:
            if len({a, b, c, d}) != 4:
                continue
            removed = edge_pair((a, b), (c, d))
            for raw_added in (((a, c), (b, d)), ((a, d), (b, c))):
                added = edge_pair(*raw_added)
                if all(candidate not in old_edge_set for candidate in added):
                    result.add((removed, added))
    return sorted(result)


def enumerate_switches_by_four_sets(graph: nx.Graph) -> list[Switch]:
    """Independent enumeration via the three matchings of every four-set."""

    old_edge_set = {edge(u, v) for u, v in graph.edges()}
    result: set[Switch] = set()
    for a, b, c, d in itertools.combinations(sorted(graph), 4):
        matchings = (
            edge_pair((a, b), (c, d)),
            edge_pair((a, c), (b, d)),
            edge_pair((a, d), (b, c)),
        )
        for removed in matchings:
            if not all(candidate in old_edge_set for candidate in removed):
                continue
            for added in matchings:
                if added == removed:
                    continue
                if all(candidate not in old_edge_set for candidate in added):
                    result.add((removed, added))
    return sorted(result)


def digest_switches(switches: list[Switch]) -> str:
    raw = json.dumps(switches, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(b"erdos151-r39-one-switch-v1\0" + raw).hexdigest()


def digest_records(label: str, records: object) -> str:
    raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(label.encode("ascii") + b"\0" + raw).hexdigest()


def adjacency_bits(graph: nx.Graph) -> list[int]:
    return [sum(1 << neighbour for neighbour in graph.neighbors(vertex)) for vertex in graph]


def switched_adjacency(base: list[int], switch: Switch) -> list[int]:
    result = base.copy()
    removed, added = switch
    for u, v in removed:
        result[u] &= ~(1 << v)
        result[v] &= ~(1 << u)
    for u, v in added:
        result[u] |= 1 << v
        result[v] |= 1 << u
    return result


def switched_edges(base_edges: set[Edge], switch: Switch) -> list[Edge]:
    result = set(base_edges)
    removed, added = switch
    result.difference_update(removed)
    result.update(added)
    return sorted(result)


def find_independent_witness(
    adjacency: list[int], allowed: int, target: int
) -> tuple[int, ...] | None:
    """Definition-level branch search for an independent set of target size."""

    def visit(candidates: int, need: int, chosen: tuple[int, ...]) -> tuple[int, ...] | None:
        if need == 0:
            return chosen
        if candidates.bit_count() < need:
            return None
        # Iterating the include branches while removing earlier vertices also
        # covers every exclude branch.
        while candidates.bit_count() >= need:
            chosen_bit = candidates & -candidates
            vertex = chosen_bit.bit_length() - 1
            candidates -= chosen_bit
            answer = visit(
                candidates & ~adjacency[vertex], need - 1, chosen + (vertex,)
            )
            if answer is not None:
                return answer
        return None

    answer = visit(allowed, target, ())
    return None if answer is None else tuple(sorted(answer))


def verify_independent_witness(
    adjacency: list[int], witness: tuple[int, ...], target: int, forbidden: Iterable[int] = ()
) -> None:
    forbidden_set = set(forbidden)
    if len(witness) != target or len(set(witness)) != target:
        raise AssertionError("independent witness has the wrong size")
    if forbidden_set.intersection(witness):
        raise AssertionError("independent witness uses a forbidden vertex")
    for u, v in itertools.combinations(witness, 2):
        if adjacency[u] & (1 << v):
            raise AssertionError("purported independent witness contains an edge")


def sat_independent_witness(
    n: int, edges: list[Edge], allowed_vertices: list[int], target: int
) -> tuple[int, ...] | None:
    """Independent CaDiCaL check used for every branch-search UNSAT claim."""

    pool = IDPool(start_from=n + 1)
    clauses = [[-(u + 1), -(v + 1)] for u, v in edges]
    clauses.extend(
        CardEnc.atleast(
            [vertex + 1 for vertex in allowed_vertices],
            bound=target,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        positive = {literal for literal in solver.get_model() if literal > 0}
    chosen = tuple(vertex for vertex in allowed_vertices if vertex + 1 in positive)
    if len(chosen) < target:
        raise AssertionError("SAT cardinality witness is too small")
    return tuple(chosen[:target])


def iter_bit_indices(mask: int):
    while mask:
        chosen = mask & -mask
        yield chosen.bit_length() - 1
        mask -= chosen


def switch_json(switch: Switch) -> dict[str, list[list[int]]]:
    removed, added = switch
    return {
        "removed": [list(candidate) for candidate in removed],
        "added": [list(candidate) for candidate in added],
    }


def main() -> int:
    graph = load_base(SOURCE)
    nx_nines, alpha = enumerate_networkx(graph)
    sat_nines = enumerate_sat(graph)
    if nx_nines != sat_nines or alpha != 9:
        raise AssertionError("the two independent-9 enumerators disagree")

    switches_a = enumerate_switches_by_edge_pairs(graph)
    switches_b = enumerate_switches_by_four_sets(graph)
    if switches_a != switches_b:
        raise AssertionError("the two switch enumerators disagree")
    switches = switches_a
    if len(switches) != 16_694:
        raise AssertionError("unexpected one-switch family size")

    degrees = dict(graph.degree())
    eligible = sorted(vertex for vertex in graph if degrees[vertex] <= 8)
    degree_eights = sorted(vertex for vertex in eligible if degrees[vertex] == 8)
    low_vertices = sorted(vertex for vertex in eligible if degrees[vertex] < 8)
    if len(eligible) != 15 or len(degree_eights) != 14 or low_vertices != [35]:
        raise AssertionError("unexpected attachment-capacity profile")
    low = low_vertices[0]

    independent_masks = [sum(1 << vertex for vertex in witness) for witness in nx_nines]
    all_independent_sets = (1 << len(nx_nines)) - 1
    all_switches = (1 << len(switches)) - 1

    # For each nonedge e, record all switches that add e.  Then, for every
    # original independent 9-set I, record all switches whose added pair
    # destroys I.
    edge_to_switches: dict[Edge, int] = {}
    destruction_masks: list[int] = []
    for switch_index, (_, added) in enumerate(switches):
        switch_bit = 1 << switch_index
        destroyed = 0
        for added_edge in added:
            edge_to_switches[added_edge] = (
                edge_to_switches.get(added_edge, 0) | switch_bit
            )
        for independent_index, witness_mask in enumerate(independent_masks):
            if any(
                witness_mask & ((1 << u) | (1 << v)) == ((1 << u) | (1 << v))
                for u, v in added
            ):
                destroyed |= 1 << independent_index
        destruction_masks.append(destroyed)

    destroyers_of_independent_set: list[int] = []
    for witness in nx_nines:
        destroyers = 0
        for candidate in itertools.combinations(witness, 2):
            destroyers |= edge_to_switches.get(edge(*candidate), 0)
        destroyers_of_independent_set.append(destroyers)

    # Cross-check the two orientations of the destruction incidence matrix.
    for switch_index, destroyed in enumerate(destruction_masks):
        reconstructed = 0
        switch_bit = 1 << switch_index
        for independent_index, destroyers in enumerate(destroyers_of_independent_set):
            if destroyers & switch_bit:
                reconstructed |= 1 << independent_index
        if reconstructed != destroyed:
            raise AssertionError("destruction-incidence cross-check failed")

    membership = {vertex: 0 for vertex in eligible}
    for independent_index, witness in enumerate(nx_nines):
        witness_bit = 1 << independent_index
        for vertex in witness:
            if vertex in membership:
                membership[vertex] |= witness_bit

    def hit_mask(vertices: Iterable[int]) -> int:
        answer = 0
        for vertex in vertices:
            answer |= membership[vertex]
        return answer

    def switches_destroying_every(mask: int) -> int:
        candidates = all_switches
        for independent_index in iter_bit_indices(mask):
            candidates &= destroyers_of_independent_set[independent_index]
            if not candidates:
                break
        return candidates

    # If S is a transversal after a switch, every original independent 9-set
    # missed by S must be destroyed by one of the two added edges.
    survivor_candidate_counts: dict[int, int] = {}
    survivor_candidates: dict[int, list[tuple[int, tuple[int, ...]]]] = {
        6: [],
        7: [],
    }
    for size in range(0, 8):
        count = 0
        for subset in itertools.combinations(eligible, size):
            missed = all_independent_sets & ~hit_mask(subset)
            candidate_switches = switches_destroying_every(missed)
            count += candidate_switches.bit_count()
            if size in survivor_candidates:
                survivor_candidates[size].extend(
                    (switch_index, subset)
                    for switch_index in iter_bit_indices(candidate_switches)
                )
        survivor_candidate_counts[size] = count

    expected_survivor_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 71, 7: 1477}
    if survivor_candidate_counts != expected_survivor_counts:
        raise AssertionError("unexpected surviving-original transversal screen")

    base_adjacency = adjacency_bits(graph)
    base_edges = {edge(u, v) for u, v in graph.edges()}
    switched_adjacencies: dict[int, list[int]] = {}
    switched_edge_lists: dict[int, list[Edge]] = {}

    def get_adjacency(switch_index: int) -> list[int]:
        if switch_index not in switched_adjacencies:
            switched_adjacencies[switch_index] = switched_adjacency(
                base_adjacency, switches[switch_index]
            )
        return switched_adjacencies[switch_index]

    def get_edges(switch_index: int) -> list[Edge]:
        if switch_index not in switched_edge_lists:
            switched_edge_lists[switch_index] = switched_edges(
                base_edges, switches[switch_index]
            )
        return switched_edge_lists[switch_index]

    full_old_mask = (1 << graph.number_of_nodes()) - 1
    exact_small: list[tuple[int, tuple[int, ...]]] = []
    new_independent_nine_certificates: list[dict[str, object]] = []
    for size in (6, 7):
        for switch_index, subset in survivor_candidates[size]:
            allowed = full_old_mask
            for vertex in subset:
                allowed &= ~(1 << vertex)
            adjacency = get_adjacency(switch_index)
            witness = find_independent_witness(adjacency, allowed, 9)
            if witness is None:
                # This is an UNSAT claim, so cross-check it with CaDiCaL.
                sat_witness = sat_independent_witness(
                    graph.number_of_nodes(),
                    get_edges(switch_index),
                    [vertex for vertex in graph if vertex not in subset],
                    9,
                )
                if sat_witness is not None:
                    raise AssertionError("branch search and SAT disagree on a transversal")
                exact_small.append((switch_index, subset))
            else:
                verify_independent_witness(adjacency, witness, 9, subset)
                if len(new_independent_nine_certificates) < 8:
                    new_independent_nine_certificates.append(
                        {
                            "switch_index": switch_index,
                            "subset": list(subset),
                            "new_independent_9": list(witness),
                        }
                    )

    exact_counts = Counter(len(subset) for _, subset in exact_small)
    if exact_counts != Counter({6: 11, 7: 363}):
        raise AssertionError("unexpected exact small-transversal catalogue")

    # The remaining case with both neighbourhoods of size at least 8 is
    # forced by capacity: the degree-6 vertex occurs twice, and the fourteen
    # degree-8 vertices are partitioned 7+7.  It suffices to retain only the
    # original independent 9-sets that survive a switch.
    balanced_partitions: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
    anchor = degree_eights[0]
    for first in itertools.combinations(degree_eights, 7):
        if anchor not in first:
            continue
        first_set = set(first)
        second = tuple(vertex for vertex in degree_eights if vertex not in first_set)
        first_neighbourhood = (low,) + first
        second_neighbourhood = (low,) + second
        failures = (
            all_independent_sets & ~hit_mask(first_neighbourhood)
        ) | (
            all_independent_sets & ~hit_mask(second_neighbourhood)
        )
        balanced_partitions.append((first, second, failures))
        if switches_destroying_every(failures):
            raise AssertionError("a balanced pair passed the necessary screen")
    if len(balanced_partitions) != 1716:
        raise AssertionError("unexpected balanced-partition count")

    # An independent switch-wise scan both cross-checks the zero count and
    # quantifies the nearest miss.
    best_balanced: tuple[int, int, tuple[int, ...]] | None = None
    for switch_index, destroyed in enumerate(destruction_masks):
        for first, _, failures in balanced_partitions:
            residual = (failures & ~destroyed).bit_count()
            if best_balanced is None or residual < best_balanced[0]:
                best_balanced = (residual, switch_index, first)
    if best_balanced is None or best_balanced[0] != 77:
        raise AssertionError("unexpected nearest balanced-pair residual")

    # Exhaust all exact transversals of size at most 7.  If S is one old
    # neighbourhood, the other is contained in U(S): the low vertex plus all
    # degree-8 vertices not already used by S.  Therefore it is enough to show
    # that U(S) itself is not a transversal.  Bases with alpha >= 10 are
    # already impossible and are separated first.
    alpha_ten_cache: dict[int, tuple[int, ...] | None] = {}
    alpha_ten_sat_checked: set[int] = set()
    alpha_bad_records: list[dict[str, object]] = []
    upper_support_failure_records: list[dict[str, object]] = []
    feasible_pairs: list[dict[str, object]] = []

    for switch_index, subset in exact_small:
        adjacency = get_adjacency(switch_index)
        if switch_index not in alpha_ten_cache:
            alpha_ten_cache[switch_index] = find_independent_witness(
                adjacency, full_old_mask, 10
            )
        alpha_ten = alpha_ten_cache[switch_index]
        if alpha_ten is not None:
            verify_independent_witness(adjacency, alpha_ten, 10)
            alpha_bad_records.append(
                {
                    "switch_index": switch_index,
                    "small_transversal": list(subset),
                    "independent_10": list(alpha_ten),
                }
            )
            continue

        if switch_index not in alpha_ten_sat_checked:
            sat_alpha_ten = sat_independent_witness(
                graph.number_of_nodes(), get_edges(switch_index), list(graph), 10
            )
            if sat_alpha_ten is not None:
                raise AssertionError("branch search and SAT disagree on alpha <= 9")
            alpha_ten_sat_checked.add(switch_index)

        upper_support = tuple(
            [low] + [vertex for vertex in degree_eights if vertex not in subset]
        )
        allowed = full_old_mask
        for vertex in upper_support:
            allowed &= ~(1 << vertex)
        missed_nine = find_independent_witness(adjacency, allowed, 9)
        if missed_nine is None:
            feasible_pairs.append(
                {
                    "switch_index": switch_index,
                    "small_transversal": list(subset),
                    "compatible_upper_support": list(upper_support),
                }
            )
        else:
            verify_independent_witness(adjacency, missed_nine, 9, upper_support)
            upper_support_failure_records.append(
                {
                    "switch_index": switch_index,
                    "small_transversal": list(subset),
                    "compatible_upper_support": list(upper_support),
                    "independent_9_missed_by_upper_support": list(missed_nine),
                }
            )

    alpha_bad_counts = Counter(
        len(record["small_transversal"]) for record in alpha_bad_records
    )
    upper_failure_counts = Counter(
        len(record["small_transversal"]) for record in upper_support_failure_records
    )
    if alpha_bad_counts != Counter({6: 8, 7: 323}):
        raise AssertionError("unexpected alpha-bad small-transversal count")
    if upper_failure_counts != Counter({6: 3, 7: 40}):
        raise AssertionError("unexpected compatible-support failure count")
    if feasible_pairs:
        raise AssertionError("a degree-compatible neighbourhood pair survived")

    best_residual, best_switch_index, best_first = best_balanced
    best_first_set = set(best_first)
    best_second = tuple(
        vertex for vertex in degree_eights if vertex not in best_first_set
    )
    best_failures = next(
        failures
        for first, _, failures in balanced_partitions
        if first == best_first
    )
    best_destroyed = destruction_masks[best_switch_index]

    exact_catalog_records = [
        {"switch_index": switch_index, "subset": list(subset)}
        for switch_index, subset in exact_small
    ]
    result = {
        "schema": "erdos151-r39-one-old-switch-extension-audit-v1",
        "source": {
            "path": str(SOURCE.resolve()),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "base": {
            "n": graph.number_of_nodes(),
            "m": graph.number_of_edges(),
            "alpha": alpha,
            "triangle_free": not any(nx.triangles(graph).values()),
            "degree_distribution": dict(sorted(Counter(degrees.values()).items())),
        },
        "independent_9_sets": {
            "networkx_count": len(nx_nines),
            "cadical_count": len(sat_nines),
            "common_sha256": digest_sets(nx_nines),
            "enumerations_identical": True,
        },
        "one_old_switch_family": {
            "definition": (
                "Delete two disjoint old edges and add one of the two cross "
                "matchings, requiring both added pairs to be old nonedges."
            ),
            "edge_pair_enumerator_count": len(switches_a),
            "four_vertex_matching_enumerator_count": len(switches_b),
            "enumerations_identical": True,
            "common_sha256": digest_switches(switches),
        },
        "attachment_capacity_under_Delta_9": {
            "eligible_old_vertices": eligible,
            "degree_8_vertices_capacity_1_each": degree_eights,
            "degree_6_vertex_effective_capacity_2": low,
            "total_effective_capacity_for_two_new_vertices": 16,
        },
        "small_transversal_screen": {
            "surviving_original_candidate_pairs_by_size": {
                str(size): survivor_candidate_counts[size] for size in range(0, 8)
            },
            "exact_transversal_pairs_by_size": {
                "6": exact_counts[6],
                "7": exact_counts[7],
            },
            "exact_transversal_unique_switches": len(
                {switch_index for switch_index, _ in exact_small}
            ),
            "exact_catalog_sha256": digest_records(
                "erdos151-r39-exact-small-transversals-v1", exact_catalog_records
            ),
            "branch_unsat_claims_crosschecked_by_cadical": len(exact_small),
            "sample_new_independent_9_certificates": new_independent_nine_certificates,
        },
        "balanced_size_8_pair_screen": {
            "unordered_partitions": len(balanced_partitions),
            "switch_partition_comparisons": len(switches) * len(balanced_partitions),
            "necessary_passes": 0,
            "nearest_residual_surviving_independent_9_sets": best_residual,
            "nearest_switch": switch_json(switches[best_switch_index]),
            "nearest_first_degree_8_side": list(best_first),
            "nearest_second_degree_8_side": list(best_second),
            "failure_sets_before_switch": best_failures.bit_count(),
            "all_original_sets_destroyed_by_switch": best_destroyed.bit_count(),
            "failure_sets_destroyed_by_switch": (
                best_failures & best_destroyed
            ).bit_count(),
        },
        "small_transversal_pair_exhaustion": {
            "exact_small_transversal_pairs": len(exact_small),
            "pairs_on_bases_with_independent_10": len(alpha_bad_records),
            "by_size_on_bases_with_independent_10": {
                "6": alpha_bad_counts[6],
                "7": alpha_bad_counts[7],
            },
            "remaining_pairs_whose_largest_compatible_support_misses_an_independent_9": len(
                upper_support_failure_records
            ),
            "remaining_by_size": {
                "6": upper_failure_counts[6],
                "7": upper_failure_counts[7],
            },
            "alpha_le_9_switches_crosschecked_unsat_by_cadical": len(
                alpha_ten_sat_checked
            ),
            "degree_compatible_neighbourhood_pairs": len(feasible_pairs),
            "alpha_bad_catalog_sha256": digest_records(
                "erdos151-r39-alpha-bad-small-transversal-v1", alpha_bad_records
            ),
            "upper_support_failure_catalog_sha256": digest_records(
                "erdos151-r39-upper-support-failures-v1",
                upper_support_failure_records,
            ),
            "upper_support_failure_certificates": upper_support_failure_records,
        },
        "theorem": (
            "For every labelled graph B' obtained from this pinned 39-vertex "
            "base by one valid old-old 2-switch, no graph obtained from B' by "
            "adding two vertices and arbitrary incident edges has both Delta "
            "<= 9 and alpha <= 9."
        ),
        "proof_summary": (
            "Only the fourteen old degree-8 vertices and the unique old "
            "degree-6 vertex can meet the new vertices, with effective total "
            "capacity 16. Each new old-neighbourhood must hit every independent "
            "9-set of B'. If both have size at least 8, capacity forces a "
            "balanced 7+7 partition of the degree-8 vertices plus the low "
            "vertex on both sides; all 1,716 partitions fail for all 16,694 "
            "switches. Otherwise one neighbourhood is an exact transversal of "
            "size at most 7. There are none through size 5, eleven size-6 pairs, "
            "and 363 size-7 pairs. Of these 374 pairs, 331 already lie on a "
            "base with an independent 10-set; for each of the remaining 43, "
            "the largest support compatible with old degree capacities misses "
            "an explicitly certified independent 9-set."
        ),
        "claim_scope": (
            "Exact only for the pinned labelled base, exactly one old-old "
            "2-switch, and then two added vertices."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
