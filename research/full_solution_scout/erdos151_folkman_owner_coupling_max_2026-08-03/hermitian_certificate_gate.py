#!/usr/bin/env python3
"""Arithmetic audit for the Hermitian random-block certificate versus #151."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    q = 3
    vertices = q**4 - q**3 + q**2
    degree = (q + 1) * (q**2 - 1)
    owners = q**3 + 1
    owner_order = q**2
    edges = vertices * degree // 2
    nondegenerate_triangles = (
        vertices * (q**3 - q) * (q + 1) * q // 6
    )
    assert (vertices, degree, owners, owner_order, edges, nondegenerate_triangles) == (
        63,
        32,
        28,
        9,
        1008,
        3024,
    )

    # Since maxcut(F)/e(F)>=1/2, positivity of the final Goodman expression
    # requires 1/2(1-delta)^2 > 1/3(1+delta)^2.
    delta_cap = (math.sqrt(3 / 2) - 1) / (math.sqrt(3 / 2) + 1)
    assert 0.101 < delta_cap < 0.102

    payload = {
        "schema": "erdos151-hermitian-certificate-gate-v1",
        "primary_source": {
            "title": "Some remarks on Folkman graphs for triangles",
            "authors": ["Eion Mulrenin", "Steven van Overberghe"],
            "arxiv": "2506.14942v4",
            "date": "2026-06-18",
        },
        "H3": {
            "vertices": vertices,
            "degree": degree,
            "edges": edges,
            "unique_owners": owners,
            "owner_order": owner_order,
            "nondegenerate_triangles": nondegenerate_triangles,
            "direct_per_owner_maxcut_certificate_possible": False,
            "reason": (
                "maxcut(F)<2e(F)/3 implies chi(F)>=4, while every "
                "triangle-free graph on at most 10 vertices is 3-colourable"
            ),
        },
        "published_union_bound": {
            "notation": "s=|V(F)|, m=|E(F)|, p=2m/s^2",
            "positive_probability_requires": (
                "(2*delta^2/3) * q*p^2/s^2 > 7*ln(s*q)+ln(2)"
            ),
            "hence": "p = Omega(s*sqrt(ln(s*q)/q))",
            "necessary_delta_upper_bound": delta_cap,
            "necessary_one_minus_delta_lower_bound": 1 - delta_cap,
        },
        "degree_for_every_instance_in_the_certified_event": {
            "identity": (
                "d_Hq*(v)=(1/q) sum over q^3-q spanning cliques C "
                "of |C intersect N*(v)|"
            ),
            "lower_bound": "(1-delta)*p*(q+1)*(q^2-1)",
        },
        "asymptotic_conflict": {
            "certified_degree_lower_scale": "Omega(s*q^(5/2)*sqrt(ln(s*q)))",
            "target_H_at_N_asymptotic": "O(q^2*sqrt(ln q)), N=q^4-q^3+q^2",
            "ratio_lower_scale": "Omega(s*sqrt(q))",
            "scope": (
                "closes parameter choices certified by the displayed McDiarmid "
                "union bound and Lemma 4.4 event, not all deterministic or "
                "finite-q Hermitian subgraphs"
            ),
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
