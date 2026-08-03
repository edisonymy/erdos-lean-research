#!/usr/bin/env python3
"""Bounded adversarial and small-packing tests for codex_verify719_strict."""

from __future__ import annotations

import itertools
import json
import tempfile
from pathlib import Path

import codex_verify719_strict as strict


def write_candidate(path: Path, edges: list[list[int]]) -> None:
    path.write_text(json.dumps({"edges": edges}, indent=2) + "\n", encoding="utf-8")


def test_small_packings() -> None:
    def masks_from_tets(tets: list[tuple[int, int, int, int]]) -> tuple[tuple[int, ...], int]:
        edges = set()
        for tet in tets:
            edges.update(itertools.combinations(tet, 3))
        return strict.present_tetrahedra(edges), len(edges)

    empty, empty_edges = masks_from_tets([])
    assert strict.exact_packing_number(empty, empty_edges, strict.SearchBudget(0)) == 0
    one, one_edges = masks_from_tets([(0, 1, 2, 3)])
    assert strict.exact_packing_number(one, one_edges, strict.SearchBudget(0)) == 1
    # These three tetrahedra share at most two vertices pairwise, hence no 3-edge.
    three, three_edges = masks_from_tets([(0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 5, 8)])
    assert strict.exact_packing_number(three, three_edges, strict.SearchBudget(0)) == 3


def test_bad_input_shapes() -> None:
    base = [list(edge) for edge in itertools.combinations(range(9), 3)]
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / "candidate.json"
        write_candidate(path, base[:60])
        report = strict.screening_report(path, 1000)
        assert report["status"] == "INVALID_CANDIDATE" and "exactly 61" in report["error"]

        write_candidate(path, base[:60] + [base[0]])
        report = strict.screening_report(path, 1000)
        assert report["status"] == "INVALID_CANDIDATE" and "duplicate" in report["error"]

        write_candidate(path, base[:60] + [[0, 1, 9]])
        report = strict.screening_report(path, 1000)
        assert report["status"] == "INVALID_CANDIDATE" and "0..8" in report["error"]

        write_candidate(path, base[:60] + [[0, 0, 1]])
        report = strict.screening_report(path, 1000)
        assert report["status"] == "INVALID_CANDIDATE" and "canonical" in report["error"]


def main() -> None:
    test_small_packings()
    test_bad_input_shapes()
    print(json.dumps({"status": "PASS", "tests": ["small exact packings", "60 edges", "duplicates", "invalid vertex", "invalid triple"]}, sort_keys=True))


if __name__ == "__main__":
    main()
