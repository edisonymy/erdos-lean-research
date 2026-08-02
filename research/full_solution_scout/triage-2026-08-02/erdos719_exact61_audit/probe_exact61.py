#!/usr/bin/env python3
"""Deterministic bounded #719 probe at r=3, n=9, e=61, nu<=2.

This freezes the corrected probe used by the 2026-08-02 outside-option audit.
It is diagnostic only: a conflict-budget UNKNOWN is neither SAT nor UNSAT.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
from pathlib import Path

import pysat
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


CONFIG_SCHEMA = "erdos719-exact61-lazy-packing3-config-v1"
TRACE_SCHEMA = "erdos719-exact61-lazy-packing3-trace-v1"
MODEL_SCHEMA = "erdos719-n9-r3-model-definition-v1"


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError(f"unexpected config schema: {config.get('schema')!r}")
    required = {
        "n": 9,
        "r": 3,
        "target_edge_count": 61,
        "maximum_allowed_packing": 2,
        "solver": "cadical195",
        "cardinality_encoding": "pysat.card.EncType.seqcounter",
        "conflict_budget_per_solve": 20000,
        "maximum_rounds": 20,
    }
    for key, expected in required.items():
        if config.get(key) != expected:
            raise ValueError(f"{key}: expected {expected!r}, got {config.get(key)!r}")
    return config


def model_definition() -> dict:
    vertices = list(range(9))
    edges = list(itertools.combinations(vertices, 3))
    edge_id = {edge: index for index, edge in enumerate(edges, start=1)}
    tetrahedra = []
    for tetrahedron_id, four_set in enumerate(
        itertools.combinations(vertices, 4), start=1
    ):
        tetrahedra.append(
            {
                "id": tetrahedron_id,
                "vertices": list(four_set),
                "edge_variables": [
                    edge_id[edge] for edge in itertools.combinations(four_set, 3)
                ],
            }
        )
    return {
        "schema": MODEL_SCHEMA,
        "vertices": vertices,
        "edge_variable_count": len(edges),
        "edge_variables": [
            {"variable": index, "vertices": list(edge)}
            for index, edge in enumerate(edges, start=1)
        ],
        "tetrahedron_count": len(tetrahedra),
        "tetrahedra": tetrahedra,
    }


def exact61_formula():
    return CardEnc.equals(
        lits=list(range(1, 85)),
        bound=61,
        top_id=84,
        encoding=EncType.seqcounter,
    )


def dimacs_text(formula) -> str:
    lines = [f"p cnf {formula.nv} {len(formula.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in formula.clauses)
    return "\n".join(lines) + "\n"


def run_probe(config: dict, model: dict, formula) -> tuple[dict, list[dict]]:
    tetrahedra = model["tetrahedra"]
    seen_cuts: set[tuple[int, ...]] = set()
    cut_rows: list[dict] = []
    rounds: list[dict] = []
    terminal_status = "ROUND_CAP_UNKNOWN"

    with Solver(name=config["solver"], bootstrap_with=formula.clauses) as solver:
        for round_number in range(1, config["maximum_rounds"] + 1):
            solver.conf_budget(config["conflict_budget_per_solve"])
            answer = solver.solve_limited(expect_interrupt=True)
            if answer is None:
                terminal_status = "CONFLICT_CAP_UNKNOWN"
                break
            if answer is False:
                terminal_status = "UNSAT_NO_PROOF_LOG"
                break

            positive_edge_variables = sorted(
                literal
                for literal in solver.get_model()
                if 1 <= literal <= model["edge_variable_count"]
            )
            if len(positive_edge_variables) != config["target_edge_count"]:
                raise AssertionError(
                    f"cardinality violation: {len(positive_edge_variables)}"
                )
            positive_set = set(positive_edge_variables)
            present = [
                tetrahedron
                for tetrahedron in tetrahedra
                if set(tetrahedron["edge_variables"]) <= positive_set
            ]

            new_clauses: list[list[int]] = []
            first_cut_index = len(cut_rows) + 1
            for left, middle, right in itertools.combinations(present, 3):
                concatenated = tuple(
                    left["edge_variables"]
                    + middle["edge_variables"]
                    + right["edge_variables"]
                )
                if len(set(concatenated)) != 12:
                    continue
                key = tuple(sorted(concatenated))
                if key in seen_cuts:
                    continue
                seen_cuts.add(key)
                # Literal order is part of the frozen solver transcript.  This
                # sorted order is what distinguishes the corrected run from an
                # earlier scratch variant with a different CDCL trajectory.
                clause = [-edge_variable for edge_variable in key]
                new_clauses.append(clause)
                cut_rows.append(
                    {
                        "cut_index": len(cut_rows) + 1,
                        "round": round_number,
                        "tetrahedron_ids": [
                            left["id"],
                            middle["id"],
                            right["id"],
                        ],
                        "edge_variable_ids": list(key),
                        "clause": clause,
                    }
                )

            solver.append_formula(new_clauses)
            rounds.append(
                {
                    "round": round_number,
                    "edge_count": len(positive_edge_variables),
                    "positive_edge_variables": positive_edge_variables,
                    "present_tetrahedron_count": len(present),
                    "present_tetrahedron_ids": [item["id"] for item in present],
                    "new_cut_count": len(new_clauses),
                    "first_new_cut_index": first_cut_index if new_clauses else None,
                    "last_new_cut_index": len(cut_rows) if new_clauses else None,
                    "cumulative_cut_count": len(cut_rows),
                    "solver_accumulated_stats": solver.accum_stats(),
                }
            )
            if not new_clauses:
                terminal_status = "CANDIDATE_FOUND"
                break

        final_stats = solver.accum_stats()

    signature = [
        [
            row["round"],
            row["edge_count"],
            row["present_tetrahedron_count"],
            row["new_cut_count"],
            row["cumulative_cut_count"],
        ]
        for row in rounds
    ]
    if signature != config["expected_round_signature"]:
        raise AssertionError(
            "solver transcript differs from frozen signature:\n"
            f"expected={config['expected_round_signature']}\nactual={signature}"
        )
    if terminal_status != config["expected_terminal_status"]:
        raise AssertionError(
            f"expected {config['expected_terminal_status']}, got {terminal_status}"
        )

    trace = {
        "schema": TRACE_SCHEMA,
        "claim_boundary": (
            "Diagnostic bounded run only; CONFLICT_CAP_UNKNOWN proves neither "
            "existence nor nonexistence."
        ),
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_sat": pysat.__version__,
            "platform": platform.platform(),
        },
        "configuration": config,
        "base_formula": {
            "edge_variable_count": model["edge_variable_count"],
            "tetrahedron_count": model["tetrahedron_count"],
            "total_variable_count": formula.nv,
            "clause_count": len(formula.clauses),
        },
        "rounds": rounds,
        "terminal_status": terminal_status,
        "total_packing3_cuts": len(cut_rows),
        "final_solver_accumulated_stats": final_stats,
    }
    return trace, cut_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model-out", type=Path, required=True)
    parser.add_argument("--cnf-out", type=Path, required=True)
    parser.add_argument("--trace-out", type=Path, required=True)
    parser.add_argument("--cuts-out", type=Path, required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    model = model_definition()
    formula = exact61_formula()
    model_text = canonical_json(model)
    cnf = dimacs_text(formula)
    write_text(args.model_out, model_text)
    write_text(args.cnf_out, cnf)

    trace, cuts = run_probe(config, model, formula)
    cuts_text = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in cuts
    )
    write_text(args.cuts_out, cuts_text)
    trace["input_and_cut_hashes"] = {
        "config_sha256": sha256_bytes(args.config.read_bytes()),
        "model_definition_sha256": sha256_bytes(model_text.encode("utf-8")),
        "base_cnf_sha256": sha256_bytes(cnf.encode("utf-8")),
        "packing3_cuts_sha256": sha256_bytes(cuts_text.encode("utf-8")),
    }
    write_text(args.trace_out, canonical_json(trace))
    print(canonical_json(trace), end="")


if __name__ == "__main__":
    main()
