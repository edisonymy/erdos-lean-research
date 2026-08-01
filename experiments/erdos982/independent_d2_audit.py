#!/usr/bin/env python3
"""Independent full-tuple audit of the D2 octagon search at a small bound.

Unlike the optimized C# program, this enumerates every normalized quadruple
and directly computes all three vertex-orbit distance sets.  It therefore
checks both the collision-based candidate reduction and the exact predicates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def profile(a: int, b: int, c: int, d: int) -> tuple[int, int, int]:
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    near_x, far_x = (a - b) ** 2 + dd, (a + b) ** 2 + dd
    near_y, far_y = bb + (c - d) ** 2, bb + (c + d) ** 2
    return (
        len({4 * aa, aa + cc, near_x, far_x}),
        len({4 * cc, aa + cc, near_y, far_y}),
        len({4 * bb, 4 * dd, 4 * (bb + dd), near_x, far_x, near_y, far_y}),
    )


def brute(bound: int) -> dict[str, object]:
    strictly_convex = axial_x_at_most_three = both_axial_at_most_three = 0
    counterexamples = 0
    best: tuple[tuple[int, int, tuple[int, int, int], tuple[int, int, int, int]], object] | None = None
    for a in range(2, bound + 1):
        for c in range(1, a + 1):
            for b in range(1, a):
                for d in range(1, c):
                    if a * d + b * c <= a * c:
                        continue
                    strictly_convex += 1
                    counts = profile(a, b, c, d)
                    if counts[0] > 3:
                        continue
                    axial_x_at_most_three += 1
                    key = (max(counts), sum(counts), counts, (a, b, c, d))
                    if best is None or key < best[0]:
                        best = (key, {"A": a, "B": b, "C": c, "D": d, "Profile": list(counts)})
                    if counts[1] <= 3:
                        both_axial_at_most_three += 1
                    if max(counts) < 4:
                        counterexamples += 1
    return {
        "bound": bound,
        "strictly_convex_full_tuple_count": strictly_convex,
        "strictly_convex_candidates": axial_x_at_most_three,
        "both_axial_orbits_at_most_three": both_axial_at_most_three,
        "counterexamples": counterexamples,
        "best": None if best is None else best[1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    result = brute(int(reference["bound"]))
    for key in (
        "strictly_convex_candidates",
        "both_axial_orbits_at_most_three",
        "counterexamples",
        "best",
    ):
        assert result[key] == reference[key], (key, result[key], reference[key])
    payload = {"reference": str(args.reference), "matches": True, "audit": result}
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
