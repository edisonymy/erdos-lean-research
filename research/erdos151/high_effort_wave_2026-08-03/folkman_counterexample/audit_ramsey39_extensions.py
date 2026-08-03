"""Exact audit of two-vertex extensions of the pinned 39-vertex Ramsey graph.

The published triangle-free graph has alpha 9 and maximum degree 9.  This
program proves, for this *fixed labelled base*, that no addition of two new
vertices can preserve both maximum degree at most 9 and independence number
at most 9, even before beta or edge-arrowing is considered.

Two independent enumerations of the base's independent 9-sets are compared:
NetworkX maximal cliques in the complement and a direct CaDiCaL exact-cardinal
enumeration.  Hitting sets are then checked both by brute force over the only
degree-eligible old vertices and by a separate SAT instance.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = (
    ROOT
    / "experiments"
    / "erdos151_siege"
    / "ramsey39_perturbation"
    / "source_r3_10_39.matrix"
)


def load_base(path: Path) -> nx.Graph:
    rows = [line.strip() for line in path.read_text(encoding="ascii").splitlines() if line.strip()]
    if len(rows) != 39 or any(len(row) != 39 for row in rows):
        raise ValueError("source matrix is not 39 by 39")
    if any(rows[i][j] != rows[j][i] for i in range(39) for j in range(39)):
        raise ValueError("source matrix is asymmetric")
    graph = nx.Graph()
    graph.add_nodes_from(range(39))
    # The sparse Ramsey colour is encoded by off-diagonal zeroes.
    graph.add_edges_from(
        (u, v)
        for u in range(39)
        for v in range(u + 1, 39)
        if rows[u][v] == "0"
    )
    return graph


def digest_sets(sets: list[tuple[int, ...]]) -> str:
    raw = json.dumps(sorted(sets), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(b"erdos151-r39-independent9-v1\0" + raw).hexdigest()


def enumerate_networkx(graph: nx.Graph) -> tuple[list[tuple[int, ...]], int]:
    maximal = [tuple(sorted(clique)) for clique in nx.find_cliques(nx.complement(graph))]
    alpha = max(map(len, maximal), default=0)
    return sorted(clique for clique in maximal if len(clique) == 9), alpha


def enumerate_sat(graph: nx.Graph) -> list[tuple[int, ...]]:
    n = graph.number_of_nodes()
    pool = IDPool(start_from=n + 1)
    clauses = [[-(u + 1), -(v + 1)] for u, v in graph.edges()]
    clauses.extend(
        CardEnc.equals(
            list(range(1, n + 1)),
            bound=9,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    result: list[tuple[int, ...]] = []
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        while solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            witness = tuple(vertex for vertex in range(n) if vertex + 1 in positive)
            if len(witness) != 9:
                raise AssertionError("SAT cardinality mismatch")
            result.append(witness)
            solver.add_clause([-(vertex + 1) for vertex in witness])
    return sorted(result)


def brute_transversals(
    eligible: list[int], independent_nines: list[tuple[int, ...]]
) -> dict[int, list[tuple[int, ...]]]:
    independent_masks = [sum(1 << vertex for vertex in witness) for witness in independent_nines]
    result: dict[int, list[tuple[int, ...]]] = {}
    for size in range(0, 10):
        hits: list[tuple[int, ...]] = []
        for subset in itertools.combinations(eligible, size):
            mask = sum(1 << vertex for vertex in subset)
            if all(mask & witness for witness in independent_masks):
                hits.append(subset)
        result[size] = hits
    return result


def sat_transversals_of_size(
    eligible: list[int], independent_nines: list[tuple[int, ...]], size: int
) -> list[tuple[int, ...]]:
    index = {vertex: position + 1 for position, vertex in enumerate(eligible)}
    pool = IDPool(start_from=len(eligible) + 1)
    clauses = [
        [index[vertex] for vertex in witness if vertex in index]
        for witness in independent_nines
    ]
    if any(not clause for clause in clauses):
        return []
    clauses.extend(
        CardEnc.equals(
            list(range(1, len(eligible) + 1)),
            bound=size,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    result: list[tuple[int, ...]] = []
    with Solver(name="glucose4", bootstrap_with=clauses) as solver:
        while solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            witness = tuple(
                vertex for vertex in eligible if index[vertex] in positive
            )
            result.append(witness)
            solver.add_clause([-index[vertex] for vertex in witness])
    return sorted(result)


def main() -> int:
    graph = load_base(SOURCE)
    nx_sets, alpha = enumerate_networkx(graph)
    sat_sets = enumerate_sat(graph)
    if nx_sets != sat_sets:
        raise AssertionError("independent-set enumerators disagree")
    if alpha != 9 or graph.number_of_edges() != 167 or any(nx.triangles(graph).values()):
        raise AssertionError("source Ramsey invariants failed")

    degrees = dict(graph.degree())
    eligible = [vertex for vertex in graph if degrees[vertex] <= 8]
    brute = brute_transversals(eligible, nx_sets)
    sat7 = sat_transversals_of_size(eligible, nx_sets, 7)
    sat8 = sat_transversals_of_size(eligible, nx_sets, 8)
    if sat7 != brute[7] or sat8 != brute[8]:
        raise AssertionError("transversal enumerators disagree")
    if brute[7] or len(brute[8]) != 1:
        raise AssertionError("unexpected minimum transversal catalogue")

    unique = brute[8][0]
    degree8_in_unique = [vertex for vertex in unique if degrees[vertex] == 8]
    low_degree_in_unique = [vertex for vertex in unique if degrees[vertex] < 8]
    effective_old_attachment_capacity = sum(
        min(2, 9 - degrees[vertex]) for vertex in graph
    )
    # Each of two new vertices needs an old-neighbourhood transversal.  The
    # total capacity forces two size-eight transversals, hence two copies of
    # the unique set.  Its degree-eight vertices cannot accept both edges.
    no_extension = (
        effective_old_attachment_capacity == 16
        and len(degree8_in_unique) == 7
        and len(low_degree_in_unique) == 1
    )
    if not no_extension:
        raise AssertionError("capacity conclusion did not fire")

    result = {
        "schema": "erdos151-r39-two-vertex-extension-audit-v1",
        "source": {
            "path": str(SOURCE.resolve()),
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "base": {
            "n": 39,
            "m": graph.number_of_edges(),
            "triangle_free": True,
            "alpha": alpha,
            "degree_distribution": dict(sorted(Counter(degrees.values()).items())),
        },
        "independent_9_sets": {
            "networkx_count": len(nx_sets),
            "cadical_count": len(sat_sets),
            "common_sha256": digest_sets(nx_sets),
            "enumerations_identical": True,
        },
        "old_vertices_eligible_for_new_adjacencies_under_Delta_9": eligible,
        "transversal_counts_by_size": {
            str(size): len(values) for size, values in brute.items()
        },
        "glucose_crosscheck": {
            "size_7_count": len(sat7),
            "size_8_count": len(sat8),
            "agrees_with_bruteforce": True,
        },
        "unique_minimum_transversal": list(unique),
        "unique_transversal_degrees": {str(v): degrees[v] for v in unique},
        "effective_total_old_new_edge_capacity_for_two_new_vertices": effective_old_attachment_capacity,
        "theorem": (
            "For this fixed 39-vertex base, no graph obtained only by adding "
            "two vertices can have both Delta <= 9 and alpha <= 9, regardless "
            "of whether the two new vertices are adjacent."
        ),
        "proof_summary": (
            "Each new vertex's old neighbourhood must hit all 4511 independent "
            "9-sets. Every such transversal has size at least 8, and the unique "
            "size-8 transversal contains seven old degree-8 vertices. The old "
            "vertices have effective capacity only 16 for edges from two new "
            "vertices, so both neighbourhoods would have to equal that unique "
            "size-8 set, forcing degree 10 at those seven vertices."
        ),
        "claim_scope": "exact for the pinned fixed base only",
    }
    output = HERE / "ramsey39_extension_audit.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
