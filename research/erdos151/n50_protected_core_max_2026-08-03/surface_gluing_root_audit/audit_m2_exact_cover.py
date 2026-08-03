#!/usr/bin/env python3
"""Independent recursive replay of the m=2 marked-factor quotient search.

This checker deliberately does not import NetworkX, PySAT, or either search
module.  It consumes the canonical branch representatives written by
``marked_factor_gluing_search.py``, reconstructs the two icosahedra and the
22-vertex sphere with its own graph6 decoder, and exhausts every marked-edge
exact cover by depth-first search.  Monotone pruning checks quotient edge
multiplicities, spurious triangles, and K4s directly.

This is an independent *branch* replay.  Completeness of the symmetry orbit
reduction is a separate obligation and is intentionally not claimed here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path


ICOSAHEDRON_EDGES = (
    (0, 1), (0, 5), (0, 7), (0, 8), (0, 11),
    (1, 2), (1, 5), (1, 6), (1, 8),
    (2, 3), (2, 6), (2, 8), (2, 9),
    (3, 4), (3, 6), (3, 9), (3, 10),
    (4, 5), (4, 6), (4, 10), (4, 11),
    (5, 6), (5, 11),
    (7, 8), (7, 9), (7, 10), (7, 11),
    (8, 9), (9, 10), (10, 11),
)


def pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def decode_graph6(record: str) -> list[int]:
    values = [ord(char) - 63 for char in record.strip()]
    if not values or values[0] < 0:
        raise ValueError("invalid graph6 record")
    if values[0] <= 62:
        n = values[0]
        payload = values[1:]
    elif len(values) >= 4 and values[0] == 63:
        n = (values[1] << 12) | (values[2] << 6) | values[3]
        payload = values[4:]
    else:
        raise ValueError("unsupported graph6 order")
    bits: list[int] = []
    for value in payload:
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = n * (n - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 record")
    adjacency = [0] * n
    cursor = 0
    # graph6's upper-triangle order is (0,1),(0,2),(1,2),... .
    for right in range(1, n):
        for left in range(right):
            if bits[cursor]:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
            cursor += 1
    return adjacency


def make_surface(sphere_g6: str) -> list[int]:
    adjacency = [0] * 46
    for offset in (0, 12):
        for left, right in ICOSAHEDRON_EDGES:
            a, b = left + offset, right + offset
            adjacency[a] |= 1 << b
            adjacency[b] |= 1 << a
    sphere = decode_graph6(sphere_g6)
    if len(sphere) != 22:
        raise ValueError("expected an order-22 sphere")
    for left in range(22):
        later = sphere[left] & ~((1 << (left + 1)) - 1)
        while later:
            bit = later & -later
            right = bit.bit_length() - 1
            a, b = left + 24, right + 24
            adjacency[a] |= 1 << b
            adjacency[b] |= 1 << a
            later ^= bit
    return adjacency


def edge_list(adjacency: list[int]) -> list[tuple[int, int]]:
    return [
        (left, right)
        for left in range(len(adjacency))
        for right in range(left + 1, len(adjacency))
        if adjacency[left] >> right & 1
    ]


def triangles(adjacency: list[int]) -> set[tuple[int, int, int]]:
    answer: set[tuple[int, int, int]] = set()
    for left in range(len(adjacency)):
        later = adjacency[left] & ~((1 << (left + 1)) - 1)
        while later:
            middle_bit = later & -later
            middle = middle_bit.bit_length() - 1
            common = adjacency[left] & adjacency[middle]
            common &= ~((1 << (middle + 1)) - 1)
            while common:
                right_bit = common & -common
                right = right_bit.bit_length() - 1
                answer.add((left, middle, right))
                common ^= right_bit
            later ^= middle_bit
    return answer


def cross_count(first: tuple[int, ...], second: tuple[int, ...], adjacency: list[int]) -> int:
    second_mask = sum(1 << vertex for vertex in second)
    return sum((adjacency[vertex] & second_mask).bit_count() for vertex in first)


def cross_edges(
    first: tuple[int, int], second: tuple[int, int], adjacency: list[int]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(
            pair(left, right)
            for left in first
            for right in second
            if adjacency[left] >> right & 1
        )
    )


def ordinary_fibre_ok(
    fibre: tuple[int, int], fixed: tuple[tuple[int, int], ...], adjacency: list[int]
) -> bool:
    left, right = fibre
    if adjacency[left] >> right & 1:
        return False
    if adjacency[left] & adjacency[right]:
        return False
    return all(cross_count(fibre, special, adjacency) < 2 for special in fixed)


def surface_sanity(adjacency: list[int]) -> dict[str, object]:
    edges = edge_list(adjacency)
    faces = triangles(adjacency)
    degrees = [mask.bit_count() for mask in adjacency]
    edge_codegrees = [(adjacency[a] & adjacency[b]).bit_count() for a, b in edges]
    return {
        "order": len(adjacency),
        "edges": len(edges),
        "triangles": len(faces),
        "degree_counts": dict(sorted(Counter(degrees).items())),
        "edge_codegree_counts": dict(sorted(Counter(edge_codegrees).items())),
        "ok": len(adjacency) == 46
        and len(edges) == 120
        and len(faces) == 80
        and Counter(degrees) == Counter({5: 44, 10: 2})
        and Counter(edge_codegrees) == Counter({2: 120}),
    }


def quotient_partial_ok(
    fibres: list[tuple[int, ...]],
    designated_heavy: set[frozenset[int]],
    adjacency: list[int],
    surface_faces: set[tuple[int, int, int]],
) -> bool:
    count = len(fibres)
    qadj = [0] * count
    multiplicity: dict[tuple[int, int], int] = {}
    for left in range(count):
        for right in range(left + 1, count):
            value = cross_count(fibres[left], fibres[right], adjacency)
            if value == 0:
                continue
            heavy = frozenset((left, right)) in designated_heavy
            if value != (2 if heavy else 1):
                return False
            qadj[left] |= 1 << right
            qadj[right] |= 1 << left
            multiplicity[(left, right)] = value

    # Every quotient triangle already visible in the partial graph must be
    # the injective image of a genuine surface face.
    face_images = set()
    vertex_to_fibre = {
        vertex: fibre_id for fibre_id, fibre in enumerate(fibres) for vertex in fibre
    }
    for face in surface_faces:
        if all(vertex in vertex_to_fibre for vertex in face):
            image = tuple(sorted(vertex_to_fibre[vertex] for vertex in face))
            if len(set(image)) != 3:
                return False
            face_images.add(image)
    for left in range(count):
        later = qadj[left] & ~((1 << (left + 1)) - 1)
        while later:
            middle_bit = later & -later
            middle = middle_bit.bit_length() - 1
            common = qadj[left] & qadj[middle]
            common &= ~((1 << (middle + 1)) - 1)
            while common:
                right_bit = common & -common
                right = right_bit.bit_length() - 1
                if (left, middle, right) not in face_images:
                    return False
                common ^= right_bit
            later ^= middle_bit

    # K4-freeness is monotone under adding more fibres.
    for first in range(count):
        later = qadj[first] & ~((1 << (first + 1)) - 1)
        while later:
            second_bit = later & -later
            second = second_bit.bit_length() - 1
            pair_common = qadj[first] & qadj[second]
            pair_common &= ~((1 << (second + 1)) - 1)
            common_scan = pair_common
            while common_scan:
                third_bit = common_scan & -common_scan
                third = third_bit.bit_length() - 1
                if qadj[third] & pair_common & ~((1 << (third + 1)) - 1):
                    return False
                common_scan ^= third_bit
            later ^= second_bit
    return True


def full_target_audit(
    fibres: list[tuple[int, ...]],
    designated_heavy: set[frozenset[int]],
    adjacency: list[int],
    surface_faces: set[tuple[int, int, int]],
) -> dict[str, object]:
    count = len(fibres)
    vertex_to_fibre = {
        vertex: fibre_id for fibre_id, fibre in enumerate(fibres) for vertex in fibre
    }
    if len(vertex_to_fibre) != len(adjacency):
        return {"exact": False, "reason": "fibres-not-a-partition"}
    multiplicity: Counter[tuple[int, int]] = Counter()
    for left, right in edge_list(adjacency):
        a, b = vertex_to_fibre[left], vertex_to_fibre[right]
        multiplicity[pair(a, b)] += 1
    if any(a == b for a, b in multiplicity):
        return {"exact": False, "reason": "loop"}
    qadj = [0] * count
    for (left, right), value in multiplicity.items():
        qadj[left] |= 1 << right
        qadj[right] |= 1 << left
        if value != (2 if frozenset((left, right)) in designated_heavy else 1):
            return {"exact": False, "reason": "wrong-edge-multiplicity"}
    degrees = [mask.bit_count() for mask in qadj]
    heavy_degrees = [0] * count
    for heavy in designated_heavy:
        left, right = tuple(heavy)
        heavy_degrees[left] += 1
        heavy_degrees[right] += 1
    codegrees = []
    bad_links = []
    for vertex in range(count):
        neighbours = [i for i in range(count) if qadj[vertex] >> i & 1]
        link_degrees = [
            sum(1 for other in neighbours if qadj[neighbour] >> other & 1)
            for neighbour in neighbours
        ]
        # C5 vee C5 has one degree-four hub and eight degree-two rim vertices.
        if Counter(link_degrees) != Counter({2: 8, 4: 1}):
            bad_links.append(vertex)
        for other in neighbours:
            if vertex < other:
                codegrees.append(
                    (
                        (qadj[vertex] & qadj[other]).bit_count(),
                        frozenset((vertex, other)) in designated_heavy,
                    )
                )
    face_images = {
        tuple(sorted(vertex_to_fibre[vertex] for vertex in face))
        for face in surface_faces
    }
    exact = (
        count == 24
        and len(multiplicity) == 108
        and Counter(multiplicity.values()) == Counter({1: 96, 2: 12})
        and degrees == [9] * 24
        and heavy_degrees == [1] * 24
        and len(face_images) == 80
        and all(value == (4 if heavy else 2) for value, heavy in codegrees)
        and not bad_links
    )
    return {
        "exact": exact,
        "edges": len(multiplicity),
        "multiplicity_counts": dict(sorted(Counter(multiplicity.values()).items())),
        "degree_counts": dict(sorted(Counter(degrees).items())),
        "heavy_degree_counts": dict(sorted(Counter(heavy_degrees).items())),
        "face_images": len(face_images),
        "codegree_counts": dict(sorted(Counter(value for value, _ in codegrees).items())),
        "bad_links": bad_links,
    }


def replay_branch(
    adjacency: list[int],
    surface_faces: set[tuple[int, int, int]],
    high: tuple[int, ...],
    fixed: tuple[tuple[int, int], ...],
    marked: tuple[tuple[int, int], ...],
) -> dict[str, object]:
    blocks: list[tuple[int, int, tuple[int, int], tuple[int, int]]] = []
    marked_count = len(marked)
    if marked_count % 2:
        raise ValueError("marked edge count must be even")
    for first_index, second_index in itertools.combinations(range(marked_count), 2):
        a, b = marked[first_index]
        c, d = marked[second_index]
        for first, second in ((pair(a, c), pair(b, d)), (pair(a, d), pair(b, c))):
            if not ordinary_fibre_ok(first, fixed, adjacency):
                continue
            if not ordinary_fibre_ok(second, fixed, adjacency):
                continue
            if set(cross_edges(first, second, adjacency)) != {
                marked[first_index], marked[second_index]
            }:
                continue
            blocks.append((first_index, second_index, first, second))
    incidence = [[] for _ in range(marked_count)]
    for block_index, block in enumerate(blocks):
        incidence[block[0]].append(block_index)
        incidence[block[1]].append(block_index)
    if len(high) != len(fixed):
        raise ValueError("each degree-ten singleton needs one exceptional mate fibre")
    constants: list[tuple[int, ...]] = [(vertex,) for vertex in high] + list(fixed)
    q = len(high)
    constant_heavy = {frozenset((index, q + index)) for index in range(q)}
    if not quotient_partial_ok(constants, constant_heavy, adjacency, surface_faces):
        return {"status": "fixed-obstruction", "blocks": len(blocks), "nodes": 0}

    block_edge_masks = [(1 << block[0]) | (1 << block[1]) for block in blocks]
    single_ok = []
    for block in blocks:
        one_fibres = constants + [block[2], block[3]]
        one_heavy = constant_heavy | {frozenset((4, 5))}
        single_ok.append(
            quotient_partial_ok(one_fibres, one_heavy, adjacency, surface_faces)
        )
    conflict_masks = [0] * len(blocks)
    for left in range(len(blocks)):
        if not single_ok[left]:
            conflict_masks[left] = (1 << len(blocks)) - 1
            continue
        for right in range(left + 1, len(blocks)):
            if block_edge_masks[left] & block_edge_masks[right]:
                conflict = True
            elif not single_ok[right]:
                conflict = True
            else:
                pair_fibres = constants + [
                    blocks[left][2],
                    blocks[left][3],
                    blocks[right][2],
                    blocks[right][3],
                ]
                pair_heavy = constant_heavy | {
                    frozenset((4, 5)),
                    frozenset((6, 7)),
                }
                conflict = not quotient_partial_ok(
                    pair_fibres, pair_heavy, adjacency, surface_faces
                )
            if conflict:
                conflict_masks[left] |= 1 << right
                conflict_masks[right] |= 1 << left

    nodes = 0
    partial_prunes = 0
    complete_covers = 0
    survivors: list[dict[str, object]] = []

    def recurse(
        used_edges: int,
        selected: list[int],
        forbidden_blocks: int,
        fibres: list[tuple[int, ...]],
        designated_heavy: set[frozenset[int]],
    ) -> None:
        nonlocal nodes, partial_prunes, complete_covers
        nodes += 1
        if used_edges == (1 << marked_count) - 1:
            complete_covers += 1
            audit = full_target_audit(
                fibres, designated_heavy, adjacency, surface_faces
            )
            if audit["exact"]:
                survivors.append({"selected_blocks": selected.copy(), "audit": audit})
            return
        uncovered = [edge for edge in range(marked_count) if not (used_edges >> edge & 1)]
        pivot = min(
            uncovered,
            key=lambda edge: sum(
                1
                for block_index in incidence[edge]
                if not (forbidden_blocks >> block_index & 1)
                and not (used_edges & block_edge_masks[block_index])
            ),
        )
        choices = [
            block_index
            for block_index in incidence[pivot]
            if not (forbidden_blocks >> block_index & 1)
            and not (used_edges & block_edge_masks[block_index])
        ]
        for block_index in choices:
            edge_a, edge_b, first, second = blocks[block_index]
            next_fibres = fibres + [first, second]
            first_id = len(fibres)
            next_heavy = designated_heavy | {frozenset((first_id, first_id + 1))}
            if not quotient_partial_ok(
                next_fibres, next_heavy, adjacency, surface_faces
            ):
                partial_prunes += 1
                continue
            recurse(
                used_edges | (1 << edge_a) | (1 << edge_b),
                selected + [block_index],
                forbidden_blocks | conflict_masks[block_index] | (1 << block_index),
                next_fibres,
                next_heavy,
            )

    recurse(0, [], 0, constants, constant_heavy)
    return {
        "status": "candidate" if survivors else "exhausted",
        "blocks": len(blocks),
        "nodes": nodes,
        "partial_prunes": partial_prunes,
        "single_block_obstructions": sum(not value for value in single_ok),
        "pair_conflicts": sum(mask.bit_count() for mask in conflict_masks) // 2,
        "complete_covers": complete_covers,
        "survivors": survivors,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--branch", type=int)
    args = parser.parse_args()
    started = time.time()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    results = []
    executed = 0
    for candidate in source["cases"]:
        adjacency = make_surface(candidate["sphere_graph6"])
        sanity = surface_sanity(adjacency)
        if not sanity["ok"]:
            raise AssertionError(f"surface sanity failed: {sanity}")
        faces = triangles(adjacency)
        high_local = tuple(
            vertex for vertex in range(22) if adjacency[vertex + 24].bit_count() == 10
        )
        if len(high_local) != 2:
            raise AssertionError("expected two degree-ten sphere vertices")
        high = tuple(vertex + 24 for vertex in high_local)
        for configuration in candidate["configuration_cases"]:
            if "factor_branches" not in configuration:
                continue
            fixed = tuple(
                pair(first + 24, second + 24)
                for first, second in configuration["exceptional_fibres"]
            )
            for branch in configuration["factor_branches"]:
                branch_id = branch["global_branch_index"]
                if args.branch is not None and branch_id != args.branch:
                    continue
                ico_first, ico_second = branch["icosahedron_orbit_pair"]
                marked = []
                for first, second in source["icosahedron_matching_representatives"][ico_first]:
                    marked.append(pair(first, second))
                for first, second in source["icosahedron_matching_representatives"][ico_second]:
                    marked.append(pair(first + 12, second + 12))
                for first, second in branch["residual_matching_representative"]:
                    marked.append(pair(first + 24, second + 24))
                marked_tuple = tuple(sorted(marked))
                if len(marked_tuple) != 20 or len({v for e in marked_tuple for v in e}) != 40:
                    raise AssertionError("marked edges are not a 20-edge matching")
                result = replay_branch(adjacency, faces, high, fixed, marked_tuple)
                results.append(
                    {
                        "branch": branch_id,
                        "candidate": candidate["candidate_index"],
                        "configuration_orbit": configuration["configuration_orbit_index"],
                        "source_status": branch["status"],
                        **result,
                    }
                )
                executed += 1
                print(
                    json.dumps(
                        {
                            "branch": branch_id,
                            "status": result["status"],
                            "nodes": result["nodes"],
                            "covers": result.get("complete_covers", 0),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    replay_passed = (
        bool(results)
        and all(result["status"] == "exhausted" for result in results)
        and all(result["source_status"] == "exhausted" for result in results)
    )
    expected_executed = sum(
        len(configuration.get("factor_branches", []))
        for candidate in source["cases"]
        for configuration in candidate["configuration_cases"]
    )
    complete_branch_replay = (
        args.branch is None and executed == expected_executed == source.get("executed_factor_branches")
    )
    payload = {
        "schema": "erdos151-m2-independent-exact-cover-replay-v1",
        "status": (
            "VERIFIED_COMPLETE_BRANCH_REPLAY"
            if replay_passed and complete_branch_replay
            else "VERIFIED_SELECTED_BRANCHES"
            if replay_passed
            else "NOT_VERIFIED"
        ),
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "script_sha256": sha256(Path(__file__)),
        "executed_branches": executed,
        "expected_executed_branches": expected_executed,
        "source_total_canonical_factor_branches": source.get(
            "total_canonical_factor_branches"
        ),
        "branch_replay_only": True,
        "symmetry_orbit_completeness_checked": False,
        "results": results,
        "elapsed_seconds": time.time() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
