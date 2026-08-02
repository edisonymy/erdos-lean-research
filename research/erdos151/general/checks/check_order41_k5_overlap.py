#!/usr/bin/env python3
"""Exact finite checks for the order-41, omega=5 residual-overlap note.

This is deliberately not an order-41 graph search.  It performs four small
audits:

1. enumerate the three integer cross-profile rows forced by the residual
   ledger;
2. verify the pinned seven-record Ramsey (3,6;17) catalogue facts used by
   the order-17 residual lemma;
3. classify all ways that three or four dominating five-vertex sides of
   those seven graphs can share the same labelled twelve-vertex graph U,
   modulo exact NetworkX VF2 isomorphism; and
4. independently check the explicit order-16 counterexample to the false
   claim that beta <= 5 forces triangle-freeness.

Catalogue completeness remains an external premise.  Hashes and record
counts are checked here, and every operation after that premise is exhaustive.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CATALOGUE_DIR = ROOT / "experiments" / "erdos128"
SIEGE_DIR = ROOT / "experiments" / "erdos151_siege"
sys.path.insert(0, str(SIEGE_DIR))

from beta_bb import beta_engine_b, parse_g6_line  # noqa: E402
from beta_lib import beta_maxsat  # noqa: E402


R36_17 = CATALOGUE_DIR / "r36_17.g6"
R36_16_GZ = CATALOGUE_DIR / "r36_16.g6.gz"
R36_17_SHA256 = "3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361"
R36_16_GZ_SHA256 = "5fd4e68d880e1d4ed05337b97cba0ce15387e1f545744aed80b91bb4b2186f25"
R36_16_DECODED_SHA256 = "25e35e1bb46b3131ff00b430b56e4679fcde7988211aefd9036c1e4c0cd7d2bf"

ORDER16_BASE_G6 = "O@?ACEIDXHDooFUQLgC{?"
ORDER16_TRIANGLE_G6 = "OB?ACEIDXHDooFUQLgC{?"
ORDER16_ADDED_EDGE = (1, 3)
ORDER16_ARTIFACT = HERE / "order16_beta5_triangle_witness.json"
BETA_A_SHA256 = "228c8d82de6a0c292f0f1c89b4a5fc9411feef051d9ddf9cb0950faa1fe6ffac"
BETA_B_SHA256 = "4f8d7fe9361d56119a4ed651ca46acb81366fba612916891178f7d28d06531d6"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def alpha_bruteforce(graph: nx.Graph) -> int:
    nodes = tuple(graph.nodes())
    for size in range(len(nodes), 0, -1):
        for subset in itertools.combinations(nodes, size):
            if graph.subgraph(subset).number_of_edges() == 0:
                return size
    return 0


def triangle_count(graph: nx.Graph) -> int:
    return sum(nx.triangles(graph).values()) // 3


def enumerate_profiles() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for t in range(7):
        for n2 in range(37):
            for n3 in range(37):
                for n4 in range(37):
                    correction = 4 * t + 3 * n2 + 7 * n3 + 11 * n4
                    if correction > 5:
                        continue
                    n1 = 25 - t - 2 * n2 - 3 * n3 - 4 * n4
                    n0 = 36 - n1 - n2 - n3 - n4
                    if n0 < 0 or n1 < 0:
                        continue
                    if n1 + 2 * n2 + 3 * n3 + 4 * n4 != 25 - t:
                        continue
                    rows.append(
                        {
                            "t": t,
                            "n0": n0,
                            "n1": n1,
                            "n2": n2,
                            "n3": n3,
                            "n4": n4,
                            "sum_Z": 80 + correction,
                        }
                    )
    rows.sort(key=lambda row: (row["t"], row["n2"], row["n3"], row["n4"]))
    expected = [
        {"t": 0, "n0": 11, "n1": 25, "n2": 0, "n3": 0, "n4": 0, "sum_Z": 80},
        {"t": 0, "n0": 12, "n1": 23, "n2": 1, "n3": 0, "n4": 0, "sum_Z": 83},
        {"t": 1, "n0": 12, "n1": 24, "n2": 0, "n3": 0, "n4": 0, "sum_Z": 84},
    ]
    if rows != expected:
        raise AssertionError(f"unexpected profile rows: {rows!r}")
    return rows


def load_and_check_r36_17() -> tuple[list[nx.Graph], dict[str, object]]:
    actual_hash = sha256_path(R36_17)
    if actual_hash != R36_17_SHA256:
        raise AssertionError(f"r36_17 hash mismatch: {actual_hash}")
    lines = [line.strip() for line in R36_17.read_bytes().splitlines() if line.strip()]
    if len(lines) != 7:
        raise AssertionError(f"expected 7 r36_17 records, found {len(lines)}")
    graphs = [nx.from_graph6_bytes(line) for line in lines]
    for index, graph in enumerate(graphs):
        if len(graph) != 17:
            raise AssertionError(f"catalogue record {index} has wrong order")
        if triangle_count(graph) != 0:
            raise AssertionError(f"catalogue record {index} is not triangle-free")
        if alpha_bruteforce(graph) > 5:
            raise AssertionError(f"catalogue record {index} has an independent 6-set")
        if min(dict(graph.degree()).values()) < 4:
            raise AssertionError(f"catalogue record {index} has minimum degree below 4")
    edge_histogram = dict(sorted(Counter(graph.number_of_edges() for graph in graphs).items()))
    degree_sequences = [sorted(dict(graph.degree()).values()) for graph in graphs]
    if edge_histogram != {40: 2, 41: 3, 42: 2}:
        raise AssertionError(f"unexpected r36_17 edge histogram: {edge_histogram}")
    return graphs, {
        "path": str(R36_17.relative_to(ROOT)).replace("\\", "/"),
        "sha256": actual_hash,
        "records": len(graphs),
        "edge_histogram": edge_histogram,
        "degree_sequences": degree_sequences,
        "all_triangle_free": True,
        "all_alpha_at_most_5": True,
        "all_minimum_degree_at_least_4": True,
    }


def refinement_key(graph: nx.Graph) -> tuple[object, ...]:
    """An isomorphism-invariant coarse key; exact grouping still uses VF2."""

    labels: dict[int, object] = {vertex: graph.degree(vertex) for vertex in graph}
    for _ in range(4):
        labels = {
            vertex: (labels[vertex], tuple(sorted(labels[neighbor] for neighbor in graph[vertex])))
            for vertex in graph
        }
    return (
        graph.number_of_edges(),
        tuple(sorted(dict(graph.degree()).values())),
        tuple(sorted(labels.values())),
    )


def dominating_partitions(graphs: list[nx.Graph]) -> list[tuple[nx.Graph, dict[int, int], int, tuple[int, ...]]]:
    records: list[tuple[nx.Graph, dict[int, int], int, tuple[int, ...]]] = []
    for graph_index, graph in enumerate(graphs):
        nodes = tuple(graph.nodes())
        for fan_tuple in itertools.combinations(nodes, 5):
            fan = set(fan_tuple)
            common = set(nodes) - fan
            cross_degrees = {
                vertex: len(set(graph.neighbors(vertex)) & fan) for vertex in common
            }
            if min(cross_degrees.values()) < 1:
                continue
            records.append((graph.subgraph(common).copy(), cross_degrees, graph_index, fan_tuple))
    return records


def exact_common_core_classes(
    records: list[tuple[nx.Graph, dict[int, int], int, tuple[int, ...]]]
) -> list[dict[str, object]]:
    buckets: dict[tuple[object, ...], list[tuple[nx.Graph, dict[int, int], int, tuple[int, ...]]]] = defaultdict(list)
    for record in records:
        buckets[refinement_key(record[0])].append(record)

    classes: list[dict[str, object]] = []
    for key in sorted(buckets, key=repr):
        local_classes: list[dict[str, object]] = []
        for graph, cross_degrees, graph_index, fan_tuple in buckets[key]:
            placed = False
            for record in local_classes:
                representative = record["graph"]
                assert isinstance(representative, nx.Graph)
                mappings = list(
                    nx.algorithms.isomorphism.GraphMatcher(
                        representative, graph
                    ).isomorphisms_iter()
                )
                if not mappings:
                    continue
                patterns = record["patterns"]
                assert isinstance(patterns, set)
                for mapping in mappings:
                    patterns.add(tuple(cross_degrees[mapping[index]] for index in range(12)))
                sources = record["sources"]
                assert isinstance(sources, set)
                sources.add((graph_index, tuple(fan_tuple)))
                placed = True
                break
            if placed:
                continue

            ordered = sorted(graph.nodes())
            relabel = {vertex: index for index, vertex in enumerate(ordered)}
            representative = nx.relabel_nodes(graph, relabel, copy=True)
            seed_pattern = tuple(cross_degrees[vertex] for vertex in ordered)
            # A newly created exact-isomorphism class must be closed under the
            # automorphism group of its representative just like a later
            # matching record is closed under every representative-to-record
            # isomorphism above.  Omitting this orbit lost 43 valid aligned
            # patterns across 39 classes in the original audited package.
            seed_orbit = {
                tuple(seed_pattern[mapping[index]] for index in range(12))
                for mapping in nx.algorithms.isomorphism.GraphMatcher(
                    representative, representative
                ).isomorphisms_iter()
            }
            local_classes.append(
                {
                    "graph": representative,
                    "patterns": seed_orbit,
                    "sources": {(graph_index, tuple(fan_tuple))},
                }
            )
        classes.extend(local_classes)
    return classes


def bounded_pattern_sums(
    patterns: set[tuple[int, ...]], capacities: tuple[int, ...], repetitions: int
) -> set[tuple[int, ...]]:
    states = {(0,) * 12}
    ordered_patterns = sorted(patterns)
    for _ in range(repetitions):
        next_states: set[tuple[int, ...]] = set()
        for state in states:
            for pattern in ordered_patterns:
                candidate = tuple(state[index] + pattern[index] for index in range(12))
                if all(candidate[index] <= capacities[index] for index in range(12)):
                    next_states.add(candidate)
        states = next_states
        if not states:
            break
    return states


def analyse_overlap(classes: list[dict[str, object]]) -> dict[str, object]:
    t1_pre_classes = 0
    t1_post_classes = 0
    n2_survivors: list[dict[str, object]] = []

    for class_index, record in enumerate(classes):
        graph = record["graph"]
        patterns = record["patterns"]
        assert isinstance(graph, nx.Graph)
        assert isinstance(patterns, set)
        degrees = tuple(graph.degree(index) for index in range(12))

        # t=1: four order-17 residual fans are already present.  Capacity
        # zero means the remaining four-vertex fan cannot meet that U vertex.
        t1_states = bounded_pattern_sums(
            patterns, tuple(9 - degree for degree in degrees), repetitions=4
        )
        if t1_states:
            t1_pre_classes += 1
        for state in t1_states:
            capacity_zero = [
                index for index in range(12) if degrees[index] + state[index] == 9
            ]
            zero_is_clique = all(
                graph.has_edge(left, right)
                for left, right in itertools.combinations(capacity_zero, 2)
            )
            if len(capacity_zero) <= 2 and zero_is_clique:
                t1_post_classes += 1
                break

        # n2=1: reserve at least one unit at every U vertex for the two
        # overlapping pair spokes.  If exactly one unit remains, adjacency to
        # the double-neighbour vertex w is forced; w has at most seven U
        # neighbours because it already has two neighbours in M.
        n2_states = bounded_pattern_sums(
            patterns, tuple(8 - degree for degree in degrees), repetitions=3
        )
        valid_states: list[tuple[tuple[int, ...], int]] = []
        for state in n2_states:
            remaining = tuple(
                9 - degrees[index] - state[index] for index in range(12)
            )
            if min(remaining) < 1:
                continue
            forced_w = sum(value == 1 for value in remaining)
            if forced_w <= 7:
                valid_states.append((state, forced_w))
        if valid_states:
            alpha = alpha_bruteforce(graph)
            n2_survivors.append(
                {
                    "class_index": class_index,
                    "representative_graph6": nx.to_graph6_bytes(
                        graph, header=False
                    ).strip().decode("ascii"),
                    "edges": graph.number_of_edges(),
                    "degree_sequence": sorted(degrees),
                    "alpha": alpha,
                    "aligned_full_fan_patterns": len(patterns),
                    "valid_three_fan_sums": len(valid_states),
                    "forced_w_range": [
                        min(forced for _, forced in valid_states),
                        max(forced for _, forced in valid_states),
                    ],
                }
            )

    aligned_patterns = sum(len(record["patterns"]) for record in classes)
    if aligned_patterns != 1963:
        raise AssertionError(
            f"expected 1963 automorphism-closed aligned patterns, got {aligned_patterns}"
        )
    if t1_pre_classes != 10:
        raise AssertionError(f"expected 10 preliminary t=1 classes, got {t1_pre_classes}")
    if t1_post_classes != 0:
        raise AssertionError(f"t=1 unexpectedly survived in {t1_post_classes} classes")
    if len(n2_survivors) != 17:
        raise AssertionError(f"expected 17 n2=1 classes, got {len(n2_survivors)}")
    return {
        "automorphism_closed_aligned_patterns": aligned_patterns,
        "t_equals_1": {
            "classes_after_four_full_residual_degree_budgets": t1_pre_classes,
            "classes_after_deficient_fan_domination": t1_post_classes,
            "verdict": "EXCLUDED_CONDITIONAL_ON_R36_17_CATALOGUE_COMPLETENESS",
        },
        "n2_equals_1": {
            "surviving_common_U_classes": len(n2_survivors),
            "survivors": n2_survivors,
            "verdict": "REDUCED_NOT_EXCLUDED",
        },
    }


def check_order16_counterexample() -> dict[str, object]:
    if sha256_path(R36_16_GZ) != R36_16_GZ_SHA256:
        raise AssertionError("compressed r36_16 catalogue hash mismatch")
    decoded = gzip.open(R36_16_GZ, "rb").read()
    if hashlib.sha256(decoded).hexdigest() != R36_16_DECODED_SHA256:
        raise AssertionError("decoded r36_16 catalogue hash mismatch")
    base_lines = {line.strip().decode("ascii") for line in decoded.splitlines() if line.strip()}
    if len(base_lines) != 2576 or ORDER16_BASE_G6 not in base_lines:
        raise AssertionError("order-16 base graph is absent from the pinned catalogue")

    base = nx.from_graph6_bytes(ORDER16_BASE_G6.encode("ascii"))
    candidate = base.copy()
    if candidate.has_edge(*ORDER16_ADDED_EDGE):
        raise AssertionError("advertised added edge is already present")
    candidate.add_edge(*ORDER16_ADDED_EDGE)
    encoded = nx.to_graph6_bytes(candidate, header=False).strip().decode("ascii")
    if encoded != ORDER16_TRIANGLE_G6:
        raise AssertionError(f"candidate graph6 mismatch: {encoded}")

    beta_a, witness = beta_maxsat(candidate)
    n_b, adjacency_b = parse_g6_line(ORDER16_TRIANGLE_G6)
    beta_b = beta_engine_b(n_b, adjacency_b)
    alpha = alpha_bruteforce(candidate)
    omega = max(len(clique) for clique in nx.find_cliques(candidate))
    triangles = triangle_count(candidate)
    degree_sequence = sorted(dict(candidate.degree()).values())
    if (len(candidate), candidate.number_of_edges(), triangles, alpha, omega) != (
        16,
        39,
        1,
        5,
        3,
    ):
        raise AssertionError("order-16 witness graph invariants changed")
    if degree_sequence != [4, 4] + [5] * 14:
        raise AssertionError(f"order-16 witness degree sequence changed: {degree_sequence}")
    if beta_a != 5 or beta_b != 5:
        raise AssertionError(f"order-16 witness beta disagreement: {beta_a}, {beta_b}")
    beta_a_path = SIEGE_DIR / "beta_lib.py"
    beta_b_path = SIEGE_DIR / "beta_bb.py"
    if sha256_path(beta_a_path) != BETA_A_SHA256:
        raise AssertionError("beta engine A source hash mismatch")
    if sha256_path(beta_b_path) != BETA_B_SHA256:
        raise AssertionError("beta engine B source hash mismatch")

    report = {
        "false_claim": "every order-16 graph with beta<=5 is triangle-free",
        "base_graph6": ORDER16_BASE_G6,
        "base_catalogue_records": len(base_lines),
        "added_edge": list(ORDER16_ADDED_EDGE),
        "candidate_graph6": ORDER16_TRIANGLE_G6,
        "order": len(candidate),
        "edges": candidate.number_of_edges(),
        "degree_sequence": degree_sequence,
        "triangles": triangles,
        "alpha": alpha,
        "omega": omega,
        "beta_engine_A_RC2": beta_a,
        "beta_engine_A_witness": sorted(witness),
        "beta_engine_B_branch_and_bound": beta_b,
        "verdict": "COUNTEREXAMPLE_INDEPENDENTLY_VERIFIED",
    }
    artifact = json.loads(ORDER16_ARTIFACT.read_text(encoding="utf-8"))
    if artifact.get("status") != report["verdict"]:
        raise AssertionError("order-16 artifact status mismatch")
    construction = artifact.get("construction", {})
    properties = artifact.get("candidate_properties", {})
    checks = artifact.get("checks", {})
    if construction.get("base_graph6") != ORDER16_BASE_G6:
        raise AssertionError("order-16 artifact base mismatch")
    if construction.get("candidate_graph6") != ORDER16_TRIANGLE_G6:
        raise AssertionError("order-16 artifact candidate mismatch")
    if construction.get("added_edge") != list(ORDER16_ADDED_EDGE):
        raise AssertionError("order-16 artifact edge mismatch")
    expected_properties = {
        "order": 16,
        "edges": 39,
        "degree_sequence": degree_sequence,
        "triangles": 1,
        "alpha": 5,
        "omega": 3,
        "beta": 5,
    }
    if properties != expected_properties:
        raise AssertionError("order-16 artifact property block mismatch")
    if checks.get("engine_A", {}).get("source_sha256") != BETA_A_SHA256:
        raise AssertionError("order-16 artifact engine A hash mismatch")
    if checks.get("engine_B", {}).get("source_sha256") != BETA_B_SHA256:
        raise AssertionError("order-16 artifact engine B hash mismatch")
    report["artifact"] = str(ORDER16_ARTIFACT.relative_to(ROOT)).replace("\\", "/")
    return report


def main() -> None:
    profiles = enumerate_profiles()
    graphs, catalogue_report = load_and_check_r36_17()
    partitions = dominating_partitions(graphs)
    if len(partitions) != 4368:
        raise AssertionError(f"expected 4368 dominating partitions, got {len(partitions)}")
    classes = exact_common_core_classes(partitions)
    if len(classes) != 786:
        raise AssertionError(f"expected 786 exact common-U classes, got {len(classes)}")
    overlap = analyse_overlap(classes)
    order16 = check_order16_counterexample()
    report = {
        "schema": "erdos151-order41-k5-overlap-check-v1",
        "status": "VERIFIED",
        "profiles": profiles,
        "r36_17_catalogue": catalogue_report,
        "dominating_partitions": len(partitions),
        "exact_common_U_isomorphism_classes": len(classes),
        "overlap": overlap,
        "order16_triangle_counterexample": order16,
        "scope_warning": (
            "The t=1 exclusion is conditional on completeness of the pinned "
            "Ramsey (3,6;17) catalogue.  The n2=1 and rigid profiles remain open."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
