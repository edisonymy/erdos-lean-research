#!/usr/bin/env python3
"""Emit a 55-edge packing-one lower-bound example for the n=9 probe."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def main() -> None:
    parts = [set(range(0, 3)), set(range(3, 6)), set(range(6, 9))]
    allowed = {(1, 1, 1), (2, 1, 0), (0, 2, 1), (1, 0, 2)}
    base = []
    for edge in itertools.combinations(range(9), 3):
        profile = tuple(len(set(edge) & part) for part in parts)
        if profile in allowed:
            base.append(edge)
    if len(base) != 54:
        raise AssertionError(len(base))
    base_set = set(base)
    added = next(edge for edge in itertools.combinations(range(9), 3) if edge not in base_set)
    payload = {
        "schema": "erdos719-n9-common-triple-lower-v1",
        "n": 9,
        "r": 3,
        "construction": "balanced cyclic 3,3,3 Turan graph plus one missing triple",
        "added_common_triple": list(added),
        "maximum_edges": 55,
        "certified_ex_3_9": 54,
        "packing_number_upper_bound": 1,
        "minimum_parts_if_packing_one": 52,
        "margin_over_ex_if_packing_one": -2,
        "edges": [list(edge) for edge in sorted(base_set | {added})],
    }
    path = Path(__file__).with_name("lower_55.json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
