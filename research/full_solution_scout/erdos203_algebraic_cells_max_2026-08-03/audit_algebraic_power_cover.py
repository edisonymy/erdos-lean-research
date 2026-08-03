#!/usr/bin/env python3
"""Independent finite audits for the #203 algebraic-power hybrid."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
TARGET = HERE / "search_algebraic_power_cover.py"
SPEC = importlib.util.spec_from_file_location("algebraic_power_cover", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {TARGET}")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def predicted_reducible(power: int, r: int, s: int) -> bool:
    return any(r % p == 0 and s % p == 0 for p in M.odd_prime_divisors(power)) or (
        power % 4 == 0 and r % 4 == 2 and s % 4 == 0
    )


def main() -> None:
    polynomial_checks = 0
    polynomial_mismatches = []
    x = sp.symbols("x")
    # This is an independent computer-algebra cross-check of the specialized
    # Capell classification, not the proof of its all-R completeness.
    for power in range(1, 9):
        for r in range(power):
            for s in range(power):
                actual = not sp.Poly(2**r * 3**s * x**power + 1, x).is_irreducible
                predicted = predicted_reducible(power, r, s)
                polynomial_checks += 1
                if actual != predicted:
                    polynomial_mismatches.append([power, r, s, actual, predicted])

    maps = M.candidate_maps(720720, 1_000_000)[:30]
    phase_checks = 0
    phase_mismatches = []
    root_checks = 0
    for power in [1, 3, 4, 5, 7, 12, 15, 20, 60, 105, 420]:
        for prime_map in maps:
            brute_powers = {
                pow(a, power, prime_map.q) for a in range(1, prime_map.q)
            }
            expected = [
                phase
                for phase in range(prime_map.group_size)
                if (
                    -pow(prime_map.value(phase), -1, prime_map.q)
                )
                % prime_map.q
                in brute_powers
            ]
            actual = M.allowed_phases(prime_map, power)
            phase_checks += prime_map.group_size
            if actual != expected:
                phase_mismatches.append(
                    {"R": power, "q": prime_map.q, "actual": actual, "expected": expected}
                )
            for phase in actual:
                M.root_for_phase(prime_map, power, phase)
                root_checks += 1

    density_checks = []
    for power in [1, 3, 4, 5, 7, 12, 15, 20, 28, 60, 105, 420]:
        numerator, denominator = M.algebraic_exact_fraction(power)
        period = M.algebraic_period(power)
        direct = sum(
            predicted_reducible(power, k, ell)
            for k in range(period)
            for ell in range(period)
        )
        density_checks.append(
            {
                "R": power,
                "period": period,
                "reduced_fraction": f"{numerator}/{denominator}",
                "direct_cells": direct,
                "total_cells": period * period,
                "pass": direct * denominator == numerator * period * period,
            }
        )

    result = {
        "status": "PASS"
        if not polynomial_mismatches
        and not phase_mismatches
        and all(row["pass"] for row in density_checks)
        else "FAIL",
        "polynomial_irreducibility_checks": polynomial_checks,
        "polynomial_mismatches": polynomial_mismatches,
        "phase_membership_checks": phase_checks,
        "phase_mismatches": phase_mismatches,
        "modular_root_checks": root_checks,
        "density_checks": density_checks,
        "scope": (
            "Finite independent checks. All-R completeness uses Capell's theorem "
            "and is proved in REPORT.md."
        ),
    }
    output = HERE / "audit.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
