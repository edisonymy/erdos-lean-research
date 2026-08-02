#!/usr/bin/env python3
"""Exhaustive definition tests, schema tamper tests, and v5 smoke adapter."""

from __future__ import annotations

import itertools
import json
import tempfile
from pathlib import Path

import verify_candidate_fastpath as fast


def pack_edges(edges: set[tuple[int, int]]) -> str:
    raw = bytearray((len(fast.PAIR_ORDER) + 7) // 8)
    for index, edge in enumerate(fast.PAIR_ORDER):
        if edge in edges:
            raw[index >> 3] |= 1 << (index & 7)
    return raw.hex()


def candidate_payload(edges: set[tuple[int, int]]) -> dict[str, object]:
    ordered = tuple(sorted(edges))
    packed = pack_edges(edges)
    adjacency = fast.build_adjacency(ordered)
    payload: dict[str, object] = {
        "schema_version": 5,
        "artifact_type": "fixed_clique_cegar_candidate",
        "created_utc": "2000-01-01T00:00:00Z",
        "run": {"fixture": "synthetic-noncandidate-only"},
        "config": fast.F4_CONFIG,
        "graph": {
            "n": fast.N,
            "graph_sha256": fast.graph_hash(fast.N, bytes.fromhex(packed)),
            "edges_hex": packed,
            "edges": [[u, v] for u, v in ordered],
            "edge_count": len(ordered),
            "degrees": [mask.bit_count() for mask in adjacency],
            "triangle_count": len(fast.enumerate_triangles(adjacency)),
        },
        "oracle_results": {"fixture": "not a search result"},
        "independent_verification": {"fixture": "not a search result"},
    }
    payload["content_sha256"] = fast.sha256(fast.canonical_json(payload))
    return payload


def brute_maximal_cliques(adjacency: tuple[int, ...]) -> set[int]:
    n = len(adjacency)
    all_vertices = (1 << n) - 1
    return {
        mask
        for mask in range(1, 1 << n)
        if mask.bit_count() >= 2
        and fast.is_clique(mask, adjacency)
        and not any(fast.is_clique(mask | (1 << vertex), adjacency) for vertex in range(n) if not (mask & (1 << vertex)))
        and mask != all_vertices + 1
    }


def brute_beta(adjacency: tuple[int, ...]) -> int:
    cliques = brute_maximal_cliques(adjacency)
    n = len(adjacency)
    return max(
        mask.bit_count()
        for mask in range(1 << n)
        if all(mask & clique != clique for clique in cliques)
    )


def brute_colorable(edges: tuple[tuple[int, int], ...], triangles: tuple[tuple[int, int, int], ...]) -> bool:
    index = {edge: i for i, edge in enumerate(edges)}
    for assignment in range(1 << len(edges)):
        if all(
            not (
                ((assignment >> index[(a, b)]) & 1)
                == ((assignment >> index[(a, c)]) & 1)
                == ((assignment >> index[(b, c)]) & 1)
            )
            for a, b, c in triangles
        ):
            return True
    return False


def test_exhaustive_small_graphs() -> None:
    # Every labelled graph through order five: 2^(5 choose 2) = 1024 cases.
    for n in range(2, 6):
        pairs = tuple(itertools.combinations(range(n), 2))
        for bits in range(1 << len(pairs)):
            edges = tuple(pair for index, pair in enumerate(pairs) if bits & (1 << index))
            adjacency = fast.build_adjacency(edges, n)
            expected_cliques = brute_maximal_cliques(adjacency)
            actual_cliques = set(fast.enumerate_ambient_maximal_cliques(adjacency))
            assert actual_cliques == expected_cliques, (n, edges, actual_cliques, expected_cliques)
            expected_beta = brute_beta(adjacency)
            # Check each possible beta threshold using the independent transversal engine.
            for target in range(1, n + 1):
                hit = fast.small_hitting_set(tuple(actual_cliques), n, n - target, fast.Budget(0))
                assert (hit is None) == (expected_beta < target), (n, edges, target, expected_beta, hit)
            if len(edges) <= 10:
                triangles = fast.enumerate_triangles(adjacency)
                clauses, ids = fast.triangle_coloring_cnf(edges, triangles)
                actual_colorable, _ = fast.dpll(clauses, len(ids), fast.Budget(0))
                assert actual_colorable == brute_colorable(edges, triangles), (n, edges)


def test_known_examples() -> None:
    # K4 has beta=3 and is not (3,3)-edge-arrowing; K6 is (3,3)-arrowing.
    k4 = tuple(itertools.combinations(range(4), 2))
    a4 = fast.build_adjacency(k4, 4)
    assert fast.independent_set_of_size(a4, 2, fast.Budget(0)) is None
    assert fast.small_hitting_set(fast.enumerate_ambient_maximal_cliques(a4), 4, 0, fast.Budget(0)) is None
    c4, ids4 = fast.triangle_coloring_cnf(k4, fast.enumerate_triangles(a4))
    assert fast.dpll(c4, len(ids4), fast.Budget(0))[0]
    k6 = tuple(itertools.combinations(range(6), 2))
    a6 = fast.build_adjacency(k6, 6)
    c6, ids6 = fast.triangle_coloring_cnf(k6, fast.enumerate_triangles(a6))
    assert not fast.dpll(c6, len(ids6), fast.Budget(0))[0]


def test_schema_tampers_and_smoke_adapter() -> None:
    # The F4 alone is validly encoded v5 JSON but is deliberately noncandidate:
    # its degrees are 3 or 0, so it must stop at the structural gate.
    edges = set(itertools.combinations(range(4), 2))
    fixture = candidate_payload(edges)
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        candidate = directory / "smoke.json"
        candidate.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report = fast.make_report(candidate, node_limit=1_000, include_sat_crosscheck=True)
        assert report["status"] == "REJECTED_STRUCTURE"
        assert report["signed_off"] is False

        tampered = json.loads(candidate.read_text(encoding="utf-8"))
        tampered["graph"]["edges"] = [[0, 1]]
        tampered["content_sha256"] = fast.sha256(fast.canonical_json({k: v for k, v in tampered.items() if k != "content_sha256"}))
        candidate.write_text(json.dumps(tampered), encoding="utf-8")
        report = fast.make_report(candidate, node_limit=1_000, include_sat_crosscheck=False)
        assert report["status"] == "REJECTED_ARTIFACT"
        assert "disagree" in report["error"]

        tampered = candidate_payload(edges)
        tampered["graph"]["graph_sha256"] = "0" * 64
        tampered["content_sha256"] = fast.sha256(fast.canonical_json({k: v for k, v in tampered.items() if k != "content_sha256"}))
        candidate.write_text(json.dumps(tampered), encoding="utf-8")
        report = fast.make_report(candidate, node_limit=1_000, include_sat_crosscheck=False)
        assert report["status"] == "REJECTED_ARTIFACT"
        assert "graph_sha256" in report["error"]


def main() -> None:
    test_exhaustive_small_graphs()
    test_known_examples()
    test_schema_tampers_and_smoke_adapter()
    print(json.dumps({"status": "PASS", "tests": ["all labelled graphs through order 5", "known K4/K6", "v5 smoke and tamper adapter"]}, sort_keys=True))


if __name__ == "__main__":
    main()
