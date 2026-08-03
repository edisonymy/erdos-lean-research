#!/usr/bin/env python3
"""Independent orbit/coverage audit for the two m=2 gluing sweeps.

This checker deliberately does not import the discovery search.  It rebuilds
the icosahedral perfect matchings, graph automorphisms, exceptional-fibre
orbits, stabilizers, residual-factor orbits, and all expected canonical
branch keys, then compares them with the retained result JSON files.

It audits finite case coverage and recorded solver termination.  It does not
turn those solver records into proof certificates.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx


CANDIDATES = (
    "U|fIJCpCG_a@C@C?b?G[@?_[ABGCKGCWCAW@?{?G",
    "U|fIID@OI?g@W@K?b?G[X?oC@_G@_G?oc?Fo??Fo",
)

Pair = tuple[int, int]
Matching = tuple[Pair, ...]


def pair(a: int, b: int) -> Pair:
    return (a, b) if a < b else (b, a)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def perfect_matchings(graph: nx.Graph, vertices: tuple[int, ...]) -> list[Matching]:
    def recurse(remaining: tuple[int, ...]):
        if not remaining:
            yield ()
            return
        first = remaining[0]
        tail = set(remaining[1:])
        for second in sorted(set(graph[first]) & tail):
            rest = tuple(vertex for vertex in remaining[1:] if vertex != second)
            for matching in recurse(rest):
                yield tuple(sorted(((first, second),) + matching))

    return sorted(set(recurse(tuple(sorted(vertices)))))


def automorphisms(graph: nx.Graph) -> list[dict[int, int]]:
    return list(nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())


def transform_matching(matching: Matching, mapping: dict[int, int]) -> Matching:
    return tuple(sorted(pair(mapping[a], mapping[b]) for a, b in matching))


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


def raw_antipodes(graph: nx.Graph, high: int) -> list[Pair]:
    link = graph.subgraph(graph[high]).copy()
    assert len(link) == 10
    assert nx.is_connected(link)
    assert all(degree == 2 for _, degree in link.degree())
    return sorted(
        pair(a, b)
        for a, b in itertools.combinations(link, 2)
        if nx.shortest_path_length(link, a, b) == 5
    )


def exact_antipodes(graph: nx.Graph, high: int) -> list[Pair]:
    return [
        candidate
        for candidate in raw_antipodes(graph, high)
        if set(graph[candidate[0]]) & set(graph[candidate[1]]) == {high}
    ]


def crossing_count(graph: nx.Graph, first: Pair, second: Pair) -> int:
    return sum(graph.has_edge(a, b) for a in first for b in second)


def configuration_orbits(
    graph: nx.Graph,
) -> tuple[list[list[tuple[Pair, ...]]], int, int]:
    high = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 10))
    raw_options = [raw_antipodes(graph, vertex) for vertex in high]
    exact_options = [exact_antipodes(graph, vertex) for vertex in high]
    raw_disjoint = sum(
        1
        for choices in itertools.product(*raw_options)
        if len(set(itertools.chain.from_iterable(choices))) == 2 * len(high)
    )
    configurations = {
        tuple(choices)
        for choices in itertools.product(*exact_options)
        if len(set(itertools.chain.from_iterable(choices))) == 2 * len(high)
    }
    mappings = automorphisms(graph)

    def transform(configuration: tuple[Pair, ...], mapping: dict[int, int]):
        image_by_center = {
            mapping[center]: pair(*(mapping[v] for v in fibre))
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
    return orbits, raw_disjoint, len(configurations)


def configuration_stabilizer(
    graph: nx.Graph, configuration: tuple[Pair, ...]
) -> list[dict[int, int]]:
    high = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 10))
    marked_stars = frozenset(
        (center, frozenset(fibre)) for center, fibre in zip(high, configuration)
    )
    return [
        mapping
        for mapping in automorphisms(graph)
        if frozenset(
            (mapping[center], frozenset(mapping[v] for v in fibre))
            for center, fibre in marked_stars
        )
        == marked_stars
    ]


def normalize_pairs(items: list[list[int]]) -> tuple[Pair, ...]:
    return tuple(pair(*item) for item in items)


def audit_result(
    result_path: Path,
    candidate_index: int,
    ico_orbits: list[list[Matching]],
) -> tuple[dict[str, object], set[tuple[int, int, int, int]]]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["schema"] == "erdos151-m2-marked-factor-gluing-search-v1"
    assert result["complete"] is True
    assert result["survivors"] == []
    assert len(result["cases"]) == 1
    candidate_record = result["cases"][0]
    assert candidate_record["candidate_index"] == candidate_index
    assert candidate_record["sphere_graph6"] == CANDIDATES[candidate_index - 1]

    sphere = nx.from_graph6_bytes(CANDIDATES[candidate_index - 1].encode("ascii"))
    high = tuple(sorted(vertex for vertex, degree in sphere.degree() if degree == 10))
    mappings = automorphisms(sphere)
    config_orbits, raw_disjoint, exact_disjoint = configuration_orbits(sphere)
    assert candidate_record["exceptional_configuration_orbit_sizes"] == [
        len(orbit) for orbit in config_orbits
    ]
    actual_config_records = {
        record["configuration_orbit_index"]: record
        for record in candidate_record["configuration_cases"]
    }
    assert set(actual_config_records) == set(range(len(config_orbits)))

    ico_sizes = [len(orbit) for orbit in ico_orbits]
    ico_pairs = list(itertools.combinations_with_replacement(range(len(ico_orbits)), 2))
    expected_keys: set[tuple[int, int, int, int]] = set()
    actual_keys: set[tuple[int, int, int, int]] = set()
    invalid_orbits = []
    valid_raw_factor_weight = 0
    status_counts: Counter[str] = Counter()
    model_count = 0
    learned_triangle = 0
    learned_k4 = 0

    for config_index, orbit in enumerate(config_orbits):
        representative = orbit[0]
        record = actual_config_records[config_index]
        assert normalize_pairs(record["exceptional_fibres"]) == representative
        assert record["orbit_size"] == len(orbit)
        invalid = any(
            crossing_count(sphere, first, second) >= 2
            for first, second in itertools.combinations(representative, 2)
        )
        if invalid:
            assert record["status"] == "exceptional-fibres-have-extra-parallel-edge"
            assert "factor_branches" not in record
            invalid_orbits.append({"orbit_index": config_index, "orbit_size": len(orbit)})
            continue

        stabilizer = configuration_stabilizer(sphere, representative)
        fixed_vertices = set(itertools.chain.from_iterable(representative))
        residual_vertices = tuple(
            sorted(
                vertex
                for vertex, degree in sphere.degree()
                if degree == 5 and vertex not in fixed_vertices
            )
        )
        residual_matchings = perfect_matchings(sphere, residual_vertices)
        residual_orbits = matching_orbits(residual_matchings, stabilizer)
        assert record["stabilizer_size"] == len(stabilizer)
        assert record["residual_matching_count"] == len(residual_matchings)
        assert record["residual_matching_orbit_sizes"] == [
            len(residual_orbit) for residual_orbit in residual_orbits
        ]
        valid_raw_factor_weight += len(orbit) * len(residual_matchings) * 125 * 125

        for ico_first, ico_second in ico_pairs:
            for residual_index in range(len(residual_orbits)):
                expected_keys.add((config_index, ico_first, ico_second, residual_index))

        for branch in record["factor_branches"]:
            ico_first, ico_second = branch["icosahedron_orbit_pair"]
            key = (config_index, ico_first, ico_second, branch["residual_orbit_index"])
            assert key not in actual_keys
            actual_keys.add(key)
            residual_orbit = residual_orbits[branch["residual_orbit_index"]]
            assert branch["residual_orbit_size"] == len(residual_orbit)
            assert normalize_pairs(branch["residual_matching_representative"]) == residual_orbit[0]
            assert branch["status"] in {
                "exhausted",
                "empty-marked-edge-column",
                "fixed-spurious-triangle",
            }
            status_counts[branch["status"]] += 1
            model_count += branch.get("models", 0)
            learned_triangle += branch.get("learned_triangle", 0)
            learned_k4 += branch.get("learned_k4", 0)

    assert actual_keys == expected_keys
    assert result["executed_factor_branches"] == len(actual_keys)
    assert result["total_canonical_factor_branches"] == len(expected_keys)

    # Weighted orbit coverage independently expands to every ordered pair of
    # raw icosahedral matching factors for each valid sphere marked factor.
    weighted_from_branches = 0
    for config_index, ico_first, ico_second, residual_index in expected_keys:
        config_orbit = config_orbits[config_index]
        representative = config_orbit[0]
        stabilizer = configuration_stabilizer(sphere, representative)
        fixed_vertices = set(itertools.chain.from_iterable(representative))
        residual_vertices = tuple(
            sorted(
                vertex
                for vertex, degree in sphere.degree()
                if degree == 5 and vertex not in fixed_vertices
            )
        )
        residual_orbit = matching_orbits(
            perfect_matchings(sphere, residual_vertices), stabilizer
        )[residual_index]
        swap_weight = 1 if ico_first == ico_second else 2
        weighted_from_branches += (
            len(config_orbit)
            * len(residual_orbit)
            * len(ico_orbits[ico_first])
            * len(ico_orbits[ico_second])
            * swap_weight
        )
    assert weighted_from_branches == valid_raw_factor_weight

    record = {
        "candidate_index": candidate_index,
        "result_path": str(result_path),
        "result_sha256": sha256_bytes(result_path.read_bytes()),
        "sphere_graph6": CANDIDATES[candidate_index - 1],
        "sphere_graph6_sha256": sha256_bytes(
            CANDIDATES[candidate_index - 1].encode("ascii")
        ),
        "sphere_graph6_line_sha256": sha256_bytes(
            (CANDIDATES[candidate_index - 1] + "\n").encode("ascii")
        ),
        "automorphism_count": len(mappings),
        "raw_disjoint_antipode_configurations": raw_disjoint,
        "exact_common_neighbour_filtered_configurations": exact_disjoint,
        "exceptional_configuration_orbit_sizes": [len(o) for o in config_orbits],
        "invalid_configuration_orbits": invalid_orbits,
        "canonical_factor_branches": len(expected_keys),
        "weighted_valid_raw_factor_cases": valid_raw_factor_weight,
        "termination_status_counts": dict(sorted(status_counts.items())),
        "solver_models_inspected": model_count,
        "learned_spurious_triangle_clauses": learned_triangle,
        "learned_k4_clauses": learned_k4,
        "survivors": 0,
        "recorded_complete": result["complete"],
        "recorded_script_sha256": result["script_sha256"],
    }
    return record, actual_keys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate1", type=Path, required=True)
    parser.add_argument("--candidate2", type=Path, required=True)
    parser.add_argument("--search-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    icosahedron = nx.icosahedral_graph()
    ico_mappings = automorphisms(icosahedron)
    ico_matchings = perfect_matchings(icosahedron, tuple(icosahedron))
    ico_orbits = matching_orbits(ico_matchings, ico_mappings)
    assert len(ico_mappings) == 120
    assert len(ico_matchings) == 125
    assert sorted(len(orbit) for orbit in ico_orbits) == [5, 10, 20, 30, 60]

    first, first_keys = audit_result(args.candidate1, 1, ico_orbits)
    second, second_keys = audit_result(args.candidate2, 2, ico_orbits)
    search_hash = sha256_bytes(args.search_script.read_bytes())
    assert first["recorded_script_sha256"] == search_hash
    assert second["recorded_script_sha256"] == search_hash
    assert len(first_keys) + len(second_keys) == 540

    payload = {
        "schema": "erdos151-m2-gluing-union-coverage-audit-v1",
        "status": "PASS",
        "search_script": {
            "path": str(args.search_script),
            "sha256": search_hash,
        },
        "icosahedron": {
            "automorphism_count": len(ico_mappings),
            "perfect_matching_count": len(ico_matchings),
            "perfect_matching_orbit_sizes": [len(orbit) for orbit in ico_orbits],
            "orbit_size_sum": sum(len(orbit) for orbit in ico_orbits),
        },
        "candidates": [first, second],
        "union": {
            "canonical_factor_branches": len(first_keys) + len(second_keys),
            "termination_status_counts": dict(
                sorted(
                    (
                        Counter(first["termination_status_counts"])
                        + Counter(second["termination_status_counts"])
                    ).items()
                )
            ),
            "survivors": 0,
            "coverage_exact": True,
        },
        "conclusion": (
            "Independent orbit reconstruction matches all 540 retained canonical "
            "factor-branch keys, and every retained branch records exhaustive "
            "termination with no quotient survivor."
        ),
        "claim_boundary": (
            "This independently audits input identities, automorphism/orbit "
            "reduction, factor coverage, branch keys, and recorded termination. "
            "It does not independently re-solve the SAT branches and is not a "
            "DRAT/LRAT proof certificate."
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["union"], sort_keys=True))


if __name__ == "__main__":
    main()
