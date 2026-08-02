"""Exact order-5-automorphism attack on Erdos problem 742 at n=25.

It generates a definition-level CNF for diameter-2-critical graphs, fixes
exactly 157 edges, and enforces a canonical automorphism of order five with a
specified number of fixed vertices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


N = 25
TARGET_EDGES = 157


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def edge_pairs(n: int = N):
    variable = 0
    for u in range(n):
        for v in range(u + 1, n):
            variable += 1
            yield variable, (u, v)


def canonical_permutation(fixed: int) -> list[int]:
    if fixed not in (0, 5, 10, 15, 20):
        raise ValueError("fixed must be one of 0, 5, 10, 15, 20")
    permutation = list(range(N))
    for start in range(fixed, N, 5):
        for offset in range(5):
            permutation[start + offset] = start + (offset + 1) % 5
    return permutation


def edge_orbits(fixed: int) -> list[list[tuple[int, int]]]:
    permutation = canonical_permutation(fixed)
    unseen = {pair for _, pair in edge_pairs()}
    answer = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current not in orbit:
            orbit.append(current)
            u, v = current
            current = tuple(sorted((permutation[u], permutation[v])))
        for pair in orbit:
            unseen.remove(pair)
        answer.append(sorted(orbit))
    return answer


def add_weighted_exact(
    formula: CNF, variables: list[int], weights: list[int], target: int
) -> dict:
    """Encode sum(weights[i] * variables[i]) == target by a one-hot DFA."""
    if len(variables) != len(weights):
        raise ValueError("variable/weight length mismatch")

    def fresh() -> int:
        formula.nv += 1
        return formula.nv

    before_nv, before_clauses = formula.nv, len(formula.clauses)
    previous = [fresh() for _ in range(target + 1)]
    formula.append([previous[0]])
    for state in previous[1:]:
        formula.append([-state])

    for variable, weight in zip(variables, weights):
        current = [fresh() for _ in range(target + 1)]
        exactly_one = CardEnc.equals(
            lits=current,
            bound=1,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(exactly_one.clauses)
        for subtotal, state in enumerate(previous):
            formula.append([-state, variable, current[subtotal]])
            if subtotal + weight <= target:
                formula.append([-state, -variable, current[subtotal + weight]])
            else:
                formula.append([-state, -variable])
        previous = current
    formula.append([previous[target]])
    return {
        "variables": formula.nv - before_nv,
        "clauses": len(formula.clauses) - before_clauses,
    }


def add_weighted_atmost(
    formula: CNF, variables: list[int], weights: list[int], bound: int
) -> dict:
    """Encode sum(weights[i] * variables[i]) <= bound by a one-hot DFA."""
    if len(variables) != len(weights):
        raise ValueError("variable/weight length mismatch")

    def fresh() -> int:
        formula.nv += 1
        return formula.nv

    before_nv, before_clauses = formula.nv, len(formula.clauses)
    previous = [fresh() for _ in range(bound + 1)]
    formula.append([previous[0]])
    for state in previous[1:]:
        formula.append([-state])
    for variable, weight in zip(variables, weights):
        current = [fresh() for _ in range(bound + 1)]
        exactly_one = CardEnc.equals(
            lits=current,
            bound=1,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(exactly_one.clauses)
        for subtotal, state in enumerate(previous):
            formula.append([-state, variable, current[subtotal]])
            if subtotal + weight <= bound:
                formula.append([-state, -variable, current[subtotal + weight]])
            else:
                formula.append([-state, -variable])
        previous = current
    return {
        "variables": formula.nv - before_nv,
        "clauses": len(formula.clauses) - before_clauses,
    }


def add_lex_leader(formula: CNF, left: list[int], right: list[int]) -> dict:
    """Encode left <=lex right for Boolean vectors (False < True)."""
    if len(left) != len(right):
        raise ValueError("lex-vector length mismatch")

    def fresh() -> int:
        formula.nv += 1
        return formula.nv

    before_nv, before_clauses = formula.nv, len(formula.clauses)
    prefix = fresh()
    formula.append([prefix])
    for x, y in zip(left, right):
        formula.append([-prefix, -x, y])
        following = fresh()
        formula.append([-following, prefix])
        formula.append([-following, -x, y])
        formula.append([-following, x, -y])
        formula.append([-prefix, -x, -y, following])
        formula.append([-prefix, x, y, following])
        prefix = following
    return {
        "variables": formula.nv - before_nv,
        "clauses": len(formula.clauses) - before_clauses,
    }


def build_formula(
    fixed: int,
    quotient: bool = False,
    fixed_edge_count: int | None = None,
    fixed_graph_type: str | None = None,
    max_degree: int | None = None,
    no_dominating_edge: bool = False,
    unique_witness_markers: bool = False,
    normalizer_lex: bool = False,
) -> tuple[CNF, dict]:
    formula = CNF()
    orbits = edge_orbits(fixed)
    if quotient:
        edge_for_pair = {}
        for variable, orbit in enumerate(orbits, start=1):
            for pair in orbit:
                edge_for_pair[pair] = variable
        primary_variables = list(range(1, len(orbits) + 1))
        primary_weights = [len(orbit) for orbit in orbits]
    else:
        edge_for_pair = {pair: variable for variable, pair in edge_pairs()}
        primary_variables = list(range(1, len(edge_for_pair) + 1))
        primary_weights = [1] * len(primary_variables)
    formula.nv = len(edge_for_pair)
    if quotient:
        formula.nv = len(orbits)

    def edge(u: int, v: int) -> int:
        return edge_for_pair[(min(u, v), max(u, v))]

    def fresh() -> int:
        formula.nv += 1
        return formula.nv

    semantic_pairs = [orbit[0] for orbit in orbits] if quotient else [
        pair for _, pair in edge_pairs()
    ]

    # Diameter at most two.  z(u,v,w) is exactly edge(u,w) AND edge(v,w).
    diameter_auxiliaries = 0
    for u, v in semantic_pairs:
        common_markers = []
        for w in range(N):
            if w in (u, v):
                continue
            marker = fresh()
            diameter_auxiliaries += 1
            common_markers.append(marker)
            uw, vw = edge(u, w), edge(v, w)
            formula.append([-marker, uw])
            formula.append([-marker, vw])
            if not unique_witness_markers:
                formula.append([marker, -uw, -vw])
        formula.append([edge(u, v), *common_markers])
        if unique_witness_markers:
            atmost = CardEnc.atmost(
                lits=common_markers,
                bound=1,
                top_id=formula.nv,
                encoding=EncType.seqcounter,
            )
            formula.extend(atmost.clauses)

    # Edge criticality via the local witness characterization.  For an edge
    # uv, deletion destroys diameter two iff either u,v have no common
    # neighbour, or an endpoint-plus-one-edge two-path is unique.
    no_common_markers = 0
    unique_path_markers = 0
    for u, v in semantic_pairs:
        alternatives = []

        no_common = fresh()
        no_common_markers += 1
        alternatives.append(no_common)
        for w in range(N):
            if w in (u, v):
                continue
            formula.append([-no_common, -edge(u, w), -edge(v, w)])

        for a, b in ((u, v), (v, u)):
            for x in range(N):
                if x in (a, b):
                    continue
                unique = fresh()
                unique_path_markers += 1
                alternatives.append(unique)
                formula.append([-unique, edge(a, x)])
                formula.append([-unique, -edge(b, x)])
                for w in range(N):
                    if w in (a, b, x):
                        continue
                    formula.append([-unique, -edge(x, w), -edge(b, w)])

        formula.append([-edge(u, v), *alternatives])
        if unique_witness_markers:
            atmost = CardEnc.atmost(
                lits=alternatives,
                bound=1,
                top_id=formula.nv,
                encoding=EncType.seqcounter,
            )
            formula.extend(atmost.clauses)

    semantic_nv = formula.nv
    semantic_clauses = len(formula.clauses)

    degree_metadata = None
    if max_degree is not None:
        permutation = canonical_permutation(fixed)
        unseen_vertices = set(range(N))
        vertex_representatives = []
        while unseen_vertices:
            representative = min(unseen_vertices)
            vertex_representatives.append(representative)
            current = representative
            while current in unseen_vertices:
                unseen_vertices.remove(current)
                current = permutation[current]
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        for vertex in vertex_representatives:
            multiplicities: dict[int, int] = {}
            for other in range(N):
                if other == vertex:
                    continue
                variable = edge(vertex, other)
                multiplicities[variable] = multiplicities.get(variable, 0) + 1
            add_weighted_atmost(
                formula,
                list(multiplicities),
                list(multiplicities.values()),
                max_degree,
            )
        degree_metadata = {
            "bound": max_degree,
            "vertex_orbit_representatives": vertex_representatives,
            "variables": formula.nv - before_nv,
            "clauses": len(formula.clauses) - before_clauses,
        }

    no_dom_metadata = None
    if no_dominating_edge:
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        markers = 0
        for u, v in semantic_pairs:
            missed = []
            for w in range(N):
                if w in (u, v):
                    continue
                marker = fresh()
                markers += 1
                missed.append(marker)
                uw, vw = edge(u, w), edge(v, w)
                formula.append([-marker, -uw])
                formula.append([-marker, -vw])
                if not unique_witness_markers:
                    formula.append([marker, uw, vw])
            formula.append([-edge(u, v), *missed])
            if unique_witness_markers:
                atmost = CardEnc.atmost(
                    lits=missed,
                    bound=1,
                    top_id=formula.nv,
                    encoding=EncType.seqcounter,
                )
                formula.extend(atmost.clauses)
        no_dom_metadata = {
            "markers": markers,
            "variables": formula.nv - before_nv,
            "clauses": len(formula.clauses) - before_clauses,
        }

    fixed_graphs = {
        "t2_path": {(0, 1), (1, 2)},
        "t2_matching": {(0, 1), (2, 3)},
        "t7_comp_triangle": {
            pair for _, pair in edge_pairs(5)
        } - {(0, 1), (0, 2), (1, 2)},
        "t7_comp_star": {
            pair for _, pair in edge_pairs(5)
        } - {(0, 1), (0, 2), (0, 3)},
        "t7_comp_path4": {
            pair for _, pair in edge_pairs(5)
        } - {(0, 1), (1, 2), (2, 3)},
        "t7_comp_path3_edge": {
            pair for _, pair in edge_pairs(5)
        } - {(0, 1), (1, 2), (3, 4)},
    }
    if fixed_graph_type is not None:
        if fixed != 5 or not quotient:
            raise ValueError("fixed graph types require --fixed 5 --quotient")
        if fixed_graph_type not in fixed_graphs:
            raise ValueError(f"unknown fixed graph type {fixed_graph_type}")
        selected_fixed_edges = fixed_graphs[fixed_graph_type]
        inferred_count = len(selected_fixed_edges)
        if fixed_edge_count is not None and fixed_edge_count != inferred_count:
            raise ValueError("fixed graph type and fixed-edge count disagree")
        fixed_edge_count = inferred_count
        for pair in [pair for _, pair in edge_pairs(5)]:
            formula.append(
                [edge_for_pair[pair] if pair in selected_fixed_edges else -edge_for_pair[pair]]
            )

    lex_metadata = None
    if normalizer_lex:
        if fixed != 5 or not quotient or fixed_graph_type is None:
            raise ValueError(
                "normalizer lex leaders require a fixed-5 quotient fixed-graph case"
            )
        generators: list[tuple[str, list[int]]] = []
        for cycle_index in range(3):
            permutation = list(range(N))
            left_start = 5 + 5 * cycle_index
            right_start = left_start + 5
            for offset in range(5):
                permutation[left_start + offset] = right_start + offset
                permutation[right_start + offset] = left_start + offset
            generators.append((f"swap_cycles_{cycle_index}_{cycle_index + 1}", permutation))
        for cycle_index in range(4):
            permutation = list(range(N))
            start = 5 + 5 * cycle_index
            for offset in range(5):
                permutation[start + offset] = start + (offset + 1) % 5
            generators.append((f"rotate_cycle_{cycle_index}", permutation))
        fixed_swaps = []
        if fixed_graph_type == "t2_path":
            fixed_swaps = [(0, 2), (3, 4)]
        elif fixed_graph_type == "t7_comp_star":
            fixed_swaps = [(1, 2), (2, 3)]
        for a, b in fixed_swaps:
            permutation = list(range(N))
            permutation[a], permutation[b] = permutation[b], permutation[a]
            generators.append((f"swap_fixed_{a}_{b}", permutation))

        before_nv, before_clauses = formula.nv, len(formula.clauses)
        primary_vector = list(range(1, len(orbits) + 1))
        for _, permutation in generators:
            image_vector = []
            for orbit in orbits:
                u, v = orbit[0]
                image_pair = tuple(sorted((permutation[u], permutation[v])))
                image_vector.append(edge_for_pair[image_pair])
            add_lex_leader(formula, primary_vector, image_vector)
        lex_metadata = {
            "generators": [name for name, _ in generators],
            "variables": formula.nv - before_nv,
            "clauses": len(formula.clauses) - before_clauses,
        }

    cardinality_case = None
    if quotient and fixed_edge_count is not None:
        fixed_variables = [
            variable
            for variable, orbit in enumerate(orbits, start=1)
            if len(orbit) == 1
        ]
        moving_variables = [
            variable
            for variable, orbit in enumerate(orbits, start=1)
            if len(orbit) == 5
        ]
        remainder = TARGET_EDGES - fixed_edge_count
        if not 0 <= fixed_edge_count <= len(fixed_variables) or remainder % 5:
            raise ValueError("fixed-edge count is incompatible with 157 total edges")
        moving_count = remainder // 5
        if not 0 <= moving_count <= len(moving_variables):
            raise ValueError("moving-orbit count is out of range")
        before_nv, before_clauses = formula.nv, len(formula.clauses)
        groups = [(moving_variables, moving_count)]
        if fixed_graph_type is None:
            groups.insert(0, (fixed_variables, fixed_edge_count))
        for literals, bound in groups:
            exact = CardEnc.equals(
                lits=literals,
                bound=bound,
                top_id=formula.nv,
                encoding=EncType.seqcounter,
            )
            formula.extend(exact.clauses)
        cardinality_nv = formula.nv - before_nv
        cardinality_clauses = len(formula.clauses) - before_clauses
        cardinality_case = {
            "fixed_edge_count": fixed_edge_count,
            "moving_orbit_count": moving_count,
            "fixed_graph_type": fixed_graph_type,
        }
    elif quotient:
        cardinality = add_weighted_exact(
            formula, primary_variables, primary_weights, TARGET_EDGES
        )
        cardinality_nv = cardinality["variables"]
        cardinality_clauses = cardinality["clauses"]
    else:
        exact = CardEnc.equals(
            lits=primary_variables,
            bound=TARGET_EDGES,
            top_id=formula.nv,
            encoding=EncType.seqcounter,
        )
        formula.extend(exact.clauses)
        cardinality_nv = formula.nv - semantic_nv
        cardinality_clauses = len(formula.clauses) - semantic_clauses

    permutation = canonical_permutation(fixed)
    equality_clauses = 0
    if not quotient:
        for _, (u, v) in edge_pairs():
            image = edge(permutation[u], permutation[v])
            original = edge(u, v)
            formula.append([-original, image])
            formula.append([original, -image])
            equality_clauses += 2

    metadata = {
        "schema": "erdos742-order5-automorphism-v1",
        "n": N,
        "fixed_vertices": fixed,
        "five_cycles": (N - fixed) // 5,
        "exact_edges": TARGET_EDGES,
        "quotient_encoding": quotient,
        "edge_orbits": len(orbits),
        "orbit_size_histogram": {
            str(size): sum(len(orbit) == size for orbit in orbits)
            for size in sorted({len(orbit) for orbit in orbits})
        },
        "edge_variables": len(primary_variables),
        "semantic_pair_representatives": len(semantic_pairs),
        "diameter_auxiliaries": diameter_auxiliaries,
        "no_common_markers": no_common_markers,
        "unique_path_markers": unique_path_markers,
        "semantic_variables": semantic_nv,
        "semantic_clauses": semantic_clauses,
        "max_degree_encoding": degree_metadata,
        "no_dominating_edge_encoding": no_dom_metadata,
        "unique_witness_markers": unique_witness_markers,
        "normalizer_lex_encoding": lex_metadata,
        "cardinality_variables": cardinality_nv,
        "cardinality_clauses": cardinality_clauses,
        "cardinality_case": cardinality_case,
        "automorphism_equality_clauses": equality_clauses,
        "total_variables": formula.nv,
        "total_clauses": len(formula.clauses),
        "permutation": permutation,
    }
    return formula, metadata


def decode_model(model: list[int], fixed: int, quotient: bool) -> dict:
    positive = {literal for literal in model if literal > 0}
    if quotient:
        edges = [
            list(pair)
            for variable, orbit in enumerate(edge_orbits(fixed), start=1)
            if variable in positive
            for pair in orbit
        ]
    else:
        edges = [
            list(pair) for variable, pair in edge_pairs() if variable in positive
        ]
    return {"n": N, "edges": edges}


def normalize_formula(formula: CNF) -> dict:
    """Remove repeated literals and tautological clauses before proof tracing."""
    before = len(formula.clauses)
    duplicate_literals = 0
    tautologies = 0
    normalized_clauses = []
    for clause in formula.clauses:
        seen = set()
        normalized = []
        tautological = False
        for literal in clause:
            if -literal in seen:
                tautological = True
                break
            if literal in seen:
                duplicate_literals += 1
                continue
            seen.add(literal)
            normalized.append(literal)
        if tautological:
            tautologies += 1
        else:
            normalized_clauses.append(normalized)
    formula.clauses = normalized_clauses
    return {
        "clauses_before": before,
        "clauses_after": len(formula.clauses),
        "duplicate_literals_removed": duplicate_literals,
        "tautological_clauses_removed": tautologies,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed", type=int, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--solver")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--quotient", action="store_true")
    parser.add_argument("--fixed-edge-count", type=int)
    parser.add_argument("--fixed-graph-type")
    parser.add_argument("--max-degree", type=int)
    parser.add_argument("--no-dominating-edge", action="store_true")
    parser.add_argument("--unique-witness-markers", action="store_true")
    parser.add_argument("--normalizer-lex", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    formula, metadata = build_formula(
        args.fixed,
        quotient=args.quotient,
        fixed_edge_count=args.fixed_edge_count,
        fixed_graph_type=args.fixed_graph_type,
        max_degree=args.max_degree,
        no_dominating_edge=args.no_dominating_edge,
        unique_witness_markers=args.unique_witness_markers,
        normalizer_lex=args.normalizer_lex,
    )
    metadata["clause_normalization"] = normalize_formula(formula)
    metadata["total_variables"] = formula.nv
    metadata["total_clauses"] = len(formula.clauses)
    built = time.perf_counter()
    args.cnf.parent.mkdir(parents=True, exist_ok=True)
    formula.to_file(str(args.cnf))
    metadata["cnf_sha256"] = sha256(args.cnf)
    metadata["build_seconds"] = built - started

    if args.solver:
        with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
            sat = solver.solve()
            metadata["solver"] = args.solver
            metadata["solver_result"] = "SAT" if sat else "UNSAT"
            metadata["solver_seconds"] = time.perf_counter() - built
            metadata["solver_stats"] = solver.accum_stats()
            if sat:
                candidate = decode_model(solver.get_model(), args.fixed, args.quotient)
                if args.candidate is None:
                    raise ValueError("SAT result requires --candidate")
                args.candidate.parent.mkdir(parents=True, exist_ok=True)
                args.candidate.write_text(
                    json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
                )
                metadata["candidate"] = str(args.candidate)
                metadata["candidate_sha256"] = sha256(args.candidate)

    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
