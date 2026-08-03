#!/usr/bin/env python3
"""Independent block/orbit/branch audit for the m=3 RP2 gluing sweep."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx

import audit_m2_gluing_coverage as independent


RP2_GRAPH6 = "TAheJ@peD?WWMKgRW?D[?GABOObG?S?PP??j"


def block_audit(graph: nx.Graph) -> dict[str, object]:
    triangles = [
        tuple(sorted(clique))
        for clique in nx.enumerate_all_cliques(graph)
        if len(clique) == 3
    ]
    edge_codegrees = [
        len(set(graph[left]) & set(graph[right])) for left, right in graph.edges()
    ]
    return {
        "vertices": len(graph),
        "edges": graph.number_of_edges(),
        "degree_counts": dict(sorted(Counter(dict(graph.degree()).values()).items())),
        "triangles": len(triangles),
        "clique_number": max(map(len, nx.find_cliques(graph))),
        "edge_codegree_counts": dict(sorted(Counter(edge_codegrees).items())),
        "links_are_cycles": all(
            nx.is_connected(graph.subgraph(graph[vertex]))
            and all(
                degree == 2
                for _, degree in graph.subgraph(graph[vertex]).degree()
            )
            for vertex in graph
        ),
        "euler_characteristic": len(graph) - graph.number_of_edges() + len(triangles),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--search-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    assert result["schema"] == "erdos151-m3-marked-factor-gluing-search-v1"
    assert result["complete"] is True
    assert result["survivors"] == []
    assert result["rp2_graph6"] == RP2_GRAPH6
    graph = nx.from_graph6_bytes(RP2_GRAPH6.encode("ascii"))
    audit = block_audit(graph)
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
    assert result["rp2_block_audit"] == {
        **audit,
        "degree_counts": {"5": 18, "10": 3},
        "edge_codegree_counts": {"2": 60},
    }

    mappings = independent.automorphisms(graph)
    config_orbits, raw_disjoint, exact_disjoint = independent.configuration_orbits(graph)
    assert len(mappings) == 4
    assert raw_disjoint == 75
    assert exact_disjoint == 4
    assert [len(orbit) for orbit in config_orbits] == [2, 2]
    assert result["exceptional_configuration_orbit_sizes"] == [2, 2]

    icosahedron = nx.icosahedral_graph()
    ico_matchings = independent.perfect_matchings(icosahedron, tuple(icosahedron))
    ico_orbits = independent.matching_orbits(
        ico_matchings, independent.automorphisms(icosahedron)
    )
    assert len(ico_matchings) == 125
    assert sorted(len(orbit) for orbit in ico_orbits) == [5, 10, 20, 30, 60]
    ico_pairs = list(itertools.combinations_with_replacement(range(5), 2))

    actual_keys = set()
    expected_keys = set()
    statuses: Counter[str] = Counter()
    models = learned_triangle = learned_k4 = 0
    weighted_raw_cases = 0
    fixed_k4_records = []
    records = {
        record["configuration_orbit_index"]: record
        for record in result["configuration_cases"]
    }
    assert set(records) == {0, 1}
    high = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 10))
    for config_index, config_orbit in enumerate(config_orbits):
        representative = config_orbit[0]
        record = records[config_index]
        assert independent.normalize_pairs(record["exceptional_fibres"]) == representative
        assert record["orbit_size"] == len(config_orbit)
        stabilizer = independent.configuration_stabilizer(graph, representative)
        assert record["stabilizer_size"] == len(stabilizer) == 2
        fixed_vertices = set(itertools.chain.from_iterable(representative))
        residual_vertices = tuple(
            sorted(
                vertex
                for vertex, degree in graph.degree()
                if degree == 5 and vertex not in fixed_vertices
            )
        )
        residual_matchings = independent.perfect_matchings(graph, residual_vertices)
        residual_orbits = independent.matching_orbits(residual_matchings, stabilizer)
        assert len(residual_matchings) == len(residual_orbits) == 1
        assert record["residual_matching_count"] == 1
        assert record["residual_matching_orbit_sizes"] == [1]
        weighted_raw_cases += len(config_orbit) * 125 * 125

        constant_fibres: list[tuple[int, ...]] = [
            (vertex,) for vertex in high
        ] + list(representative)
        fixed_k4s = []
        for four in itertools.combinations(range(len(constant_fibres)), 4):
            edge_witnesses = {}
            for left, right in itertools.combinations(four, 2):
                witnesses = [
                    (a, b)
                    for a in constant_fibres[left]
                    for b in constant_fibres[right]
                    if graph.has_edge(a, b)
                ]
                if not witnesses:
                    break
                edge_witnesses[f"{left}-{right}"] = [list(edge) for edge in witnesses]
            else:
                fixed_k4s.append(
                    {
                        "fibre_indices": list(four),
                        "surface_fibres": [list(constant_fibres[index]) for index in four],
                        "edge_witnesses": edge_witnesses,
                    }
                )
        assert [item["fibre_indices"] for item in fixed_k4s] == [[2, 3, 4, 5]]
        fixed_k4_records.append(
            {
                "configuration_orbit_index": config_index,
                "orbit_size": len(config_orbit),
                "fixed_k4s": fixed_k4s,
            }
        )

        for ico_first, ico_second in ico_pairs:
            expected_keys.add((config_index, ico_first, ico_second))
        for branch in record["factor_branches"]:
            ico_first, ico_second = branch["icosahedron_orbit_pair"]
            key = (config_index, ico_first, ico_second)
            assert key not in actual_keys
            actual_keys.add(key)
            assert independent.normalize_pairs(
                branch["residual_matching_representative"]
            ) == residual_orbits[0][0]
            assert branch["status"] in {
                "exhausted",
                "empty-marked-edge-column",
                "fixed-spurious-triangle",
            }
            statuses[branch["status"]] += 1
            models += branch.get("models", 0)
            learned_triangle += branch.get("learned_triangle", 0)
            learned_k4 += branch.get("learned_k4", 0)

    assert actual_keys == expected_keys
    assert len(actual_keys) == 30
    assert result["executed_factor_branches"] == 30
    assert result["total_canonical_factor_branches"] == 30
    search_hash = hashlib.sha256(args.search_script.read_bytes()).hexdigest()
    assert result["script_sha256"] == search_hash

    payload = {
        "schema": "erdos151-m3-gluing-coverage-audit-v1",
        "status": "PASS",
        "rp2_input": {
            "graph6": RP2_GRAPH6,
            "graph6_sha256": hashlib.sha256(RP2_GRAPH6.encode("ascii")).hexdigest(),
            "graph6_line_sha256": hashlib.sha256(
                (RP2_GRAPH6 + "\n").encode("ascii")
            ).hexdigest(),
            "automorphism_count": len(mappings),
            "audit": audit,
        },
        "search_script": {"path": str(args.search_script), "sha256": search_hash},
        "result": {
            "path": str(args.result),
            "sha256": hashlib.sha256(args.result.read_bytes()).hexdigest(),
        },
        "fibre_derivation": {
            "resolved_degree5_vertices": 42,
            "resolved_degree10_vertices": 3,
            "paired_degree5_fibres": 21,
            "singleton_degree10_fibres": 3,
            "quotient_vertices": 24,
            "exceptional_antipode_fibres": 3,
            "ordinary_marked_surface_edges": 18,
            "ordinary_heavy_quotient_edges": 9,
        },
        "exceptional_coverage": {
            "raw_disjoint_antipode_configurations": raw_disjoint,
            "exact_common_neighbour_filtered_configurations": exact_disjoint,
            "orbit_sizes": [len(orbit) for orbit in config_orbits],
            "orbit_size_sum": sum(len(orbit) for orbit in config_orbits),
            "residual_matching_counts": [1, 1],
        },
        "icosahedron": {
            "perfect_matching_count": len(ico_matchings),
            "perfect_matching_orbit_sizes": [len(orbit) for orbit in ico_orbits],
        },
        "branch_coverage": {
            "canonical_factor_branches": len(actual_keys),
            "weighted_valid_raw_factor_cases": weighted_raw_cases,
            "termination_status_counts": dict(sorted(statuses.items())),
            "solver_models_inspected": models,
            "learned_spurious_triangle_clauses": learned_triangle,
            "learned_k4_clauses": learned_k4,
            "survivors": 0,
            "coverage_exact": True,
        },
        "solver_free_fixed_k4_obstruction": {
            "verified": True,
            "records": fixed_k4_records,
            "conclusion": (
                "For each valid exceptional-configuration orbit, the third "
                "degree-ten singleton together with all three exceptional pair "
                "fibres already induces a quotient K4. Ordinary fibre choices "
                "cannot remove these six fixed adjacencies."
            ),
        },
        "conclusion": (
            "The two valid exceptional-configuration orbits each force a fixed "
            "quotient K4 before ordinary gluing. Independently, branch-key "
            "reconstruction matches all 30 retained m=3 branches and every "
            "branch records exhaustive termination with no survivor."
        ),
        "claim_boundary": (
            "The fixed-K4 obstruction is solver-free and excludes quotients of "
            "this supplied RP2 graph. The audit does not establish that a census "
            "of all eligible m=3 RP2 blocks is complete."
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["branch_coverage"], sort_keys=True))


if __name__ == "__main__":
    main()
