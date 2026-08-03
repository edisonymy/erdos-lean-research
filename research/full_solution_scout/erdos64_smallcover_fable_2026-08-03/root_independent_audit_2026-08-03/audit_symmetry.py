#!/usr/bin/env python3
"""Finite hostile checks for the packet's DoubleLex implementation."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


def lex_aux_satisfies(a, b, e):
    if not e[0]:
        return False
    for i in range(len(a)):
        clauses = (
            (not e[i]) or a[i] or (not b[i]),
            (not e[i + 1]) or e[i],
            (not e[i + 1]) or a[i] or (not b[i]),
            (not e[i + 1]) or (not a[i]) or b[i],
            (not e[i]) or (not a[i]) or (not b[i]) or e[i + 1],
            (not e[i]) or a[i] or b[i] or e[i + 1],
        )
        if not all(clauses):
            return False
    return True


def rows_cols_sorted(matrix):
    rows = [tuple(row) for row in matrix]
    cols = [tuple(row[j] for row in matrix) for j in range(len(matrix[0]))]
    return all(rows[i] >= rows[i + 1] for i in range(len(rows) - 1)) and all(
        cols[j] >= cols[j + 1] for j in range(len(cols) - 1)
    )


def permute(matrix, rp, cp):
    return [[matrix[i][j] for j in cp] for i in rp]


def main(output: Path) -> int:
    aux_mismatches = 0
    aux_cases = 0
    for k in range(1, 6):
        for a in itertools.product((False, True), repeat=k):
            for b in itertools.product((False, True), repeat=k):
                exists = any(
                    lex_aux_satisfies(a, b, e)
                    for e in itertools.product((False, True), repeat=k + 1)
                )
                expected = a >= b
                aux_cases += 1
                aux_mismatches += int(exists != expected)

    r, c = 3, 4
    row_perms = tuple(itertools.permutations(range(r)))
    col_perms = tuple(itertools.permutations(range(c)))
    matrix_failures = 0
    matrix_cases = 0
    for bits in itertools.product((0, 1), repeat=r * c):
        matrix = [list(bits[i * c:(i + 1) * c]) for i in range(r)]
        found = any(
            rows_cols_sorted(permute(matrix, rp, cp))
            for rp in row_perms for cp in col_perms
        )
        matrix_cases += 1
        matrix_failures += int(not found)

    result = {
        "lex_aux_truth_table": {"cases": aux_cases, "mismatches": aux_mismatches},
        "doublelex_orbit_check": {
            "dimensions": [r, c], "matrices": matrix_cases,
            "orbits_without_doublelex_representative": matrix_failures,
        },
        "general_soundness_argument": (
            "Choose a row/column permutation whose row-major bitstring is "
            "lexicographically maximal. Any inverted adjacent row or column "
            "could be swapped to increase that bitstring, so both orders hold."
        ),
        "verdict": "PASS" if aux_mismatches == matrix_failures == 0 else "FAIL",
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["verdict"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
