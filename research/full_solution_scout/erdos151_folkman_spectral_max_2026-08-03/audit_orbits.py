#!/usr/bin/env python3
"""Independent completeness audit for the three Cayley orbit enumerations."""

from __future__ import annotations

import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scan_abelian_n50 as ab50  # noqa: E402
import scan_circulants_n50 as cy50  # noqa: E402
import scan_circulants_n59 as cy59  # noqa: E402


SCHEMA = "erdos151-cayley-orbit-audit-v1"


def audit_cyclic_50() -> dict:
    raw: set[tuple[int, ...]] = set()
    paired = range(1, 25)
    for use_opposite in (False, True):
        maximum = 5 if not use_opposite else 4
        for size in range(maximum + 1):
            for combo in itertools.combinations(paired, size):
                steps = combo + ((25,) if use_opposite else ())
                if steps and math.gcd(50, *steps) == 1:
                    raw.add(steps)
    canonical = {cy50.canonical_steps(steps) for steps in raw}
    generator = set(cy50.all_orbit_representatives())
    if canonical != generator:
        raise AssertionError("cyclic-50 orbit representatives are incomplete")
    result = json.loads((HERE / "scan_circulants_n50.result.json").read_text(encoding="utf-8"))
    if result["counters"]["orbits_tested"] != len(generator):
        raise AssertionError("cyclic-50 result count mismatch")
    return {
        "raw_connected_connection_sets": len(raw),
        "multiplier_orbits": len(generator),
        "unit_count": len(cy50.UNITS),
        "result_orbits_tested": result["counters"]["orbits_tested"],
        "complete": True,
    }


def audit_abelian_50() -> dict:
    if len(ab50.GL2) != 480 or len(set(ab50.GL2)) != 480:
        raise AssertionError("GL(2,5) order mismatch")
    if any(sorted(perm) != list(range(24)) for perm in ab50.ACTION_PERMS):
        raise AssertionError("a GL(2,5) action is not a permutation")

    expected: set[tuple[bool, tuple[int, ...]]] = set()
    for use_involution in (False, True):
        maximum = 5 if not use_involution else 4
        for size in range(maximum + 1):
            for combo in itertools.combinations(range(24), size):
                if combo or use_involution:
                    expected.add((use_involution, combo))

    representatives = list(ab50.all_orbit_representatives())
    owner: dict[tuple[bool, tuple[int, ...]], tuple[bool, tuple[int, ...]]] = {}
    for representative in representatives:
        use_involution, combo = representative
        orbit = {
            (use_involution, image)
            for image in ab50.orbit_images(combo)
        }
        for item in orbit:
            prior = owner.setdefault(item, representative)
            if prior != representative:
                raise AssertionError("two abelian representatives share an orbit")
    if set(owner) != expected:
        raise AssertionError("abelian-50 orbit union does not cover the raw family")

    connected_reps = []
    raw_connected = 0
    for item in expected:
        use_involution, combo = item
        if ab50.connected(ab50.adjacency(use_involution, combo)):
            raw_connected += 1
    for representative in representatives:
        use_involution, combo = representative
        if ab50.connected(ab50.adjacency(use_involution, combo)):
            connected_reps.append(representative)
    result = json.loads((HERE / "scan_abelian_n50.result.json").read_text(encoding="utf-8"))
    if result["counters"]["connected_orbits_tested"] != len(connected_reps):
        raise AssertionError("abelian-50 connected orbit count mismatch")
    return {
        "raw_nonempty_connection_sets": len(expected),
        "raw_connected_connection_sets": raw_connected,
        "gl2_order": len(ab50.GL2),
        "all_orbits": len(representatives),
        "connected_orbits": len(connected_reps),
        "disconnected_orbits": len(representatives) - len(connected_reps),
        "result_connected_orbits_tested": result["counters"]["connected_orbits_tested"],
        "complete": True,
    }


def audit_cyclic_59() -> dict:
    raw = {
        combo
        for size in range(1, 6)
        for combo in itertools.combinations(range(1, 30), size)
    }
    canonical = {cy59.canonical_steps(steps) for steps in raw}
    generator = set(cy59.all_orbit_representatives())
    if canonical != generator:
        raise AssertionError("cyclic-59 orbit representatives are incomplete")
    result = json.loads((HERE / "scan_circulants_n59.result.json").read_text(encoding="utf-8"))
    if result["counters"]["orbits_tested"] != len(generator):
        raise AssertionError("cyclic-59 result count mismatch")
    return {
        "raw_connection_sets": len(raw),
        "multiplier_orbits": len(generator),
        "unit_count": len(cy59.UNITS),
        "result_orbits_tested": result["counters"]["orbits_tested"],
        "complete": True,
    }


def main() -> int:
    output = {
        "schema": SCHEMA,
        "cyclic_50": audit_cyclic_50(),
        "abelian_50": audit_abelian_50(),
        "cyclic_59": audit_cyclic_59(),
        "method": {
            "cyclic": "enumerate every raw step set and compare its multiplier-canonical image set with the scan generator",
            "abelian": "form every raw inverse-closed connection set and verify that the disjoint union of all GL(2,5) representative orbits equals it",
        },
    }
    path = HERE / "audit_orbits.result.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
