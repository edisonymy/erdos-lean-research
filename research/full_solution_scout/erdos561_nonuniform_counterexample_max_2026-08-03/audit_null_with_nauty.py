#!/usr/bin/env python3
"""Independent audit of the <=7-edge null result for the selected #561 tuple.

Independence from search_all_hosts.py:

* connected graph types come from nauty geng, not the NetworkX atlas/tree
  generators;
* target containment is decided by NetworkX VF2 graph monomorphism, not by
  the searcher's hand-written edge-pattern masks;
* the component multiset catalogue is reconstructed from scratch.

The audit is optional for a null result but makes the bounded computation
reproducible.  A future candidate still requires the dedicated injection
verifier and a second definition-level implementation.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import time
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
SOURCE = HERE / "search_result.json"
WITNESSES = HERE / "host_avoiding_colorings.json"
OUT = HERE / "independent_null_audit.json"
MAX_EDGES = 7


def target_red() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from(((0, 1), (0, 2), (3, 4)))
    return graph


def target_blue() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from(((0, 1), (0, 2), (3, 4), (3, 5)))
    return graph


RED = target_red()
BLUE = target_blue()


def contains_monomorph(host: nx.Graph, target: nx.Graph) -> bool:
    if host.number_of_nodes() < target.number_of_nodes() or host.number_of_edges() < target.number_of_edges():
        return False
    return nx.algorithms.isomorphism.GraphMatcher(host, target).subgraph_is_monomorphic()


def connected_types_from_geng():
    types: list[dict] = []
    stream_hash = hashlib.sha256()
    stderr_rows = []
    for n in range(2, MAX_EDGES + 2):
        command = [str(GENG), "-cq", str(n), f"1:{MAX_EDGES}"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert process.stdout is not None
        for raw in process.stdout:
            stream_hash.update(raw)
            graph = nx.from_graph6_bytes(raw.strip())
            m = graph.number_of_edges()
            if 1 <= m <= MAX_EDGES:
                edges = tuple(sorted(tuple(sorted(e)) for e in graph.edges()))
                types.append({"n": n, "m": m, "edges": edges, "g6": raw.strip().decode("ascii")})
        stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        code = process.wait()
        if code:
            raise RuntimeError(f"geng failed at n={n} with code {code}: {stderr}")
        stderr_rows.append(stderr)
    types.sort(key=lambda c: (c["m"], c["n"], c["g6"]))
    return types, stream_hash.hexdigest(), stderr_rows


def component_multisets(types: list[dict], total_edges: int):
    def rec(start: int, remaining: int, acc: list[dict]):
        if remaining == 0:
            yield tuple(acc)
            return
        for i in range(start, len(types)):
            component = types[i]
            if component["m"] > remaining:
                break
            acc.append(component)
            yield from rec(i, remaining - component["m"], acc)
            acc.pop()

    yield from rec(0, total_edges, [])


def assemble(components: tuple[dict, ...]) -> nx.Graph:
    host = nx.Graph()
    offset = 0
    for component in components:
        host.add_nodes_from(range(offset, offset + component["n"]))
        host.add_edges_from((a + offset, b + offset) for a, b in component["edges"])
        offset += component["n"]
    return host


def avoiding_coloring(host: nx.Graph) -> int | None:
    edges = tuple(sorted(tuple(sorted(edge)) for edge in host.edges()))
    full = (1 << len(edges)) - 1
    for red_mask in range(full + 1):
        red = nx.Graph()
        blue = nx.Graph()
        red.add_nodes_from(host.nodes())
        blue.add_nodes_from(host.nodes())
        red.add_edges_from(edges[i] for i in range(len(edges)) if red_mask >> i & 1)
        blue.add_edges_from(edges[i] for i in range(len(edges)) if not (red_mask >> i & 1))
        if not contains_monomorph(red, RED) and not contains_monomorph(blue, BLUE):
            return red_mask
    return None


def saved_coloring_is_avoiding(row: dict) -> bool:
    n = int(row["n"])
    edges = tuple(tuple(edge) for edge in row["edges"])
    red_mask = int(row["avoiding_red_mask"])
    red = nx.Graph()
    blue = nx.Graph()
    red.add_nodes_from(range(n))
    blue.add_nodes_from(range(n))
    red.add_edges_from(edges[i] for i in range(len(edges)) if red_mask >> i & 1)
    blue.add_edges_from(edges[i] for i in range(len(edges)) if not (red_mask >> i & 1))
    return not contains_monomorph(red, RED) and not contains_monomorph(blue, BLUE)


def main() -> None:
    started = time.time()
    if not GENG.exists():
        raise FileNotFoundError(GENG)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    saved = json.loads(WITNESSES.read_text(encoding="utf-8"))
    saved_failures = [
        index for index, row in enumerate(saved["records"])
        if not saved_coloring_is_avoiding(row)
    ]
    types, stream_hash, stderr_rows = connected_types_from_geng()
    connected_counts = Counter(component["m"] for component in types)
    host_counts: Counter[int] = Counter()
    arrowing = []
    witness_rows = []
    for m in range(1, MAX_EDGES + 1):
        for components in component_multisets(types, m):
            host = assemble(components)
            witness = avoiding_coloring(host)
            host_counts[m] += 1
            signature = ",".join(component["g6"] for component in components)
            if witness is None:
                arrowing.append({"m": m, "component_graph6": signature.split(",")})
            else:
                witness_rows.append(f"{m}:{signature}:{witness}")

    main_connected = {int(k): int(v) for k, v in source["connected_type_counts_by_edges"].items()}
    main_hosts = {int(k): int(v) for k, v in source["host_type_counts_by_edges"].items()}
    counts_agree = (
        dict(connected_counts) == main_connected and dict(host_counts) == main_hosts
    )
    saved_count_ok = len(saved["records"]) == sum(host_counts.values())
    saved_hash_ok = (
        hashlib.sha256(WITNESSES.read_bytes()).hexdigest()
        == source["avoiding_colorings_file_sha256"]
    )
    verified = (
        counts_agree
        and not arrowing
        and not saved_failures
        and saved_count_ok
        and saved_hash_ok
        and source["outcome"] == "NO_COUNTEREXAMPLE_AT_MOST_7_EDGES"
    )
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "geng_path": str(GENG),
        "geng_sha256": hashlib.sha256(GENG.read_bytes()).hexdigest(),
        "geng_graph6_stream_sha256": stream_hash,
        "geng_stderr": stderr_rows,
        "method": "nauty geng connected types; component multisets; NetworkX VF2 monomorphism; all colorings",
        "independent_connected_type_counts_by_edges": {
            str(m): connected_counts[m] for m in range(1, MAX_EDGES + 1)
        },
        "independent_host_type_counts_by_edges": {
            str(m): host_counts[m] for m in range(1, MAX_EDGES + 1)
        },
        "counts_agree": counts_agree,
        "saved_avoiding_colorings_checked": len(saved["records"]),
        "saved_avoiding_coloring_failures": saved_failures,
        "saved_count_ok": saved_count_ok,
        "saved_hash_ok": saved_hash_ok,
        "arrowing_hosts": arrowing,
        "avoiding_witness_rows_sha256": hashlib.sha256(
            "\n".join(witness_rows).encode("ascii")
        ).hexdigest(),
        "elapsed_seconds": time.time() - started,
        "full_problem_resolved": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
