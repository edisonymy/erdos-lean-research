#!/usr/bin/env python3
"""Independent CAS/ideal certificate for nonextendibility of H8."""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".deps"))

import sympy as sp


def main():
    q = sp.sqrt(3)
    r = 1 + q
    points = [
        (r, 0), (1, 1), (0, r), (-1, 1),
        (-r, 0), (-1, -1), (0, -r), (1, -1),
    ]
    x, y = sp.symbols("x y")

    def d2(p, z):
        return sp.expand((p[0] - z[0]) ** 2 + (p[1] - z[1]) ** 2)

    allowed = [
        sorted({d2(points[i], points[j]) for j in range(8) if i != j}, key=lambda z: float(z.evalf()))
        for i in range(8)
    ]
    assert all(len(row) == 3 for row in allowed)

    # F_i(x,y)=0 says that the new point is on one of the three already-used
    # circles around old vertex i.  A common zero of all eight F_i would be an
    # extension preserving all old local distance counts.
    z = (x, y)
    polynomials = [sp.expand(sp.prod(d2(z, points[i]) - rho for rho in allowed[i])) for i in range(8)]
    basis = sp.groebner(polynomials, x, y, extension=q, order="grevlex")
    assert list(basis) == [sp.Integer(1)]

    result = {
        "checker": f"SymPy {sp.__version__} Groebner basis over Q(sqrt(3))",
        "variables": ["x", "y"],
        "constraint_degrees": [sp.Poly(f, x, y).total_degree() for f in polynomials],
        "number_of_constraints": len(polynomials),
        "reduced_basis": [str(g) for g in basis],
        "conclusion": "no extension point exists, even over the algebraic closure",
        "status": "VERIFIED_NO_EXTENSION",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
