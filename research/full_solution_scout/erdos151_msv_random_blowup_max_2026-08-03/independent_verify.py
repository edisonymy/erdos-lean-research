"""Independent definition-level verifier for exported MSV finite graphs.

This checker deliberately imports nothing from msv_s3_probe.py.  It reparses
the edge list, enumerates triangles, checks K4-freeness, and replays every
reported independent-set and induced-triangle-free witness.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


R3_UPPER = {
    2: 3, 3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36,
    10: 41, 11: 50, 12: 59, 13: 68, 14: 77, 15: 87, 16: 97,
    17: 109, 18: 120, 19: 132, 20: 145, 21: 157, 22: 171, 23: 185,
}


def certified_h(n: int) -> int:
    return max(k for k, upper in R3_UPPER.items() if upper <= n)


def parse_graph(record: dict) -> tuple[int, list[set[int]]]:
    graph = record["graph"]
    n = graph["n"]
    if not isinstance(n, int) or n < 0:
        raise AssertionError("invalid vertex count")
    adjacency = [set() for _ in range(n)]
    seen: set[tuple[int, int]] = set()
    for raw in graph["edges"]:
        if not isinstance(raw, list) or len(raw) != 2:
            raise AssertionError(f"malformed edge {raw!r}")
        u, v = raw
        if not all(isinstance(x, int) and 0 <= x < n for x in (u, v)):
            raise AssertionError(f"out-of-range edge {raw!r}")
        if u == v:
            raise AssertionError(f"loop {raw!r}")
        edge = (min(u, v), max(u, v))
        if edge in seen:
            raise AssertionError(f"duplicate edge {edge!r}")
        seen.add(edge)
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    return n, adjacency


def triangles(adjacency: list[set[int]]) -> list[tuple[int, int, int]]:
    found = []
    for a in range(len(adjacency)):
        for b in (v for v in adjacency[a] if v > a):
            for c in adjacency[a].intersection(adjacency[b]):
                if c > b:
                    found.append((a, b, c))
    return found


def find_k4(adjacency: list[set[int]]) -> tuple[int, int, int, int] | None:
    # Independent common-neighbour implementation on Python sets.
    for a in range(len(adjacency)):
        for b in (v for v in adjacency[a] if v > a):
            common = sorted(v for v in adjacency[a].intersection(adjacency[b]) if v > b)
            for i, c in enumerate(common):
                for d in common[i + 1:]:
                    if d in adjacency[c]:
                        return a, b, c, d
    return None


def replay_witness(
    adjacency: list[set[int]], witness: list[int], triangle_free: bool
) -> None:
    if len(witness) != len(set(witness)):
        raise AssertionError("witness repeats a vertex")
    if any(not isinstance(v, int) or not 0 <= v < len(adjacency) for v in witness):
        raise AssertionError("witness contains an invalid vertex")
    if triangle_free:
        for a, b, c in itertools.combinations(witness, 3):
            if b in adjacency[a] and c in adjacency[a] and c in adjacency[b]:
                raise AssertionError(f"claimed triangle-free witness contains {(a,b,c)}")
    else:
        for a, b in itertools.combinations(witness, 2):
            if b in adjacency[a]:
                raise AssertionError(f"claimed independent witness contains edge {(a,b)}")


def verify_record(record: dict) -> dict:
    n, adjacency = parse_graph(record)
    h = record["h_certificate"]["h"]
    expected_h = certified_h(n)
    if h != expected_h:
        raise AssertionError(f"H certificate mismatch: reported {h}, table gives {expected_h}")
    k4 = find_k4(adjacency)
    if k4 is not None:
        raise AssertionError(f"K4 found: {k4}")
    tri = triangles(adjacency)
    reported_tri = record["final"]["intrinsic_triangles_surviving_d2"]
    if len(tri) != reported_tri:
        raise AssertionError(
            f"triangle-count mismatch: enumerated {len(tri)}, reported {reported_tri}"
        )
    degrees = [len(neighbours) for neighbours in adjacency]
    if max(degrees, default=0) != record["degree"]["max"]:
        raise AssertionError("maximum degree mismatch")
    if sum(degrees) // 2 != record["final"]["final_edges"]:
        raise AssertionError("edge count mismatch")

    graph_edges = {
        (min(u, v), max(u, v))
        for u in range(n)
        for v in adjacency[u]
        if u < v
    }
    colour_map: dict[tuple[int, int], str] = {}
    for raw in record.get("good_edge_colouring", []):
        if not isinstance(raw, list) or len(raw) != 3:
            raise AssertionError(f"malformed coloured edge {raw!r}")
        u, v, colour = raw
        edge = (min(u, v), max(u, v))
        if colour not in ("red", "blue") or edge in colour_map:
            raise AssertionError(f"invalid or duplicate coloured edge {raw!r}")
        colour_map[edge] = colour
    if colour_map:
        if set(colour_map) != graph_edges:
            raise AssertionError("edge colouring does not cover the graph exactly")
        for a, b, c in tri:
            colours = {
                colour_map[(a, b)],
                colour_map[(a, c)],
                colour_map[(b, c)],
            }
            if len(colours) == 1:
                raise AssertionError(f"monochromatic triangle {(a,b,c)}")

    lower = record["lower_bounds"]
    if "alpha_witness" in lower:
        replay_witness(adjacency, lower["alpha_witness"], triangle_free=False)
        if len(lower["alpha_witness"]) != lower["alpha_lower"]:
            raise AssertionError("alpha witness length mismatch")
    if "tf3_witness" in lower:
        replay_witness(adjacency, lower["tf3_witness"], triangle_free=True)
        if len(lower["tf3_witness"]) != lower["tf3_lower"]:
            raise AssertionError("tf3 witness length mismatch")

    necessary = math.ceil(math.comb(n, 3) / math.comb(h, 3))
    return {
        "status": "PASS",
        "n": n,
        "h": h,
        "edges": sum(degrees) // 2,
        "max_degree": max(degrees, default=0),
        "triangles": len(tri),
        "triangle_coverage_necessary_minimum": necessary,
        "k4_check": "PASS",
        "alpha_witness_replay": "PASS" if "alpha_witness" in lower else "NOT_PRESENT",
        "tf3_witness_replay": "PASS" if "tf3_witness" in lower else "NOT_PRESENT",
        "nonarrowing_edge_colouring": "PASS" if colour_map else "NOT_PRESENT",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else [payload]
    result = {
        "status": "PASS",
        "checker": "independent_verify.py (no import from generator)",
        "records": [verify_record(record) for record in records],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
