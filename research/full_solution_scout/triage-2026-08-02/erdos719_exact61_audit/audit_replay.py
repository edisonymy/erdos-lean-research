#!/usr/bin/env python3
"""Replay and adversarially audit the frozen #719 exact-61 probe artifacts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path

from pysat.solvers import Solver

from certify_ex54 import build_certificate
from probe_exact61 import (
    canonical_json,
    dimacs_text,
    exact61_formula,
    load_config,
    model_definition,
)


AUDIT_SCHEMA = "erdos719-exact61-audit-replay-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate_model(stored: dict) -> None:
    expected = model_definition()
    if stored != expected:
        raise AssertionError("stored model definition differs from deterministic model")
    if stored["edge_variable_count"] != 84:
        raise AssertionError("expected C(9,3)=84 edge variables")
    if stored["tetrahedron_count"] != 126:
        raise AssertionError("expected C(9,4)=126 tetrahedra")
    edge_ids = {row["variable"] for row in stored["edge_variables"]}
    if edge_ids != set(range(1, 85)):
        raise AssertionError("edge-variable ids are not exactly 1..84")
    for tetrahedron in stored["tetrahedra"]:
        if len(tetrahedron["vertices"]) != 4:
            raise AssertionError("tetrahedron has wrong vertex count")
        expected_edges = {
            tuple(edge)
            for edge in itertools.combinations(tetrahedron["vertices"], 3)
        }
        actual_edges = {
            tuple(stored["edge_variables"][variable - 1]["vertices"])
            for variable in tetrahedron["edge_variables"]
        }
        if actual_edges != expected_edges or len(actual_edges) != 4:
            raise AssertionError("tetrahedron incidence is malformed")


def validate_cardinality_cnf(cnf_path: Path, solver_name: str) -> dict:
    formula = exact61_formula()
    expected_text = dimacs_text(formula)
    actual_text = cnf_path.read_text(encoding="utf-8")
    if actual_text != expected_text:
        raise AssertionError("stored DIMACS differs from regenerated exact-61 CNF")
    if formula.nv != 2890 or len(formula.clauses) != 5612:
        raise AssertionError((formula.nv, len(formula.clauses)))

    # The stored formula is byte-identical to PySAT's sequential exact-cardinality
    # encoding.  Exercise every possible cardinality on the canonical prefix
    # assignment, then boundary counts under cyclically shifted assignments.
    semantic_checks = 0
    with Solver(name=solver_name, bootstrap_with=formula.clauses) as solver:
        for count in range(85):
            assumptions = [
                variable if variable <= count else -variable
                for variable in range(1, 85)
            ]
            if solver.solve(assumptions=assumptions) != (count == 61):
                raise AssertionError(f"exact-cardinality failure at count={count}")
            semantic_checks += 1
        for count in (60, 61, 62):
            for shift in range(0, 84, 7):
                selected = {
                    ((shift + offset) % 84) + 1 for offset in range(count)
                }
                assumptions = [
                    variable if variable in selected else -variable
                    for variable in range(1, 85)
                ]
                if solver.solve(assumptions=assumptions) != (count == 61):
                    raise AssertionError(
                        f"shifted cardinality failure count={count}, shift={shift}"
                    )
                semantic_checks += 1
    return {
        "total_variable_count": formula.nv,
        "clause_count": len(formula.clauses),
        "semantic_assignment_checks": semantic_checks,
    }


def validate_trace_and_cuts(
    config: dict, model: dict, trace: dict, cuts: list[dict]
) -> dict:
    if trace.get("schema") != "erdos719-exact61-lazy-packing3-trace-v1":
        raise AssertionError("unexpected trace schema")
    if trace.get("configuration") != config:
        raise AssertionError("trace does not embed the frozen configuration")
    if trace.get("terminal_status") != "CONFLICT_CAP_UNKNOWN":
        raise AssertionError("bounded run must end CONFLICT_CAP_UNKNOWN")
    if trace.get("total_packing3_cuts") != len(cuts):
        raise AssertionError("trace/cut-file count mismatch")

    tetrahedra = model["tetrahedra"]
    tetrahedron_by_id = {row["id"]: row for row in tetrahedra}
    seen: set[tuple[int, ...]] = set()
    cursor = 0
    expected_signature = []
    for round_row in trace["rounds"]:
        round_number = round_row["round"]
        positive = round_row["positive_edge_variables"]
        if positive != sorted(set(positive)) or len(positive) != 61:
            raise AssertionError(f"round {round_number}: model is not exactly 61 edges")
        if any(variable < 1 or variable > 84 for variable in positive):
            raise AssertionError(f"round {round_number}: invalid edge variable")
        positive_set = set(positive)
        present = [
            tetrahedron
            for tetrahedron in tetrahedra
            if set(tetrahedron["edge_variables"]) <= positive_set
        ]
        present_ids = [row["id"] for row in present]
        if present_ids != round_row["present_tetrahedron_ids"]:
            raise AssertionError(f"round {round_number}: wrong present tetrahedra")
        if len(present) != round_row["present_tetrahedron_count"]:
            raise AssertionError(f"round {round_number}: wrong tetrahedron count")

        expected_new = []
        for left, middle, right in itertools.combinations(present, 3):
            concatenated = tuple(
                left["edge_variables"]
                + middle["edge_variables"]
                + right["edge_variables"]
            )
            if len(set(concatenated)) != 12:
                continue
            key = tuple(sorted(concatenated))
            if key in seen:
                continue
            seen.add(key)
            expected_new.append(
                {
                    "tetrahedron_ids": [left["id"], middle["id"], right["id"]],
                    "edge_variable_ids": list(key),
                    "clause": [-variable for variable in key],
                }
            )

        count = round_row["new_cut_count"]
        actual_new = cuts[cursor : cursor + count]
        if len(actual_new) != len(expected_new):
            raise AssertionError(f"round {round_number}: incomplete cut block")
        for offset, (actual, expected) in enumerate(zip(actual_new, expected_new)):
            expected_index = cursor + offset + 1
            if actual.get("cut_index") != expected_index:
                raise AssertionError("non-sequential cut index")
            if actual.get("round") != round_number:
                raise AssertionError("cut assigned to wrong round")
            for field in ("tetrahedron_ids", "edge_variable_ids", "clause"):
                if actual.get(field) != expected[field]:
                    raise AssertionError(
                        f"cut {expected_index}: malformed or missing {field}"
                    )

            source_edge_sets = [
                set(tetrahedron_by_id[tetrahedron_id]["edge_variables"])
                for tetrahedron_id in actual["tetrahedron_ids"]
            ]
            if any(
                source_edge_sets[left] & source_edge_sets[right]
                for left, right in itertools.combinations(range(3), 2)
            ):
                raise AssertionError(f"cut {expected_index}: sources are not edge-disjoint")
            union = set().union(*source_edge_sets)
            if len(union) != 12 or union != set(actual["edge_variable_ids"]):
                raise AssertionError(f"cut {expected_index}: wrong 12-edge union")
            if not union <= positive_set:
                raise AssertionError(f"cut {expected_index}: not violated by source model")
        cursor += count
        if round_row["cumulative_cut_count"] != cursor:
            raise AssertionError(f"round {round_number}: wrong cumulative cut count")
        expected_signature.append(
            [round_number, 61, len(present), len(expected_new), cursor]
        )

    if cursor != len(cuts) or len(seen) != len(cuts):
        raise AssertionError("unconsumed or duplicate cuts")
    if expected_signature != config["expected_round_signature"]:
        raise AssertionError("trace signature differs from frozen signature")
    return {
        "round_count": len(trace["rounds"]),
        "stored_models_checked": len(trace["rounds"]),
        "packing3_cuts_checked": len(cuts),
        "round_signature": expected_signature,
    }


def expect_rejection(callback, label: str) -> str:
    try:
        callback()
    except (AssertionError, KeyError, TypeError, ValueError):
        return label
    raise AssertionError(f"tamper self-test was not rejected: {label}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--cuts", type=Path, required=True)
    parser.add_argument("--ex54-certificate", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    model = load_json(args.model)
    trace = load_json(args.trace)
    cuts = load_jsonl(args.cuts)
    certificate = load_json(args.ex54_certificate)

    validate_model(model)
    cardinality = validate_cardinality_cnf(args.cnf, config["solver"])
    transcript = validate_trace_and_cuts(config, model, trace, cuts)
    regenerated_certificate = build_certificate()
    if certificate != regenerated_certificate:
        raise AssertionError("stored ex_3(9,K_4^3)=54 certificate does not replay")
    if certificate["n9"]["exact_ex_3_9"] != 54:
        raise AssertionError("extremal certificate did not establish 54")

    tamper_tests = []
    bad_model = copy.deepcopy(model)
    bad_model["edge_variable_count"] = 83
    tamper_tests.append(
        expect_rejection(lambda: validate_model(bad_model), "model-count-tamper")
    )
    bad_trace = copy.deepcopy(trace)
    bad_trace["rounds"][0]["positive_edge_variables"].pop()
    tamper_tests.append(
        expect_rejection(
            lambda: validate_trace_and_cuts(config, model, bad_trace, cuts),
            "61-cardinality-tamper",
        )
    )
    bad_cuts = copy.deepcopy(cuts)
    bad_cuts[0]["clause"][0] *= -1
    tamper_tests.append(
        expect_rejection(
            lambda: validate_trace_and_cuts(config, model, trace, bad_cuts),
            "packing3-cut-tamper",
        )
    )
    bad_certificate = copy.deepcopy(certificate)
    bad_certificate["n9"]["exact_ex_3_9"] = 53
    tamper_tests.append(
        expect_rejection(
            lambda: (
                None
                if bad_certificate == regenerated_certificate
                else (_ for _ in ()).throw(AssertionError("certificate mismatch"))
            ),
            "ex54-certificate-tamper",
        )
    )

    result = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "model_checks": {
            "edge_variable_count": model["edge_variable_count"],
            "tetrahedron_count": model["tetrahedron_count"],
        },
        "cardinality_cnf_checks": cardinality,
        "transcript_checks": transcript,
        "extremal_certificate_checks": {
            "exact_t7": certificate["t7_exhaustive_base"]["exact_minimum_hitter"],
            "exact_t8": certificate["n8"]["exact_t8"],
            "exact_t9": certificate["n9"]["exact_t9"],
            "exact_ex_3_9": certificate["n9"]["exact_ex_3_9"],
        },
        "tamper_tests_rejected": tamper_tests,
        "artifact_sha256": {
            "probe_config.json": sha256_file(args.config),
            "model_definition.json": sha256_file(args.model),
            "base_exact61.cnf": sha256_file(args.cnf),
            "probe_trace.json": sha256_file(args.trace),
            "packing3_cuts.jsonl": sha256_file(args.cuts),
            "ex54_certificate.json": sha256_file(args.ex54_certificate),
        },
        "claim_boundary": (
            "The replay validates the recorded bounded UNKNOWN transcript and "
            "the finite extremal value 54; it does not settle #719."
        ),
    }
    rendered = canonical_json(result)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()
