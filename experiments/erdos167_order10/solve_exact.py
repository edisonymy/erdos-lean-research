#!/usr/bin/env python3
"""Compute exact Tuza invariants on the screened order-10 residual."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import deque
from functools import lru_cache
from itertools import combinations
from pathlib import Path


N = 10
G6_EDGES = tuple((i, j) for j in range(1, N) for i in range(j))
LEX_EDGES = tuple((i, j) for i in range(N) for j in range(i + 1, N))
LEX_INDEX = {edge: index for index, edge in enumerate(LEX_EDGES)}
FULL = (1 << 45) - 1


def enumerate_triangles(graph: int):
    masks = []
    vertices = []
    for triple in combinations(range(N), 3):
        mask = sum(1 << LEX_INDEX[edge] for edge in combinations(triple, 2))
        if graph & mask == mask:
            masks.append(mask)
            vertices.append(triple)
    return tuple(masks), tuple(vertices)


@lru_cache(maxsize=None)
def minimum_parity_deletion(edges: int) -> int:
    adjacency = [[] for _ in range(N)]
    degrees = [0] * N
    for index, (u, v) in enumerate(LEX_EDGES):
        if edges & (1 << index):
            adjacency[u].append(v)
            adjacency[v].append(u)
            degrees[u] += 1
            degrees[v] += 1
    odd_vertices = tuple(v for v in range(N) if degrees[v] % 2)
    if not odd_vertices:
        return 0

    distances = []
    for source in odd_vertices:
        distance = [N + 1] * N
        distance[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if distance[v] == N + 1:
                    distance[v] = distance[u] + 1
                    queue.append(v)
        distances.append(distance)

    @lru_cache(maxsize=None)
    def pair_cost(unpaired: int) -> int:
        if not unpaired:
            return 0
        first_bit = unpaired & -unpaired
        first = first_bit.bit_length() - 1
        rest = unpaired ^ first_bit
        best = 10**6
        partners = rest
        while partners:
            partner_bit = partners & -partners
            partners ^= partner_bit
            partner = partner_bit.bit_length() - 1
            best = min(
                best,
                distances[first][odd_vertices[partner]]
                + pair_cost(rest ^ partner_bit),
            )
        return best

    return pair_cost((1 << len(odd_vertices)) - 1)


def decode_complement_lex(line: bytes) -> int:
    line = line.strip()
    if len(line) != 9 or line[0] != 73:
        raise ValueError(line)
    mask = 0
    bit_index = 0
    for char in line[1:]:
        value = char - 63
        for shift in range(5, -1, -1):
            if bit_index < 45 and value & (1 << shift):
                edge = G6_EDGES[bit_index]
                mask |= 1 << LEX_INDEX[edge]
            bit_index += 1
    return mask


def stable(record: dict[str, object]) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parity_cardinality_upper(active_edges: int) -> int:
    """Eulerian-union upper bound, including the edge count modulo three."""
    odd = 0
    for index, (u, v) in enumerate(LEX_EDGES):
        if active_edges & (1 << index):
            odd ^= (1 << u) | (1 << v)
    attainable = [0] * (1 << N)
    attainable[0] = 1  # bit d means a d-edge deletion set is attainable
    for index, (u, v) in enumerate(LEX_EDGES):
        if not active_edges & (1 << index):
            continue
        endpoints = (1 << u) | (1 << v)
        previous = attainable.copy()
        for parity, counts in enumerate(previous):
            if counts:
                attainable[parity ^ endpoints] |= counts << 1
    edge_count = active_edges.bit_count()
    for packing_size in range(edge_count // 3, -1, -1):
        deleted = edge_count - 3 * packing_size
        if attainable[odd] & (1 << deleted):
            return packing_size
    raise AssertionError("empty packing should be parity-feasible")


def greedy_packing(
    triangle_masks: tuple[int, ...],
    triangle_vertices: tuple[tuple[int, int, int], ...],
    target: int,
) -> tuple[tuple[int, int, int], ...]:
    conflicts = []
    for triangle in triangle_masks:
        conflict = 0
        for index, other in enumerate(triangle_masks):
            if triangle & other:
                conflict |= 1 << index
        conflicts.append(conflict)

    def complete(active: int) -> tuple[int, ...]:
        chosen = []
        while active:
            scan = active
            selected = -1
            score = 10**9
            while scan:
                bit = scan & -scan
                scan ^= bit
                index = bit.bit_length() - 1
                candidate_score = (active & conflicts[index]).bit_count()
                if candidate_score < score:
                    selected, score = index, candidate_score
            chosen.append(selected)
            active &= ~conflicts[selected]
        return tuple(chosen)

    all_triangles = (1 << len(triangle_masks)) - 1
    best = complete(all_triangles)
    if len(best) < target:
        for forced in range(len(triangle_masks)):
            candidate = (forced,) + complete(all_triangles & ~conflicts[forced])
            if len(candidate) > len(best):
                best = candidate
                if len(best) == target:
                    break
    return tuple(triangle_vertices[index] for index in best)


def clique_packing(
    triangle_masks: tuple[int, ...],
    triangle_vertices: tuple[tuple[int, int, int], ...],
    initial: tuple[tuple[int, int, int], ...],
    target: int,
) -> tuple[tuple[int, int, int], ...]:
    """Independent maximum-clique fallback on triangle compatibility."""
    all_triangles = (1 << len(triangle_masks)) - 1
    compatibility = []
    for triangle in triangle_masks:
        compatible = 0
        for index, other in enumerate(triangle_masks):
            if not triangle & other:
                compatible |= 1 << index
        compatibility.append(compatible)

    vertex_to_index = {vertices: index for index, vertices in enumerate(triangle_vertices)}
    best = tuple(vertex_to_index[vertices] for vertices in initial)

    def color_sort(active: int) -> tuple[list[int], list[int]]:
        order: list[int] = []
        colors: list[int] = []
        uncolored = active
        color = 0
        while uncolored:
            color += 1
            available = uncolored
            while available:
                bit = available & -available
                vertex = bit.bit_length() - 1
                order.append(vertex)
                colors.append(color)
                uncolored &= ~bit
                available &= ~bit
                available &= ~compatibility[vertex]
        return order, colors

    def search(active: int, chosen: tuple[int, ...]) -> None:
        nonlocal best
        if len(best) == target:
            return
        if not active:
            if len(chosen) > len(best):
                best = chosen
            return
        order, colors = color_sort(active)
        for position in range(len(order) - 1, -1, -1):
            if len(chosen) + colors[position] <= len(best):
                return
            vertex = order[position]
            bit = 1 << vertex
            if active & bit:
                search(active & compatibility[vertex], chosen + (vertex,))
                active &= ~bit
                if len(best) == target:
                    return

    search(all_triangles, ())
    return tuple(triangle_vertices[index] for index in best)


def fast_cut_mantel_cover(graph: int):
    """Max-cut cover and induced Mantel bound (exact when they meet)."""
    adjacency = [0] * N
    for index, (u, v) in enumerate(LEX_EDGES):
        if graph & (1 << index):
            adjacency[u] |= 1 << v
            adjacency[v] |= 1 << u
    all_vertices = (1 << N) - 1

    best_cut = -1
    best_side = 0
    for side in range(1 << (N - 1)):
        outside = all_vertices ^ side
        cut = 0
        scan = side
        while scan:
            bit = scan & -scan
            scan ^= bit
            cut += (adjacency[bit.bit_length() - 1] & outside).bit_count()
        if cut > best_cut:
            best_cut, best_side = cut, side

    internal = [0] * (1 << N)
    largest_forced = 0
    forcing_subset = 0
    for vertices in range(1, 1 << N):
        bit = vertices & -vertices
        v = bit.bit_length() - 1
        rest = vertices ^ bit
        internal[vertices] = internal[rest] + (adjacency[v] & rest).bit_count()
        forced = internal[vertices] - vertices.bit_count() ** 2 // 4
        if forced > largest_forced:
            largest_forced, forcing_subset = forced, vertices

    upper_retained = graph.bit_count() - largest_forced
    cover = tuple(
        edge
        for index, edge in enumerate(LEX_EDGES)
        if graph & (1 << index)
        and bool(best_side & (1 << edge[0])) == bool(best_side & (1 << edge[1]))
    )
    certificate = {
        "max_cut_retained": best_cut,
        "mantel_upper_retained": upper_retained,
        "forcing_vertex_subset": forcing_subset,
    }
    return best_cut == upper_retained, len(cover), cover, certificate


def exact_hitting_cover(
    triangle_masks: tuple[int, ...],
    initial_cover: tuple[tuple[int, int], ...],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    """Exact three-way triangle hitting with a packing lower bound."""
    incidence = [0] * len(LEX_EDGES)
    conflicts = [0] * len(triangle_masks)
    for triangle_index, triangle in enumerate(triangle_masks):
        for edge_index in range(len(LEX_EDGES)):
            if triangle & (1 << edge_index):
                incidence[edge_index] |= 1 << triangle_index
        conflict = 0
        for other_index, other in enumerate(triangle_masks):
            if triangle & other:
                conflict |= 1 << other_index
        conflicts[triangle_index] = conflict

    def packing_lower(active: int) -> int:
        packed = 0
        while active:
            scan = active
            selected = -1
            score = 10**9
            while scan:
                bit = scan & -scan
                scan ^= bit
                index = bit.bit_length() - 1
                candidate_score = (active & conflicts[index]).bit_count()
                if candidate_score < score:
                    selected, score = index, candidate_score
            packed += 1
            active &= ~conflicts[selected]
        return packed

    best = len(initial_cover)
    best_deleted = 0
    for edge in initial_cover:
        best_deleted |= 1 << LEX_INDEX[edge]
    seen: dict[int, int] = {}

    def search(active: int, deleted: int) -> None:
        nonlocal best, best_deleted
        chosen = deleted.bit_count()
        if not active:
            if chosen < best:
                best, best_deleted = chosen, deleted
            return
        if chosen + packing_lower(active) >= best:
            return
        if seen.get(active, 10**9) <= chosen:
            return
        seen[active] = chosen

        scan = active
        pivot = -1
        pivot_score = -1
        while scan:
            bit = scan & -scan
            scan ^= bit
            triangle_index = bit.bit_length() - 1
            score = sum(
                (incidence[edge_index] & active).bit_count()
                for edge_index in range(len(LEX_EDGES))
                if triangle_masks[triangle_index] & (1 << edge_index)
            )
            if score > pivot_score:
                pivot, pivot_score = triangle_index, score

        branches = []
        edges = triangle_masks[pivot]
        while edges:
            edge_bit = edges & -edges
            edges ^= edge_bit
            edge_index = edge_bit.bit_length() - 1
            remaining = active & ~incidence[edge_index]
            branches.append((remaining.bit_count(), edge_bit, remaining))
        for _, edge_bit, remaining in sorted(branches):
            search(remaining, deleted | edge_bit)

    search((1 << len(triangle_masks)) - 1, 0)
    cover = tuple(
        edge for index, edge in enumerate(LEX_EDGES) if best_deleted & (1 << index)
    )
    return best, cover


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("residual", type=Path)
    parser.add_argument("records", type=Path)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()

    count = 0
    violations = 0
    equality = 0
    max_gap = -10**9
    distributions: dict[str, int] = {}
    records_digest = hashlib.sha256()
    start = time.perf_counter()

    with args.residual.open("rb") as source, args.records.open("wb") as output:
        for line in source:
            complement = decode_complement_lex(line)
            graph = FULL ^ complement
            triangle_masks, triangle_vertices = enumerate_triangles(graph)
            active_union = 0
            for triangle in triangle_masks:
                active_union |= triangle
            parity_cardinality_bound = parity_cardinality_upper(active_union)
            packing = greedy_packing(
                triangle_masks, triangle_vertices, parity_cardinality_bound
            )
            if len(packing) == parity_cardinality_bound:
                nu = len(packing)
                packing_route = "greedy witness equals parity-cardinality upper"
            else:
                print(
                    f"hard packing at record {count + 1}: "
                    f"lower={len(packing)} upper={parity_cardinality_bound}",
                    flush=True,
                )
                packing = clique_packing(
                    triangle_masks,
                    triangle_vertices,
                    packing,
                    parity_cardinality_bound,
                )
                nu = len(packing)
                packing_route = "compatibility maximum-clique fallback"
            cover_exact, tau, cover, cover_certificate = fast_cut_mantel_cover(graph)
            if not cover_exact:
                print(f"hard cover at record {count + 1}", flush=True)
                tau, cover = exact_hitting_cover(triangle_masks, cover)
            parity_deletion = minimum_parity_deletion(active_union)

            gap = tau - 2 * nu
            count += 1
            violations += gap > 0
            equality += gap == 0
            max_gap = max(max_gap, gap)
            key = f"nu={nu},tau={tau},gap={gap}"
            distributions[key] = distributions.get(key, 0) + 1
            record = {
                "complement_g6": line.strip().decode("ascii"),
                "complement_edges": complement.bit_count(),
                "graph_mask_lex": f"{graph:012x}",
                "triangles": len(triangle_masks),
                "nu": nu,
                "tau": tau,
                "gap": gap,
                "packing": [list(t) for t in packing],
                "packing_route": packing_route,
                "packing_parity_cardinality_upper": parity_cardinality_bound,
                "packing_parity_deletion": parity_deletion,
                "cover": [list(e) for e in cover],
                "cover_max_cut_retained": cover_certificate["max_cut_retained"],
                "cover_mantel_upper_retained": cover_certificate[
                    "mantel_upper_retained"
                ],
                "cover_forcing_vertex_subset": cover_certificate[
                    "forcing_vertex_subset"
                ],
            }
            payload = stable(record)
            output.write(payload)
            records_digest.update(payload)
            if count % 250 == 0:
                elapsed = time.perf_counter() - start
                print(f"{count} records in {elapsed:.1f}s", flush=True)

    summary = {
        "schema": "tuza-order-10-primary-exact-v1",
        "records": count,
        "violations": violations,
        "equality_cases": equality,
        "maximum_gap": max_gap,
        "record_sha256": records_digest.hexdigest(),
        "value_distribution": distributions,
        "elapsed_seconds": round(time.perf_counter() - start, 6),
        "engine": "parity-cardinality + compatibility-clique packing; cut/Mantel + exact hitting cover",
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
