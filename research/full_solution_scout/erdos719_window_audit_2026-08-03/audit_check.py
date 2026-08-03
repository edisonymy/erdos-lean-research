#!/usr/bin/env python3
"""Definition-level checks for the Erdős #719 n=9 window reduction.

This script is deliberately solver-free.  It checks the explicit SQS(10),
the derived 18-tetrahedron packing on nine vertices, every integer window
calculation, and the numerical pair-energy bounds used in the audit report.
"""

from __future__ import annotations

import itertools
import json
import math


V9 = tuple(range(9))
V10 = tuple(range(10))
TRIPLES9 = tuple(itertools.combinations(V9, 3))
FOURSETS9 = tuple(itertools.combinations(V9, 4))

# The twelve triples of the affine plane AG(2,3), in row-major point labels.
AFFINE_LINES = (
    (0, 1, 2), (0, 3, 6), (0, 4, 8), (0, 5, 7),
    (1, 3, 8), (1, 4, 7), (1, 5, 6), (2, 3, 7),
    (2, 4, 6), (2, 5, 8), (3, 4, 5), (6, 7, 8),
)

# Blocks not containing infinity in an SQS(10).  Their 72 constituent
# triples are pairwise distinct, so these are 18 edge-disjoint K_4^(3)s.
PACKING18 = (
    (0, 1, 3, 4), (0, 1, 5, 8), (0, 1, 6, 7),
    (0, 2, 3, 5), (0, 2, 4, 7), (0, 2, 6, 8),
    (0, 3, 7, 8), (0, 4, 5, 6), (1, 2, 3, 6),
    (1, 2, 4, 5), (1, 2, 7, 8), (1, 3, 5, 7),
    (1, 4, 6, 8), (2, 3, 4, 8), (2, 5, 6, 7),
    (3, 4, 6, 7), (3, 5, 6, 8), (4, 5, 7, 8),
)


def minimum_pair_energy(h: int) -> tuple[int, tuple[int, ...]]:
    """Minimise sum C(d,2) for 36 nonnegative integers summing to 3h."""
    quotient, remainder = divmod(3 * h, 36)
    degrees = (quotient,) * (36 - remainder) + (quotient + 1,) * remainder
    energy = sum(math.comb(d, 2) for d in degrees)
    return energy, degrees


def check_sqs() -> dict[str, object]:
    assert len(set(AFFINE_LINES)) == 12
    assert all(tuple(sorted(line)) == line and len(line) == 3 for line in AFFINE_LINES)
    assert len(set(PACKING18)) == 18
    assert all(tuple(sorted(block)) == block and len(block) == 4 for block in PACKING18)

    packing_triples = [
        triple
        for block in PACKING18
        for triple in itertools.combinations(block, 3)
    ]
    assert len(packing_triples) == 72
    assert len(set(packing_triples)) == 72
    uncovered = set(TRIPLES9) - set(packing_triples)
    assert uncovered == set(AFFINE_LINES)

    infinity_blocks = tuple(tuple(sorted((*line, 9))) for line in AFFINE_LINES)
    sqs_blocks = PACKING18 + infinity_blocks
    assert len(sqs_blocks) == 30
    counts = {triple: 0 for triple in itertools.combinations(V10, 3)}
    for block in sqs_blocks:
        for triple in itertools.combinations(block, 3):
            counts[triple] += 1
    assert set(counts.values()) == {1}

    return {
        "packing_block_count": len(PACKING18),
        "packing_covered_triples": len(set(packing_triples)),
        "packing_uncovered_triples": [list(x) for x in sorted(uncovered)],
        "sqs_block_count": len(sqs_blocks),
        "sqs_triple_count": len(counts),
        "sqs_all_triples_exactly_once": True,
    }


def check_window() -> dict[str, object]:
    # A counterexample has h+3k <= 29.  Packing-one reduction gives
    # h+4k >= 31.  The 18-packing/averaging argument gives h >= 17.
    raw_window = []
    for h in range(85):
        for k in range(19):
            if h + 3 * k <= 29 and h + 4 * k >= 31 and h >= 17:
                raw_window.append((84 - h, k, h))
    assert raw_window == [(67, 4, 17), (65, 3, 19), (64, 3, 20), (61, 2, 23)]

    # If h <= 16, union-bound the number q of present tetrahedra by
    # q >= 126-6h.  Averaging an 18-packing gives q <= 7k.
    dense_rows = []
    for h in range(17):
        k_upper = (29 - h) // 3
        q_lower = 126 - 6 * h
        gap = q_lower - 7 * k_upper
        assert gap > 0
        dense_rows.append({
            "h": h,
            "m": 84 - h,
            "k_upper": k_upper,
            "q_lower": q_lower,
            "q_lower_minus_7k_upper": gap,
        })

    # Pair-energy improvement at the two boundary pairs.
    energy_rows = []
    for h, k, expected_energy, expected_q_lower in ((17, 4, 15, 32), (19, 3, 21, 23)):
        energy, degrees = minimum_pair_energy(h)
        q_lower = 126 - 6 * h + math.ceil(energy / 2)
        assert energy == expected_energy
        assert q_lower == expected_q_lower
        assert q_lower > 7 * k
        energy_rows.append({
            "h": h,
            "m": 84 - h,
            "k": k,
            "balanced_pair_codegrees": list(degrees),
            "minimum_pair_energy": energy,
            "present_tetrahedra_lower_bound": q_lower,
            "packing_average_upper_bound_7k": 7 * k,
            "contradiction_gap": q_lower - 7 * k,
        })

    survivors = [row for row in raw_window if (row[2], row[1]) not in {(17, 4), (19, 3)}]
    assert survivors == [(64, 3, 20), (61, 2, 23)]
    return {
        "raw_window_m_k_h": [list(row) for row in raw_window],
        "dense_exclusion_rows": dense_rows,
        "pair_energy_exclusions": energy_rows,
        "survivors_m_k_h": [list(row) for row in survivors],
    }


def count_four_packings() -> int:
    """Count unordered sets of four pairwise edge-disjoint tetrahedra."""
    compatible = [
        [len(set(a) & set(b)) <= 2 for b in FOURSETS9]
        for a in FOURSETS9
    ]
    count = 0
    for i in range(126):
        for j in range(i + 1, 126):
            if not compatible[i][j]:
                continue
            for k in range(j + 1, 126):
                if not (compatible[i][k] and compatible[j][k]):
                    continue
                for ell in range(k + 1, 126):
                    if compatible[i][ell] and compatible[j][ell] and compatible[k][ell]:
                        count += 1
    assert count == 3_321_675
    return count


def main() -> None:
    report = {
        "schema": "erdos719-window-audit-check-v1",
        "sqs_and_packing": check_sqs(),
        "window": check_window(),
        "exact64_four_packing_constraint_count": count_four_packings(),
        "status": "PASS",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
