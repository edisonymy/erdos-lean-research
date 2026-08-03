#!/usr/bin/env python3
"""Bind a frozen pure19 final CNF to the live base encoder and block file."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sat_search


SIGMA = 19


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse_dimacs(path: Path) -> tuple[int, int, list[list[int]]]:
    variables = declared = None
    clauses: list[list[int]] = []
    with path.open("r", encoding="ascii") as stream:
        for number, raw in enumerate(stream, start=1):
            line = raw.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p "):
                fields = line.split()
                if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                    raise ValueError(f"bad header at line {number}: {line}")
                variables, declared = map(int, fields[2:])
                continue
            literals = list(map(int, line.split()))
            if not literals or literals[-1] != 0 or 0 in literals[:-1]:
                raise ValueError(f"bad clause at line {number}")
            clauses.append(literals[:-1])
    if variables is None or declared is None:
        raise ValueError("missing header")
    return variables, declared, clauses


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("usage: audit_pure19_final_cnf.py FINAL.cnf [OUT.json]")
    cnf_path = Path(argv[1]).resolve()
    block_path = Path(__file__).resolve().parent / "blocks_pure19.jsonl"
    variables, declared, actual = parse_dimacs(cnf_path)

    pool, _, _, max_lines, base = sat_search.build(SIGMA, verbose=False, symmetry=True)
    records = [json.loads(line) for line in block_path.read_text(encoding="utf-8").splitlines()]
    blocks = [record["clause"] for record in records]
    expected = base + blocks
    first_mismatch = next(
        (index for index, (a, b) in enumerate(zip(actual, expected)) if a != b),
        None,
    )
    if first_mismatch is None and len(actual) != len(expected):
        first_mismatch = min(len(actual), len(expected))

    checks = {
        "header_variable_count": variables == pool.top,
        "header_clause_count": declared == len(actual),
        "max_line_count": max_lines == 57,
        "actual_clause_count": len(actual) == len(expected),
        "base_prefix_exact": actual[: len(base)] == base,
        "block_suffix_exact": actual[len(base) :] == blocks,
        "all_clauses_exact": first_mismatch is None,
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "cnf": str(cnf_path),
        "cnf_sha256": digest(cnf_path),
        "blocks_sha256": digest(block_path),
        "variables": variables,
        "declared_clauses": declared,
        "base_clauses": len(base),
        "block_clauses": len(blocks),
        "actual_clauses": len(actual),
        "first_mismatch": first_mismatch,
        "checks": checks,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if len(argv) > 2:
        Path(argv[2]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
