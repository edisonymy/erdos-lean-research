#!/usr/bin/env python3
"""Exhaust the three-list Hall obstruction used in MINIMAL_COUNTEREXAMPLE_LOCAL.md."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def has_distinct_representatives(lists: tuple[frozenset[int], ...]) -> bool:
    return any(len(set(choice)) == 3 for choice in itertools.product(*lists))


def main() -> None:
    # Five abstract colours suffice: every Hall obstruction has union size <=2.
    colours = range(5)
    subsets = [
        frozenset(s)
        for size in range(2, 6)
        for s in itertools.combinations(colours, size)
    ]
    checked = locked = 0
    for lists in itertools.product(subsets, repeat=3):
        checked += 1
        actual_failure = not has_distinct_representatives(lists)
        predicted_failure = lists[0] == lists[1] == lists[2] and len(lists[0]) == 2
        assert actual_failure == predicted_failure
        locked += int(actual_failure)
    result = {
        "schema": "erdos149-degree3-list-hall-audit-v1",
        "triples_checked": checked,
        "palette_locked_failures": locked,
        "mismatches": 0,
        "status": "VERIFIED",
    }
    output = Path(__file__).with_name("local_extension_audit.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

