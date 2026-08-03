#!/usr/bin/env python3
"""Independent definition-level verifier for a #701 MiniCard model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


N = 8
M = 1 << N


def powerset_submasks(mask: int):
    sub = mask
    while True:
        yield sub
        if sub == 0:
            return
        sub = (sub - 1) & mask


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    raw = args.result.read_bytes()
    data = json.loads(raw)
    if data.get("status") != "SAT":
        raise SystemExit("NO_SAT_MODEL")
    F = frozenset(map(int, data["family_masks"]))
    A = frozenset(map(int, data["witness_masks"]))
    checks = {}
    checks["masks_in_range"] = all(0 <= s < M for s in F | A)
    checks["empty_in_F"] = 0 in F
    checks["empty_not_in_A"] = 0 not in A
    checks["A_subset_F"] = A <= F
    checks["ground_union_8"] = 0
    for s in F:
        checks["ground_union_8"] |= s
    checks["ground_union_8"] = checks["ground_union_8"] == M - 1
    checks["downset"] = all(t in F for s in F for t in powerset_submasks(s))
    ordered = sorted(A)
    checks["intersecting"] = all(
        ordered[i] & ordered[j]
        for i in range(len(ordered))
        for j in range(i + 1, len(ordered))
    )
    stars = [sum(bool(s & (1 << x)) for s in F) for x in range(N)]
    checks["strictly_beats_every_star"] = all(len(A) >= z + 1 for z in stars)
    # These are audit diagnostics, not required for the original statement.
    down_A = {t for s in A for t in powerset_submasks(s)}
    diagnostics = {
        "normal_form_F_equals_down_A": F == down_A,
        "union_A_8": 0 if not A else __import__("functools").reduce(int.__or__, A) == M - 1,
        "A_maximal_intersecting_in_F": all(
            t in A or any((s & t) == 0 for s in A) for t in F
        ),
    }
    if not all(checks.values()):
        raise AssertionError({k: v for k, v in checks.items() if not v})
    report = {
        "schema": "erdos701-independent-definition-verification-v1",
        "verified": True,
        "source": str(args.result),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "family_size": len(F),
        "witness_size": len(A),
        "star_sizes": stars,
        "minimum_gap": min(len(A) - z for z in stars),
        "definition_checks": checks,
        "normalization_diagnostics": diagnostics,
    }
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if args.out:
        args.out.write_bytes(encoded)
    print(encoded.decode(), end="")


if __name__ == "__main__":
    main()
