#!/usr/bin/env python3
"""Integration audit for the owner/cross-owner continuation packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--authoritative-target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    p = args.package

    target_sha = digest(args.authoritative_target)
    assert target_sha == "129e292c307923c10e3d2d7897c9acd0a07803dd1c5e6a5b5393d0c24001173f"

    links9 = load(p / "k4free_links_through9_direct.result.json")
    assert links9["counts"]["all_graphs"] == 31
    assert links9["counts"]["nonuniversally_adaptable"] == 0

    links11 = load(p / "k4free_links_through11_direct.result.json")
    assert links11["counts"]["all_graphs"] == 161
    assert links11["counts"]["nonuniversally_adaptable"] == 10
    assert min(x["m"] for x in links11["all_obstructions"]) == 10
    assert all(x["direct_definition_checked"] for x in links11["all_obstructions"])

    n50 = load(p / "n50_protected_core_interface.result.json")
    assert n50["target"]["H"] == 11
    assert n50["link_census"]["obstructions_through_11_edges"] == 10
    assert len(n50["degree_ten_saturation"]["surviving_integer_cases"]) == 5

    cross = load(p / "cross_owner_propertyb.result.json")
    assert cross["property_b"]["all_three_checkers_agree_unsat"]
    assert cross["no_four_selected_triangles_span_K4"]
    assert cross["owner_decomposition"]["unique_edge_ownership"]
    assert cross["owner_decomposition"]["all_selected_triangles_cross_owner"]
    assert cross["shadow"] == {
        "H_order": 4,
        "beta": 10,
        "beta_less_than_H": False,
        "clique_number": 11,
        "edge_count": 55,
        "is_complete": True,
        "tf3": 2,
    }

    atlas = load(p / "signal_sender_atlas.result.json")
    order8 = load(p / "signal_sender_order8.result.json")
    assert atlas["sender_count"] == 0
    assert atlas["independent_sat_audit"]["agreement_on_every_graph"]
    assert order8["k4free_graphs"] == 5606
    assert order8["sender_graph_count"] == 0
    assert order8["all_assumption_queries_agree"]

    hermitian = load(p / "hermitian_certificate_gate.result.json")
    assert hermitian["H3"]["vertices"] == 63
    assert hermitian["H3"]["unique_owners"] == 28
    assert not hermitian["H3"]["direct_per_owner_maxcut_certificate_possible"]

    artifacts = sorted(
        path for path in p.iterdir()
        if path.is_file() and path.name not in {args.output.name, "MANIFEST.json"}
    )
    payload = {
        "schema": "erdos151-owner-coupling-packet-audit-v1",
        "status": "VERIFIED",
        "authoritative_target_sha256": target_sha,
        "assertions": {
            "target_lock": True,
            "link_threshold_and_direct_definition": True,
            "n50_interface": True,
            "cross_owner_property_b": True,
            "signal_sender_negative_through_order8": True,
            "hermitian_arithmetic": True,
        },
        "artifact_sha256_before_audit_output": {
            path.name: digest(path) for path in artifacts
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
