#!/usr/bin/env python3
"""Hybrid algebraic/prime-fibre search for Erdos problem 203.

We impose m=A^R.  Capell's criterion applied to

    2^r 3^s X^R + 1

shows that the polynomial is reducible over Q precisely in either of the
following cases:

* some odd prime p|R divides both r and s (ordinary x^p+1);
* 4|R, r=2 (mod 4), and s=0 (mod 4) (Sophie Germain).

Those exponent cells are marked covered without a prime fibre.  On all other
cells, a prime q may be used only when the required residue

    A^R = -(2^k 3^ell)^(-1) (mod q)

is an R-th power.  The script optimizes the resulting restricted fibres on a
fixed reproducible sample.  If a sampled cover is ever found, Z3 is asked for
an exact uncovered cell on the full finite torus; UNSAT is an exact cover
certificate and causes a CRT witness for A to be emitted.

The search result remains heuristic unless ``exact_status`` is ``UNSAT``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research" / "full_solution_scout" / "search_203_cover.py"
SPEC = importlib.util.spec_from_file_location("search_203_cover", BASE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {BASE}")
BASE_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE_MODULE
SPEC.loader.exec_module(BASE_MODULE)
PrimeMap = BASE_MODULE.PrimeMap
candidate_maps = BASE_MODULE.candidate_maps


def odd_prime_divisors(n: int) -> list[int]:
    return [int(p) for p in sp.factorint(n) if p % 2]


def algebraic_mask(ks: np.ndarray, ells: np.ndarray, exponent: int) -> np.ndarray:
    covered = np.zeros(len(ks), dtype=bool)
    for prime in odd_prime_divisors(exponent):
        covered |= (ks % prime == 0) & (ells % prime == 0)
    if exponent % 4 == 0:
        covered |= (ks % 4 == 2) & (ells % 4 == 0)
    return covered


def algebraic_exact_fraction(exponent: int) -> tuple[int, int]:
    mod = algebraic_period(exponent)
    count = 0
    for k in range(mod):
        for ell in range(mod):
            if any(k % p == 0 and ell % p == 0 for p in odd_prime_divisors(exponent)):
                count += 1
            elif exponent % 4 == 0 and k % 4 == 2 and ell % 4 == 0:
                count += 1
    divisor = math.gcd(count, mod * mod)
    return count // divisor, mod * mod // divisor


def algebraic_period(exponent: int) -> int:
    return math.lcm(
        4 if exponent % 4 == 0 else 1,
        *odd_prime_divisors(exponent),
    )


def allowed_phases(prime_map: PrimeMap, exponent: int) -> list[int]:
    """Labels whose required m residue is an R-th power modulo q."""
    modulus = prime_map.q - 1
    obstruction = math.gcd(exponent, modulus)
    minus_one_exponent = modulus // 2
    return [
        label
        for label in range(prime_map.group_size)
        if (minus_one_exponent - prime_map.exponent_gcd * label) % obstruction == 0
    ]


def root_for_phase(prime_map: PrimeMap, exponent: int, phase: int) -> int:
    """Return one A with A^R = -c^-1 mod q for this fibre phase."""
    modulus = prime_map.q - 1
    target_exponent = (
        modulus // 2 - prime_map.exponent_gcd * phase
    ) % modulus
    divisor = math.gcd(exponent, modulus)
    if target_exponent % divisor:
        raise AssertionError("phase is not power-compatible")
    reduced_modulus = modulus // divisor
    reduced_exponent = exponent // divisor
    reduced_target = target_exponent // divisor
    log_a = (
        reduced_target * pow(reduced_exponent, -1, reduced_modulus)
    ) % reduced_modulus
    value = pow(prime_map.primitive_root, log_a, prime_map.q)
    c = prime_map.value(phase)
    if (pow(value, exponent, prime_map.q) * c + 1) % prime_map.q:
        raise AssertionError("bad modular R-th root")
    return value


def exact_uncovered_z3(
    maps: list[PrimeMap], phases: list[int], period: int, exponent: int
) -> dict[str, object]:
    try:
        import z3
    except ImportError:
        return {"status": "Z3_UNAVAILABLE"}
    k = z3.Int("k")
    ell = z3.Int("ell")
    solver = z3.Solver()
    solver.add(k >= 0, k < period, ell >= 0, ell < period)
    for p in odd_prime_divisors(exponent):
        solver.add(z3.Or(k % p != 0, ell % p != 0))
    if exponent % 4 == 0:
        solver.add(z3.Or(k % 4 != 2, ell % 4 != 0))
    for prime_map, phase in zip(maps, phases, strict=True):
        solver.add(
            (prime_map.a * k + prime_map.b * ell) % prime_map.group_size
            != phase
        )
    check = solver.check()
    if check == z3.unsat:
        return {"status": "UNSAT"}
    if check == z3.unknown:
        return {"status": "UNKNOWN", "reason": solver.reason_unknown()}
    model = solver.model()
    return {
        "status": "SAT",
        "uncovered_cell": [model[k].as_long(), model[ell].as_long()],
    }


def crt_a_witness(
    maps: list[PrimeMap], phases: list[int], exponent: int
) -> dict[str, object]:
    moduli = [6] + [prime_map.q for prime_map in maps]
    roots = [1] + [
        root_for_phase(prime_map, exponent, phase)
        for prime_map, phase in zip(maps, phases, strict=True)
    ]
    raw, product = sp.ntheory.modular.crt(moduli, roots, check=True)
    if raw is None:
        raise AssertionError("CRT unexpectedly inconsistent")
    a = int(raw)
    product = int(product)
    if a <= 1:
        a += product
    return {
        "A": str(a),
        "m_equals_A_pow_R": str(pow(a, exponent)),
        "R": exponent,
        "crt_modulus": str(product),
        "gcd_A_6": math.gcd(a, 6),
        "rows": [
            {
                "q": prime_map.q,
                "phase": phase,
                "A_mod_q": root,
                "check": (
                    pow(root, exponent, prime_map.q)
                    * prime_map.value(phase)
                    + 1
                )
                % prime_map.q,
            }
            for prime_map, phase, root in zip(maps, phases, roots[1:], strict=True)
        ],
    }


def optimize_one(
    exponent: int,
    all_maps: list[PrimeMap],
    labels: list[np.ndarray],
    ks: np.ndarray,
    ells: np.ndarray,
    restarts: int,
    sweeps: int,
    rng: np.random.Generator,
    period: int,
) -> dict[str, object]:
    permitted = [allowed_phases(pm, exponent) for pm in all_maps]
    selected_indices = [i for i, phases in enumerate(permitted) if phases]
    maps = [all_maps[i] for i in selected_indices]
    map_labels = [labels[i] for i in selected_indices]
    allowed = [permitted[i] for i in selected_indices]
    alg = algebraic_mask(ks, ells, exponent)
    best_uncovered = len(ks) + 1
    best_phases: list[int] | None = None
    trace: list[dict[str, int]] = []

    for restart in range(restarts):
        phases = [int(rng.choice(options)) for options in allowed]
        counts = alg.astype(np.int16)
        for label_row, phase in zip(map_labels, phases, strict=True):
            counts += label_row == phase
        restart_best = int(np.count_nonzero(counts == 0))
        for _sweep in range(sweeps):
            before_sweep = restart_best
            for i in rng.permutation(len(maps)):
                i = int(i)
                old_phase = phases[i]
                counts -= map_labels[i] == old_phase
                uncovered = counts == 0
                frequencies = np.bincount(
                    map_labels[i][uncovered].astype(np.int64),
                    minlength=maps[i].group_size,
                )
                options = allowed[i]
                option_counts = frequencies[np.asarray(options, dtype=np.int64)]
                max_count = int(option_counts.max())
                tied = [
                    option
                    for option, count in zip(options, option_counts, strict=True)
                    if int(count) == max_count
                ]
                new_phase = int(rng.choice(tied))
                phases[i] = new_phase
                counts += map_labels[i] == new_phase
                restart_best = int(np.count_nonzero(counts == 0))
            if restart_best < best_uncovered:
                best_uncovered = restart_best
                best_phases = phases.copy()
            if restart_best == 0 or restart_best >= before_sweep:
                break
        trace.append({"restart": restart, "sample_uncovered": restart_best})
        if best_uncovered == 0:
            break

    exact = None
    witness = None
    if best_uncovered == 0 and best_phases is not None:
        exact = exact_uncovered_z3(maps, best_phases, period, exponent)
        if exact["status"] == "UNSAT":
            witness = crt_a_witness(maps, best_phases, exponent)
    numerator, denominator = algebraic_exact_fraction(exponent)
    return {
        "R": exponent,
        "R_factorization": {str(p): e for p, e in sp.factorint(exponent).items()},
        "algebraic_exact_fraction": f"{numerator}/{denominator}",
        "algebraic_exact_density": numerator / denominator,
        "algebraic_sample_density": float(np.mean(alg)),
        "prime_maps_total": len(all_maps),
        "prime_maps_with_allowed_phase": len(maps),
        "allowed_phase_counts": [len(options) for options in allowed],
        "restricted_density_upper_sum": sum(1 / pm.group_size for pm in maps),
        "best_sample_uncovered": best_uncovered,
        "best_sample_uncovered_fraction": best_uncovered / len(ks),
        "best_phases": best_phases,
        "selected_prime_maps": [asdict(pm) for pm in maps],
        "exact_check_if_sample_covered": exact,
        "witness_if_exact_cover": witness,
        "trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", type=int, default=720720)
    parser.add_argument("--prime-limit", type=int, default=1_000_000)
    parser.add_argument(
        "--maps-json",
        type=Path,
        help="Reuse the top-level prime_maps array from an audited census JSON",
    )
    parser.add_argument("--samples", type=int, default=500_000)
    parser.add_argument("--restarts", type=int, default=12)
    parser.add_argument("--sweeps", type=int, default=40)
    parser.add_argument("--seed", type=int, default=203_202_608_03)
    parser.add_argument(
        "--exponents",
        type=int,
        nargs="+",
        default=[3, 4, 5, 7, 11, 12, 15, 21, 35, 60, 105, 420, 1155, 4620],
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    rng = np.random.default_rng(args.seed)
    if args.maps_json is None:
        maps = candidate_maps(args.period, args.prime_limit)
    else:
        imported = json.loads(args.maps_json.read_text(encoding="utf-8"))
        maps = [
            PrimeMap(
                q=int(row["q"]),
                group_size=int(row["group_size"]),
                primitive_root=int(row["primitive_root"]),
                exponent_gcd=int(row["exponent_gcd"]),
                a=int(row["a"]),
                b=int(row["b"]),
            )
            for row in imported["prime_maps"]
        ]
    # This is a genuine common period even when imported maps do not share the
    # legacy period or R has a new algebraic-cell modulus.
    effective_period = math.lcm(
        *(prime_map.group_size for prime_map in maps),
        *(algebraic_period(exponent) for exponent in args.exponents),
    )
    # The exact period can be hundreds of digits for a union census.  A long
    # int64 interval is used only for the heuristic sample; every label first
    # reduces the coordinate modulo its own order.  Exact checking still uses
    # the true effective_period.
    sample_coordinate_bound = min(effective_period, 2**61)
    ks = rng.integers(0, sample_coordinate_bound, size=args.samples, dtype=np.int64)
    ells = rng.integers(0, sample_coordinate_bound, size=args.samples, dtype=np.int64)
    labels = [
        (
            (
                prime_map.a * (ks % prime_map.group_size)
                + prime_map.b * (ells % prime_map.group_size)
            )
            % prime_map.group_size
        ).astype(np.uint32)
        for prime_map in maps
    ]
    results = [
        optimize_one(
            exponent,
            maps,
            labels,
            ks,
            ells,
            args.restarts,
            args.sweeps,
            rng,
            effective_period,
        )
        for exponent in args.exponents
    ]
    result = {
        "problem": "Erdos #203 algebraic-power/CRT hybrid",
        "status": (
            "EXACT_COVER"
            if any(row["witness_if_exact_cover"] is not None for row in results)
            else "NO_EXACT_COVER_FOUND"
        ),
        "parameters": vars(args)
        | {
            "output": str(args.output),
            "maps_json": str(args.maps_json) if args.maps_json else None,
        },
        "effective_common_period": str(effective_period),
        "sample_coordinate_bound": sample_coordinate_bound,
        "classification": {
            "ordinary": "p|R odd and k=l=0 (mod p): X^p+1",
            "exceptional": "4|R, k=2 (mod 4), l=0 (mod 4): 4X^4+1",
            "completeness": "Capell criterion for 2^r 3^s X^R+1 over Q",
        },
        "results": results,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "summary": [
                    {
                        "R": row["R"],
                        "alg": row["algebraic_exact_fraction"],
                        "maps": row["prime_maps_with_allowed_phase"],
                        "residual": row["best_sample_uncovered_fraction"],
                    }
                    for row in results
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
