#!/usr/bin/env python3
"""Standard-library verification of the retained n=10 leave construction.

This does not trust the MILP's uncovered-quad variables or packing claim.  It
reconstructs the leave from the 38 missing triples and exactly enumerates all
subfamilies of the resulting fourteen quads.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "n10_leave_milp_result.json"
OUT = HERE / "n10_leave_independent_check.json"


def main() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    missing = {tuple(sorted(x)) for x in raw["missing_triples"]}
    all_triples = set(itertools.combinations(range(10), 3))
    assert len(missing) == 38 and missing <= all_triples

    clean = []
    for Q in itertools.combinations(range(10), 4):
        if all(e not in missing for e in itertools.combinations(Q, 3)):
            clean.append(Q)
    assert len(clean) == 14
    assert clean == [tuple(x) for x in raw["uncovered_quads"]]

    best: tuple[int, ...] = ()
    for mask in range(1 << len(clean)):
        if mask.bit_count() <= len(best):
            continue
        chosen = tuple(i for i in range(len(clean)) if mask >> i & 1)
        if all(
            len(set(clean[i]).intersection(clean[j])) <= 2
            for p, i in enumerate(chosen)
            for j in chosen[p + 1 :]
        ):
            best = chosen
    assert len(best) == 8

    payload = {
        "verdict": "VERIFIED_CONSTRUCTION_ONLY",
        "claim_boundary": "38 missing triples leave exactly 14 clean quads; their exact packing number is 8. No optimality claim for 14.",
        "missing_count": len(missing),
        "clean_quad_count": len(clean),
        "exact_clean_quad_packing_number": len(best),
        "packing_witness": [list(clean[i]) for i in best],
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
