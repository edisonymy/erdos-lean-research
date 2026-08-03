#!/usr/bin/env python3
"""Independent root replay of the bounded Erdos #149 theorem through order 13.

This checker deliberately does not import the campaign's order-13 checkers.
It validates both complete catalogues and directly constructs enough
induced-matching pairs to obtain a strong 20-edge-colouring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

import networkx as nx


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compatible_pairs(graph: nx.Graph, edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for i, (a, b) in enumerate(edges):
        for j in range(i + 1, len(edges)):
            c, d = edges[j]
            if len({a, b, c, d}) != 4:
                continue
            if not any(graph.has_edge(x, y) for x in (a, b) for y in (c, d)):
                result.append((i, j))
    return result


def find_pairs(candidate_pairs: list[tuple[int, int]], required: int) -> list[tuple[int, int]] | None:
    """Find a required-size matching by a deterministic, independently ordered DFS."""
    incidence: dict[int, list[int]] = {}
    for a, b in candidate_pairs:
        incidence.setdefault(a, []).append(b)
        incidence.setdefault(b, []).append(a)

    def search(available: frozenset[int], need: int) -> list[tuple[int, int]] | None:
        if need == 0:
            return []
        if len(available) < 2 * need:
            return None
        live = [v for v in available if any(w in available for w in incidence.get(v, ()))]
        if len(live) < 2 * need:
            return None
        # Minimum live degree is a fail-first order distinct from the two
        # catalogue checkers' forward/reverse candidate scans.
        vertex = min(
            live,
            key=lambda v: (sum(w in available for w in incidence.get(v, ())), -v),
        )
        neighbours = sorted(
            (w for w in incidence.get(vertex, ()) if w in available),
            key=lambda w: (sum(z in available for z in incidence.get(w, ())), -w),
        )
        for other in neighbours:
            tail = search(available - {vertex, other}, need - 1)
            if tail is not None:
                return [(vertex, other), *tail]
        # A matching need not use this compatibility-graph vertex.
        return search(available - {vertex}, need)

    vertices = frozenset(v for pair in candidate_pairs for v in pair)
    return search(vertices, required)


def parse_public_regular(line: str) -> nx.Graph:
    fields = line.split()
    if len(fields) != 2 or fields[0] != "13" or len(fields[1]) != 78:
        raise ValueError("bad public 13-vertex regular-catalogue record")
    graph = nx.Graph()
    graph.add_nodes_from(range(13))
    cursor = 0
    for left in range(13):
        for right in range(left + 1, 13):
            if fields[1][cursor] == "1":
                graph.add_edge(left, right)
            cursor += 1
    return graph


def geng_count(geng: Path, arguments: list[str]) -> tuple[int, str]:
    run = subprocess.run(
        [str(geng), *arguments], check=True, capture_output=True, text=True
    )
    transcript = run.stdout + run.stderr
    match = re.search(r"([0-9]+) graphs generated", transcript)
    if not match:
        raise RuntimeError(f"could not parse geng count: {transcript}")
    return int(match.group(1)), transcript.strip()


def catalogue_completeness_replay(
    package: Path, geng: Path, labelg: Path, temporary_root: Path
) -> dict:
    """Regenerate m=25 and compare canonical isomorphism sets for m=26."""
    with tempfile.TemporaryDirectory(prefix="order13-catalogues-", dir=temporary_root) as raw_tmp:
        tmp = Path(raw_tmp)
        regenerated_m25 = tmp / "m25.g6"
        subprocess.run(
            [str(geng), "-q", "-c", "-d3", "-D4", "13", "25", str(regenerated_m25)],
            check=True,
        )
        stored_m25 = package / "13_m25_min3.g6"

        regenerated_m26 = tmp / "m26-geng.g6"
        subprocess.run(
            [str(geng), "-q", "-c", "-d4", "-D4", "13", str(regenerated_m26)],
            check=True,
        )
        public_m26_g6 = tmp / "m26-public.g6"
        with public_m26_g6.open("wb") as stream:
            for line in (package / "13_4reg.txt").read_text(encoding="ascii").splitlines():
                stream.write(nx.to_graph6_bytes(parse_public_regular(line), header=False))

        canonical_geng = tmp / "m26-geng-canonical.g6"
        canonical_public = tmp / "m26-public-canonical.g6"
        subprocess.run(
            [str(labelg), "-q", "-g", str(regenerated_m26), str(canonical_geng)],
            check=True,
        )
        subprocess.run(
            [str(labelg), "-q", "-g", str(public_m26_g6), str(canonical_public)],
            check=True,
        )
        geng_set = set(canonical_geng.read_bytes().splitlines())
        public_set = set(canonical_public.read_bytes().splitlines())
        return {
            "m25_regenerated_bytes_identical": regenerated_m25.read_bytes() == stored_m25.read_bytes(),
            "m25_regenerated_sha256": sha256(regenerated_m25),
            "m26_geng_canonical_records": len(geng_set),
            "m26_public_canonical_records": len(public_set),
            "m26_canonical_sets_identical": geng_set == public_set,
            "m26_only_in_geng": len(geng_set - public_set),
            "m26_only_in_public": len(public_set - geng_set),
            "labelg_path": str(labelg),
            "labelg_sha256": sha256(labelg),
        }


def audit_m25(path: Path) -> dict:
    raw = path.read_bytes()
    records = raw.splitlines()
    failures: list[dict] = []
    for index, record in enumerate(records):
        graph = nx.from_graph6_bytes(record)
        edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
        degrees = sorted(degree for _, degree in graph.degree())
        witness = find_pairs(compatible_pairs(graph, edges), 5)
        if (
            len(graph) != 13
            or len(edges) != 25
            or degrees != [3, 3] + [4] * 11
            or not nx.is_connected(graph)
            or witness is None
        ):
            failures.append(
                {
                    "index": index,
                    "graph6": record.decode("ascii"),
                    "edges": len(edges),
                    "degrees": degrees,
                    "connected": nx.is_connected(graph),
                    "witness": witness,
                }
            )
            if len(failures) >= 10:
                break
    return {
        "records": len(records),
        "unique_records": len(set(records)),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "graphs_with_five_pairs": len(records) - len(failures),
        "failures": failures,
    }


def audit_m26(path: Path) -> dict:
    raw = path.read_bytes()
    lines = raw.decode("ascii").splitlines()
    failures: list[dict] = []
    for index, line in enumerate(lines):
        graph = parse_public_regular(line)
        edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
        witness = find_pairs(compatible_pairs(graph, edges), 6)
        if (
            len(graph) != 13
            or len(edges) != 26
            or set(dict(graph.degree()).values()) != {4}
            or not nx.is_connected(graph)
            or witness is None
        ):
            failures.append(
                {
                    "index": index,
                    "edges": len(edges),
                    "degrees": sorted(dict(graph.degree()).values()),
                    "connected": nx.is_connected(graph),
                    "witness": witness,
                }
            )
            if len(failures) >= 10:
                break
    return {
        "records": len(lines),
        "unique_records": len(set(lines)),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "graphs_with_six_pairs": len(lines) - len(failures),
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--labelg", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    started = time.perf_counter()

    m25 = audit_m25(package / "13_m25_min3.g6")
    m26 = audit_m26(package / "13_4reg.txt")
    m25_count, m25_transcript = geng_count(
        args.geng.resolve(), ["-c", "-d3", "-D4", "-u", "13", "25"]
    )
    m26_count, m26_transcript = geng_count(
        args.geng.resolve(), ["-c", "-d4", "-D4", "-u", "13"]
    )
    completeness = catalogue_completeness_replay(
        package,
        args.geng.resolve(),
        args.labelg.resolve(),
        args.output.resolve().parent,
    )
    structural_cases = [
        {
            "edges": edges,
            "degree_three_vertices": 52 - 2 * edges,
            "packing_holds": 3 * (52 - 2 * edges) <= 13 - (52 - 2 * edges),
        }
        for edges in range(20, 27)
    ]
    assertions = {
        "m25_expected_hash": m25["sha256"] == "fb25f684d2d15d3cb6a77a796d1f8fe487d545d72f92251b4a3ef0437c456f1c",
        "m25_complete_count": m25["records"] == m25["unique_records"] == m25_count == 300361,
        "m25_all_witnesses": not m25["failures"],
        "m26_expected_hash": m26["sha256"] == "bce601e43bf1f6274c6d550c112196ff1c5f5c167ca8aa40eabb4e779da168cd",
        "m26_complete_count": m26["records"] == m26["unique_records"] == m26_count == 10778,
        "m26_all_witnesses": not m26["failures"],
        "m25_regeneration_identical": completeness["m25_regenerated_bytes_identical"],
        "m26_isomorphism_sets_identical": completeness["m26_canonical_sets_identical"],
        "structural_survivors": [
            item["edges"] for item in structural_cases if item["packing_holds"]
        ] == [25, 26],
    }
    output = {
        "schema": "erdos149-order13-independent-root-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "claim": "Every simple graph G with |V(G)| <= 13 and Delta(G) <= 4 has strong chromatic index at most 20.",
        "claim_boundary": "Bounded theorem only; not a resolution of Erdos problem 149.",
        "package": str(package),
        "catalogue_25_edges": m25,
        "catalogue_26_edges": m26,
        "geng": {
            "path": str(args.geng.resolve()),
            "sha256": sha256(args.geng.resolve()),
            "m25_count": m25_count,
            "m25_transcript": m25_transcript,
            "m26_count": m26_count,
            "m26_transcript": m26_transcript,
        },
        "catalogue_completeness_replay": completeness,
        "structural_cases": structural_cases,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "assertions": assertions, "elapsed_seconds": output["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
