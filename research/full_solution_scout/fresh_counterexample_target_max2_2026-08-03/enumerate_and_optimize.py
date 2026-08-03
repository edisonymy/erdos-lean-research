#!/usr/bin/env python3
"""Complete small-image-order census and sampled phase search for Erdős #203.

The factor census is exact.  The phase search is heuristic: a sampled zero is
never reported as a cover and must pass a separate exhaustive/hierarchical
checker before promotion.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import sympy as sp


@dataclass(frozen=True)
class PrimeMap:
    q: int
    group_size: int
    primitive_root: int
    exponent_gcd: int
    a: int
    b: int
    source: str

    def label_array(self, ks: np.ndarray, ells: np.ndarray) -> np.ndarray:
        # The coordinates are kept below 2^61 and the coefficients/order below
        # 10^6 in the runs recorded here, so signed int64 multiplication is safe.
        return (
            (self.a * (ks % self.group_size)
             + self.b * (ells % self.group_size))
            % self.group_size
        )


def direction(q: int, source: str) -> PrimeMap:
    root = int(sp.primitive_root(q))
    e2 = int(sp.discrete_log(q, 2, root))
    e3 = int(sp.discrete_log(q, 3, root))
    d = math.gcd(q - 1, e2, e3)
    r = (q - 1) // d
    result = PrimeMap(q, r, root, d, e2 // d, e3 // d, source)
    assert math.gcd(r, result.a, result.b) == 1
    assert pow(root, d * result.a, q) == 2 % q
    assert pow(root, d * result.b, q) == 3 % q
    return result


def exact_factor_census(max_order: int) -> tuple[dict[int, PrimeMap], list[dict]]:
    primes: dict[int, PrimeMap] = {}
    audit: list[dict] = []
    for r in range(1, max_order + 1):
        g = math.gcd((1 << r) - 1, pow(3, r) - 1)
        factors = {int(p): int(e) for p, e in sp.factorint(g).items()}
        reconstructed = math.prod(p**e for p, e in factors.items())
        if reconstructed != g or any(not sp.isprime(p) for p in factors):
            raise AssertionError(f"incomplete factorisation at r={r}")
        audit.append(
            {
                "r": r,
                "gcd": str(g),
                "factors": {str(p): e for p, e in sorted(factors.items())},
                "reconstruction_pass": True,
            }
        )
        for q in factors:
            if q <= 3:
                continue
            order = math.lcm(int(sp.n_order(2, q)), int(sp.n_order(3, q)))
            if order <= max_order and q not in primes:
                primes[q] = direction(q, "complete_order_census")
                if primes[q].group_size != order:
                    raise AssertionError("direction/order disagreement")
    return primes, audit


def independent_prime_scan(max_order: int, limit: int) -> set[int]:
    found: set[int] = set()
    for q0 in sp.primerange(5, limit + 1):
        q = int(q0)
        order = math.lcm(int(sp.n_order(2, q)), int(sp.n_order(3, q)))
        if order <= max_order:
            found.add(q)
    return found


def legacy_period_pool(period: int, prime_limit: int) -> dict[int, PrimeMap]:
    maps: dict[int, PrimeMap] = {}
    for q0 in sp.primerange(5, prime_limit + 1):
        q = int(q0)
        if pow(2, period, q) == 1 and pow(3, period, q) == 1:
            pm = direction(q, "legacy_period_pool")
            if period % pm.group_size:
                raise AssertionError("legacy order does not divide period")
            maps[q] = pm
    return maps


def prime_divisors(n: int) -> list[int]:
    return sorted(int(p) for p in sp.factorint(n))


def legal_phases(pm: PrimeMap, power: int) -> np.ndarray:
    if power == 1:
        return np.arange(pm.group_size, dtype=np.int64)
    g = math.gcd(power, pm.q - 1)
    values = [t for t in range(pm.group_size) if (pm.exponent_gcd * t) % g == 0]
    if not values:
        raise AssertionError("phase zero must always be legal for odd powers")
    return np.asarray(values, dtype=np.int64)


def algebraic_mask(ks: np.ndarray, ells: np.ndarray, power: int) -> np.ndarray:
    mask = np.zeros(len(ks), dtype=bool)
    if power == 1:
        return mask
    for p in prime_divisors(power):
        if p == 2:
            raise ValueError("only odd-power variants are definitionally justified here")
        mask |= ((ks % p) == 0) & ((ells % p) == 0)
    return mask


def optimize(
    maps: list[PrimeMap],
    ks: np.ndarray,
    ells: np.ndarray,
    power: int,
    restarts: int,
    sweeps: int,
    rng: np.random.Generator,
) -> dict:
    max_r = max(pm.group_size for pm in maps)
    dtype = np.uint16 if max_r < 2**16 else np.uint32
    labels = np.empty((len(maps), len(ks)), dtype=dtype)
    for i, pm in enumerate(maps):
        labels[i] = pm.label_array(ks, ells).astype(dtype)
    allowed = [legal_phases(pm, power) for pm in maps]
    auto = algebraic_mask(ks, ells, power)
    best_uncovered = len(ks) + 1
    best_phases: list[int] | None = None
    trace: list[dict] = []
    for restart in range(restarts):
        phases = [int(a[rng.integers(len(a))]) for a in allowed]
        counts = np.zeros(len(ks), dtype=np.int16)
        for i, phase in enumerate(phases):
            counts += labels[i] == phase
        current = int(np.count_nonzero((counts == 0) & ~auto))
        start_value = current
        used_sweeps = 0
        for sweep in range(sweeps):
            changed = False
            for i0 in rng.permutation(len(maps)):
                i = int(i0)
                old = phases[i]
                counts -= labels[i] == old
                needs = (counts == 0) & ~auto
                freq = np.bincount(
                    labels[i, needs].astype(np.int64),
                    minlength=maps[i].group_size,
                )
                choices = allowed[i]
                new = int(choices[int(np.argmax(freq[choices]))])
                phases[i] = new
                counts += labels[i] == new
                now = int(np.count_nonzero((counts == 0) & ~auto))
                if new != old:
                    changed = True
                if now > current:
                    raise AssertionError("coordinate step increased uncovered count")
                current = now
            used_sweeps = sweep + 1
            if current < best_uncovered:
                best_uncovered = current
                best_phases = phases.copy()
            if not changed or current == 0:
                break
        trace.append(
            {
                "restart": restart,
                "start_uncovered": start_value,
                "final_uncovered": current,
                "sweeps": used_sweeps,
            }
        )
        if best_uncovered == 0:
            break
    assert best_phases is not None
    return {
        "power": power,
        "power_prime_divisors": prime_divisors(power) if power > 1 else [],
        "automatic_sample_fraction": float(np.count_nonzero(auto) / len(auto)),
        "best_sample_uncovered": best_uncovered,
        "best_sample_uncovered_fraction": best_uncovered / len(ks),
        "best_phases": best_phases,
        "legal_phase_counts": [len(x) for x in allowed],
        "trace": trace,
        "scope_warning": "HEURISTIC SAMPLE ONLY; zero would require exact cover checking",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-order", type=int, default=1000)
    parser.add_argument("--legacy-period", type=int, default=720720)
    parser.add_argument("--legacy-prime-limit", type=int, default=1_000_000)
    parser.add_argument("--samples", type=int, default=200_000)
    parser.add_argument("--restarts", type=int, default=10)
    parser.add_argument("--sweeps", type=int, default=30)
    parser.add_argument("--powers", default="1,3,5,7,15,21,35,105,1155")
    parser.add_argument("--seed", type=int, default=203_202_608_03)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()

    census, factor_audit = exact_factor_census(args.max_order)
    largest_census_prime = max(census, default=3)
    scan = independent_prime_scan(args.max_order, largest_census_prime)
    if scan != set(census):
        raise AssertionError(
            f"independent scan mismatch: factor-only={set(census)-scan}, scan-only={scan-set(census)}"
        )
    legacy = legacy_period_pool(args.legacy_period, args.legacy_prime_limit)
    union = dict(legacy)
    for q, pm in census.items():
        union[q] = pm if q not in legacy else PrimeMap(**(asdict(pm) | {"source": "both"}))
    maps = sorted(union.values(), key=lambda pm: (pm.group_size, pm.q))

    rng = np.random.default_rng(args.seed)
    ks = rng.integers(0, 2**61, size=args.samples, dtype=np.int64)
    ells = rng.integers(0, 2**61, size=args.samples, dtype=np.int64)
    powers = [int(x) for x in args.powers.split(",") if x.strip()]
    if any(n < 1 or n % 2 == 0 for n in powers):
        raise ValueError("powers must be positive odd integers")

    searches = []
    for power in powers:
        searches.append(
            optimize(maps, ks, ells, power, args.restarts, args.sweeps, rng)
        )

    result = {
        "problem": "Erdos #203",
        "status": "sampled_phase_search_only",
        "parameters": vars(args) | {"output": str(args.output)},
        "census_completeness_argument": (
            "If |<2,3> mod q|=r<=R then q divides gcd(2^r-1,3^r-1); "
            "every such gcd was completely factored and reconstructed."
        ),
        "factor_census_count": len(census),
        "factor_census_density_sum": sum(1 / pm.group_size for pm in census.values()),
        "largest_census_prime": largest_census_prime,
        "census_primes_above_legacy_cutoff": sorted(q for q in census if q > args.legacy_prime_limit),
        "independent_prime_scan_limit": largest_census_prime,
        "independent_prime_scan_pass": True,
        "legacy_pool_count": len(legacy),
        "legacy_pool_density_sum": sum(1 / pm.group_size for pm in legacy.values()),
        "union_pool_count": len(maps),
        "union_pool_density_sum": sum(1 / pm.group_size for pm in maps),
        "prime_maps": [asdict(pm) for pm in maps],
        "factor_audit": factor_audit,
        "searches": searches,
        "elapsed_seconds": time.monotonic() - started,
        "claim_boundary": (
            "Census is exact through max_order; phase results are heuristic samples, "
            "not a cover, witness, lower bound, or solution."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "factor_census_count": result["factor_census_count"],
        "legacy_pool_count": result["legacy_pool_count"],
        "union_pool_count": result["union_pool_count"],
        "density": result["union_pool_density_sum"],
        "searches": [
            {"power": x["power"], "uncovered": x["best_sample_uncovered_fraction"]}
            for x in searches
        ],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
