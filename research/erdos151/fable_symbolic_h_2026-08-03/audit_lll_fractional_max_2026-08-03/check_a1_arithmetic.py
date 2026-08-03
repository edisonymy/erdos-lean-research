#!/usr/bin/env python3
"""Independent arithmetic checks for Program Alpha's A1/A1.1 chain.

This script is deliberately independent of the campaign's graph-search code.
It checks only finite numerical implications whose mathematical proofs are
spelled out in AUDIT_REPORT.md; it is not a substitute for those proofs.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "PROGRAM_ALPHA.md"
LOG = ROOT / "RESEARCH_LOG.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def a1_k(t_max: int) -> int:
    if t_max < 0:
        raise ValueError("t_max must be nonnegative")
    return math.ceil(math.sqrt(3.0 * math.e * t_max)) + 1


def lll_ratio(t_max: int) -> float:
    """The symmetric-LLL left side e p (D+1), using D=3(t-1)."""
    if t_max < 1:
        raise ValueError("the no-triangle case has no bad events")
    k = a1_k(t_max)
    return math.e * (3 * t_max - 2) / (k * k)


def exact_forced_t_lower(n: int, h: int) -> int:
    """Integer consequence of beta<=h-1 and beta>=n/a1_k(t).

    If q=ceil(n/(h-1)), then ceil(sqrt(3 e t))+1 >= q, hence
    sqrt(3 e t)>q-2.  Thus t> (q-2)^2/(3e), and the returned integer is
    the least integer satisfying that strict lower bound.
    """
    if h < 2 or n < 1:
        raise ValueError("need h>=2 and n>=1")
    q = math.ceil(n / (h - 1))
    if q <= 1:
        return 0
    strict_floor = (q - 2) ** 2 / (3.0 * math.e)
    return math.floor(strict_floor) + 1


def check_fractional_averaging_sanity(seed: int = 151) -> dict[str, int]:
    """Random finite-set sanity checks of the double-counting identity.

    Families are forced to contain every singleton, so every vertex has
    positive marginal.  For a distribution mu and p=min_v Pr(v in S),
    x_S=mu(S)/p is checked to be a fractional cover of total weight 1/p,
    and max |S| >= n p is checked.  This is arithmetic corroboration only.
    """
    rng = random.Random(seed)
    trials = 0
    for n in range(1, 9):
        universe = range(n)
        for _ in range(250):
            family = [{v} for v in universe]
            for mask in range(1, 1 << n):
                if rng.random() < 0.15:
                    family.append({v for v in universe if mask & (1 << v)})
            raw = [rng.random() + 1e-9 for _ in family]
            total = sum(raw)
            mu = [x / total for x in raw]
            marginals = [
                sum(weight for weight, subset in zip(mu, family) if v in subset)
                for v in universe
            ]
            p = min(marginals)
            scaled = [weight / p for weight in mu]
            coverages = [
                sum(weight for weight, subset in zip(scaled, family) if v in subset)
                for v in universe
            ]
            weighted_size = sum(
                weight * len(subset) for weight, subset in zip(scaled, family)
            )
            assert min(coverages) >= 1.0 - 1e-11
            assert abs(weighted_size - sum(coverages)) <= 1e-9 * max(1, n)
            assert max(map(len, family)) + 1e-11 >= n * p
            assert abs(sum(scaled) - 1.0 / p) <= 1e-9 * max(1.0, 1.0 / p)
            trials += 1
    return {"seed": seed, "trials": trials}


def main() -> None:
    scan_limit = 1_000_000
    ratios = [(lll_ratio(t), t) for t in range(1, scan_limit + 1)]
    max_ratio, argmax = max(ratios)
    assert max_ratio < 1.0

    # The published +1 is redundant for t>=1: ceil(sqrt(3 e t)) already
    # makes e(3t-2)/k^2 < 1.  Verify that finite sharpening on the scan.
    no_plus_one_max = 0.0
    no_plus_one_argmax = 0
    for t in range(1, scan_limit + 1):
        k0 = math.ceil(math.sqrt(3.0 * math.e * t))
        ratio = math.e * (3 * t - 2) / (k0 * k0)
        if ratio > no_plus_one_max:
            no_plus_one_max = ratio
            no_plus_one_argmax = t
    assert no_plus_one_max < 1.0

    # Finite inversion checks: the returned lower bound must be incompatible
    # with every smaller t whenever beta<=h-1 is combined with n/k<=h-1.
    inversion_cases = 0
    for h in range(4, 501):
        for multiplier in (0.25, 0.5, 0.75, 1.0):
            n = max(1, math.floor(multiplier * h * h / max(1.0, math.log(h))))
            lower = exact_forced_t_lower(n, h)
            for t in range(0, lower):
                assert a1_k(t) < math.ceil(n / (h - 1))
            inversion_cases += 1

    sqrt_3e = math.sqrt(3.0 * math.e)
    result = {
        "status": "PASS",
        "scope": "finite arithmetic corroboration of A1/A1.1 and A4.1 scaling",
        "source_sha256": {
            "PROGRAM_ALPHA.md": sha256(PROGRAM),
            "RESEARCH_LOG.md": sha256(LOG),
            "check_a1_arithmetic.py": sha256(Path(__file__).resolve()),
        },
        "a1": {
            "scan_t_max_inclusive": scan_limit,
            "published_k_max_lll_ratio": max_ratio,
            "published_k_argmax_t": argmax,
            "without_redundant_plus_one_max_lll_ratio": no_plus_one_max,
            "without_redundant_plus_one_argmax_t": no_plus_one_argmax,
        },
        "constants": {
            "sqrt_3e": sqrt_3e,
            "one_over_3e": 1.0 / (3.0 * math.e),
            "forced_coefficient_at_ramsey_half": 0.25 / (3.0 * math.e),
            "program_rounded_coefficient": (0.5 / 2.86) ** 2,
        },
        "finite_inversion_cases": inversion_cases,
        "fractional_averaging": check_fractional_averaging_sanity(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
