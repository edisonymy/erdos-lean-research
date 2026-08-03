#!/usr/bin/env python3
"""Strict, standalone screening for a proposed Erdős #719 exact-61 witness.

The input is a JSON object whose ``edges`` field is a list of exactly 61
distinct canonical 3-subsets of vertices 0..8.  This file deliberately does
not import ``attack719.py`` or any shared graph constants: it reconstructs the
complete 3-graph, its present K_4^(3)s, and the edge-disjoint packing problem
from first principles.

This is candidate screening only.  In particular, no proof certificate is
emitted for the maximum-packing computation and this program makes no claim
about the open status, priority, or resolution of Erdős #719.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


VERTEX_COUNT = 9
REQUIRED_EDGE_COUNT = 61


class CandidateError(ValueError):
    pass


class NodeLimit(RuntimeError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_edges(path: Path) -> tuple[tuple[int, int, int], ...]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateError(f"cannot read JSON candidate: {exc}") from exc
    if not isinstance(raw, dict):
        raise CandidateError("candidate root must be a JSON object")
    rows = raw.get("edges")
    if not isinstance(rows, list):
        raise CandidateError("candidate.edges must be a list")
    if len(rows) != REQUIRED_EDGE_COUNT:
        raise CandidateError(f"candidate must contain exactly {REQUIRED_EDGE_COUNT} edges, got {len(rows)}")
    edges: list[tuple[int, int, int]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 3:
            raise CandidateError("each edge must be a JSON list of three vertices")
        a, b, c = row
        if type(a) is not int or type(b) is not int or type(c) is not int:
            raise CandidateError(f"noninteger 3-edge: {row!r}")
        if not (0 <= a < b < c < VERTEX_COUNT):
            raise CandidateError(f"edge is not a canonical 3-subset of vertices 0..8: {row!r}")
        edges.append((a, b, c))
    if len(set(edges)) != REQUIRED_EDGE_COUNT:
        raise CandidateError("candidate contains duplicate 3-edges")
    return tuple(sorted(edges))


def all_triples() -> tuple[tuple[int, int, int], ...]:
    return tuple(itertools.combinations(range(VERTEX_COUNT), 3))


def present_tetrahedra(edges: Iterable[tuple[int, int, int]]) -> tuple[int, ...]:
    """Return 84-bit masks of all present K_4^(3)s, reconstructed locally."""
    universe = all_triples()
    index = {edge: i for i, edge in enumerate(universe)}
    present = set(edges)
    tetra_masks: list[int] = []
    for vertices in itertools.combinations(range(VERTEX_COUNT), 4):
        tetra_edges = tuple(itertools.combinations(vertices, 3))
        if all(edge in present for edge in tetra_edges):
            mask = 0
            for edge in tetra_edges:
                mask |= 1 << index[edge]
            tetra_masks.append(mask)
    return tuple(tetra_masks)


@dataclass
class SearchBudget:
    limit: int
    nodes: int = 0

    def visit(self) -> None:
        self.nodes += 1
        if self.limit and self.nodes > self.limit:
            raise NodeLimit(f"packing search reached node limit {self.limit}")


def exact_packing_number(tetra_masks: Sequence[int], present_edge_count: int, budget: SearchBudget) -> int:
    """Exact maximum cardinality edge-disjoint tetrahedron packing.

    This is a from-scratch branch-and-bound set-packing solver over 84-bit edge
    masks.  It shares neither state nor helper code with the attack encoding.
    """
    best = 0
    ordered = tuple(sorted(set(tetra_masks)))

    def recurse(candidates: tuple[int, ...], used: int, count: int) -> None:
        nonlocal best
        budget.visit()
        free_edge_bound = (present_edge_count - used.bit_count()) // 4
        if count + min(len(candidates), free_edge_bound) <= best:
            return
        if not candidates:
            best = max(best, count)
            return
        # Take a highly conflicting tetrahedron first to make the include
        # branch restrictive.  The alternative branch remains exhaustive.
        chosen = max(candidates, key=lambda item: sum(bool(item & other) for other in candidates))
        rest = tuple(item for item in candidates if item != chosen)
        if not (chosen & used):
            recurse(tuple(item for item in rest if not (item & chosen)), used | chosen, count + 1)
        recurse(rest, used, count)

    recurse(ordered, 0, 0)
    return best


def screening_report(path: Path, node_limit: int) -> dict[str, object]:
    report: dict[str, object] = {
        "schema": "erdos719-strict-screening-v1",
        "candidate": str(path.resolve()),
        "checker_file_sha256": file_sha256(Path(__file__)),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": (
            "This is a candidate-screening computation only. It establishes neither "
            "a proof certificate nor the open status, priority, or resolution of Erdős #719."
        ),
        "limits": {"packing_node_limit": node_limit, "vertices": VERTEX_COUNT, "required_edges": REQUIRED_EDGE_COUNT},
    }
    try:
        edges = parse_edges(path)
    except CandidateError as exc:
        report.update(status="INVALID_CANDIDATE", screened=False, error=str(exc))
        report["report_content_sha256"] = sha256_bytes(canonical_json_bytes(report))
        return report
    tetra_masks = present_tetrahedra(edges)
    report.update(
        candidate_file_sha256=file_sha256(path),
        canonical_edges_sha256=sha256_bytes(canonical_json_bytes([[a, b, c] for a, b, c in edges])),
        edge_count=len(edges),
        present_tetrahedron_count=len(tetra_masks),
    )
    budget = SearchBudget(node_limit)
    try:
        packing = exact_packing_number(tetra_masks, len(edges), budget)
    except NodeLimit as exc:
        report.update(status="INCONCLUSIVE_NODE_LIMIT", screened=False, packing_search_nodes=budget.nodes, error=str(exc))
        report["report_content_sha256"] = sha256_bytes(canonical_json_bytes(report))
        return report
    report.update(packing_search_nodes=budget.nodes, nu_exact=packing, nu_at_most_2=packing <= 2)
    if packing <= 2:
        report.update(status="SCREENED_NU_LE_2", screened=True)
    else:
        report.update(status="REJECTED_NU_GT_2", screened=False)
    report["report_content_sha256"] = sha256_bytes(canonical_json_bytes(report))
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--node-limit", type=int, default=2_000_000, help="zero disables the guard")
    args = parser.parse_args(argv)
    if args.node_limit < 0:
        parser.error("--node-limit must be nonnegative")
    result = screening_report(args.candidate.resolve(), args.node_limit)
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["screened"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
