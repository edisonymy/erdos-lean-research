#!/usr/bin/env python3
"""Independent structural audit of the persisted sigma=19 cycle blocks.

This deliberately does not import either SAT searcher.  In sat_search.build,
all incidence variables X[p,j] are allocated first, in lexicographic loop
order p then j.  Hence, for SIGMA=19 and M=floor(C(19,2)/3)=57,

    variable(X[p,j]) = 1 + p*M + j.

Used lines form a nonempty prefix and every used line has at least three
points.  Consequently incidence_graph labels the used line with original
index j by vertex SIGMA+j.  Those two facts make each stored cycle sufficient
to reconstruct its blocking clause without the SAT model that discovered it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


SIGMA = 19
M = (SIGMA * (SIGMA - 1) // 2) // 3


def xvar(point: int, line: int) -> int:
    return 1 + point * M + line


def expected_clause(cycle: list[int]) -> list[int]:
    result: list[int] = []
    for i, a in enumerate(cycle):
        b = cycle[(i + 1) % len(cycle)]
        if (a < SIGMA) == (b < SIGMA):
            raise ValueError(f"non-bipartite step {a}-{b}")
        point, line_vertex = (a, b) if a < SIGMA else (b, a)
        line = line_vertex - SIGMA
        if not 0 <= point < SIGMA:
            raise ValueError(f"point out of range: {point}")
        if not 0 <= line < M:
            raise ValueError(f"line out of range: {line}")
        result.append(-xvar(point, line))
    return result


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    records = []
    errors = []
    lengths = Counter()
    clause_keys = Counter()
    cycle_keys = Counter()

    for number, line in enumerate(raw.splitlines(), start=1):
        try:
            rec = json.loads(line)
            if set(rec) != {"cycle", "clause"}:
                raise ValueError(f"unexpected keys {sorted(rec)}")
            cycle = rec["cycle"]
            clause = rec["clause"]
            if not isinstance(cycle, list) or not all(isinstance(v, int) for v in cycle):
                raise ValueError("cycle is not a list of integers")
            if not isinstance(clause, list) or not all(isinstance(v, int) for v in clause):
                raise ValueError("clause is not a list of integers")
            if len(cycle) not in (16, 32):
                raise ValueError(f"bad cycle length {len(cycle)}")
            if len(set(cycle)) != len(cycle):
                raise ValueError("cycle repeats a vertex")
            expected = expected_clause(cycle)
            if clause != expected:
                raise ValueError(f"clause mismatch; expected {expected}, got {clause}")
            if len(set(clause)) != len(clause):
                raise ValueError("clause repeats an incidence literal")
            lengths[len(cycle)] += 1
            clause_keys[tuple(sorted(clause))] += 1
            cycle_keys[frozenset(zip(cycle, cycle[1:] + cycle[:1]))] += 1
            records.append(rec)
        except Exception as exc:  # report every corrupt record in one pass
            errors.append({"line": number, "error": str(exc)})

    duplicate_clauses = sum(count - 1 for count in clause_keys.values() if count > 1)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest().upper(),
        "bytes": len(raw),
        "records": len(raw.splitlines()),
        "validated_records": len(records),
        "cycle_length_counts": dict(sorted(lengths.items())),
        "duplicate_clause_records": duplicate_clauses,
        "errors": errors,
        "encoding_constants": {"sigma": SIGMA, "max_lines": M, "max_x_var": SIGMA * M},
        "audit_basis": (
            "Every stored vertex sequence is a simple alternating C16/C32; "
            "the recorded clause exactly equals the disjunction of negated "
            "X[p,j] incidences on that cycle under the deterministic prefix-line labeling."
        ),
    }
    return report


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    source = Path(argv[1]) if len(argv) > 1 else here / "blocks_pure19.jsonl"
    report = audit(source)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if len(argv) > 2:
        Path(argv[2]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
