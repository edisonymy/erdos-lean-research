#!/usr/bin/env python3
"""Exact marked-factor quotient search for the verified m=3 RP2 block.

For m=3 the simple resolution has 42 degree-five vertices and three
degree-ten vertices.  Therefore an inverse quotient has exactly 21 paired
degree-five fibres and three singleton degree-ten fibres.  Each singleton is
heavy-mated to an antipodal pair in its C10 link.  Removing those six
degree-five vertices leaves 36 degree-five vertices and hence 18 ordinary
marked surface edges, paired into nine ordinary heavy quotient edges.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

import marked_factor_gluing_search as shared
import surface_quotient_search as base


RP2_GRAPH6 = "TAheJ@peD?WWMKgRW?D[?GABOObG?S?PP??j"

Pair = tuple[int, int]
Matching = tuple[Pair, ...]


def make_surface(block_graph6: str) -> nx.Graph:
    pieces = [
        nx.icosahedral_graph(),
        nx.icosahedral_graph(),
        nx.from_graph6_bytes(block_graph6.encode("ascii")),
    ]
    offsets = (0, 12, 24)
    graph = nx.Graph()
    for component, (piece, offset) in enumerate(zip(pieces, offsets)):
        shifted = nx.relabel_nodes(piece, {vertex: vertex + offset for vertex in piece})
        graph = nx.compose(graph, shifted)
        for vertex in shifted:
            graph.nodes[vertex]["component"] = component
    return graph


def block_audit(block: nx.Graph) -> dict[str, object]:
    triangles = [
        tuple(sorted(clique))
        for clique in nx.enumerate_all_cliques(block)
        if len(clique) == 3
    ]
    links = [block.subgraph(block[vertex]).copy() for vertex in block]
    edge_codegrees = [
        len(set(block[left]) & set(block[right])) for left, right in block.edges()
    ]
    return {
        "vertices": len(block),
        "edges": block.number_of_edges(),
        "degree_counts": dict(sorted(Counter(dict(block.degree()).values()).items())),
        "triangles": len(triangles),
        "clique_number": max(map(len, nx.find_cliques(block))),
        "edge_codegree_counts": dict(sorted(Counter(edge_codegrees).items())),
        "links_are_cycles": all(
            nx.is_connected(link) and all(degree == 2 for _, degree in link.degree())
            for link in links
        ),
        "euler_characteristic": len(block) - block.number_of_edges() + len(triangles),
    }


def exact_antipodes(graph: nx.Graph, high: int) -> list[Pair]:
    link = graph.subgraph(graph[high]).copy()
    assert len(link) == 10 and nx.is_connected(link)
    assert all(degree == 2 for _, degree in link.degree())
    return sorted(
        base.pair(left, right)
        for left, right in itertools.combinations(link, 2)
        if nx.shortest_path_length(link, left, right) == 5
        and set(graph[left]) & set(graph[right]) == {high}
    )


def configuration_orbits(graph: nx.Graph) -> list[list[tuple[Pair, ...]]]:
    high = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 10))
    options = [exact_antipodes(graph, vertex) for vertex in high]
    configurations = {
        tuple(choices)
        for choices in itertools.product(*options)
        if len(set(itertools.chain.from_iterable(choices))) == 2 * len(high)
    }
    mappings = shared.automorphisms(graph)

    def transform(configuration: tuple[Pair, ...], mapping: dict[int, int]):
        image_by_center = {
            mapping[center]: base.pair(*(mapping[v] for v in fibre))
            for center, fibre in zip(high, configuration)
        }
        return tuple(image_by_center[center] for center in high)

    unseen = set(configurations)
    orbits = []
    while unseen:
        representative = min(unseen)
        orbit = {transform(representative, mapping) for mapping in mappings}
        orbit &= configurations
        orbits.append(sorted(orbit))
        unseen -= orbit
    return orbits


def configuration_stabilizer(
    graph: nx.Graph, configuration: tuple[Pair, ...]
) -> list[dict[int, int]]:
    high = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 10))
    marked_stars = frozenset(
        (center, frozenset(fibre)) for center, fibre in zip(high, configuration)
    )
    return [
        mapping
        for mapping in shared.automorphisms(graph)
        if frozenset(
            (mapping[center], frozenset(mapping[v] for v in fibre))
            for center, fibre in marked_stars
        )
        == marked_stars
    ]


def quotient_from_blocks(
    surface: nx.Graph,
    high: tuple[int, ...],
    fixed: tuple[Pair, ...],
    chosen: list[tuple[int, base.Block]],
) -> tuple[nx.Graph, list[tuple[int, ...]], list[int], Counter[Pair]]:
    fibres: list[tuple[int, ...]] = [(vertex,) for vertex in high] + list(fixed)
    selectors = [0] * len(fibres)
    for block_id, block in chosen:
        fibres.extend((block.first, block.second))
        selectors.extend((block_id, block_id))
    assert len(fibres) == 24
    vertex_to_fibre = {
        vertex: fibre_id
        for fibre_id, fibre in enumerate(fibres)
        for vertex in fibre
    }
    assert len(vertex_to_fibre) == len(surface) == 45
    multiplicity: Counter[Pair] = Counter()
    for left, right in surface.edges():
        qleft, qright = vertex_to_fibre[left], vertex_to_fibre[right]
        multiplicity[base.pair(qleft, qright)] += 1
    quotient = nx.Graph()
    quotient.add_nodes_from(range(24))
    quotient.add_edges_from(edge for edge in multiplicity if edge[0] != edge[1])
    return quotient, fibres, selectors, multiplicity


def solve_factor_case(
    surface: nx.Graph,
    high: tuple[int, ...],
    fixed: tuple[Pair, ...],
    marked_edges: Matching,
    solver_name: str,
) -> tuple[dict[str, object], dict[str, object] | None]:
    started = time.time()
    remaining = sorted({vertex for edge in marked_edges for vertex in edge})
    assert len(marked_edges) == 18 and len(remaining) == 36
    all_fibres = set(base.ordinary_fibres(surface, remaining, fixed))
    blocks = shared.marked_blocks(surface, marked_edges, all_fibres)
    fibres = sorted({fibre for block in blocks for fibre in (block.first, block.second)})
    fibre_owner: dict[Pair, int] = {}
    for block_id, block in enumerate(blocks, 1):
        for fibre in (block.first, block.second):
            assert fibre not in fibre_owner
            fibre_owner[fibre] = block_id

    edge_incidence: dict[Pair, list[int]] = {edge: [] for edge in marked_edges}
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
    masks = shared.adjacency_masks(surface)
    parallel_clauses: set[tuple[int, int]] = set()
    for left_index, first in enumerate(fibres):
        for second in fibres[left_index + 1 :]:
            if shared.crossing_count(first, second, masks) < 2:
                continue
            left_block, right_block = fibre_owner[first], fibre_owner[second]
            if left_block == right_block:
                continue
            parallel_clauses.add(tuple(sorted((-left_block, -right_block))))
    for clause in sorted(parallel_clauses):
        cnf.append(list(clause))

    surface_edges = [base.pair(left, right) for left, right in surface.edges()]
    surface_faces = [
        tuple(sorted(clique))
        for clique in nx.enumerate_all_cliques(surface)
        if len(clique) == 3
    ]
    models = learned_triangle = learned_k4 = learned_other = 0
    with Solver(name=solver_name, bootstrap_with=cnf) as solver:
        while solver.solve():
            models += 1
            positive = {literal for literal in solver.get_model() if literal > 0}
            chosen = [
                (block_id, blocks[block_id - 1])
                for block_id in range(1, len(blocks) + 1)
                if block_id in positive
            ]
            assert len(chosen) == 9
            quotient_fibres: list[tuple[int, ...]] = [
                (vertex,) for vertex in high
            ] + list(fixed)
            selectors = [0] * len(quotient_fibres)
            for block_id, block in chosen:
                quotient_fibres.extend((block.first, block.second))
                selectors.extend((block_id, block_id))
            triangle_clauses, k4_clauses, collapsed = shared.fast_obstruction_clauses(
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

            quotient, quotient_fibres, selectors, multiplicity = quotient_from_blocks(
                surface, high, fixed, chosen
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
                            "marked_surface_edges": [
                                list(edge) for edge in block_crossings[block_id]
                            ],
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
                        "parallel_gate_clauses": len(parallel_clauses),
                        "models": models,
                        "learned_triangle": learned_triangle,
                        "learned_k4": learned_k4,
                        "learned_other": learned_other,
                        "elapsed_seconds": time.time() - started,
                    },
                    survivor,
                )
            solver.add_clause([-block_id for block_id, _ in chosen])
            learned_other += 1

    return (
        {
            "status": "exhausted",
            "blocks": len(blocks),
            "fibres": len(fibres),
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "parallel_gate_clauses": len(parallel_clauses),
            "models": models,
            "learned_triangle": learned_triangle,
            "learned_k4": learned_k4,
            "learned_other": learned_other,
            "elapsed_seconds": time.time() - started,
        },
        None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver", default="cadical195", choices=("cadical195", "glucose42"))
    parser.add_argument("--branch", type=int)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    started = time.time()

    block = nx.from_graph6_bytes(RP2_GRAPH6.encode("ascii"))
    audit = block_audit(block)
    assert audit == {
        "vertices": 21,
        "edges": 60,
        "degree_counts": {5: 18, 10: 3},
        "triangles": 40,
        "clique_number": 3,
        "edge_codegree_counts": {2: 60},
        "links_are_cycles": True,
        "euler_characteristic": 1,
    }
    high_local = tuple(sorted(vertex for vertex, degree in block.degree() if degree == 10))
    config_orbits = configuration_orbits(block)
    assert [len(orbit) for orbit in config_orbits] == [2, 2]

    icosahedron = nx.icosahedral_graph()
    ico_matchings = shared.perfect_matchings(icosahedron, tuple(icosahedron))
    ico_orbits = shared.matching_orbits(ico_matchings, shared.automorphisms(icosahedron))
    ico_representatives = [orbit[0] for orbit in ico_orbits]
    ico_pairs = list(itertools.combinations_with_replacement(range(5), 2))

    surface = make_surface(RP2_GRAPH6)
    high = tuple(vertex + 24 for vertex in high_local)
    payload: dict[str, object] = {
        "schema": "erdos151-m3-marked-factor-gluing-search-v1",
        "rp2_graph6": RP2_GRAPH6,
        "rp2_graph6_sha256": hashlib.sha256(RP2_GRAPH6.encode("ascii")).hexdigest(),
        "rp2_block_audit": audit,
        "solver": args.solver,
        "fibre_form": {
            "degree10_singleton_fibres": 3,
            "degree5_pair_fibres": 21,
            "exceptional_pair_fibres": 3,
            "ordinary_marked_surface_edges": 18,
            "ordinary_heavy_quotient_edges": 9,
        },
        "icosahedron_matching_count": len(ico_matchings),
        "icosahedron_matching_orbit_sizes": [len(orbit) for orbit in ico_orbits],
        "exceptional_configuration_orbit_sizes": [len(orbit) for orbit in config_orbits],
        "configuration_cases": [],
        "survivors": [],
        "claim_boundary": (
            "An exhausted run is a symmetry-reduced computational exclusion of "
            "quotients of the supplied RP2 block under the proved m=3 fibre form. "
            "It has no DRAT/LRAT certificate. A survivor is only an exact local "
            "uniform-type5 graph until independent checking."
        ),
    }
    branch_index = 0
    stop = False
    for config_index, config_orbit in enumerate(config_orbits):
        fixed_local = config_orbit[0]
        assert all(
            len(base.cross_edges(block, first, second)) <= 1
            for first, second in itertools.combinations(fixed_local, 2)
        )
        stabilizer = configuration_stabilizer(block, fixed_local)
        fixed_vertices = set(itertools.chain.from_iterable(fixed_local))
        residual_vertices = tuple(
            sorted(
                vertex
                for vertex, degree in block.degree()
                if degree == 5 and vertex not in fixed_vertices
            )
        )
        residual_matchings = shared.perfect_matchings(block, residual_vertices)
        residual_orbits = shared.matching_orbits(residual_matchings, stabilizer)
        config_record: dict[str, object] = {
            "configuration_orbit_index": config_index,
            "exceptional_fibres": [list(fibre) for fibre in fixed_local],
            "orbit_size": len(config_orbit),
            "stabilizer_size": len(stabilizer),
            "residual_matching_count": len(residual_matchings),
            "residual_matching_orbit_sizes": [len(orbit) for orbit in residual_orbits],
            "factor_branches": [],
        }
        payload["configuration_cases"].append(config_record)
        assert len(residual_matchings) == len(residual_orbits) == 1
        fixed = tuple(
            base.pair(*(vertex + 24 for vertex in fibre)) for fibre in fixed_local
        )
        for ico_first, ico_second in ico_pairs:
            current_branch = branch_index
            branch_index += 1
            if args.branch is not None and args.branch != current_branch:
                continue
            marked = tuple(
                sorted(
                    shared.shifted_matching(ico_representatives[ico_first], 0)
                    + shared.shifted_matching(ico_representatives[ico_second], 12)
                    + shared.shifted_matching(residual_orbits[0][0], 24)
                )
            )
            stats, survivor = solve_factor_case(surface, high, fixed, marked, args.solver)
            branch_record = {
                "global_branch_index": current_branch,
                "icosahedron_orbit_pair": [ico_first, ico_second],
                "residual_matching_representative": [
                    list(edge) for edge in residual_orbits[0][0]
                ],
                **stats,
            }
            config_record["factor_branches"].append(branch_record)
            if not args.quiet:
                print(
                    json.dumps(
                        {
                            "branch": current_branch,
                            "configuration_orbit": config_index,
                            "ico_orbits": [ico_first, ico_second],
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
                        "configuration_orbit_index": config_index,
                        **survivor,
                    }
                )
                stop = True
                break
        if stop:
            break

    branch_records = [
        branch
        for config in payload["configuration_cases"]
        for branch in config["factor_branches"]
    ]
    payload["total_canonical_factor_branches"] = branch_index
    payload["executed_factor_branches"] = len(branch_records)
    payload["complete"] = (
        args.branch is None
        and not payload["survivors"]
        and len(branch_records) == 30
        and all(
            branch["status"]
            in {"exhausted", "empty-marked-edge-column", "fixed-spurious-triangle"}
            for branch in branch_records
        )
    )
    payload["elapsed_seconds"] = time.time() - started
    payload["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload["shared_search_script_sha256"] = hashlib.sha256(
        Path(shared.__file__).read_bytes()
    ).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "complete": payload["complete"],
                "canonical_factor_branches": branch_index,
                "executed_factor_branches": len(branch_records),
                "status_counts": dict(
                    sorted(Counter(branch["status"] for branch in branch_records).items())
                ),
                "survivors": len(payload["survivors"]),
                "elapsed_seconds": payload["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
