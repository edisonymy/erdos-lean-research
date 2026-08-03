#!/usr/bin/env python3
"""Exact finite-pool obstruction to the common-shear lift for Erdős #203.

For a linear prime map, 3 = 2^e (mod q), so its fibre is a congruence in
the single sheared coordinate k + e*l.  A family obtained by transplanting
one one-dimensional covering system with one common shear E can use the map
only if E = e (mod ord_q(2)).  Reducing E modulo 12 gives a cheap exact
upper bound on the reciprocal density of every such compatible family.

The input is the audited 281-map pool serialized by the independent census
lane.  All arithmetic in the bound is rational; no optimizer is trusted.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coarse-modulus", type=int, default=12)
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    maps = source["prime_maps"]
    linear: list[dict[str, int]] = []
    for prime_map in maps:
        h = int(prime_map["group_size"])
        a = int(prime_map["a"])
        b = int(prime_map["b"])
        # ord_q(2)=h iff a is a unit modulo h.  This is equivalent to
        # 3 belonging to <2>, and then e=b/a is the unique discrete log.
        if math.gcd(a, h) != 1:
            continue
        e = (b * pow(a, -1, h)) % h
        q = int(prime_map["q"])
        if pow(2, e, q) != 3 % q:
            raise AssertionError(f"bad linear-map discrete log at q={q}")
        linear.append({"q": q, "h": h, "e": e})

    modulus = args.coarse_modulus
    rows: list[dict[str, object]] = []
    for residue in range(modulus):
        compatible = [
            item
            for item in linear
            if (residue - item["e"]) % math.gcd(modulus, item["h"]) == 0
        ]
        density = sum((Fraction(1, item["h"]) for item in compatible), Fraction())
        rows.append(
            {
                "residue": residue,
                "compatible_map_count": len(compatible),
                "density_numerator": density.numerator,
                "density_denominator": density.denominator,
                "density_decimal": float(density),
                "compatible_primes": [item["q"] for item in compatible],
            }
        )

    maximum = max(
        Fraction(row["density_numerator"], row["density_denominator"])
        for row in rows
    )
    maximizing = [
        row["residue"]
        for row in rows
        if Fraction(row["density_numerator"], row["density_denominator"]) == maximum
    ]
    if maximum >= 1:
        raise AssertionError("coarse density bound did not obstruct a cover")

    result = {
        "problem": "Erdos #203 common-shear finite-pool obstruction",
        "input": str(args.input),
        "input_map_count": len(maps),
        "linear_map_count": len(linear),
        "linear_density_numerator": sum(
            (Fraction(1, item["h"]) for item in linear), Fraction()
        ).numerator,
        "linear_density_denominator": sum(
            (Fraction(1, item["h"]) for item in linear), Fraction()
        ).denominator,
        "coarse_modulus": modulus,
        "rows": rows,
        "maximum_density_numerator": maximum.numerator,
        "maximum_density_denominator": maximum.denominator,
        "maximum_density_decimal": float(maximum),
        "maximizing_residues": maximizing,
        "verified_strictly_below_one": maximum < 1,
        "scope": (
            "This exactly rules out a common-shear one-dimensional lift using "
            "the audited input pool. It does not rule out mixed-shear covers, "
            "larger prime pools, or the full one-prime-one-fibre CRT ansatz."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "linear_maps": len(linear),
                "max_density": float(maximum),
                "maximizing_residues": maximizing,
                "pass": maximum < 1,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
