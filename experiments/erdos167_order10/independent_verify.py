#!/usr/bin/env python3
"""Independent certificate verifier for the order-10 Tuza residual.

This deliberately uses NetworkX's graph6 decoder and decision recurrences,
not the primary screen/parser or its optimization entry points.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from functools import lru_cache
from itertools import combinations
from pathlib import Path

import networkx as nx


N = 10
EDGES = tuple(combinations(range(N), 2))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}


def graph_data(g6: str):
    complement = nx.from_graph6_bytes(g6.encode("ascii"))
    graph = nx.complement(complement)
    graph_mask = 0
    for u, v in graph.edges:
        graph_mask |= 1 << EDGE_INDEX[tuple(sorted((u, v)))]
    triangles = []
    vertices = []
    for triple in combinations(range(N), 3):
        if all(graph.has_edge(*edge) for edge in combinations(triple, 2)):
            mask = 0
            for edge in combinations(triple, 2):
                mask |= 1 << EDGE_INDEX[edge]
            triangles.append(mask)
            vertices.append(triple)
    return graph, graph_mask, tuple(triangles), tuple(vertices)


def parity_cardinality_upper(active_edges: int) -> int:
    target_parity = 0
    active_indices = []
    for index, (u, v) in enumerate(EDGES):
        if active_edges & (1 << index):
            active_indices.append(index)
            target_parity ^= (1 << u) | (1 << v)
    # Bit d of attainable[p] means a d-edge deletion with parity p exists.
    attainable = [0] * (1 << N)
    attainable[0] = 1
    for index in active_indices:
        u, v = EDGES[index]
        endpoints = (1 << u) | (1 << v)
        updated = attainable.copy()
        for parity, counts in enumerate(attainable):
            if counts:
                updated[parity ^ endpoints] |= counts << 1
        attainable = updated
    m = len(active_indices)
    feasible_deletions = attainable[target_parity]
    for packing in range(m // 3, -1, -1):
        deleted = m - 3 * packing
        if feasible_deletions & (1 << deleted):
            return packing
    raise AssertionError("empty packing must be feasible")


def packing_infeasible_above(triangles: tuple[int, ...], claimed: int) -> bool:
    conflicts = []
    incidence = [0] * len(EDGES)
    for index, triangle in enumerate(triangles):
        conflict = 0
        for other_index, other in enumerate(triangles):
            if triangle & other:
                conflict |= 1 << other_index
        conflicts.append(conflict)
        for edge_index in range(len(EDGES)):
            if triangle & (1 << edge_index):
                incidence[edge_index] |= 1 << index

    union_cache: dict[int, int] = {}

    def union(active: int) -> int:
        if active not in union_cache:
            value = 0
            scan = active
            while scan:
                bit = scan & -scan
                scan ^= bit
                value |= triangles[bit.bit_length() - 1]
            union_cache[active] = value
        return union_cache[active]

    @lru_cache(maxsize=None)
    def possible(active: int, needed: int) -> bool:
        if needed <= 0:
            return True
        if active.bit_count() < needed or union(active).bit_count() < 3 * needed:
            return False
        pivot_incidence = 0
        pivot_size = -1
        for incident in incidence:
            current = incident & active
            if current.bit_count() > pivot_size:
                pivot_incidence, pivot_size = current, current.bit_count()
        scan = pivot_incidence
        while scan:
            bit = scan & -scan
            scan ^= bit
            triangle_index = bit.bit_length() - 1
            if possible(active & ~conflicts[triangle_index], needed - 1):
                return True
        return possible(active & ~pivot_incidence, needed)

    all_triangles = (1 << len(triangles)) - 1
    return not possible(all_triangles, claimed + 1)


def cover_infeasible_below(triangles: tuple[int, ...], claimed: int) -> bool:
    incidence = [0] * len(EDGES)
    conflicts = []
    for index, triangle in enumerate(triangles):
        for edge_index in range(len(EDGES)):
            if triangle & (1 << edge_index):
                incidence[edge_index] |= 1 << index
        conflict = 0
        for other_index, other in enumerate(triangles):
            if triangle & other:
                conflict |= 1 << other_index
        conflicts.append(conflict)

    def packing_lower(active: int) -> int:
        count = 0
        while active:
            scan = active
            index = -1
            score = 10**9
            while scan:
                bit = scan & -scan
                scan ^= bit
                candidate = bit.bit_length() - 1
                candidate_score = (conflicts[candidate] & active).bit_count()
                if candidate_score < score:
                    index, score = candidate, candidate_score
            count += 1
            active &= ~conflicts[index]
        return count

    @lru_cache(maxsize=None)
    def possible(active: int, budget: int) -> bool:
        if not active:
            return True
        if budget <= 0 or packing_lower(active) > budget:
            return False
        # Choose a triangle whose three deletion branches jointly hit many
        # active triangles.
        pivot = -1
        pivot_score = -1
        scan = active
        while scan:
            bit = scan & -scan
            scan ^= bit
            index = bit.bit_length() - 1
            hits = [
                (incidence[e] & active).bit_count()
                for e in range(len(EDGES))
                if triangles[index] & (1 << e)
            ]
            score = sum(hits)
            if score > pivot_score:
                pivot, pivot_score = index, score
        branches = []
        edge_bits = triangles[pivot]
        while edge_bits:
            edge_bit = edge_bits & -edge_bits
            edge_bits ^= edge_bit
            edge_index = edge_bit.bit_length() - 1
            remaining = active & ~incidence[edge_index]
            branches.append((remaining.bit_count(), remaining))
        return any(possible(remaining, budget - 1) for _, remaining in sorted(branches))

    all_triangles = (1 << len(triangles)) - 1
    return not possible(all_triangles, claimed - 1)


def mantel_cover_lower(graph: nx.Graph) -> int:
    adjacency = [0] * N
    for u, v in graph.edges:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    internal = [0] * (1 << N)
    largest_forced = 0
    for subset in range(1, 1 << N):
        bit = subset & -subset
        vertex = bit.bit_length() - 1
        rest = subset ^ bit
        internal[subset] = internal[rest] + (adjacency[vertex] & rest).bit_count()
        largest_forced = max(
            largest_forced,
            internal[subset] - subset.bit_count() ** 2 // 4,
        )
    return largest_forced


def verify_witnesses(record, graph, triangles, triangle_vertices):
    actual = {vertices: mask for vertices, mask in zip(triangle_vertices, triangles)}
    used = 0
    for raw in record["packing"]:
        vertices = tuple(sorted(raw))
        if vertices not in actual or used & actual[vertices]:
            raise AssertionError("invalid packing witness")
        used |= actual[vertices]
    if len(record["packing"]) != record["nu"]:
        raise AssertionError("packing size")

    cover = {tuple(sorted(raw)) for raw in record["cover"]}
    if len(cover) != record["tau"] or not all(graph.has_edge(*edge) for edge in cover):
        raise AssertionError("invalid cover edges")
    cover_mask = sum(1 << EDGE_INDEX[edge] for edge in cover)
    if any(not (triangle & cover_mask) for triangle in triangles):
        raise AssertionError("unhit triangle")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    count = 0
    parity_closed = 0
    packing_searches = 0
    mantel_closed = 0
    cover_searches = 0
    digest = hashlib.sha256()
    maximum_gap = -10**9
    violations = 0

    with args.records.open("rb") as source:
        for raw_line in source:
            digest.update(raw_line)
            record = json.loads(raw_line)
            graph, mask, triangles, vertices = graph_data(record["complement_g6"])
            if f"{mask:012x}" != record["graph_mask_lex"] or len(triangles) != record["triangles"]:
                raise AssertionError("independent decode mismatch")
            verify_witnesses(record, graph, triangles, vertices)

            active_union = 0
            for triangle in triangles:
                active_union |= triangle
            parity_upper = parity_cardinality_upper(active_union)
            if parity_upper == record["nu"]:
                parity_closed += 1
            else:
                packing_searches += 1
                if not packing_infeasible_above(triangles, record["nu"]):
                    raise AssertionError("packing optimum mismatch")

            mantel_lower = mantel_cover_lower(graph)
            if mantel_lower == record["tau"]:
                mantel_closed += 1
            else:
                cover_searches += 1
                if not cover_infeasible_below(triangles, record["tau"]):
                    raise AssertionError("cover optimum mismatch")

            gap = record["tau"] - 2 * record["nu"]
            maximum_gap = max(maximum_gap, gap)
            violations += gap > 0
            count += 1
            if count % 250 == 0:
                print(f"verified {count}", flush=True)

    summary = {
        "schema": "tuza-order-10-independent-verifier-v1",
        "records": count,
        "records_sha256": digest.hexdigest(),
        "parity_closed_packings": parity_closed,
        "packing_decision_searches": packing_searches,
        "mantel_closed_covers": mantel_closed,
        "cover_decision_searches": cover_searches,
        "maximum_gap": maximum_gap,
        "violations": violations,
        "elapsed_seconds": round(time.perf_counter() - start, 6),
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
