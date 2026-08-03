#!/usr/bin/env python3
"""Structured construction pulse for Erdos problem 149 at Delta = 4.

This is deliberately not a general graph generator.  It checks two small,
theory-motivated families:

* one-vertex perturbations of the extremal C5[2] blow-up, and
* 4-regular circulant graphs Cay(Z_n,{+-a,+-b}).

For an optional 4-regular catalogue it also checks whether every graph has an
explicit strong edge-colouring with at most 20 colours.  The compatibility
graph J has one vertex for each edge of G, adjacent when the two G-edges are
strongly independent.  Colour classes of a strong edge-colouring are cliques
of J.  With 24 G-edges, saving four colours is equivalent to one of the five
block-size patterns handled by ``saving_four_witness``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


Edge = tuple[int, int]


def norm_edge(a: int, b: int) -> Edge:
    if a == b:
        raise ValueError("loops are not allowed")
    return (a, b) if a < b else (b, a)


def validate_graph(n: int, edges: Iterable[Edge], max_degree: int = 4) -> tuple[list[Edge], list[set[int]]]:
    edge_list = sorted({norm_edge(a, b) for a, b in edges})
    adjacency = [set() for _ in range(n)]
    for a, b in edge_list:
        if not (0 <= a < b < n):
            raise ValueError("edge endpoint outside graph")
        adjacency[a].add(b)
        adjacency[b].add(a)
    if any(len(row) > max_degree for row in adjacency):
        raise ValueError("maximum degree exceeded")
    return edge_list, adjacency


def compatibility_graph(n: int, edges: Iterable[Edge]) -> tuple[list[Edge], list[int]]:
    edge_list, adjacency = validate_graph(n, edges)
    masks = [0] * len(edge_list)
    for i, (a, b) in enumerate(edge_list):
        for j in range(i + 1, len(edge_list)):
            c, d = edge_list[j]
            if len({a, b, c, d}) != 4:
                continue
            if any(y in adjacency[x] for x in (a, b) for y in (c, d)):
                continue
            masks[i] |= 1 << j
            masks[j] |= 1 << i
    return edge_list, masks


def mask_vertices(mask: int) -> list[int]:
    out: list[int] = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


def find_matching(masks: list[int], available: int, wanted: int) -> list[list[int]] | None:
    """Find ``wanted`` vertex-disjoint edges of J by bounded recursion."""

    memo: set[tuple[int, int]] = set()

    def rec(avail: int, left: int) -> list[list[int]] | None:
        if left == 0:
            return []
        if avail.bit_count() < 2 * left:
            return None
        state = (avail, left)
        if state in memo:
            return None
        # Prefer a vertex with few available neighbours; the skip branch then
        # rapidly proves failure in the only cases that are remotely tight.
        vertices = mask_vertices(avail)
        v = min(vertices, key=lambda x: (masks[x] & avail).bit_count())
        vbit = 1 << v
        partners = masks[v] & avail & ~vbit
        while partners:
            ubit = partners & -partners
            u = ubit.bit_length() - 1
            tail = rec(avail & ~vbit & ~ubit, left - 1)
            if tail is not None:
                return [[v, u], *tail]
            partners ^= ubit
        skipped = rec(avail & ~vbit, left)
        if skipped is not None:
            return skipped
        memo.add(state)
        return None

    return rec(available, wanted)


def cliques_of_size(masks: list[int], wanted: int) -> list[int]:
    all_vertices = (1 << len(masks)) - 1
    out: list[int] = []

    def rec(chosen: int, candidates: int, depth: int) -> None:
        if depth == wanted:
            out.append(chosen)
            return
        if candidates.bit_count() < wanted - depth:
            return
        while candidates:
            bit = candidates & -candidates
            v = bit.bit_length() - 1
            candidates ^= bit
            rec(chosen | bit, candidates & masks[v], depth + 1)

    rec(0, all_vertices, 0)
    return out


def verify_blocks(masks: list[int], blocks: list[list[int]]) -> None:
    used: set[int] = set()
    for block in blocks:
        if used.intersection(block):
            raise AssertionError("colour blocks are not disjoint")
        used.update(block)
        for i, a in enumerate(block):
            for b in block[i + 1 :]:
                if not (masks[a] >> b) & 1:
                    raise AssertionError("a claimed colour block is not a J-clique")


def saving_two_witness(masks: list[int]) -> dict | None:
    all_vertices = (1 << len(masks)) - 1
    triangles = cliques_of_size(masks, 3)
    if triangles:
        blocks = [mask_vertices(triangles[0])]
        verify_blocks(masks, blocks)
        return {"kind": "triangle", "blocks": blocks, "saving": 2}
    matching = find_matching(masks, all_vertices, 2)
    if matching is not None:
        verify_blocks(masks, matching)
        return {"kind": "matching_2", "blocks": matching, "saving": 2}
    return None


def saving_four_witness(masks: list[int]) -> dict | None:
    """Find an exact certificate that 24 edges use at most 20 colours.

    A partition saving at least four singleton colours has, after shrinking
    oversized classes if needed, one of: 5; 4+2; 3+3; 3+2+2; 2+2+2+2.
    """

    all_vertices = (1 << len(masks)) - 1
    matching = find_matching(masks, all_vertices, 4)
    if matching is not None:
        verify_blocks(masks, matching)
        return {"kind": "matching_4", "blocks": matching, "saving": 4}

    five_cliques = cliques_of_size(masks, 5)
    if five_cliques:
        blocks = [mask_vertices(five_cliques[0])]
        verify_blocks(masks, blocks)
        return {"kind": "clique_5", "blocks": blocks, "saving": 4}

    four_cliques = cliques_of_size(masks, 4)
    for clique in four_cliques:
        edge = find_matching(masks, all_vertices & ~clique, 1)
        if edge is not None:
            blocks = [mask_vertices(clique), *edge]
            verify_blocks(masks, blocks)
            return {"kind": "clique_4_plus_edge", "blocks": blocks, "saving": 4}

    triangles = cliques_of_size(masks, 3)
    for i, first in enumerate(triangles):
        remaining = all_vertices & ~first
        matching2 = find_matching(masks, remaining, 2)
        if matching2 is not None:
            blocks = [mask_vertices(first), *matching2]
            verify_blocks(masks, blocks)
            return {"kind": "triangle_plus_matching_2", "blocks": blocks, "saving": 4}
        for second in triangles[i + 1 :]:
            if not first & second:
                blocks = [mask_vertices(first), mask_vertices(second)]
                verify_blocks(masks, blocks)
                return {"kind": "two_triangles", "blocks": blocks, "saving": 4}
    return None


def graph6(n: int, edges: Iterable[Edge]) -> str:
    if not 0 <= n <= 62:
        raise ValueError("this compact encoder handles n <= 62")
    edge_set = {norm_edge(a, b) for a, b in edges}
    bits = [1 if (i, j) in edge_set else 0 for j in range(1, n) for i in range(j)]
    while len(bits) % 6:
        bits.append(0)
    chars = [chr(n + 63)]
    for start in range(0, len(bits), 6):
        value = 0
        for bit in bits[start : start + 6]:
            value = (value << 1) | bit
        chars.append(chr(value + 63))
    return "".join(chars)


def c5_blowup_edges() -> set[Edge]:
    edges: set[Edge] = set()
    for part in range(5):
        next_part = (part + 1) % 5
        for a in (2 * part, 2 * part + 1):
            for b in (2 * next_part, 2 * next_part + 1):
                edges.add(norm_edge(a, b))
    if len(edges) != 20:
        raise AssertionError("bad C5[2] construction")
    return edges


def perturbation_family(d: int, removed: int) -> Iterable[set[Edge]]:
    base = c5_blowup_edges()
    for deleted_tuple in itertools.combinations(sorted(base), removed):
        deleted = set(deleted_tuple)
        remaining = base - deleted
        _, adjacency = validate_graph(11, remaining)
        eligible = [v for v in range(10) if len(adjacency[v]) <= 3]
        for neighbours in itertools.combinations(eligible, d):
            graph = set(remaining)
            graph.update(norm_edge(10, v) for v in neighbours)
            try:
                validate_graph(11, graph)
            except ValueError:
                continue
            yield graph


def analyse_family(name: str, n: int, graphs: Iterable[set[Edge]], target_edges: int) -> dict:
    seen: set[frozenset[Edge]] = set()
    witness_types: Counter[str] = Counter()
    pair_counts: Counter[int] = Counter()
    closest: dict | None = None
    candidate: dict | None = None
    for graph in graphs:
        key = frozenset(graph)
        if key in seen:
            continue
        seen.add(key)
        edge_list, masks = compatibility_graph(n, graph)
        if len(edge_list) != target_edges:
            raise AssertionError("unexpected edge count")
        pair_count = sum(mask.bit_count() for mask in masks) // 2
        pair_counts[pair_count] += 1
        if target_edges == 21:
            matching = find_matching(masks, (1 << len(masks)) - 1, 1)
            witness = None if matching is None else {"kind": "edge", "blocks": matching, "saving": 1}
        elif target_edges == 22:
            witness = saving_two_witness(masks)
        elif target_edges == 24:
            witness = saving_four_witness(masks)
        else:
            raise ValueError("unsupported target")
        if witness is not None:
            verify_blocks(masks, witness["blocks"])
            witness_types[witness["kind"]] += 1
        else:
            candidate = {
                "edges": [list(edge) for edge in edge_list],
                "graph6": graph6(n, edge_list),
                "compatibility_edges": [
                    [i, j] for i, mask in enumerate(masks) for j in mask_vertices(mask) if i < j
                ],
            }
            break
        record = {
            "compatibility_pair_count": pair_count,
            "edges": [list(edge) for edge in edge_list],
            "graph6": graph6(n, edge_list),
            "witness": witness,
        }
        if closest is None or pair_count < closest["compatibility_pair_count"]:
            closest = record
    return {
        "name": name,
        "graphs_checked": len(seen),
        "edge_count": target_edges,
        "witness_type_distribution": dict(sorted(witness_types.items())),
        "compatibility_pair_count_distribution": dict(sorted(pair_counts.items())),
        "candidate": candidate,
        "closest_checked_graph": closest,
        "status": "CANDIDATE_FOUND" if candidate is not None else "NO_CANDIDATE_IN_SCOPE",
    }


def circulants(n: int) -> Iterable[set[Edge]]:
    # For n=11 or 12, the two inverse pairs are represented by 1,...,5.
    for a, b in itertools.combinations(range(1, (n - 1) // 2 + 1), 2):
        graph = {
            norm_edge(v, (v + step) % n)
            for v in range(n)
            for step in (a, -a, b, -b)
        }
        yield graph


def parse_upper_triangle_catalogue(path: Path, expected_n: int) -> Iterable[set[Edge]]:
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        fields = line.split()
        if len(fields) != 2 or int(fields[0]) != expected_n:
            raise ValueError(f"bad catalogue line {line_number}")
        bits = fields[1]
        if len(bits) != expected_n * (expected_n - 1) // 2 or set(bits) - {"0", "1"}:
            raise ValueError(f"bad bit string on line {line_number}")
        cursor = 0
        edges: set[Edge] = set()
        # This catalogue uses row-major upper-triangle order.
        for a in range(expected_n):
            for b in range(a + 1, expected_n):
                if bits[cursor] == "1":
                    edges.add((a, b))
                cursor += 1
        edge_list, adjacency = validate_graph(expected_n, edges)
        if len(edge_list) != 2 * expected_n or any(len(row) != 4 for row in adjacency):
            raise ValueError(f"catalogue graph {line_number} is not 4-regular")
        yield edges


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalogue-12", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    families = []
    for d, removed in ((2, 1), (3, 2), (4, 3)):
        families.append(
            analyse_family(
                f"C5[2]+x: degree(x)={d}, removed={removed}",
                11,
                perturbation_family(d, removed),
                21,
            )
        )
    families.append(
        analyse_family(
            "C5[2]+x: degree(x)=4, removed matching-sized set=2",
            11,
            perturbation_family(4, 2),
            22,
        )
    )
    families.append(analyse_family("4-regular circulants n=11", 11, circulants(11), 22))
    families.append(analyse_family("4-regular circulants n=12", 12, circulants(12), 24))

    catalogue = None
    if args.catalogue_12 is not None:
        raw = args.catalogue_12.read_bytes()
        catalogue = analyse_family(
            "connected 4-regular n=12 catalogue",
            12,
            parse_upper_triangle_catalogue(args.catalogue_12, 12),
            24,
        )
        catalogue["source"] = {
            "path": str(args.catalogue_12),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "url": "https://webhome.cs.uvic.ca/~wendym/manjeet/12_4reg.txt",
        }

    result = {
        "schema": "erdos149-structured-pulse-v1",
        "scope_warning": (
            "The perturbation and circulant families are construction probes, not exhaustive. "
            "The optional catalogue result is exhaustive only for its cited connected 4-regular class."
        ),
        "families": families,
        "catalogue_12": catalogue,
        "candidate_count": sum(
            family["candidate"] is not None for family in families
        ) + (int(catalogue is not None and catalogue["candidate"] is not None)),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "families": [
            {"name": f["name"], "graphs_checked": f["graphs_checked"], "status": f["status"]}
            for f in families
        ],
        "catalogue": None if catalogue is None else {
            "graphs_checked": catalogue["graphs_checked"], "status": catalogue["status"]
        },
        "candidate_count": result["candidate_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
