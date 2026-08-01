#!/usr/bin/env python3
"""Independent exact checker for the weak and strong forms of Erdos 699.

This deliberately uses Python's arbitrary-precision binomial coefficients and
Euclid gcd.  It is slow, but it is structurally independent of the Kummer
checker in ``kummer_search.cpp`` and is useful as a reference implementation.
"""

from __future__ import annotations

import argparse
import json
import math
import time


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (
                (limit - p * p) // p + 1
            )
    return [p for p in range(2, limit + 1) if sieve[p]]


def scan(max_n: int) -> dict[str, object]:
    primes = primes_through(max_n)
    weak_counterexamples: list[tuple[int, int, int, int]] = []
    strong_exceptions: list[tuple[int, int, int, int]] = []
    pairs = 0
    started = time.perf_counter()

    for n in range(1, max_n + 1):
        half = n // 2
        row = [math.comb(n, k) for k in range(half + 1)]
        row_primes = [p for p in primes if p <= n]
        for i in range(1, half):
            weak_candidates = [p for p in row_primes if p >= i and row[i] % p == 0]
            strong_candidates = [p for p in weak_candidates if p > i]
            for j in range(i + 1, half + 1):
                pairs += 1
                has_weak = any(row[j] % p == 0 for p in weak_candidates)
                if not has_weak:
                    g = math.gcd(row[i], row[j])
                    weak_counterexamples.append((n, i, j, g))
                    return {
                        "max_n": max_n,
                        "pairs": pairs,
                        "weak_counterexamples": weak_counterexamples,
                        "strong_exceptions": strong_exceptions,
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                has_strong = any(row[j] % p == 0 for p in strong_candidates)
                if not has_strong:
                    g = math.gcd(row[i], row[j])
                    strong_exceptions.append((n, i, j, g))

    return {
        "max_n": max_n,
        "pairs": pairs,
        "weak_counterexamples": weak_counterexamples,
        "strong_exceptions": strong_exceptions,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=300)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = scan(args.max_n)
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")


if __name__ == "__main__":
    main()
