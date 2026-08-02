#!/usr/bin/env python3
"""Try to extend the exact n=8 packing-one near miss to 56 edges at n=9.

The eight-vertex seed is recorded by its 18 missing triples.  Edges containing
the new vertex correspond to a link graph L on the old eight vertices.  A
new forbidden K_4^3 occurs exactly when L contains a triangle whose old
triple is present.  The 28-variable SAT instance maximizes only this link.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


MISSING_SEED = {
    (0, 1, 4), (0, 1, 6), (0, 1, 7), (0, 2, 5), (0, 3, 5), (0, 4, 6),
    (0, 4, 7), (1, 2, 5), (1, 3, 5), (1, 4, 6), (1, 4, 7), (2, 3, 6),
    (2, 3, 7), (2, 4, 5), (2, 6, 7), (3, 4, 5), (3, 6, 7), (5, 6, 7),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--link-threshold", type=int, default=18)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    old_edges = [
        edge for edge in itertools.combinations(range(8), 3)
        if edge not in MISSING_SEED
    ]
    if len(old_edges) != 38:
        raise AssertionError(len(old_edges))
    pairs = list(itertools.combinations(range(8), 2))
    pair_id = {pair: i + 1 for i, pair in enumerate(pairs)}
    solver = Solver(name=args.solver)
    for triple in old_edges:
        solver.add_clause(
            [-pair_id[pair] for pair in itertools.combinations(triple, 2)]
        )
    cardinality = CardEnc.atleast(
        lits=list(range(1, len(pairs) + 1)),
        bound=args.link_threshold,
        top_id=len(pairs),
        encoding=EncType.totalizer,
    )
    solver.append_formula(cardinality.clauses)
    status = solver.solve()
    payload = {
        "schema": "erdos719-n8-nearmiss-extension-v1",
        "solver": args.solver,
        "link_threshold": args.link_threshold,
        "status": "sat" if status else "unsat",
        "old_edge_count": len(old_edges),
        "edges": [],
    }
    if status:
        model = set(solver.get_model())
        link = [pair for pair in pairs if pair_id[pair] in model]
        combined = old_edges + [(u, v, 8) for u, v in link]
        payload.update(
            {
                "link_edges": [list(pair) for pair in link],
                "link_edge_count": len(link),
                "maximum_edges": len(combined),
                "certified_ex_3_9": 54,
                "minimum_parts_if_packing_one": len(combined) - 3,
                "margin_over_ex_if_packing_one": len(combined) - 3 - 54,
                "edges": [list(edge) for edge in sorted(combined)],
            }
        )
    solver.delete()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
