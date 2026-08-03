#!/usr/bin/env python3
"""Compute the exact union coverage of the full uniform-type5 case tree."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


PACKET = Path(__file__).resolve().parent
DIRECT_PATTERN = re.compile(
    r"type5_full_matching_exact_case_(\d+)_(\d+)_(\d+)_(\d+)_cadical\.result\.json"
)
HARD_PATTERN = re.compile(r"type5_hard0020_link1_(\d+)_(\d+)_cadical\.result\.json")
SECOND_AUDIT_PATTERN = re.compile(
    r"audit_type5_second_link_(\d+)_(\d+)_(\d+)_(\d+)\.result\.json"
)
SECOND_RESULT_PATTERN = re.compile(
    r"type5_second_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)_(\d+)_"
    r"(cadical|kissat|glucose|maplecm)\.result\.json"
)
HARD_PARENT = (0, 0, 2, 0)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    rim_audit = load(PACKET / "audit_type5_rkh_rim_split.result.json")
    rk_audit = load(PACKET / "audit_type5_rk_split.result.json")
    rkh_audit = load(PACKET / "audit_type5_rkh_split.result.json")
    hard_audit = load(PACKET / "audit_type5_hard0020_link1_split.result.json")
    assert all(
        audit["status"] == "PASS"
        for audit in (rim_audit, rk_audit, rkh_audit, hard_audit)
    )

    refined = set()
    coarse_totals = {}
    for record in rim_audit["cases"]:
        coarse = (record["r"], record["k"], record["h"])
        count = record["orbit_representatives"]
        coarse_totals[coarse] = count
        refined.update((*coarse, rim_index) for rim_index in range(count))
    assert len(refined) == rim_audit["refined_case_count"] == 34
    assert len(coarse_totals) == rkh_audit["case_count"] == 23

    direct = set()
    direct_files = []
    for path in sorted(PACKET.glob("type5_full_matching_exact_case_*_cadical.result.json")):
        match = DIRECT_PATTERN.fullmatch(path.name)
        if not match:
            continue
        case = tuple(map(int, match.groups()))
        payload = load(path)
        assert payload["case_count"] == 1
        assert payload["records"][0]["satisfiable"] is False
        assert (
            payload["records"][0]["r"],
            payload["records"][0]["k"],
            payload["records"][0]["h"],
            payload["records"][0]["rim_index"],
        ) == case
        assert case in refined
        direct.add(case)
        direct_files.append(path.name)

    hard_leaves = set()
    hard_files = []
    for path in sorted(PACKET.glob("type5_hard0020_link1_*_cadical.result.json")):
        match = HARD_PATTERN.fullmatch(path.name)
        if not match:
            continue
        leaf = tuple(map(int, match.groups()))
        payload = load(path)
        assert payload["case_count"] == 1
        assert payload["records"][0]["satisfiable"] is False
        assert (
            payload["records"][0]["h1"],
            payload["records"][0]["rim1_index"],
        ) == leaf
        hard_leaves.add(leaf)
        hard_files.append(path.name)
    expected_hard_leaves = {
        (record["h1"], rim_index)
        for record in hard_audit["records"]
        for rim_index in range(record["orbit_representatives"])
    }
    hard_complete = hard_leaves == expected_hard_leaves
    assert len(expected_hard_leaves) == hard_audit["case_count"] == 6

    second_expected = {}
    second_audit_files = {}
    mismatch_by_parent = {}
    for path in sorted(PACKET.glob("audit_type5_second_link_*.result.json")):
        match = SECOND_AUDIT_PATTERN.fullmatch(path.name)
        if not match:
            continue
        parent = tuple(map(int, match.groups()))
        audit = load(path)
        assert audit["status"] == "PASS"
        assert tuple(audit["parent"]) == parent
        assert parent in refined
        mismatch_by_parent[parent] = {
            "values": audit["central_heavy_edge_mismatch_values"],
            "global_lower": audit["global_m_lower_from_central_edge_only"],
            "global_upper": audit["global_m_upper_from_central_edge_only"],
            "claim_boundary": audit["mismatch_claim_boundary"],
        }
        if parent == HARD_PARENT:
            # This parent is accounted for by the independently implemented
            # and proof-certified hard0020 split above.
            continue
        leaves = {
            (record["b_index"], rim_index)
            for record in audit["records"]
            for rim_index in range(record["rim_orbit_representatives"])
        }
        assert len(leaves) == audit["leaf_case_count"]
        second_expected[parent] = leaves
        second_audit_files[parent] = path.name
    assert set(mismatch_by_parent) == refined

    second_found = defaultdict(set)
    second_result_files = defaultdict(list)
    for path in sorted(PACKET.glob("type5_second_*.result.json")):
        match = SECOND_RESULT_PATTERN.fullmatch(path.name)
        if not match:
            continue
        values = tuple(map(int, match.groups()[:6]))
        parent, leaf = values[:4], values[4:]
        payload = load(path)
        assert parent in second_expected
        assert payload["case_count"] == 1
        assert tuple(payload["parent"]) == parent
        assert payload["records"][0]["satisfiable"] is False
        assert (
            payload["records"][0]["b_index"],
            payload["records"][0]["rim1_index"],
        ) == leaf
        assert leaf in second_expected[parent]
        second_found[parent].add(leaf)
        second_result_files[parent].append(path.name)

    second_discovery_complete = {
        parent
        for parent, leaves in second_expected.items()
        if leaves and second_found[parent] == leaves
    }
    second_records = []
    second_proof_statuses = {}
    second_proof_complete = set()
    for parent in sorted(second_expected):
        tag = "_".join(map(str, parent))
        proof_path = PACKET / (
            "type5_second_" + tag + "_proof_coverage.result.json"
        )
        proof_status = "NOT_PRESENT"
        if proof_path.is_file():
            proof_payload = load(proof_path)
            proof_status = proof_payload["status"]
            export_path = PACKET / f"type5_second_{tag}_cases.manifest.json"
            export_payload = load(export_path)
            exported_leaves = {
                (record["b_index"], record["rim1_index"])
                for record in export_payload["records"]
            }
            assert tuple(export_payload["parent"]) == parent
            assert export_payload["case_count"] == len(exported_leaves)
            assert exported_leaves == second_expected[parent]
            assert proof_payload["case_count"] == len(second_expected[parent])
            if proof_status == "VERIFIED":
                second_proof_complete.add(parent)
        second_proof_statuses[parent] = proof_status
        second_records.append(
            {
                "parent": list(parent),
                "audit_file": second_audit_files[parent],
                "audit_leaf_count": len(second_expected[parent]),
                "discovery_unsat_leaves": len(second_found[parent]),
                "discovery_complete": parent in second_discovery_complete,
                "proof_complete": parent in second_proof_complete,
                "complete": parent
                in (second_discovery_complete | second_proof_complete),
                "result_files": sorted(second_result_files[parent]),
                "proof_coverage_status": proof_status,
            }
        )

    resolved = set(direct)
    if hard_complete:
        resolved.add(HARD_PARENT)
    second_complete = second_discovery_complete | second_proof_complete
    resolved.update(second_complete)
    unresolved = refined - resolved

    grouped_resolved = defaultdict(int)
    for r, k, h, _rim in resolved:
        grouped_resolved[(r, k, h)] += 1
    coarse_records = []
    for coarse in sorted(coarse_totals):
        total = coarse_totals[coarse]
        done = grouped_resolved[coarse]
        state = "FULL" if done == total else ("PARTIAL" if done else "NONE")
        coarse_records.append(
            {
                "r": coarse[0],
                "k": coarse[1],
                "h": coarse[2],
                "refined_total": total,
                "refined_discovery_unsat": done,
                "state": state,
            }
        )
    full_coarse = {
        (item["r"], item["k"], item["h"])
        for item in coarse_records
        if item["state"] == "FULL"
    }
    rk_totals = defaultdict(int)
    rk_full = defaultdict(int)
    for coarse in coarse_totals:
        rk_totals[coarse[:2]] += 1
        if coarse in full_coarse:
            rk_full[coarse[:2]] += 1
    rk_records = [
        {
            "r": r,
            "k": k,
            "coarse_total": rk_totals[(r, k)],
            "coarse_full": rk_full[(r, k)],
            "state": "FULL"
            if rk_full[(r, k)] == rk_totals[(r, k)]
            else ("PARTIAL" if rk_full[(r, k)] else "NONE"),
        }
        for r, k in sorted(rk_totals)
    ]

    hard_proof_path = PACKET / "type5_hard0020_proof_coverage.result.json"
    hard_proof_status = "NOT_PRESENT"
    if hard_proof_path.is_file():
        proof_payload = load(hard_proof_path)
        hard_proof_status = proof_payload["status"]
        assert proof_payload["case_count"] == len(expected_hard_leaves)

    direct_proof_path = PACKET / "type5_direct_proof_coverage.result.json"
    direct_manifest_path = PACKET / "type5_direct_cases.manifest.json"
    direct_proof_status = "NOT_PRESENT"
    if direct_proof_path.is_file():
        direct_proof = load(direct_proof_path)
        direct_proof_status = direct_proof["status"]
        assert direct_proof["case_count"] == len(direct)
        direct_manifest = load(direct_manifest_path)
        assert direct_manifest["case_count"] == len(direct)
        assert {tuple(item["case"]) for item in direct_manifest["records"]} == direct

    certified = set()
    if direct_proof_status == "VERIFIED":
        certified.update(direct)
    if hard_complete and hard_proof_status == "VERIFIED":
        certified.add(HARD_PARENT)
    certified.update(second_proof_complete)
    assert certified <= resolved

    case_manifest = []
    for case in sorted(refined):
        if case in direct:
            route = "direct"
            leaf_done = leaf_total = 1
            route_proof_status = direct_proof_status
            route_proof_file = direct_proof_path.name
        elif case == HARD_PARENT:
            route = "hard0020_second_link"
            leaf_done = len(hard_leaves)
            leaf_total = len(expected_hard_leaves)
            route_proof_status = hard_proof_status
            route_proof_file = hard_proof_path.name
        elif case in second_expected:
            route = "generic_second_link"
            leaf_done = len(second_found[case])
            leaf_total = len(second_expected[case])
            route_proof_status = second_proof_statuses[case]
            route_proof_file = (
                "type5_second_"
                + "_".join(map(str, case))
                + "_proof_coverage.result.json"
            )
        else:
            route = "not_split_at_second_link"
            leaf_done = 0
            leaf_total = None
            route_proof_status = "NOT_PRESENT"
            route_proof_file = None
        discovery_status = (
            "UNSAT"
            if case in resolved
            else ("PARTIAL_SUBSPLIT" if leaf_done else "UNRESOLVED")
        )
        case_manifest.append(
            {
                "case": list(case),
                "discovery_status": discovery_status,
                "certification_status": (
                    "VERIFIED" if case in certified else "NOT_CERTIFIED"
                ),
                "route": route,
                "leaf_discovery_unsat": leaf_done,
                "leaf_total": leaf_total,
                "proof_coverage_status": route_proof_status,
                "proof_coverage_file": route_proof_file,
                "central_heavy_edge_mismatch_values": mismatch_by_parent[case][
                    "values"
                ],
                "global_m_lower_from_central_edge_only": mismatch_by_parent[case][
                    "global_lower"
                ],
                "global_m_upper_from_central_edge_only": mismatch_by_parent[case][
                    "global_upper"
                ],
            }
        )
    assert len(case_manifest) == 34

    payload = {
        "schema": "erdos151-type5-full-matching-global-coverage-v1",
        "status": "PASS",
        "claim_boundary": (
            "coverage accounting only; discovery UNSAT is not certified unless "
            "the corresponding proof coverage is VERIFIED"
        ),
        "symmetry_tree": {
            "raw_reciprocity_signatures": rk_audit["raw_signatures"],
            "rk_orbits": rk_audit["case_count"],
            "rkh_coarse_cases": rkh_audit["case_count"],
            "rkh_rim_refined_cases": rim_audit["refined_case_count"],
        },
        "discovery_coverage": {
            "direct_refined_unsat": len(direct),
            "complete_subsplit_parents_unsat": (1 if hard_complete else 0)
            + len(second_complete),
            "refined_unsat_union": len(resolved),
            "refined_unresolved": len(unresolved),
            "coarse_full": sum(item["state"] == "FULL" for item in coarse_records),
            "coarse_partial": sum(item["state"] == "PARTIAL" for item in coarse_records),
            "coarse_none": sum(item["state"] == "NONE" for item in coarse_records),
            "rk_full": sum(item["state"] == "FULL" for item in rk_records),
            "rk_partial": sum(item["state"] == "PARTIAL" for item in rk_records),
            "rk_none": sum(item["state"] == "NONE" for item in rk_records),
        },
        "certification_coverage": {
            "refined_certified_unsat": len(certified),
            "refined_discovery_unsat_not_certified": len(resolved - certified),
            "refined_not_discovery_resolved": len(refined - resolved),
        },
        "mismatch_annotation": {
            "status": "AUDITED_LOCAL_ONLY",
            "cases_with_delta0_both_0_and_1": sum(
                item["values"] == [0, 1] for item in mismatch_by_parent.values()
            ),
            "claim_boundary": (
                "the 34 first-link refined cases do not determine global mismatch "
                "count m; each locally permits both central-edge values delta0=0,1"
            ),
        },
        "refined_case_certification_manifest": case_manifest,
        "direct_result_files": direct_files,
        "direct_proof_coverage_status": direct_proof_status,
        "direct_proof_coverage_file": direct_proof_path.name,
        "hard_parent": list(HARD_PARENT),
        "hard_subsplit": {
            "audit_case_count": len(expected_hard_leaves),
            "discovery_unsat_leaves": len(hard_leaves),
            "complete": hard_complete,
            "result_files": hard_files,
            "proof_coverage_status": hard_proof_status,
        },
        "generic_second_link_subsplits": second_records,
        "resolved_refined_cases": [list(item) for item in sorted(resolved)],
        "unresolved_refined_cases": [list(item) for item in sorted(unresolved)],
        "coarse_records": coarse_records,
        "rk_records": rk_records,
    }
    output = PACKET / "audit_type5_global_coverage.result.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
