#!/usr/bin/env python3
"""Canonical marked-factor gluing search for the m=2 surface case.

This is a symmetry-reduced refinement of ``surface_quotient_search.py``.
The preimages of the twelve heavy quotient edges form a perfect matching on
each icosahedron and, after removing the four forced spokes at the two
degree-ten vertices, a perfect matching on the remaining sixteen vertices of
the 22-vertex sphere.  Component automorphisms reduce the 125 icosahedral
matchings to five orbits and the residual sphere matchings to small orbit
lists.  Once these marked factors are fixed, only pairings of twenty marked
K2s remain.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

import surface_quotient_search as base


Edge = tuple[int, int]
Matching = tuple[Edge, ...]


def adjacency_masks(graph: nx.Graph) -> list[int]:
    # NetworkX preserves node insertion order, which need not be numerical
    # order (notably the built-in icosahedron inserts vertex 6 last).  Every
    # caller indexes this array by the actual integer vertex label.
    assert set(graph) == set(range(graph.number_of_nodes()))
    masks = [0] * graph.number_of_nodes()
    for vertex in graph:
        masks[vertex] = sum(1 << neighbour for neighbour in graph[vertex])
    return masks


def crossing_count(first: tuple[int, ...], second: tuple[int, ...], masks: list[int]) -> int:
    second_mask = sum(1 << vertex for vertex in second)
    return sum((masks[vertex] & second_mask).bit_count() for vertex in first)


def perfect_matchings(graph: nx.Graph, vertices: tuple[int, ...]) -> list[Matching]:
    def recurse(remaining: tuple[int, ...]):
        if not remaining:
            yield ()
            return
        first = remaining[0]
        tail = set(remaining[1:])
        for second in sorted(set(graph[first]) & tail):
            rest = tuple(v for v in remaining[1:] if v != second)
            for matching in recurse(rest):
                yield tuple(sorted(((first, second),) + matching))

    return sorted(set(recurse(tuple(sorted(vertices)))))


def automorphisms(graph: nx.Graph) -> list[dict[int, int]]:
    return list(nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())


def transform_matching(matching: Matching, mapping: dict[int, int]) -> Matching:
    return tuple(sorted(base.pair(mapping[a], mapping[b]) for a, b in matching))


def matching_orbits(
    matchings: list[Matching], mappings: list[dict[int, int]]
) -> list[list[Matching]]:
    universe = set(matchings)
    unseen = set(matchings)
    orbits = []
    while unseen:
        representative = min(unseen)
        orbit = {transform_matching(representative, mapping) for mapping in mappings}
        orbit &= universe
        orbits.append(sorted(orbit))
        unseen -= orbit
    return orbits


def exceptional_configuration_orbits(
    sphere: nx.Graph,
) -> list[list[tuple[base.Pair, base.Pair]]]:
    high = tuple(sorted(vertex for vertex, degree in sphere.degree() if degree == 10))
    options = tuple(base.exceptional_options(sphere, vertex) for vertex in high)
    configurations = {
        (first, second)
        for first, second in itertools.product(*options)
        if not (set(first) & set(second))
    }
    mappings = automorphisms(sphere)

    def transform_configuration(
        configuration: tuple[base.Pair, base.Pair], mapping: dict[int, int]
    ) -> tuple[base.Pair, base.Pair]:
        image_by_center = {
            mapping[high[0]]: base.pair(*(mapping[v] for v in configuration[0])),
            mapping[high[1]]: base.pair(*(mapping[v] for v in configuration[1])),
        }
        return (image_by_center[high[0]], image_by_center[high[1]])

    unseen = set(configurations)
    orbits = []
    while unseen:
        representative = min(unseen)
        orbit = {
            transform_configuration(representative, mapping) for mapping in mappings
        }
        orbit &= configurations
        orbits.append(sorted(orbit))
        unseen -= orbit
    return orbits


def configuration_stabilizer(
    sphere: nx.Graph, fixed: tuple[base.Pair, base.Pair]
) -> list[dict[int, int]]:
    high = tuple(sorted(vertex for vertex, degree in sphere.degree() if degree == 10))
    configuration = frozenset(
        ((high[0], frozenset(fixed[0])), (high[1], frozenset(fixed[1])))
    )
    stabilizer = []
    for mapping in automorphisms(sphere):
        image = frozenset(
            (mapping[center], frozenset(mapping[v] for v in fibre))
            for center, fibre in configuration
        )
        if image == configuration:
            stabilizer.append(mapping)
    return stabilizer


def marked_blocks(
    surface: nx.Graph,
    marked_edges: Matching,
    allowed_fibres: set[base.Pair],
) -> list[base.Block]:
    blocks = set()
    for first_edge, second_edge in itertools.combinations(marked_edges, 2):
        a, b = first_edge
        c, d = second_edge
        for first, second in (
            (base.pair(a, c), base.pair(b, d)),
            (base.pair(a, d), base.pair(b, c)),
        ):
            if first not in allowed_fibres or second not in allowed_fibres:
                continue
            crossing = base.cross_edges(surface, first, second)
            if set(crossing) != {first_edge, second_edge}:
                continue
            blocks.add(base.Block(*sorted((first, second))))
    return sorted(blocks, key=lambda block: (block.first, block.second))


def add_triangle_clauses_for_nodes(
    cnf: CNF,
    surface: nx.Graph,
    constant_nodes: list[tuple[int, ...]],
    fibres: list[base.Pair],
    fibre_variables: dict[base.Pair, int],
) -> dict[str, int | bool]:
    nodes = constant_nodes + fibres
    selectors = [0] * len(constant_nodes) + [fibre_variables[fibre] for fibre in fibres]
    adjacency = [set() for _ in nodes]
    for left, first in enumerate(nodes):
        for right in range(left + 1, len(nodes)):
            second = nodes[right]
            if set(first) & set(second):
                continue
            if base.cross_edges(surface, first, second):
                adjacency[left].add(right)
                adjacency[right].add(left)
    surface_faces = {
        frozenset(clique)
        for clique in nx.enumerate_all_cliques(surface)
        if len(clique) == 3
    }
    counts = Counter()
    forbidden_clauses: set[tuple[int, ...]] = set()
    fixed_obstruction = False
    for left in range(len(nodes)):
        for middle in (v for v in adjacency[left] if v > left):
            for right in (v for v in adjacency[left] & adjacency[middle] if v > middle):
                counts["possible"] += 1
                triple = (nodes[left], nodes[middle], nodes[right])
                if any(
                    frozenset((a, b, c)) in surface_faces
                    for a in triple[0]
                    for b in triple[1]
                    for c in triple[2]
                ):
                    counts["legitimate"] += 1
                    continue
                clause = tuple(
                    sorted(
                        {
                            -selectors[node]
                            for node in (left, middle, right)
                            if selectors[node] > 0
                        }
                    )
                )
                if not clause:
                    fixed_obstruction = True
                    continue
                forbidden_clauses.add(clause)
    for clause in sorted(forbidden_clauses, key=lambda item: (len(item), item)):
        cnf.append(list(clause))
    counts["clauses"] = len(forbidden_clauses)
    return {
        "possible_fibre_triangles": counts["possible"],
        "legitimate_fibre_triangles": counts["legitimate"],
        "spurious_triangle_clauses": counts["clauses"],
        "fixed_triangle_obstruction": fixed_obstruction,
    }


def fast_obstruction_clauses(
    surface_edges: list[Edge],
    surface_faces: list[tuple[int, int, int]],
    quotient_fibres: list[tuple[int, ...]],
    selectors: list[int],
) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]], bool]:
    """Return local block clauses for spurious triangles and quotient K4s.

    This bitset checker is used on every SAT model.  The much more redundant
    NetworkX target audit is reserved for models with no local obstruction.
    """

    vertex_to_fibre = {
        vertex: fibre_id
        for fibre_id, fibre in enumerate(quotient_fibres)
        for vertex in fibre
    }
    adjacency = [0] * 24
    for left, right in surface_edges:
        qleft, qright = vertex_to_fibre[left], vertex_to_fibre[right]
        if qleft == qright:
            return set(), set(), True
        adjacency[qleft] |= 1 << qright
        adjacency[qright] |= 1 << qleft

    face_images = set()
    collapsed_face = False
    for face in surface_faces:
        image = tuple(sorted(vertex_to_fibre[vertex] for vertex in face))
        if len(set(image)) != 3:
            collapsed_face = True
        face_images.add(image)
    if len(face_images) != len(surface_faces):
        collapsed_face = True

    triangle_clauses: set[tuple[int, ...]] = set()
    k4_clauses: set[tuple[int, ...]] = set()
    for left in range(24):
        left_later = adjacency[left] & ~((1 << (left + 1)) - 1)
        middle_bits = left_later
        while middle_bits:
            middle_bit = middle_bits & -middle_bits
            middle = middle_bit.bit_length() - 1
            common = left_later & adjacency[middle]
            common &= ~((1 << (middle + 1)) - 1)
            right_bits = common
            while right_bits:
                right_bit = right_bits & -right_bits
                right = right_bit.bit_length() - 1
                triangle = (left, middle, right)
                if triangle not in face_images:
                    clause = tuple(base.selector_clause(triangle, selectors))
                    if clause:
                        triangle_clauses.add(clause)
                    else:
                        collapsed_face = True
                fourth_bits = common & adjacency[right]
                fourth_bits &= ~((1 << (right + 1)) - 1)
                while fourth_bits:
                    fourth_bit = fourth_bits & -fourth_bits
                    fourth = fourth_bit.bit_length() - 1
                    clause = tuple(
                        base.selector_clause((left, middle, right, fourth), selectors)
                    )
                    if clause:
                        k4_clauses.add(clause)
                    else:
                        collapsed_face = True
                    fourth_bits ^= fourth_bit
                right_bits ^= right_bit
            middle_bits ^= middle_bit
    return triangle_clauses, k4_clauses, collapsed_face


def solve_factor_case(
    surface: nx.Graph,
    high: tuple[int, int],
    fixed: tuple[base.Pair, base.Pair],
    marked_edges: Matching,
    solver_name: str,
    precompute_triangles: bool,
) -> tuple[dict[str, object], dict[str, object] | None]:
    started = time.time()
    remaining = sorted({vertex for edge in marked_edges for vertex in edge})
    assert len(marked_edges) == 20 and len(remaining) == 40
    all_fibres = set(base.ordinary_fibres(surface, remaining, fixed))
    blocks = marked_blocks(surface, marked_edges, all_fibres)
    fibres = sorted({fibre for block in blocks for fibre in (block.first, block.second)})
    # Because the marked edges form a matching, one candidate fibre fixes the
    # two marked K2s being paired and hence fixes its companion fibre.  Thus a
    # candidate fibre belongs to exactly one block, and its selection literal
    # can be the block literal itself.  This quotient removes hundreds of
    # redundant fibre variables and deduplicates the triangle clauses.
    fibre_variables: dict[base.Pair, int] = {}
    for block_id, block in enumerate(blocks, 1):
        for fibre in (block.first, block.second):
            assert fibre not in fibre_variables
            fibre_variables[fibre] = block_id
    edge_incidence: dict[Edge, list[int]] = {edge: [] for edge in marked_edges}
    block_crossings = {}
    for block_id, block in enumerate(blocks, 1):
        crossing = base.cross_edges(surface, block.first, block.second)
        assert len(crossing) == 2
        block_crossings[block_id] = crossing
        for edge in crossing:
            edge_incidence[edge].append(block_id)
    if any(not choices for choices in edge_incidence.values()):
        return ({"status": "empty-marked-edge-column", "blocks": len(blocks)}, None)

    cnf = CNF()
    pool = IDPool(start_from=len(blocks) + 1)
    for edge in marked_edges:
        cnf.extend(
            CardEnc.equals(
                edge_incidence[edge], 1, vpool=pool, encoding=EncType.seqcounter
            ).clauses
        )
    parallel_gate_clauses = 0
    parallel_clauses: set[tuple[int, int]] = set()
    surface_masks = adjacency_masks(surface)
    for left_index, first in enumerate(fibres):
        for right_index in range(left_index + 1, len(fibres)):
            second = fibres[right_index]
            multiplicity = crossing_count(first, second, surface_masks)
            if multiplicity < 2:
                continue
            left_block = fibre_variables[first]
            right_block = fibre_variables[second]
            if left_block == right_block:
                assert multiplicity == 2
                continue
            parallel_clauses.add(tuple(sorted((-left_block, -right_block))))
    for clause in sorted(parallel_clauses):
        cnf.append(list(clause))
    parallel_gate_clauses = len(parallel_clauses)

    triangle_stats = (
        add_triangle_clauses_for_nodes(
            cnf,
            surface,
            [(high[0],), (high[1],), fixed[0], fixed[1]],
            fibres,
            fibre_variables,
        )
        if precompute_triangles
        else {
            "possible_fibre_triangles": 0,
            "legitimate_fibre_triangles": 0,
            "spurious_triangle_clauses": 0,
            "fixed_triangle_obstruction": False,
        }
    )
    if triangle_stats["fixed_triangle_obstruction"]:
        return (
            {
                "status": "fixed-spurious-triangle",
                "blocks": len(blocks),
                "fibres": len(fibres),
                "parallel_gate_clauses": parallel_gate_clauses,
                **triangle_stats,
                "elapsed_seconds": time.time() - started,
            },
            None,
        )

    models = 0
    learned_triangle = 0
    learned_k4 = 0
    learned_other = 0
    surface_edges = [base.pair(a, b) for a, b in surface.edges()]
    surface_faces = [
        tuple(sorted(clique))
        for clique in nx.enumerate_all_cliques(surface)
        if len(clique) == 3
    ]
    with Solver(name=solver_name, bootstrap_with=cnf) as solver:
        while solver.solve():
            models += 1
            positive = {literal for literal in solver.get_model() if literal > 0}
            chosen = [
                (block_id, blocks[block_id - 1])
                for block_id in range(1, len(blocks) + 1)
                if block_id in positive
            ]
            assert len(chosen) == 10
            quotient_fibres: list[tuple[int, ...]] = [
                (high[0],),
                (high[1],),
                fixed[0],
                fixed[1],
            ]
            selectors = [0, 0, 0, 0]
            for block_id, block in chosen:
                quotient_fibres.extend((block.first, block.second))
                selectors.extend((block_id, block_id))
            triangle_clauses, k4_clauses, collapsed = fast_obstruction_clauses(
                surface_edges, surface_faces, quotient_fibres, selectors
            )
            if triangle_clauses or k4_clauses or collapsed:
                for clause in triangle_clauses:
                    solver.add_clause(list(clause))
                    learned_triangle += 1
                for clause in k4_clauses:
                    solver.add_clause(list(clause))
                    learned_k4 += 1
                if collapsed and not (triangle_clauses or k4_clauses):
                    solver.add_clause([-block_id for block_id, _ in chosen])
                    learned_other += 1
                continue

            quotient, quotient_fibres, selectors, multiplicity = base.quotient_from_blocks(
                surface, high, fixed, chosen, fibre_variables
            )
            audit = base.target_audit(surface, quotient, quotient_fibres, multiplicity)
            if audit["exact"]:
                survivor = {
                    "graph6": nx.to_graph6_bytes(quotient, header=False)
                    .decode("ascii")
                    .strip(),
                    "edges": [list(edge) for edge in sorted(quotient.edges())],
                    "surface_fibres": [list(fibre) for fibre in quotient_fibres],
                    "selected_blocks": [
                        {
                            "block_id": block_id,
                            "fibres": [list(block.first), list(block.second)],
                            "marked_surface_edges": [list(e) for e in block_crossings[block_id]],
                        }
                        for block_id, block in chosen
                    ],
                    "audit": audit,
                }
                return (
                    {
                        "status": "candidate",
                        "blocks": len(blocks),
                        "fibres": len(fibres),
                        "variables": pool.top,
                        "clauses": len(cnf.clauses),
                        "parallel_gate_clauses": parallel_gate_clauses,
                        **triangle_stats,
                        "models": models,
                        "learned_triangle": learned_triangle,
                        "learned_k4": learned_k4,
                        "learned_other": learned_other,
                        "elapsed_seconds": time.time() - started,
                    },
                    survivor,
                )

            learned = False
            for clique in audit["k4s"]:
                clause = base.selector_clause(tuple(clique), selectors)
                if clause:
                    solver.add_clause(clause)
                    learned_k4 += 1
                    learned = True
            if not learned:
                solver.add_clause([-block_id for block_id, _ in chosen])
                learned_other += 1

    return (
        {
            "status": "exhausted",
            "blocks": len(blocks),
            "fibres": len(fibres),
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "parallel_gate_clauses": parallel_gate_clauses,
            **triangle_stats,
            "models": models,
            "learned_triangle": learned_triangle,
            "learned_k4": learned_k4,
            "learned_other": learned_other,
            "elapsed_seconds": time.time() - started,
        },
        None,
    )


def shifted_matching(matching: Matching, offset: int) -> Matching:
    return tuple(base.pair(a + offset, b + offset) for a, b in matching)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate", type=int, choices=(1, 2))
    parser.add_argument("--branch", type=int, help="run only this zero-based factor branch")
    parser.add_argument(
        "--precompute-triangles",
        action="store_true",
        help="materialize all spurious-triangle clauses instead of learning them lazily",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--solver",
        default="cadical195",
        choices=("cadical195", "glucose42", "minisat22"),
    )
    args = parser.parse_args()
    started = time.time()

    icosahedron = nx.icosahedral_graph()
    ico_matchings = perfect_matchings(icosahedron, tuple(icosahedron))
    ico_orbits = matching_orbits(ico_matchings, automorphisms(icosahedron))
    assert len(ico_matchings) == 125
    assert sorted(len(orbit) for orbit in ico_orbits) == [5, 10, 20, 30, 60]
    ico_representatives = [orbit[0] for orbit in ico_orbits]
    ico_orbit_pairs = list(itertools.combinations_with_replacement(range(5), 2))

    candidate_indices = [args.candidate - 1] if args.candidate else [0, 1]
    payload: dict[str, object] = {
        "schema": "erdos151-m2-marked-factor-gluing-search-v1",
        "solver": args.solver,
        "icosahedron_matching_count": len(ico_matchings),
        "icosahedron_matching_orbit_sizes": [len(orbit) for orbit in ico_orbits],
        "icosahedron_matching_representatives": [
            [list(edge) for edge in matching] for matching in ico_representatives
        ],
        "cases": [],
        "survivors": [],
        "claim_boundary": (
            "Completeness uses the proved m=2 fibre correspondence and independent "
            "component automorphisms. Exhausted SAT branches are reproducible but "
            "not yet accompanied by proof certificates. A survivor is only a local "
            "uniform-type5 graph until separately checked."
        ),
    }
    branch_index = 0
    stop = False
    for candidate_index in candidate_indices:
        sphere = nx.from_graph6_bytes(base.CANDIDATES[candidate_index].encode("ascii"))
        sphere_high = tuple(sorted(v for v, d in sphere.degree() if d == 10))
        configuration_orbits = exceptional_configuration_orbits(sphere)
        candidate_record: dict[str, object] = {
            "candidate_index": candidate_index + 1,
            "sphere_graph6": base.CANDIDATES[candidate_index],
            "exceptional_configuration_orbit_sizes": [len(o) for o in configuration_orbits],
            "configuration_cases": [],
        }
        payload["cases"].append(candidate_record)

        for configuration_orbit_index, configuration_orbit in enumerate(configuration_orbits):
            fixed_local = configuration_orbit[0]
            # A doubled edge between the two already-heavy exceptional fibres
            # makes this entire configuration orbit impossible.
            if len(base.cross_edges(sphere, fixed_local[0], fixed_local[1])) >= 2:
                candidate_record["configuration_cases"].append(
                    {
                        "configuration_orbit_index": configuration_orbit_index,
                        "exceptional_fibres": [list(p) for p in fixed_local],
                        "orbit_size": len(configuration_orbit),
                        "status": "exceptional-fibres-have-extra-parallel-edge",
                    }
                )
                continue

            stabilizer = configuration_stabilizer(sphere, fixed_local)
            sphere_degree_five = {v for v, d in sphere.degree() if d == 5}
            residual_vertices = tuple(
                sorted(sphere_degree_five - set(fixed_local[0] + fixed_local[1]))
            )
            residual_matchings = perfect_matchings(sphere, residual_vertices)
            residual_orbits = matching_orbits(residual_matchings, stabilizer)
            configuration_record: dict[str, object] = {
                "configuration_orbit_index": configuration_orbit_index,
                "exceptional_fibres": [list(p) for p in fixed_local],
                "orbit_size": len(configuration_orbit),
                "stabilizer_size": len(stabilizer),
                "residual_matching_count": len(residual_matchings),
                "residual_matching_orbit_sizes": [len(o) for o in residual_orbits],
                "factor_branches": [],
            }
            candidate_record["configuration_cases"].append(configuration_record)

            surface = base.make_surface(base.CANDIDATES[candidate_index])
            high = tuple(v + 24 for v in sphere_high)
            fixed = tuple(
                base.pair(*(v + 24 for v in fibre)) for fibre in fixed_local
            )
            for ico_first, ico_second in ico_orbit_pairs:
                for residual_orbit_index, residual_orbit in enumerate(residual_orbits):
                    current_branch = branch_index
                    branch_index += 1
                    if args.branch is not None and current_branch != args.branch:
                        continue
                    marked = tuple(
                        sorted(
                            shifted_matching(ico_representatives[ico_first], 0)
                            + shifted_matching(ico_representatives[ico_second], 12)
                            + shifted_matching(residual_orbit[0], 24)
                        )
                    )
                    stats, survivor = solve_factor_case(
                        surface,
                        high,
                        fixed,
                        marked,
                        args.solver,
                        args.precompute_triangles,
                    )
                    branch_record = {
                        "global_branch_index": current_branch,
                        "icosahedron_orbit_pair": [ico_first, ico_second],
                        "residual_orbit_index": residual_orbit_index,
                        "residual_orbit_size": len(residual_orbit),
                        "residual_matching_representative": [
                            list(edge) for edge in residual_orbit[0]
                        ],
                        **stats,
                    }
                    configuration_record["factor_branches"].append(branch_record)
                    if not args.quiet:
                        print(
                            json.dumps(
                                {
                                    "branch": current_branch,
                                    "candidate": candidate_index + 1,
                                    "configuration_orbit": configuration_orbit_index,
                                    "ico_orbits": [ico_first, ico_second],
                                    "residual_orbit": residual_orbit_index,
                                    "status": stats["status"],
                                    "seconds": stats.get("elapsed_seconds"),
                                },
                                sort_keys=True,
                            ),
                            flush=True,
                        )
                    if survivor is not None:
                        payload["survivors"].append(
                            {
                                "global_branch_index": current_branch,
                                "candidate_index": candidate_index + 1,
                                "configuration_orbit_index": configuration_orbit_index,
                                "exceptional_fibres": [list(p) for p in fixed],
                                **survivor,
                            }
                        )
                        stop = True
                        break
                if stop:
                    break
            if stop:
                break
        if stop:
            break

    branch_records = [
        branch
        for candidate in payload["cases"]
        for configuration in candidate["configuration_cases"]
        for branch in configuration.get("factor_branches", [])
    ]
    payload["total_canonical_factor_branches"] = branch_index
    payload["executed_factor_branches"] = len(branch_records)
    payload["complete"] = (
        args.branch is None
        and not payload["survivors"]
        and branch_records
        and all(
            branch["status"]
            in {
                "exhausted",
                "empty-marked-edge-column",
                "fixed-spurious-triangle",
            }
            for branch in branch_records
        )
    )
    payload["elapsed_seconds"] = time.time() - started
    payload["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "complete": payload["complete"],
                "survivors": len(payload["survivors"]),
                "canonical_factor_branches": branch_index,
                "executed_factor_branches": len(branch_records),
                "status_counts": dict(
                    sorted(Counter(branch["status"] for branch in branch_records).items())
                ),
                "elapsed_seconds": payload["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
