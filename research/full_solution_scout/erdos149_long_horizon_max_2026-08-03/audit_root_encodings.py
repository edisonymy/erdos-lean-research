#!/usr/bin/env python3
"""Hostile, independently executable audit of the root order-12 encodings.

This does not infer correctness from solver agreement.  It checks the abstract
saving-pattern lemma exhaustively, reconstructs both mathematical suffixes,
tests the sequential cardinality blocks under forced assignments, compares
the regenerated DIMACS byte-for-byte, checks stored hashes, and replays LRAT.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import random
import subprocess
from functools import lru_cache
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
ROOT = WORKSPACE / "research/full_solution_scout/erdos149_long_horizon_root_2026-08-03"
LRAT_CHECK = WORKSPACE / "tools/proof_checkers/windows_drat/bin/lrat-check.exe"
N = 12
PAIRS = [(a, b) for a in range(N) for b in range(a + 1, N)]
VAR = {edge: index + 1 for index, edge in enumerate(PAIRS)}
TRIANGLE = ((0, 1), (2, 3), (4, 5))


def norm(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def ve(edge: tuple[int, int]) -> int:
    return VAR[norm(*edge)]


def crosses(e: tuple[int, int], f: tuple[int, int]) -> list[tuple[int, int]]:
    a, b = e
    c, d = f
    return [norm(a, c), norm(a, d), norm(b, c), norm(b, d)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_dimacs(path: Path) -> tuple[int, list[list[int]]]:
    nv = None
    expected = None
    clauses: list[list[int]] = []
    for raw in path.read_text(encoding="ascii").splitlines():
        if not raw or raw.startswith("c"):
            continue
        if raw.startswith("p "):
            _, kind, nvs, ncs = raw.split()
            assert kind == "cnf"
            nv, expected = int(nvs), int(ncs)
            continue
        values = [int(x) for x in raw.split()]
        assert values and values[-1] == 0
        clauses.append(values[:-1])
    assert nv is not None and expected == len(clauses)
    assert all(0 < abs(lit) <= nv for clause in clauses for lit in clause)
    return nv, clauses


def is_clique(vertices: int, adjacency: list[int]) -> bool:
    bits = vertices
    while bits:
        low = bits & -bits
        v = low.bit_length() - 1
        rest = vertices ^ low
        if rest & ~adjacency[v]:
            return False
        bits ^= low
    return True


def packing_saving(adjacency: list[int]) -> int:
    """Exact maximum sum(|C|-1) over disjoint cliques."""

    @lru_cache(maxsize=None)
    def best(mask: int) -> int:
        if not mask:
            return 0
        low = mask & -mask
        v = low.bit_length() - 1
        remaining = mask ^ low
        ans = best(remaining)  # leave v as a singleton
        candidates = remaining & adjacency[v]
        sub = candidates
        while sub:
            clique = low | sub
            if is_clique(clique, adjacency):
                ans = max(ans, clique.bit_count() - 1 + best(mask ^ clique))
            sub = (sub - 1) & candidates
        return ans

    return best((1 << len(adjacency)) - 1)


def listed_triangle_patterns(adjacency: list[int]) -> bool:
    """The four patterns stated in RESULT.md, with T={0,1,2}."""
    outside = range(3, len(adjacency))

    # An edge of J disjoint from T.
    if any((adjacency[u] >> v) & 1 for u, v in itertools.combinations(outside, 2)):
        return True

    # A K4 containing T.
    if any(all((adjacency[u] >> i) & 1 for i in range(3)) for u in outside):
        return True

    # An alternate triangle on u and two T vertices, plus v--remaining-T.
    for u in outside:
        for i, j in itertools.combinations(range(3), 2):
            k = 3 - i - j
            if not ((adjacency[u] >> i) & 1 and (adjacency[u] >> j) & 1):
                continue
            if any(v != u and ((adjacency[v] >> k) & 1) for v in outside):
                return True

    # A matching of size three.  With no outside edge, it is a bijection T--outside.
    for chosen in itertools.combinations(outside, 3):
        for permutation in itertools.permutations(range(3)):
            if all((adjacency[chosen[p]] >> permutation[p]) & 1 for p in range(3)):
                return True
    return False


def exhaustive_pattern_audit() -> dict:
    # Every minimal saving-three obstruction uses at most six vertices.  Enumerate
    # all 2^(15-3)=4096 graphs on six vertices containing the fixed triangle.
    all_edges = list(itertools.combinations(range(6), 2))
    fixed = {(0, 1), (0, 2), (1, 2)}
    free = [e for e in all_edges if e not in fixed]
    mismatches = []
    saving_histogram: dict[int, int] = {}
    for mask in range(1 << len(free)):
        adjacency = [0] * 6
        selected = set(fixed)
        selected.update(free[i] for i in range(len(free)) if (mask >> i) & 1)
        for u, v in selected:
            adjacency[u] |= 1 << v
            adjacency[v] |= 1 << u
        saving = packing_saving(adjacency)
        saving_histogram[saving] = saving_histogram.get(saving, 0) + 1
        listed = listed_triangle_patterns(adjacency)
        if (saving >= 3) != listed:
            mismatches.append({"mask": mask, "saving": saving, "listed": listed})
    assert not mismatches
    return {
        "graphs_checked": 1 << len(free),
        "free_edges": len(free),
        "mismatches": 0,
        "saving_histogram": saving_histogram,
    }


def cardinality_prefix(m: int) -> tuple[list[list[int]], list[tuple[list[list[int]], list[int]]], list[list[int]], list[int], int]:
    pool = IDPool(start_from=len(PAIRS) + 1)
    prefix: list[list[int]] = []
    degree_blocks = []
    for vertex in range(N):
        inputs = [ve(norm(vertex, other)) for other in range(N) if other != vertex]
        block = CardEnc.atmost(inputs, 4, vpool=pool, encoding=EncType.seqcounter).clauses
        prefix.extend(block)
        degree_blocks.append((block, inputs))
    global_inputs = [ve(edge) for edge in PAIRS]
    global_block = CardEnc.equals(global_inputs, m, vpool=pool, encoding=EncType.seqcounter).clauses
    prefix.extend(global_block)
    return prefix, degree_blocks, global_block, global_inputs, pool.top


def audit_cardinality_semantics(m: int) -> dict:
    prefix, degree_blocks, global_block, global_inputs, top = cardinality_prefix(m)
    local_tests = 0
    for block, inputs in degree_blocks:
        with Solver(name="g4", bootstrap_with=block) as solver:
            for mask in range(1 << len(inputs)):
                assumptions = [lit if (mask >> i) & 1 else -lit for i, lit in enumerate(inputs)]
                assert solver.solve(assumptions=assumptions) == (mask.bit_count() <= 4)
                local_tests += 1

    rng = random.Random(149000 + m)
    global_tests = 0
    with Solver(name="g4", bootstrap_with=global_block) as solver:
        for count in range(len(global_inputs) + 1):
            representatives = [
                set(range(count)),
                set(range(len(global_inputs) - count, len(global_inputs))),
                set(rng.sample(range(len(global_inputs)), count)),
            ]
            for chosen in representatives:
                assumptions = [lit if i in chosen else -lit for i, lit in enumerate(global_inputs)]
                assert solver.solve(assumptions=assumptions) == (count == m)
                global_tests += 1
    return {
        "m": m,
        "prefix_clauses": len(prefix),
        "last_cardinality_variable": top,
        "degree_forced_assignments_checked": local_tests,
        "global_representatives_checked": global_tests,
    }


def eval_cnf(clauses: list[list[int]], positive: set[int]) -> bool:
    return all(any((lit > 0 and lit in positive) or (lit < 0 and -lit not in positive) for lit in clause) for clause in clauses)


def compatible(e: tuple[int, int], f: tuple[int, int], present: set[tuple[int, int]]) -> bool:
    return len(set(e) | set(f)) == 4 and all(cross not in present for cross in crosses(e, f))


def expected_m22_suffix() -> list[list[int]]:
    centre, leaf = (0, 1), (2, 3)
    suffix = [[ve(centre)], [ve(leaf)]]
    suffix.extend([[-ve(cross)] for cross in crosses(centre, leaf)])
    for index, first in enumerate(PAIRS):
        if first == centre:
            continue
        for second in PAIRS[index + 1 :]:
            if second == centre or len(set(first) | set(second)) != 4:
                continue
            suffix.append([-ve(first), -ve(second), *[ve(x) for x in crosses(first, second)]])
    return suffix


def audit_m22_structure(clauses: list[list[int]], prefix_length: int) -> dict:
    suffix = clauses[prefix_length:]
    expected = expected_m22_suffix()
    assert suffix == expected
    rng = random.Random(14922)
    trials = 5000
    for _ in range(trials):
        present = {edge for edge in PAIRS if rng.random() < 0.34}
        present.update(((0, 1), (2, 3)))
        present.difference_update(crosses((0, 1), (2, 3)))
        positives = {ve(edge) for edge in present}
        compat = [(e, f) for e, f in itertools.combinations(present, 2) if compatible(e, f, present)]
        semantic = compatible((0, 1), (2, 3), present) and all((0, 1) in pair for pair in compat)
        assert eval_cnf(suffix, positives) == semantic
    return {"suffix_clauses": len(suffix), "random_semantic_trials": trials, "exact_clause_match": True}


def expected_m23_suffix(card_top: int) -> tuple[list[list[int]], dict[tuple[tuple[int, int], int], int]]:
    suffix: list[list[int]] = []
    for edge in TRIANGLE:
        suffix.append([ve(edge)])
    for first, second in itertools.combinations(TRIANGLE, 2):
        suffix.extend([[-ve(cross)] for cross in crosses(first, second)])

    outside = [edge for edge in PAIRS if edge not in TRIANGLE]
    for index, first in enumerate(outside):
        for second in outside[index + 1 :]:
            if len(set(first) | set(second)) == 4:
                suffix.append([-ve(first), -ve(second), *[ve(x) for x in crosses(first, second)]])

    compat_vars: dict[tuple[tuple[int, int], int], int] = {}
    next_id = card_top + 1
    for edge in outside:
        for index, fixed in enumerate(TRIANGLE):
            if len(set(edge) | set(fixed)) != 4:
                continue
            indicator = next_id
            next_id += 1
            compat_vars[(edge, index)] = indicator
            suffix.append([-indicator, ve(edge)])
            suffix.extend([[-indicator, -ve(cross)] for cross in crosses(edge, fixed)])
            suffix.append([-ve(edge), *[ve(cross) for cross in crosses(edge, fixed)], indicator])

    for edge in outside:
        indicators = [compat_vars.get((edge, index)) for index in range(3)]
        if all(indicators):
            suffix.append([-int(x) for x in indicators])

    for u in outside:
        for i, j in itertools.combinations(range(3), 2):
            k = 3 - i - j
            ui, uj = compat_vars.get((u, i)), compat_vars.get((u, j))
            if ui is None or uj is None:
                continue
            for v in outside:
                if v != u and (vk := compat_vars.get((v, k))) is not None:
                    suffix.append([-ui, -uj, -vk])

    for chosen in itertools.combinations(outside, 3):
        for permutation in itertools.permutations(range(3)):
            indicators = [compat_vars.get((chosen[p], permutation[p])) for p in range(3)]
            if all(indicators):
                suffix.append([-int(x) for x in indicators])
    return suffix, compat_vars


def direct_listed_patterns_for_graph(present: set[tuple[int, int]]) -> bool:
    outside = [edge for edge in present if edge not in TRIANGLE]
    if any(compatible(u, v, present) for u, v in itertools.combinations(outside, 2)):
        return True
    neighbours = {u: {i for i, t in enumerate(TRIANGLE) if compatible(u, t, present)} for u in outside}
    if any(len(neighbours[u]) == 3 for u in outside):
        return True
    for u in outside:
        for i, j in itertools.combinations(neighbours[u], 2):
            k = 3 - i - j
            if any(v != u and k in neighbours[v] for v in outside):
                return True
    for chosen in itertools.combinations(outside, 3):
        for permutation in itertools.permutations(range(3)):
            if all(permutation[p] in neighbours[chosen[p]] for p in range(3)):
                return True
    return False


def audit_m23_structure(clauses: list[list[int]], prefix_length: int, card_top: int) -> dict:
    suffix = clauses[prefix_length:]
    expected, compat_vars = expected_m23_suffix(card_top)
    assert suffix == expected
    rng = random.Random(14923)
    trials = 1000
    with Solver(name="g4", bootstrap_with=suffix) as solver:
        for _ in range(trials):
            present = {edge for edge in PAIRS if rng.random() < 0.34}
            present.update(TRIANGLE)
            for first, second in itertools.combinations(TRIANGLE, 2):
                present.difference_update(crosses(first, second))
            assumptions = [ve(edge) if edge in present else -ve(edge) for edge in PAIRS]
            expected_sat = not direct_listed_patterns_for_graph(present)
            assert solver.solve(assumptions=assumptions) == expected_sat
    return {
        "suffix_clauses": len(suffix),
        "compatibility_indicators": len(compat_vars),
        "random_semantic_trials": trials,
        "exact_clause_match": True,
    }


def replay_lrat(cnf: Path, proof: Path) -> dict:
    proc = subprocess.run([str(LRAT_CHECK), str(cnf), str(proof)], capture_output=True, text=True, check=True)
    output = proc.stdout + proc.stderr
    assert "c VERIFIED" in output
    return {"verified": True, "output": output.strip().splitlines()}


def main() -> None:
    certification = json.loads((ROOT / "CERTIFICATION.json").read_text(encoding="utf-8"))
    expected_hashes = {
        "exact_n12_m22_star_sat.py": certification["generator"]["sha256"],
        "m22_cert.cnf": certification["cnf"]["sha256"],
        "m22_pinned.drat": certification["drat"]["sha256"],
        "m22_pinned.lrat": certification["lrat"]["sha256"],
        "exact_n12_m23_triangle_sat.py": certification["m23_triangle_slice"]["generator"]["sha256"],
        "m23_triangle.cnf": certification["m23_triangle_slice"]["cnf"]["sha256"],
        "m23_triangle_pinned.drat": certification["m23_triangle_slice"]["drat"]["sha256"],
        "m23_triangle_pinned.lrat": certification["m23_triangle_slice"]["lrat"]["sha256"],
    }
    observed_hashes = {name: sha256(ROOT / name) for name in expected_hashes}
    assert observed_hashes == expected_hashes
    assert sha256(LRAT_CHECK) == certification["lrat"]["checker_sha256"]

    m22_module = load_module(ROOT / "exact_n12_m22_star_sat.py", "root_m22")
    m23_module = load_module(ROOT / "exact_n12_m23_triangle_sat.py", "root_m23")
    m22_generated = m22_module.dimacs_bytes(m22_module.build_cnf())
    m23_generated_cnf, _ = m23_module.build_cnf()
    m23_generated = m23_module.dimacs_bytes(m23_generated_cnf)
    assert m22_generated == (ROOT / "m22_cert.cnf").read_bytes()
    assert m23_generated == (ROOT / "m23_triangle.cnf").read_bytes()

    nv22, clauses22 = parse_dimacs(ROOT / "m22_cert.cnf")
    nv23, clauses23 = parse_dimacs(ROOT / "m23_triangle.cnf")
    prefix22, _, _, _, top22 = cardinality_prefix(22)
    prefix23, _, _, _, top23 = cardinality_prefix(23)
    assert clauses22[: len(prefix22)] == prefix22
    assert clauses23[: len(prefix23)] == prefix23

    report = {
        "schema": "erdos149-root-definition-audit-v1",
        "status": "VERIFIED",
        "hashes": observed_hashes,
        "dimacs": {
            "m22": {"variables": nv22, "clauses": len(clauses22), "byte_exact_regeneration": True},
            "m23_triangle": {"variables": nv23, "clauses": len(clauses23), "byte_exact_regeneration": True},
        },
        "abstract_saving_pattern_classification": exhaustive_pattern_audit(),
        "cardinality_m22": audit_cardinality_semantics(22),
        "cardinality_m23": audit_cardinality_semantics(23),
        "m22_structure": audit_m22_structure(clauses22, len(prefix22)),
        "m23_triangle_structure": audit_m23_structure(clauses23, len(prefix23), top23),
        "lrat": {
            "m22": replay_lrat(ROOT / "m22_cert.cnf", ROOT / "m22_pinned.lrat"),
            "m23_triangle": replay_lrat(ROOT / "m23_triangle.cnf", ROOT / "m23_triangle_pinned.lrat"),
        },
        "claim_boundary": (
            "This verifies the two stored formulas and their mappings only.  It excludes the order-12 m=22 slice "
            "and the triangle-containing order-12 m=23 slice after the separately written mathematical reduction; "
            "it neither covers triangle-free m=23 nor resolves the full conjecture."
        ),
    }
    output = HERE / "root_definition_audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
