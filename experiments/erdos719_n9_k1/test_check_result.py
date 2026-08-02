#!/usr/bin/env python3
"""Adversarial scope tests for check_result.py."""

from __future__ import annotations

import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check_result.py"
BASE = json.loads((HERE / "lower_55.json").read_text(encoding="utf-8"))


def run(payload: dict, expected_success: bool) -> dict | None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "input.json"
        output = tmp_path / "output.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(CHECKER), str(source), "--json-out", str(output)],
            check=False,
            capture_output=True,
            text=True,
        )
        if (completed.returncode == 0) != expected_success:
            raise AssertionError(
                f"unexpected return code {completed.returncode}: {completed.stderr}"
            )
        return json.loads(output.read_text(encoding="utf-8")) if expected_success else None


def tetrahedron(vertices: tuple[int, int, int, int]) -> list[list[int]]:
    return [list(edge) for edge in itertools.combinations(vertices, 3)]


def main() -> None:
    checked = run(BASE, True)
    assert checked is not None
    assert checked["status"] == "VERIFIED_GRAPH_QUANTITIES"
    assert checked["exact_edge_disjoint_packing_number"] == 1

    wrong_schema = dict(BASE)
    wrong_schema["schema"] = "wrong"
    run(wrong_schema, False)

    false_bound = dict(BASE)
    false_bound["packing_number_upper_bound"] = 0
    run(false_bound, False)

    out_of_scope = dict(BASE)
    out_of_scope["edges"] = tetrahedron((0, 1, 2, 3)) + tetrahedron((4, 5, 6, 7))
    out_of_scope["maximum_edges"] = 8
    out_of_scope["minimum_parts_if_packing_one"] = 2
    out_of_scope["margin_over_ex_if_packing_one"] = -52
    run(out_of_scope, False)

    print("CHECKER_SCOPE_TESTS_PASS cases=4")


if __name__ == "__main__":
    main()
