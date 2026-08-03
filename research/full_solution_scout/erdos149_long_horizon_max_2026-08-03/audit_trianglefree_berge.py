#!/usr/bin/env python3
"""Fresh definition-level audit of exact_n12_m23_trianglefree_berge.py.

The audit reconstructs each clause family independently, exhausts the abstract
Berge obstruction and endpoint-overlap classifications, tests cardinality
semantics, regenerates every CNF, checks hashes, and replays each LRAT proof.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
GENERATOR = HERE / "exact_n12_m23_trianglefree_berge.py"
ARTIFACTS = HERE / "trianglefree_cnfs"
LRAT_CHECK = WORKSPACE / "tools/proof_checkers/windows_drat/bin/lrat-check.exe"
N, M = 12, 23
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
VAR = {edge: i + 1 for i, edge in enumerate(PAIRS)}
CASES = {
    "overlap0": ((0, 1), (2, 3), (4, 5), (6, 7)),
    "overlap1": ((0, 1), (2, 3), (0, 4), (5, 6)),
    "overlap2": ((0, 1), (2, 3), (0, 4), (2, 5)),
}


def norm(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def ve(edge: tuple[int, int]) -> int:
    return VAR[norm(*edge)]


def crosses(e: tuple[int, int], f: tuple[int, int]) -> list[tuple[int, int]]:
    return [norm(x, y) for x in e for y in f]


def key(e: tuple[int, int], f: tuple[int, int]):
    return (e, f) if VAR[e] < VAR[f] else (f, e)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> tuple[int, list[list[int]]]:
    nv = nc = None
    clauses = []
    for line in path.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            _, kind, nvs, ncs = line.split()
            assert kind == "cnf"
            nv, nc = int(nvs), int(ncs)
        else:
            row = [int(x) for x in line.split()]
            assert row[-1] == 0
            clauses.append(row[:-1])
    assert nv is not None and nc == len(clauses)
    assert all(0 < abs(lit) <= nv for clause in clauses for lit in clause)
    return nv, clauses


def canonical_counter(clauses: list[list[int]]) -> Counter:
    return Counter(tuple(sorted(clause)) for clause in clauses)


def independent_base() -> tuple[list[list[int]], dict, int, dict]:
    degree = []
    for v in range(N):
        incident = [norm(v, w) for w in range(N) if w != v]
        degree.extend([[-ve(edge) for edge in five] for five in itertools.combinations(incident, 5)])

    pool = IDPool(start_from=67)
    totalizer = CardEnc.equals(
        [ve(edge) for edge in PAIRS], M, vpool=pool, encoding=EncType.totalizer
    ).clauses
    totalizer_top = pool.top

    qvars = {}
    qclauses = []
    for e, f in itertools.combinations(PAIRS, 2):
        if len(set(e) | set(f)) != 4:
            continue
        q = pool.id(("compat", e, f))
        qvars[key(e, f)] = q
        qclauses.extend([[-q, ve(e)], [-q, ve(f)]])
        qclauses.extend([[-q, -ve(c)] for c in crosses(e, f)])
        qclauses.append([-ve(e), -ve(f), *[ve(c) for c in crosses(e, f)], q])
    metadata = {
        "degree_clauses": len(degree),
        "totalizer_clauses": len(totalizer),
        "totalizer_top": totalizer_top,
        "compatibility_variables": len(qvars),
        "compatibility_clauses": len(qclauses),
        "base_clauses": len(degree) + len(totalizer) + len(qclauses),
    }
    return degree + totalizer + qclauses, qvars, pool.top, metadata


def q(qvars, e, f):
    return qvars.get(key(e, f))


def independent_triangles(qvars) -> list[list[int]]:
    clauses = []
    for a, b, c in itertools.combinations(PAIRS, 3):
        values = (q(qvars, a, b), q(qvars, a, c), q(qvars, b, c))
        if all(x is not None for x in values):
            clauses.append([-int(x) for x in values])
    return clauses


def independent_star(qvars) -> list[list[int]]:
    centre, leaf = (0, 1), (2, 3)
    clauses = [[q(qvars, centre, leaf)]]
    clauses.extend([[-value] for (e, f), value in qvars.items() if centre not in (e, f)])
    return clauses


def independent_berge(qvars, fixed) -> tuple[list[list[int]], dict]:
    a, b, c, d = fixed
    matching = ((a, b), (c, d))
    clauses = [[q(qvars, a, b)], [q(qvars, c, d)]]
    unmatched = [edge for edge in PAIRS if edge not in set(fixed)]
    counts = {"length1": 0, "length3": 0, "length5": 0}

    for u, v in itertools.combinations(unmatched, 2):
        value = q(qvars, u, v)
        if value is not None:
            clauses.append([-value])
            counts["length1"] += 1

    for x, y in matching:
        for u, v in itertools.permutations(unmatched, 2):
            ux, yv = q(qvars, u, x), q(qvars, y, v)
            if ux is not None and yv is not None:
                clauses.append([-ux, -yv])
                counts["length3"] += 1

    for first, second in ((matching[0], matching[1]), (matching[1], matching[0])):
        for x1, y1 in (first, first[::-1]):
            for x2, y2 in (second, second[::-1]):
                middle = q(qvars, y1, x2)
                if middle is None:
                    continue
                for u, v in itertools.permutations(unmatched, 2):
                    left, right = q(qvars, u, x1), q(qvars, y2, v)
                    if left is not None and right is not None:
                        clauses.append([-left, -middle, -right])
                        counts["length5"] += 1

    triangles = independent_triangles(qvars)
    clauses.extend(triangles)
    counts["triangles"] = len(triangles)
    return clauses, counts


def audit_totalizer() -> dict:
    pool = IDPool(start_from=67)
    block = CardEnc.equals(
        [ve(edge) for edge in PAIRS], M, vpool=pool, encoding=EncType.totalizer
    ).clauses
    rng = random.Random(1492301)
    tests = 0
    with Solver(name="g4", bootstrap_with=block) as solver:
        for count in range(67):
            samples = [
                set(range(count)),
                set(range(66 - count, 66)),
                set(rng.sample(range(66), count)),
            ]
            for chosen in samples:
                assumptions = [i + 1 if i in chosen else -(i + 1) for i in range(66)]
                assert solver.solve(assumptions=assumptions) == (count == M)
                tests += 1
    return {"forced_assignments_checked": tests, "semantic_failures": 0}


def audit_compatibility_tseitin(qvars) -> dict:
    # Exhaust all 2^6 truth assignments for the two edge variables and four
    # crosses, for every one of the 1485 indicators, against the seven clauses.
    tests = 0
    for (e, f), indicator in qvars.items():
        inputs = [ve(e), ve(f), *[ve(c) for c in crosses(e, f)]]
        block = [[-indicator, ve(e)], [-indicator, ve(f)]]
        block.extend([[-indicator, -ve(c)] for c in crosses(e, f)])
        block.append([-ve(e), -ve(f), *[ve(c) for c in crosses(e, f)], indicator])
        with Solver(name="g4", bootstrap_with=block) as solver:
            for mask in range(64):
                assumptions = [lit if (mask >> i) & 1 else -lit for i, lit in enumerate(inputs)]
                expected = bool(mask & 1 and mask & 2 and not (mask & 0b111100))
                sat_true = solver.solve(assumptions=assumptions + [indicator])
                sat_false = solver.solve(assumptions=assumptions + [-indicator])
                assert sat_true == expected and sat_false == (not expected)
                tests += 1
    return {"indicators": len(qvars), "input_assignments_checked": tests, "semantic_failures": 0}


def no_augmenting_path(adjacency: list[set[int]]) -> bool:
    matching = ((0, 1), (2, 3))
    unmatched = range(4, 6)
    if any(v in adjacency[u] for u, v in itertools.combinations(unmatched, 2)):
        return False
    for x, y in matching:
        for u, v in itertools.permutations(unmatched, 2):
            if x in adjacency[u] and v in adjacency[y]:
                return False
    for first, second in ((matching[0], matching[1]), (matching[1], matching[0])):
        for x1, y1 in (first, first[::-1]):
            for x2, y2 in (second, second[::-1]):
                for u, v in itertools.permutations(unmatched, 2):
                    if x1 in adjacency[u] and x2 in adjacency[y1] and v in adjacency[y2]:
                        return False
    return True


def exhaustive_berge_audit() -> dict:
    vertices = range(6)
    fixed = {(0, 1), (2, 3)}
    free = [e for e in itertools.combinations(vertices, 2) if e not in fixed]
    mismatches = 0
    for mask in range(1 << len(free)):
        graph = nx.Graph()
        graph.add_nodes_from(vertices)
        selected = set(fixed)
        selected.update(free[i] for i in range(len(free)) if (mask >> i) & 1)
        graph.add_edges_from(selected)
        adjacency = [set(graph.neighbors(v)) for v in vertices]
        maximum_two = len(nx.max_weight_matching(graph, maxcardinality=True)) == 2
        if no_augmenting_path(adjacency) != maximum_two:
            mismatches += 1
    assert mismatches == 0
    return {"abstract_graphs_checked": 1 << len(free), "mismatches": 0}


def endpoint_overlap_audit() -> dict:
    # Fix the first compatible pair as 01,23. Enumerate the second pair on
    # eight vertices, retaining exactly the configurations in which neither
    # fixed G-edge destroys compatibility of the other pair.
    first = ((0, 1), (2, 3))
    edges8 = list(itertools.combinations(range(8), 2))
    histogram = Counter()
    for e, f in itertools.combinations(edges8, 2):
        if e in first or f in first or len(set(e) | set(f)) != 4:
            continue
        if e in crosses(*first) or f in crosses(*first):
            continue
        if first[0] in crosses(e, f) or first[1] in crosses(e, f):
            continue
        overlap_graph = nx.Graph()
        overlap_graph.add_nodes_from(range(4))
        all_edges = (*first, e, f)
        for i in range(2):
            for j in range(2, 4):
                if set(all_edges[i]) & set(all_edges[j]):
                    overlap_graph.add_edge(i, j)
        assert max(dict(overlap_graph.degree()).values(), default=0) <= 1
        histogram[overlap_graph.number_of_edges()] += 1
    assert set(histogram) == {0, 1, 2}
    return {
        "valid_fixed_configurations": sum(histogram.values()),
        "overlap_histogram": dict(histogram),
        "types": 3,
        "reason_complete": "the cross-pair endpoint-overlap graph is a matching, hence is classified by size 0, 1, or 2",
    }


def replay(cnf: Path, lrat: Path) -> list[str]:
    proc = subprocess.run([str(LRAT_CHECK), str(cnf), str(lrat)], capture_output=True, text=True, check=True)
    output = (proc.stdout + proc.stderr).strip().splitlines()
    assert any("c VERIFIED" in line for line in output)
    return output


def main() -> None:
    spec = importlib.util.spec_from_file_location("residual_generator", GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    stored = json.loads((ARTIFACTS / "result.json").read_text(encoding="utf-8"))
    base, qvars, top, base_meta = independent_base()
    assert top == 2351
    reports = {}
    for case in ("star", *CASES):
        path = ARTIFACTS / f"{case}.cnf"
        nv, clauses = parse(path)
        assert nv == 2351
        assert clauses[: len(base)] == base
        expected_tail = independent_star(qvars) if case == "star" else independent_berge(qvars, CASES[case])[0]
        assert canonical_counter(clauses[len(base) :]) == canonical_counter(expected_tail)

        regenerated, _ = module.build(case)
        assert module.dimacs_bytes(regenerated) == path.read_bytes()
        assert sha(path) == stored["cases"][case]["cnf"]["sha256"]
        reports[case] = {
            "variables": nv,
            "clauses": len(clauses),
            "base_clause_match": True,
            "case_clause_multiset_match": True,
            "byte_exact_regeneration": True,
            "cnf_sha256": sha(path),
            "drat": {"bytes": (ARTIFACTS / f"{case}.drat").stat().st_size, "sha256": sha(ARTIFACTS / f"{case}.drat")},
            "lrat": {"bytes": (ARTIFACTS / f"{case}.lrat").stat().st_size, "sha256": sha(ARTIFACTS / f"{case}.lrat"), "replay": replay(path, ARTIFACTS / f"{case}.lrat")},
        }

    report = {
        "schema": "erdos149-n12-m23-trianglefree-fresh-audit-v1",
        "status": "VERIFIED",
        "generator": {"bytes": GENERATOR.stat().st_size, "sha256": sha(GENERATOR)},
        "proof_checker": {"path": str(LRAT_CHECK), "sha256": sha(LRAT_CHECK)},
        "base": base_meta,
        "degree_semantics": "all 5-subsets of each 11-edge incidence set are forbidden, exactly equivalent to degree at most four",
        "totalizer_semantics": audit_totalizer(),
        "compatibility_tseitin": audit_compatibility_tseitin(qvars),
        "triangle_clause_count": len(independent_triangles(qvars)),
        "berge_completeness": exhaustive_berge_audit(),
        "matching_endpoint_symmetry": endpoint_overlap_audit(),
        "cases": reports,
        "claim_boundary": (
            "The four UNSAT formulas exclude order-12 m=23 graphs whose triangle-free compatibility graph has matching number one or two. "
            "They do not by themselves cover the already separate triangle-containing slice, other edge counts, larger orders, or the full conjecture."
        ),
    }
    output = HERE / "trianglefree_fresh_audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
