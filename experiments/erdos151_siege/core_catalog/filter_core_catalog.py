#!/usr/bin/env python3
"""Apply the proper-clique residual obstruction to a graph6 core catalogue."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import itertools
import json
import os
from collections import Counter
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

from catalog_lib import iter_graph6, sha256_decompressed, sha256_path


THRESHOLDS = {2: 28, 3: 23, 4: 18, 5: 14}


@contextmanager
def deterministic_gzip_text(path: Path):
    """Write gzip text with mtime=0 and no original filename in the header."""

    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as text:
                yield text


@dataclass(frozen=True)
class CandidateClique:
    vertices: tuple[int, ...]
    common_neighbors: int
    degree_deficit: int

    @property
    def size(self) -> int:
        return len(self.vertices)

    @property
    def extender(self) -> int:
        return (self.common_neighbors & -self.common_neighbors).bit_length() - 1

    def lhs(self, target_order: int, core_order: int) -> int:
        return target_order - core_order - self.degree_deficit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--targets", type=int, nargs="+", default=(40, 41))
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--source-url")
    parser.add_argument(
        "--write-all-candidates",
        action="store_true",
        help="also write one gzip JSONL record for every candidate clique",
    )
    return parser.parse_args()


def is_clique(adjacency: Sequence[int], vertices: tuple[int, ...]) -> bool:
    for offset, u in enumerate(vertices):
        for v in vertices[offset + 1 :]:
            if not ((adjacency[u] >> v) & 1):
                return False
    return True


def candidate_cliques(adjacency: Sequence[int]) -> Iterator[CandidateClique]:
    """Enumerate every clique P of size 2..5 with an extender in Q minus P."""

    order = len(adjacency)
    all_vertices = (1 << order) - 1
    degrees = [mask.bit_count() for mask in adjacency]
    for size in range(2, 6):
        for vertices in itertools.combinations(range(order), size):
            if not is_clique(adjacency, vertices):
                continue
            common = all_vertices
            selected = 0
            for vertex in vertices:
                common &= adjacency[vertex]
                selected |= 1 << vertex
            common &= ~selected
            if not common:
                continue
            yield CandidateClique(
                vertices=vertices,
                common_neighbors=common,
                degree_deficit=sum(9 - degrees[vertex] for vertex in vertices),
            )


def candidate_json(
    candidate: CandidateClique, target_orders: Sequence[int], core_order: int
) -> dict[str, object]:
    return {
        "k": candidate.size,
        "vertices": list(candidate.vertices),
        "extenders": [
            vertex
            for vertex in range(core_order)
            if (candidate.common_neighbors >> vertex) & 1
        ],
        "degree_deficit": candidate.degree_deficit,
        "targets": {
            str(target): {
                "lhs": candidate.lhs(target, core_order),
                "threshold": THRESHOLDS[candidate.size],
                "inequality_holds": candidate.lhs(target, core_order)
                >= THRESHOLDS[candidate.size],
            }
            for target in target_orders
        },
    }


def witness_key(
    candidate: CandidateClique, target_order: int, core_order: int
) -> tuple[object, ...]:
    margin = candidate.lhs(target_order, core_order) - THRESHOLDS[candidate.size]
    return (-margin, candidate.size, candidate.vertices, candidate.extender)


def main() -> int:
    args = parse_args()
    targets = tuple(sorted(set(args.targets)))
    if any(target <= 0 for target in targets):
        raise ValueError("target orders must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.input.name
    while Path(stem).suffix.lower() in (".gz", ".g6"):
        stem = Path(stem).stem

    certificate_path = args.output_dir / f"{stem}.certificates.jsonl.gz"
    candidates_path = args.output_dir / f"{stem}.all-candidates.jsonl.gz"
    summary_path = args.output_dir / f"{stem}.summary.json"
    survivor_paths = {
        target: args.output_dir / f"{stem}.n{target}.survivors.g6" for target in targets
    }
    certificate_tmp = certificate_path.with_name(certificate_path.name + ".tmp")
    candidates_tmp = candidates_path.with_name(candidates_path.name + ".tmp")
    survivor_tmps = {
        target: path.with_name(path.name + ".tmp") for target, path in survivor_paths.items()
    }

    counts = {
        "graphs": 0,
        "degree_cap_infeasible": 0,
        "candidates_by_k": Counter(),
        "extender_incidences_by_k": Counter(),
        "excluded_by_target": Counter(),
        "survived_by_target": Counter(),
        "witnesses_by_target_and_k": Counter(),
        "graphs_qualifying_by_target_and_k": Counter(),
        "qualifying_candidates_by_target_and_k": Counter(),
    }
    order_seen: int | None = None

    survivor_streams = {
        target: temporary.open("wb") for target, temporary in survivor_tmps.items()
    }
    try:
        with deterministic_gzip_text(certificate_tmp) as certificates, ExitStack() as stack:
            candidate_context = (
                stack.enter_context(deterministic_gzip_text(candidates_tmp))
                if args.write_all_candidates
                else None
            )
            for index, record, adjacency in iter_graph6(args.input):
                counts["graphs"] += 1
                order = len(adjacency)
                if order_seen is None:
                    order_seen = order
                elif order != order_seen:
                    raise ValueError("mixed graph orders in one catalogue")
                degrees = [mask.bit_count() for mask in adjacency]
                degree_cap_feasible = max(degrees, default=0) <= 9
                if not degree_cap_feasible:
                    counts["degree_cap_infeasible"] += 1

                candidates = list(candidate_cliques(adjacency))
                digest = hashlib.sha256()
                maxima: dict[int, CandidateClique] = {}
                for candidate in candidates:
                    k = candidate.size
                    counts["candidates_by_k"][k] += 1
                    counts["extender_incidences_by_k"][k] += (
                        candidate.common_neighbors.bit_count()
                    )
                    digest.update(
                        (
                            f"{k}:{','.join(map(str, candidate.vertices))}:"
                            f"{candidate.common_neighbors:x}\n"
                        ).encode("ascii")
                    )
                    current = maxima.get(k)
                    if current is None or (
                        candidate.degree_deficit,
                        candidate.vertices,
                        candidate.extender,
                    ) < (
                        current.degree_deficit,
                        current.vertices,
                        current.extender,
                    ):
                        maxima[k] = candidate
                    if candidate_context is not None:
                        candidate_context.write(
                            json.dumps(
                                {
                                    "graph_index": index,
                                    **candidate_json(candidate, targets, order),
                                },
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                            + "\n"
                        )

                target_results: dict[str, object] = {}
                for target in targets:
                    qualifying = [
                        candidate
                        for candidate in candidates
                        if degree_cap_feasible
                        and candidate.lhs(target, order) >= THRESHOLDS[candidate.size]
                    ]
                    qualifying_by_k = Counter(item.size for item in qualifying)
                    for k, qualifying_count in qualifying_by_k.items():
                        counts["graphs_qualifying_by_target_and_k"][(target, k)] += 1
                        counts["qualifying_candidates_by_target_and_k"][(target, k)] += (
                            qualifying_count
                        )
                    witness = (
                        min(
                            qualifying,
                            key=lambda item: witness_key(item, target, order),
                        )
                        if qualifying
                        else None
                    )
                    if not degree_cap_feasible:
                        pass
                    elif witness is not None:
                        counts["excluded_by_target"][target] += 1
                        counts["witnesses_by_target_and_k"][(target, witness.size)] += 1
                    else:
                        counts["survived_by_target"][target] += 1
                        survivor_streams[target].write(record + b"\n")
                    target_results[str(target)] = {
                        "degree_cap_excluded": not degree_cap_feasible,
                        "residual_evaluated": degree_cap_feasible,
                        "residual_excluded": (
                            witness is not None if degree_cap_feasible else None
                        ),
                        "witness": (
                            candidate_json(witness, (target,), order)
                            if witness is not None
                            else None
                        ),
                        "survivor_certificate_maximum_by_k": {
                            str(k): (
                                candidate_json(maxima[k], (target,), order)
                                if k in maxima
                                else None
                            )
                            for k in THRESHOLDS
                        },
                    }

                certificates.write(
                    json.dumps(
                        {
                            "graph_index": index,
                            "graph6": record.decode("ascii"),
                            "order": order,
                            "degrees": degrees,
                            "degree_cap_9_feasible": degree_cap_feasible,
                            "candidate_clique_count": len(candidates),
                            "candidate_count_by_k": {
                                str(k): sum(item.size == k for item in candidates)
                                for k in THRESHOLDS
                            },
                            "candidate_enumeration_sha256": digest.hexdigest(),
                            "targets": target_results,
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
    finally:
        for stream in survivor_streams.values():
            stream.close()

    graph_count = counts["graphs"]
    if args.expected_count is not None and graph_count != args.expected_count:
        raise ValueError(f"input count {graph_count} != expected {args.expected_count}")
    os.replace(certificate_tmp, certificate_path)
    if args.write_all_candidates:
        os.replace(candidates_tmp, candidates_path)
    for target in targets:
        os.replace(survivor_tmps[target], survivor_paths[target])

    summary = {
        "input": str(args.input.resolve()),
        "input_bytes": args.input.stat().st_size,
        "input_sha256": sha256_path(args.input),
        "input_decompressed_sha256": sha256_decompressed(args.input),
        "source_url": args.source_url,
        "order": order_seen,
        "graph_count": graph_count,
        "expected_count": args.expected_count,
        "degree_cap": {
            "cap": 9,
            "infeasible": counts["degree_cap_infeasible"],
            "feasible": graph_count - counts["degree_cap_infeasible"],
            "note": "This is recorded separately from the residual obstruction.",
        },
        "lemma": {
            "candidate": "proper clique P of size k=2..5 with a common neighbor in Q\\P",
            "lhs": "n-q-sum_{v in P}(9-d_Q(v))",
            "thresholds": {str(k): value for k, value in THRESHOLDS.items()},
            "exclude_when": "lhs >= threshold[k]",
        },
        "candidate_cliques": {
            "count_by_k": {
                str(k): counts["candidates_by_k"][k] for k in THRESHOLDS
            },
            "extender_incidence_count_by_k": {
                str(k): counts["extender_incidences_by_k"][k] for k in THRESHOLDS
            },
            "enumeration": (
                str(candidates_path.resolve())
                if args.write_all_candidates
                else "enumerated exhaustively; per-graph count and SHA-256 transcript digest are in certificates"
            ),
        },
        "targets": {
            str(target): {
                "degree_cap_feasible_considered": graph_count
                - counts["degree_cap_infeasible"],
                "residual_excluded_among_degree_cap_feasible": counts[
                    "excluded_by_target"
                ][target],
                "residual_survivors_among_degree_cap_feasible": counts[
                    "survived_by_target"
                ][target],
                "pipeline_excluded": counts["degree_cap_infeasible"]
                + counts["excluded_by_target"][target],
                "pipeline_survivors": counts["survived_by_target"][target],
                "exclusion_witnesses_by_k": {
                    str(k): counts["witnesses_by_target_and_k"][(target, k)]
                    for k in THRESHOLDS
                },
                "graphs_with_a_qualifying_candidate_by_k": {
                    str(k): counts["graphs_qualifying_by_target_and_k"][(target, k)]
                    for k in THRESHOLDS
                },
                "qualifying_candidate_count_by_k": {
                    str(k): counts["qualifying_candidates_by_target_and_k"][(target, k)]
                    for k in THRESHOLDS
                },
                "survivor_graph6": str(survivor_paths[target].resolve()),
            }
            for target in targets
        },
        "certificates": str(certificate_path.resolve()),
        "certificates_sha256": sha256_path(certificate_path),
        "all_candidates_output": (
            {
                "path": str(candidates_path.resolve()),
                "bytes": candidates_path.stat().st_size,
                "sha256": sha256_path(candidates_path),
            }
            if args.write_all_candidates
            else None
        ),
        "outputs": {
            str(target): {
                "sha256": sha256_path(survivor_paths[target]),
                "bytes": survivor_paths[target].stat().st_size,
            }
            for target in targets
        },
    }
    temporary_summary = summary_path.with_name(summary_path.name + ".tmp")
    with temporary_summary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary_summary, summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
