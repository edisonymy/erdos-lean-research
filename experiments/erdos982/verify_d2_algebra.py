#!/usr/bin/env python3
"""Symbolically audit the substitutions in D2_OCTAGON_NO_GO.md."""

import sympy as s

b, c = s.symbols("b c", real=True)
d2 = 3 - 2 * b - b**2
values = [
    b**2,
    d2,
    b**2 + d2,
    ((1 - b) ** 2 + d2) / 4,
    ((1 + b) ** 2 + d2) / 4,
]
targets = [b**2, 3 - 2 * b - b**2, 3 - 2 * b, 1 - b, 1]
for value, target in zip(values, targets):
    assert s.expand(value - target) == 0

left_minus_right = s.expand(
    (c**2 - 2 * b - b**2) - c**2 * (1 - b) ** 2
)
assert s.factor(left_minus_right) == -b * (2 + b - 2 * c**2 + b * c**2)

print("all D2 octagon algebra identities verified")
