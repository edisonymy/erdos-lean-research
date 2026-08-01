#!/usr/bin/env python3
"""Independent elementary checker for an Erdos 273 JSON certificate."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text())
    period = int(data["period"])
    classes = [(int(c["residue"]), int(c["modulus"])) for c in data["classes"]]

    assert classes, "empty certificate"
    moduli = [m for _, m in classes]
    assert len(moduli) == len(set(moduli)), "moduli are not distinct"
    assert all(m >= 4 and m % 2 == 0 and is_prime(m + 1) for m in moduli)
    assert all(0 <= r < m for r, m in classes)
    assert all(period % m == 0 for m in moduli), "period not common multiple"

    uncovered = [x for x in range(period) if not any(x % m == r for r, m in classes)]
    assert not uncovered, f"uncovered residues (first 20): {uncovered[:20]}"
    print(f"VERIFIED period={period} classes={len(classes)}")


if __name__ == "__main__":
    main()
