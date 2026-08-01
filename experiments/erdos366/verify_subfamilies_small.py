"""Independent brute-force cross-check of the power-subfamily reductions.

Unlike the C++ search, this simply factors x**j - 1 with SymPy for every x
in a small interval.  It is intended to catch candidate-generation or special
prime (2 and 3) valuation mistakes in the large exact search.
"""

from __future__ import annotations

import argparse
from sympy import factorint


def powerful(n: int) -> bool:
    return all(e >= 2 for e in factorint(n).values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xmax", type=int, default=10_000)
    args = parser.parse_args()
    for exponent in (3, 4):
        hits = []
        for x in range(2, args.xmax + 1):
            if powerful(x**exponent - 1):
                hits.append(x)
        print(f"power={exponent} xmax={args.xmax} brute_hits={hits}")


if __name__ == "__main__":
    main()
