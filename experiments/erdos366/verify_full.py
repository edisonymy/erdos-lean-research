"""Exact factorization checker for any proposed Erdős 366 witness."""

from __future__ import annotations

import argparse
from sympy import factorint


def full(n: int, k: int) -> bool:
    return all(e >= k for e in factorint(n).values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    args = parser.parse_args()
    n = args.n
    fn = factorint(n)
    fm = factorint(n + 1)
    print(f"n={n} factors={fn} 2_full={full(n, 2)}")
    print(f"n+1={n+1} factors={fm} 3_full={full(n+1, 3)}")
    if n <= 0 or not full(n, 2) or not full(n + 1, 3):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
