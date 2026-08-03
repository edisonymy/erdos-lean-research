#!/usr/bin/env python3
"""Audit the adjacency-mask correction and preserve old/corrected provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx

import marked_factor_gluing_search as search


OLD_SEARCH_SHA256 = "48aa7e2eb2effb354384de5dca8c5b0097a6d6fd97dd91847e7071245cb1cf27"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_projection(payload: dict[str, object]) -> dict[str, object]:
    """Project a result onto data that defines the canonical SAT branches."""

    cases = []
    for candidate in payload["cases"]:
        configurations = []
        for configuration in candidate["configuration_cases"]:
            branches = []
            for branch in configuration.get("factor_branches", []):
                branches.append(
                    {
                        "global_branch_index": branch["global_branch_index"],
                        "icosahedron_orbit_pair": branch["icosahedron_orbit_pair"],
                        "residual_orbit_index": branch["residual_orbit_index"],
                        "residual_orbit_size": branch["residual_orbit_size"],
                        "residual_matching_representative": branch[
                            "residual_matching_representative"
                        ],
                    }
                )
            configurations.append(
                {
                    "configuration_orbit_index": configuration[
                        "configuration_orbit_index"
                    ],
                    "exceptional_fibres": configuration["exceptional_fibres"],
                    "orbit_size": configuration["orbit_size"],
                    "branches": branches,
                }
            )
        cases.append(
            {
                "candidate_index": candidate["candidate_index"],
                "sphere_graph6": candidate["sphere_graph6"],
                "configs": configurations,
            }
        )
    return {
        "ico": payload["icosahedron_matching_representatives"],
        "cases": cases,
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(
        canonical_projection(payload), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def summarize_result(path: Path, expected_script_sha: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    branches = [
        branch
        for candidate in payload["cases"]
        for configuration in candidate["configuration_cases"]
        for branch in configuration.get("factor_branches", [])
    ]
    assert payload["script_sha256"] == expected_script_sha
    return {
        "path": str(path),
        "sha256": sha256(path),
        "recorded_script_sha256": payload["script_sha256"],
        "solver": payload["solver"],
        "complete": payload["complete"],
        "canonical_factor_branches": len(branches),
        "termination_status_counts": dict(
            sorted(Counter(branch["status"] for branch in branches).items())
        ),
        "survivors": len(payload["survivors"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-cadical1", type=Path, required=True)
    parser.add_argument("--old-cadical2", type=Path, required=True)
    parser.add_argument("--old-glucose1", type=Path, required=True)
    parser.add_argument("--old-glucose2", type=Path, required=True)
    parser.add_argument("--corrected-cadical1", type=Path, required=True)
    parser.add_argument("--corrected-cadical2", type=Path, required=True)
    parser.add_argument("--corrected-glucose1", type=Path, required=True)
    parser.add_argument("--corrected-glucose2", type=Path, required=True)
    parser.add_argument("--search-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    current_search_sha = sha256(args.search_script)

    # Permanent regression: the built-in icosahedron really has a nonnumeric
    # insertion order, and the helper must nevertheless be indexed by label.
    icosahedron = nx.icosahedral_graph()
    insertion_order = list(icosahedron)
    assert insertion_order != sorted(insertion_order)
    masks = search.adjacency_masks(icosahedron)
    mismatches = []
    for vertex in icosahedron:
        decoded = {other for other in icosahedron if masks[vertex] & (1 << other)}
        if decoded != set(icosahedron[vertex]):
            mismatches.append(vertex)
    assert not mismatches

    paths_by_candidate = {
        1: (
            args.old_cadical1,
            args.old_glucose1,
            args.corrected_cadical1,
            args.corrected_glucose1,
        ),
        2: (
            args.old_cadical2,
            args.old_glucose2,
            args.corrected_cadical2,
            args.corrected_glucose2,
        ),
    }
    projections = []
    for candidate, paths in paths_by_candidate.items():
        payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        encoded = [canonical_bytes(payload) for payload in payloads]
        assert len(set(encoded)) == 1
        projections.append(
            {
                "candidate_index": candidate,
                "paths": [str(path) for path in paths],
                "canonical_json_bytes": len(encoded[0]),
                "canonical_projection_sha256": hashlib.sha256(encoded[0]).hexdigest(),
                "all_old_and_corrected_projections_identical": True,
            }
        )

    old_paths = (
        args.old_cadical1,
        args.old_cadical2,
        args.old_glucose1,
        args.old_glucose2,
    )
    corrected_paths = (
        args.corrected_cadical1,
        args.corrected_cadical2,
        args.corrected_glucose1,
        args.corrected_glucose2,
    )
    invalidated = [summarize_result(path, OLD_SEARCH_SHA256) for path in old_paths]
    corrected = [summarize_result(path, current_search_sha) for path in corrected_paths]
    assert all(record["complete"] for record in corrected)
    assert all(record["survivors"] == 0 for record in corrected)
    assert sum(record["canonical_factor_branches"] for record in corrected[:2]) == 540
    assert sum(record["canonical_factor_branches"] for record in corrected[2:]) == 540

    result = {
        "schema": "erdos151-label-order-correction-audit-v1",
        "status": "PASS",
        "regression": {
            "icosahedron_insertion_order": insertion_order,
            "insertion_order_is_nonnumeric": True,
            "adjacency_masks_match_graph_neighbours_for_every_label": True,
            "mismatching_labels": mismatches,
        },
        "bug": {
            "old_search_script_sha256": OLD_SEARCH_SHA256,
            "corrected_search_script_sha256": current_search_sha,
            "description": (
                "The old helper emitted masks in NetworkX insertion order but callers "
                "indexed them by integer vertex label. This could add unsound SAT "
                "parallel-gate clauses. Old SAT termination records are invalidated."
            ),
            "scope": (
                "Canonical matching/configuration/branch construction did not use the "
                "helper; the identical projections below preserve that independent "
                "branch-manifest evidence."
            ),
        },
        "invalidated_old_sat_results": invalidated,
        "corrected_sat_results": corrected,
        "canonical_input_projection_checks": projections,
        "claim_boundary": (
            "This audit detects the historical label-order failure, confirms the fixed "
            "helper on the triggering graph, distinguishes invalid SAT terminations from "
            "unchanged canonical inputs, and checks corrected result metadata. Separate "
            "coverage audits reconstruct orbit completeness and branch keys."
        ),
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "regression": True,
                "projection_hashes": [
                    item["canonical_projection_sha256"] for item in projections
                ],
                "corrected_branches": [
                    item["canonical_factor_branches"] for item in corrected
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
