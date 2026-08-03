#!/usr/bin/env python3
"""Independent definition-level verifier for an exact-64 #719 candidate.

Accepted JSON contains either ``missing_edges`` (20 canonical triples) or
``edges`` (64 canonical triples), or both consistently.  No code or constants
are imported from the search lane.  The verifier independently reconstructs
all tetrahedra, exhaustively rules out a packing of four, finds the exact
packing number when it is at most three, and recomputes ex_3(9,K_4^3)=54.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable


class CandidateError(ValueError):
    pass


def canonical_triples(rows: object, expected: int, field: str) -> tuple[tuple[int, int, int], ...]:
    if not isinstance(rows, list) or len(rows) != expected:
        got = len(rows) if isinstance(rows, list) else "non-list"
        raise CandidateError(f"{field} must be a list of exactly {expected} triples; got {got}")
    result = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 3 or any(type(x) is not int for x in row):
            raise CandidateError(f"invalid row in {field}: {row!r}")
        triple = tuple(row)
        if not (0 <= triple[0] < triple[1] < triple[2] < 9):
            raise CandidateError(f"noncanonical triple in {field}: {row!r}")
        result.append(triple)
    if len(set(result)) != expected:
        raise CandidateError(f"{field} contains a duplicate")
    return tuple(sorted(result))


def read_candidate(path: Path) -> tuple[set[tuple[int, int, int]], set[tuple[int, int, int]]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateError(f"cannot read candidate JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise CandidateError("candidate root must be an object")
    universe = set(itertools.combinations(range(9), 3))
    missing = None
    present = None
    if "missing_edges" in raw:
        missing = set(canonical_triples(raw["missing_edges"], 20, "missing_edges"))
        present = universe - missing
    if "edges" in raw:
        supplied_present = set(canonical_triples(raw["edges"], 64, "edges"))
        if present is not None and supplied_present != present:
            raise CandidateError("edges and missing_edges are not complements")
        present = supplied_present
        missing = universe - present
    if present is None or missing is None:
        raise CandidateError("candidate must contain edges or missing_edges")
    return present, missing


def tetrahedra(present: set[tuple[int, int, int]]) -> tuple[tuple[tuple[int, int, int, int], int], ...]:
    edge_index = {edge: i for i, edge in enumerate(itertools.combinations(range(9), 3))}
    result = []
    for vertices in itertools.combinations(range(9), 4):
        edges = tuple(itertools.combinations(vertices, 3))
        if all(edge in present for edge in edges):
            mask = sum(1 << edge_index[edge] for edge in edges)
            result.append((vertices, mask))
    return tuple(result)


def find_packing(blocks: tuple[tuple[tuple[int, int, int, int], int], ...], target: int):
    """Return one target-packing, or None after exhaustive lexicographic search."""
    chosen: list[tuple[int, int, int, int]] = []

    def visit(start: int, used: int):
        if len(chosen) == target:
            return tuple(chosen)
        need = target - len(chosen)
        if len(blocks) - start < need:
            return None
        for i in range(start, len(blocks)):
            vertices, mask = blocks[i]
            if mask & used:
                continue
            chosen.append(vertices)
            answer = visit(i + 1, used | mask)
            if answer is not None:
                return answer
            chosen.pop()
        return None

    return visit(0, 0)


def exact_t7() -> tuple[int, int]:
    """Compute the minimum triple hitter of all 4-sets on seven vertices."""
    triples = tuple(itertools.combinations(range(7), 3))
    foursets = tuple(itertools.combinations(range(7), 4))
    full = (1 << len(foursets)) - 1
    cover = []
    for triple in triples:
        mask = 0
        for i, block in enumerate(foursets):
            if set(triple) <= set(block):
                mask |= 1 << i
        cover.append(mask)
    block_edges = [tuple(triples.index(edge) for edge in itertools.combinations(block, 3)) for block in foursets]

    @functools.lru_cache(maxsize=None)
    def solve(covered: int) -> int:
        if covered == full:
            return 0
        uncovered_bit = ((~covered) & full) & -((~covered) & full)
        block_index = uncovered_bit.bit_length() - 1
        return 1 + min(solve(covered | cover[e]) for e in block_edges[block_index])

    optimum = solve(0)
    return optimum, solve.cache_info().currsize


def verify_ex54() -> dict[str, object]:
    t7, states = exact_t7()
    if t7 != 12:
        raise AssertionError(f"unexpected exact t7={t7}")
    t8_lower = (8 * t7 + 4) // 5
    t9_lower = (9 * t8_lower + 5) // 6
    if (t8_lower, t9_lower) != (20, 30):
        raise AssertionError("deletion-bound arithmetic failed")

    parts = (set(range(0, 3)), set(range(3, 6)), set(range(6, 9)))
    allowed = {(0, 2, 1), (1, 0, 2), (1, 1, 1), (2, 1, 0)}
    construction = set()
    for edge in itertools.combinations(range(9), 3):
        profile = tuple(len(set(edge) & part) for part in parts)
        if profile in allowed:
            construction.add(edge)
    if len(construction) != 54:
        raise AssertionError("54-edge construction has wrong size")
    for block in itertools.combinations(range(9), 4):
        if all(edge in construction for edge in itertools.combinations(block, 3)):
            raise AssertionError(f"54-edge construction contains tetrahedron {block}")
    return {
        "exact_t7": t7,
        "t7_memoized_states": states,
        "deletion_lower_bound_t8": t8_lower,
        "deletion_lower_bound_t9": t9_lower,
        "checked_k4_free_construction_edges": len(construction),
        "exact_ex_3_9_k4_3": 54,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path) -> dict[str, object]:
    present, missing = read_candidate(path)
    blocks = tetrahedra(present)
    packing4 = find_packing(blocks, 4)
    if packing4 is not None:
        return {
            "status": "REJECTED_PACKING_AT_LEAST_4",
            "candidate_sha256": sha256(path),
            "edge_count": len(present),
            "missing_edge_count": len(missing),
            "present_tetrahedra": len(blocks),
            "packing_of_four": [list(x) for x in packing4],
            "verified_counterexample": False,
        }

    packing = None
    nu = 0
    for target in (3, 2, 1):
        packing = find_packing(blocks, target)
        if packing is not None:
            nu = target
            break
    extremal = verify_ex54()
    pieces = len(present) - 3 * nu
    verified = len(present) == 64 and len(missing) == 20 and pieces > 54
    return {
        "status": "VERIFIED_EXACT64_COUNTEREXAMPLE" if verified else "REJECTED_NOT_COUNTEREXAMPLE",
        "candidate_sha256": sha256(path),
        "checker_sha256": sha256(Path(__file__)),
        "edge_count": len(present),
        "missing_edge_count": len(missing),
        "present_tetrahedra": len(blocks),
        "no_packing_of_four_exhaustively_checked": True,
        "nu_exact": nu,
        "maximum_packing_witness": [list(x) for x in (packing or ())],
        "minimum_decomposition_pieces": pieces,
        "exact_extremal_number": 54,
        "margin": pieces - 54,
        "extremal_certificate": extremal,
        "verified_counterexample": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.candidate.resolve())
    except CandidateError as exc:
        report = {"status": "INVALID_CANDIDATE", "error": str(exc), "verified_counterexample": False}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if report["verified_counterexample"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
