#!/usr/bin/env python3
"""Independent exact audit for the bounded non-affine Erdős #203 lane.

The script does not use SymPy or any probabilistic primality test.  It:

* rechecks the 20 rows of Vela's retained partial-cover witness directly;
* verifies that (k,l)=(1,8) lies on none of those affine fibres; and
* verifies a complete recursive Lucas primality certificate for
  2*3^8*m+1.

Lucas criterion used below: if the complete factorisation of n-1 is known,
and one a satisfies a^(n-1)=1 (mod n) while
gcd(a^((n-1)/q)-1,n)=1 for every prime q dividing n-1, then n is prime.
The primality of every q is certified recursively by the same criterion.
"""

from __future__ import annotations

import json
import math


M = 8_168_305_011_630_835_886_634_520_238_999
K = 1
L = 8
N = 107_184_498_362_619_828_504_418_174_576_144_879


# (p, ord_2, ord_3, h, t_p, m mod p, (alpha,beta,gamma,h))
VELA_ROWS = (
    (5, 4, 4, 4, 1, 4, (1, 3, 0, 4)),
    (7, 3, 6, 6, 1, 6, (2, 1, 0, 6)),
    (11, 10, 5, 10, 1, 10, (1, 8, 0, 10)),
    (23, 11, 11, 11, 1, 22, (1, 8, 0, 11)),
    (13, 12, 3, 12, 2, 6, (1, 4, 1, 12)),
    (17, 8, 16, 16, 10, 5, (14, 1, 3, 16)),
    (19, 18, 18, 18, 8, 7, (1, 13, 3, 18)),
    (47, 23, 23, 23, 1, 46, (9, 10, 0, 23)),
    (29, 28, 28, 28, 2, 14, (1, 5, 1, 28)),
    (31, 5, 30, 30, 3, 10, (24, 1, 1, 30)),
    (71, 35, 35, 35, 49, 42, (3, 13, 1, 35)),
    (37, 36, 18, 36, 13, 17, (1, 26, 11, 36)),
    (73, 9, 12, 36, 12, 6, (4, 3, 11, 36)),
    (41, 20, 8, 40, 17, 12, (26, 15, 33, 40)),
    (43, 14, 42, 42, 28, 23, (27, 1, 5, 42)),
    (431, 43, 43, 43, 1, 430, (22, 28, 0, 43)),
    (97, 48, 48, 48, 64, 50, (17, 35, 6, 48)),
    (53, 52, 52, 52, 8, 33, (1, 17, 3, 52)),
    (59, 58, 29, 58, 1, 58, (1, 50, 0, 58)),
    (61, 60, 10, 60, 8, 38, (1, 6, 3, 60)),
)


# n -> (Lucas witness a, complete factorisation of n-1 as (q,e) pairs).
# The leaf 2 is accepted directly.
LUCAS_CERT = {
    N: (6, ((2, 1), (3, 8), (9_898_779_643_091, 1), (825_183_033_277_442_989, 1))),
    3: (2, ((2, 1),)),
    9_898_779_643_091: (2, ((2, 1), (5, 1), (13, 2), (5_857_266_061, 1))),
    5: (2, ((2, 2),)),
    13: (2, ((2, 2), (3, 1))),
    5_857_266_061: (2, ((2, 2), (3, 3), (5, 1), (317, 1), (34_217, 1))),
    317: (2, ((2, 2), (79, 1))),
    79: (3, ((2, 1), (3, 1), (13, 1))),
    34_217: (3, ((2, 3), (7, 1), (13, 1), (47, 1))),
    7: (3, ((2, 1), (3, 1))),
    47: (5, ((2, 1), (23, 1))),
    23: (5, ((2, 1), (11, 1))),
    11: (2, ((2, 1), (5, 1))),
    825_183_033_277_442_989: (2, ((2, 2), (3, 1), (14_683, 1), (4_683_324_441_403, 1))),
    14_683: (3, ((2, 1), (3, 1), (2_447, 1))),
    2_447: (5, ((2, 1), (1_223, 1))),
    1_223: (5, ((2, 1), (13, 1), (47, 1))),
    4_683_324_441_403: (2, ((2, 1), (3, 2), (103, 1), (2_526_064_963, 1))),
    103: (5, ((2, 1), (3, 1), (17, 1))),
    17: (3, ((2, 4),)),
    2_526_064_963: (2, ((2, 1), (3, 1), (37, 1), (11_378_671, 1))),
    37: (2, ((2, 2), (3, 2))),
    11_378_671: (12, ((2, 1), (3, 1), (5, 1), (379_289, 1))),
    379_289: (3, ((2, 3), (7, 1), (13, 1), (521, 1))),
    521: (3, ((2, 3), (5, 1), (13, 1))),
}


def is_small_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def multiplicative_order(a: int, p: int) -> int:
    x = 1
    for order in range(1, p):
        x = x * a % p
        if x == 1:
            return order
    raise AssertionError(f"no order for {a} modulo {p}")


def verify_vela_rows() -> None:
    assert math.gcd(M, 6) == 1
    assert len({row[0] for row in VELA_ROWS}) == len(VELA_ROWS)
    for p, ord2, ord3, h, t_p, m_mod_p, line in VELA_ROWS:
        assert is_small_prime(p)
        assert multiplicative_order(2, p) == ord2
        assert multiplicative_order(3, p) == ord3
        assert math.lcm(ord2, ord3) == h == line[3]
        assert M % p == m_mod_p != 0
        assert (-pow(m_mod_p, -1, p)) % p == t_p
        alpha, beta, gamma, modulus = line
        for k in range(h):
            for ell in range(h):
                divides = (pow(2, k, p) * pow(3, ell, p) * m_mod_p + 1) % p == 0
                on_line = (alpha * k + beta * ell - gamma) % modulus == 0
                assert divides == on_line


def verify_lucas_prime(n: int, done: set[int], active: set[int]) -> None:
    if n == 2 or n in done:
        return
    assert n not in active, "cyclic certificate"
    active.add(n)
    assert n in LUCAS_CERT, f"missing certificate for {n}"
    a, factors = LUCAS_CERT[n]
    product = 1
    distinct: set[int] = set()
    for q, exponent in factors:
        assert exponent >= 1 and q not in distinct
        distinct.add(q)
        verify_lucas_prime(q, done, active)
        product *= q**exponent
    assert product == n - 1
    assert 1 < a < n
    assert pow(a, n - 1, n) == 1
    for q in distinct:
        assert math.gcd(pow(a, (n - 1) // q, n) - 1, n) == 1
    active.remove(n)
    done.add(n)


def main() -> None:
    verify_vela_rows()
    assert M * 2**K * 3**L + 1 == N
    assert M == 9_898_779_643_091 * 825_183_033_277_442_989

    covering_rows = []
    for p, _, _, _, _, _, line in VELA_ROWS:
        alpha, beta, gamma, h = line
        if (alpha * K + beta * L - gamma) % h == 0:
            covering_rows.append(p)
    assert covering_rows == []

    done: set[int] = set()
    verify_lucas_prime(N, done, set())
    assert set(LUCAS_CERT) == done

    print(
        json.dumps(
            {
                "status": "PASS",
                "vela_rows_verified": len(VELA_ROWS),
                "uncovered_point": [K, L],
                "covering_row_primes": covering_rows,
                "value": str(N),
                "lucas_certificate_primes_verified": len(done),
                "conclusion": "Vela's retained m is not an Erdos #203 witness: the displayed value is prime.",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
