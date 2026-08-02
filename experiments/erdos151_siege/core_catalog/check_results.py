#!/usr/bin/env python3
"""Cross-check the committed residual summaries, dumps, and certificates."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from catalog_lib import decode_graph6, iter_graph6, sha256_path
from filter_core_catalog import THRESHOLDS, is_clique


ROOT = Path(__file__).resolve().parent
CASES = ((12, 124), (13, 13))


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_jsonl_gzip(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def check_case(order: int, expected_count: int) -> None:
    stem = f"minimal_ramsey_q{order}_alpha2"
    result_dir = ROOT / "results" / f"q{order}_alpha2"
    summary_path = result_dir / f"{stem}.summary.json"
    certificate_path = result_dir / f"{stem}.certificates.jsonl.gz"
    candidates_path = result_dir / f"{stem}.all-candidates.jsonl.gz"
    summary = load_json(summary_path)
    certificates = load_jsonl_gzip(certificate_path)

    assert summary["graph_count"] == expected_count
    assert len(certificates) == expected_count
    assert summary["certificates_sha256"] == sha256_path(certificate_path)
    assert summary["all_candidates_output"]["sha256"] == sha256_path(candidates_path)

    certificate_by_index = {item["graph_index"]: item for item in certificates}
    transcript_digests: dict[int, object] = {}
    candidate_counts: dict[int, int] = {}
    aggregate_by_k = {k: 0 for k in THRESHOLDS}
    with gzip.open(candidates_path, "rt", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            graph_index = item["graph_index"]
            digest = transcript_digests.setdefault(graph_index, hashlib.sha256())
            common_mask = sum(1 << vertex for vertex in item["extenders"])
            digest.update(
                (
                    f"{item['k']}:{','.join(map(str, item['vertices']))}:"
                    f"{common_mask:x}\n"
                ).encode("ascii")
            )
            candidate_counts[graph_index] = candidate_counts.get(graph_index, 0) + 1
            aggregate_by_k[item["k"]] += 1

    assert aggregate_by_k == {
        int(k): value for k, value in summary["candidate_cliques"]["count_by_k"].items()
    }

    for graph_index, certificate in certificate_by_index.items():
        assert candidate_counts.get(graph_index, 0) == certificate["candidate_clique_count"]
        assert (
            transcript_digests.get(graph_index, hashlib.sha256()).hexdigest()
            == certificate["candidate_enumeration_sha256"]
        )
        adjacency = decode_graph6(certificate["graph6"])
        assert [mask.bit_count() for mask in adjacency] == certificate["degrees"]
        for target_text, target_result in certificate["targets"].items():
            assert target_result["degree_cap_excluded"] is False
            assert target_result["residual_evaluated"] is True
            assert target_result["residual_excluded"] is True
            witness = target_result["witness"]
            vertices = tuple(witness["vertices"])
            assert is_clique(adjacency, vertices)
            assert witness["extenders"]
            for extender in witness["extenders"]:
                assert extender not in vertices
                assert all((adjacency[vertex] >> extender) & 1 for vertex in vertices)
            expected_deficit = sum(9 - adjacency[vertex].bit_count() for vertex in vertices)
            assert witness["degree_deficit"] == expected_deficit
            target = int(target_text)
            inequality = witness["targets"][target_text]
            assert inequality["lhs"] == target - order - expected_deficit
            assert inequality["threshold"] == THRESHOLDS[len(vertices)]
            assert inequality["inequality_holds"] is True

    for target in (40, 41):
        survivor_path = result_dir / f"{stem}.n{target}.survivors.g6"
        survivor_count = sum(1 for _ in iter_graph6(survivor_path))
        assert survivor_count == summary["targets"][str(target)]["pipeline_survivors"]
        assert summary["outputs"][str(target)]["sha256"] == sha256_path(survivor_path)
    print(f"q={order}: certificates and candidate transcript verified")


def main() -> None:
    for order, expected_count in CASES:
        check_case(order, expected_count)
    print("check_results: ok")


if __name__ == "__main__":
    main()
