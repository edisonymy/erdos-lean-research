#!/usr/bin/env python3
"""Symbolically audit the algebra in TWO_RADIUS_DIHEDRAL_NO_GO.md."""

import sympy as s


def zero(expr: s.Expr) -> None:
    assert s.simplify(s.expand_trig(s.trigsimp(expr, method="fu"))) == 0


q, theta, r = s.symbols("q theta r", real=True)
u = 2 * q + theta
cross_distance = r**2 + 1 - 2 * r * s.cos(u)
outer_k = 2 * r**2 * (1 - s.cos(2 * q))
outer_next = 2 * r**2 * (1 - s.cos(2 * q + 2 * theta))

zero((cross_distance - outer_k).subs(r, 1) - 2 * (s.cos(2 * q) - s.cos(u)))
zero(
    ((cross_distance - outer_k) * s.cos(theta) ** 2).subs(r, 1 / s.cos(theta))
    - s.sin(theta) * (2 * s.sin(u) - s.sin(theta))
)
zero((outer_next - cross_distance).subs(r, 1) - 2 * (s.cos(u) - s.cos(2 * q + 2 * theta)))
zero(
    ((outer_next - cross_distance) * s.cos(theta) ** 2).subs(r, 1 / s.cos(theta))
    - s.sin(theta) * (2 * s.sin(u) + s.sin(theta))
)

# Convexity turns.
a0 = s.Matrix([r, 0])
b0 = s.Matrix([s.cos(theta), s.sin(theta)])
a1 = s.Matrix([r * s.cos(2 * theta), r * s.sin(2 * theta)])
bminus = s.Matrix([s.cos(-theta), s.sin(-theta)])
cross2 = lambda v, w: v[0] * w[1] - v[1] * w[0]
zero(cross2(b0 - a0, a1 - b0) - 2 * r * s.sin(theta) * (1 - r * s.cos(theta)))
zero(cross2(a0 - bminus, b0 - a0) - 2 * s.sin(theta) * (r - s.cos(theta)))

# Odd-order endpoint factors after x=cos(theta/2), d=2x-1.
x = s.symbols("x", real=True)
d = 2 * x - 1
r0 = 1 / d
cos_theta = 2 * x**2 - 1
cos_2theta = 2 * cos_theta**2 - 1
h_first = 1 - r0**2 + 2 * r0 * cos_theta - 2 * cos_2theta
h_last = 1 - r0**2 - 2 * r0 * cos_2theta + 2 * cos_theta
assert s.factor(d**2 * h_first) == -8 * x**2 * (x - 1) * (8 * x**3 - 6 * x + 1)
assert s.factor(d**2 * h_last) == -16 * x**2 * (x - 1) * (2 * x**2 - 1)

print("all dihedral two-radius algebra identities verified")
