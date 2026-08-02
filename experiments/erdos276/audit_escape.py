#!/usr/bin/env python3
"""Exact audit of the Ismailescu--Son candidate for Erdős problem 276.

The script verifies their finite compositeness data and the concrete repeated-
modulus obstruction to applying modern *distinct* covering-system theorems.
It does not claim to prove the required infinite escape property.
"""

from __future__ import annotations

import json
import math

import sympy


Q = int(
    "12951150255508108245872399074061259209531943793351"
    "2025195406541068394745828231264515958532145970461367703231950382110924410768870"
)

# (prime, Fibonacci index m used in the paper, covered residue, c, q mod prime)
ROWS = [
    (2, 3, 1, 1, 0), (5, 5, 1, 2, 0), (13, 7, 1, 5, 0),
    (17, 9, 3, 11, 11), (29, 14, 2, 5, 20), (41, 20, 4, 3, 34),
    (61, 15, 2, 41, 55), (181, 90, 8, 46, 149),
    (241, 120, 14, 109, 134), (281, 28, 4, 207, 45),
    (421, 21, 3, 171, 140), (541, 90, 38, 243, 307),
    (1009, 126, 90, 294, 818), (1601, 80, 34, 1259, 1347),
    (2161, 40, 10, 1706, 799), (2521, 60, 20, 636, 1934),
    (3041, 80, 74, 790, 455), (8641, 360, 18, 4664, 1277),
    (20641, 120, 110, 1405, 13565), (31249, 126, 42, 901, 24574),
    (103681, 72, 54, 80856, 22094), (109441, 45, 23, 16635, 43164),
    (141961, 35, 12, 12156, 112001),
    (721561, 420, 180, 529617, 170379),
    (1461601, 252, 186, 970625, 442479),
    (35239681, 63, 6, 25860534, 5419606),
    (764940961, 252, 0, 562105967, 483887978),
    (8288823481, 105, 33, 83463210, 6095337569),
    (10783342081, 180, 162, 7785411056, 54018520),
    (571385160581761, 504, 222, 49367403415248, 504780818763137),
]


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_mod(n: int, modulus: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % modulus
    return a


def sequence_term(n: int, modulus: int | None = None) -> int:
    a = 1 + Q * Q
    b = Q * Q + 2 * Q
    if modulus is not None:
        a %= modulus
        b %= modulus
    for _ in range(n):
        a, b = b, a + b
        if modulus is not None:
            b %= modulus
    return a


def fibonacci_rank(prime: int) -> int:
    a, b = 0, 1
    for n in range(1, 2 * prime + 3):
        a, b = b, (a + b) % prime
        if a == 0:
            return n
    raise AssertionError(f"rank search failed for {prime}")


def first_sequence_zero(prime: int) -> int:
    a = sequence_term(0, prime)
    b = sequence_term(1, prime)
    if a == 0:
        return 0
    for n in range(1, 2 * prime + 3):
        a, b = b, (a + b) % prime
        if a == 0:
            return n
    raise AssertionError(f"zero search failed for {prime}")


def main() -> None:
    a0 = 1 + Q * Q
    a1 = Q * Q + 2 * Q
    assert len(str(Q)) == 129
    assert math.gcd(a0, a1) == 1

    for prime, rank, residue, coefficient, q_residue in ROWS:
        assert sympy.isprime(prime)
        assert fib_mod(rank, prime) == 0
        assert Q % prime == q_residue
        assert a0 % prime == coefficient * fib_mod(rank - residue, prime) % prime
        assert a1 % prime == coefficient * fib_mod(rank - residue + 1, prime) % prime

    period = math.lcm(*(rank for _, rank, _, _, _ in ROWS))
    assert period == 5040
    uncovered_even = [
        n for n in range(0, period, 2)
        if not any(n % rank == residue for _, rank, residue, _, _ in ROWS)
    ]
    assert not uncovered_even

    covering_product = math.prod(prime for prime, *_ in ROWS)
    assert math.gcd(sequence_term(5), covering_product) == 1

    # On n = 27 + 5040t there is no modulus-one class from any prime:
    # a shared prime divisor of a_27 and F_5040 would be exactly such a class.
    gcd_a27_f5040 = math.gcd(sequence_term(27), fib(5040))
    assert gcd_a27_f5040 == 1

    duplicate_data = []
    for prime in (103, 1951, 3329):
        assert sympy.isprime(prime)
        rank = fibonacci_rank(prime)
        zero = first_sequence_zero(prime)
        assert sequence_term(zero, prime) == 0
        induced = rank // math.gcd(rank, 5040)
        solutions = [
            t for t in range(induced)
            if (27 + 5040 * t - zero) % rank == 0
        ]
        assert len(solutions) == 1
        duplicate_data.append({
            "prime": prime,
            "zero_class": zero,
            "fibonacci_rank": rank,
            "induced_modulus": induced,
            "induced_residue": solutions[0],
        })
    assert {row["induced_modulus"] for row in duplicate_data} == {13}
    assert {row["induced_residue"] for row in duplicate_data} == {2, 10, 11}

    odd_discriminant_quarter = a0 * a0 + a0 * a1 - a1 * a1
    parameter_square = (1 + Q - Q * Q) ** 2
    assert odd_discriminant_quarter == parameter_square

    print(json.dumps({
        "problem": 276,
        "status": "candidate_compositeness_verified_escape_unproved",
        "q_digits": len(str(Q)),
        "seed_gcd": math.gcd(a0, a1),
        "covering_rows": len(ROWS),
        "covering_period": period,
        "uncovered_even_residues": uncovered_even,
        "gcd_a5_covering_product": math.gcd(sequence_term(5), covering_product),
        "gcd_a27_f5040": gcd_a27_f5040,
        "repeated_induced_modulus": duplicate_data,
        "opposite_discriminants": {
            "odd_quarter": str(odd_discriminant_quarter),
            "even_quarter": str(-odd_discriminant_quarter),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
