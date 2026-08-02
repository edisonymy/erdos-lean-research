"""Independent standard-library replay for ORDER41_K4_GLOBAL_COUPLING.md.

It checks two bounded claims only:

1. the previously published fixed local abstraction has an explicit
   ten-vertex obstruction to every cross-fan-only completion which preserves
   its 24 singleton-fibre maximal edges;
2. the stored 1,000-iteration status artifact contains a valid last outer
   model with the advertised static properties and advertised failures.

This checker does not validate SAT solver iteration/cut counters and cannot
turn the recorded NO_CONCLUSION status into SAT or UNSAT.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
STATUS = HERE / "incidence_coupling_status.json"
BASE_CHECKER = (
    ROOT / "research" / "erdos151" / "general" / "checks"
    / "k4_fibre_attack" / "check_k4_fibre_attack.py"
)


def load_base():
    spec = importlib.util.spec_from_file_location("k4_fibre_base_replay", BASE_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def edge(x, y):
    return (x, y) if x < y else (y, x)


def adjacency(order, edges):
    result = [set() for _ in range(order)]
    for x, y in edges:
        assert 0 <= x < y < order
        result[x].add(y)
        result[y].add(x)
    return result


def independent(vertices, adj):
    return all(y not in adj[x] for x, y in itertools.combinations(vertices, 2))


def maximum_independent_set(vertices, adj):
    """Exact branch-and-bound written independently of the search script."""
    vertices = tuple(vertices)
    index = {v: i for i, v in enumerate(vertices)}
    forbidden = [0] * len(vertices)
    for v in vertices:
        mask = 0
        for w in adj[v]:
            if w in index:
                mask |= 1 << index[w]
        forbidden[index[v]] = mask

    best = 0

    def branch(candidates, chosen):
        nonlocal best
        if chosen.bit_count() + candidates.bit_count() <= best.bit_count():
            return
        if not candidates:
            if chosen.bit_count() > best.bit_count():
                best = chosen
            return
        # Branch first on a maximum-degree vertex of the current subproblem.
        scan = candidates
        pivot = None
        pivot_degree = -1
        while scan:
            bit = scan & -scan
            v = bit.bit_length() - 1
            scan ^= bit
            degree = (forbidden[v] & candidates).bit_count()
            if degree > pivot_degree:
                pivot = v
                pivot_degree = degree
        bit = 1 << pivot
        branch(candidates & ~bit & ~forbidden[pivot], chosen | bit)
        branch(candidates & ~bit, chosen)

    branch((1 << len(vertices)) - 1, 0)
    return tuple(vertices[i] for i in range(len(vertices)) if best >> i & 1)


def ambient_maximal_edge(x, y, adj):
    return y in adj[x] and not (adj[x] & adj[y])


def fixed_parts(module):
    original_edges, original_adjacency = module.make_graph()
    fan_of = {v: c for c, fan in enumerate(module.FANS) for v in fan}
    fixed = {
        pair for pair in original_edges
        if (
            (pair[0] in module.U and pair[1] in module.U)
            or (
                pair[0] in fan_of and pair[1] in fan_of
                and fan_of[pair[0]] == fan_of[pair[1]]
            )
            or pair[0] in module.M
            or pair[1] in module.M
        )
    }
    return original_edges, original_adjacency, fan_of, fixed


def check_fixed_witness_obstruction(module):
    _, base_adj = module.make_graph()
    fan_of = {v: c for c, fan in enumerate(module.FANS) for v in fan}
    protected = set()
    for fan in module.FANS:
        fan_set = set(fan)
        for u in module.U:
            neighbours = base_adj[u] & fan_set
            if len(neighbours) == 1:
                protected.add(edge(u, next(iter(neighbours))))
    assert len(protected) == 24
    assert all(ambient_maximal_edge(x, y, base_adj) for x, y in protected)

    fatal = (1, 3, 7, 10, 17, 19, 21, 26, 34, 35)
    assert independent(fatal, base_adj)
    fan_vertices = tuple(v for v in fatal if v in fan_of)
    blocked = []
    for a, b in itertools.combinations(fan_vertices, 2):
        if fan_of[a] == fan_of[b]:
            continue
        witnesses = []
        for u in sorted(base_adj[a] & base_adj[b] & set(module.U)):
            if edge(u, a) in protected:
                witnesses.append((u, a))
            if edge(u, b) in protected:
                witnesses.append((u, b))
        assert witnesses, (a, b)
        blocked.append((a, b, witnesses[0]))
    assert len(blocked) == 13
    return fatal, protected, blocked


def check_stored_outer_model(module):
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    assert data["schema"] == "erdos151-order41-k4-incidence-coupling-status-v1"
    assert data["status"] == "NO_CONCLUSION_ITERATION_LIMIT"
    assert data["sat_iterations"] == 1000
    assert data["residual_alpha_cuts"] == 1359
    assert data["global_alpha_cuts"] == 17477
    assert data["static_clauses"] == 112381
    assert data["static_variables"] == 12136
    assert data["k5_static_clauses"] == 79693
    assert hashlib.sha256(BASE_CHECKER.read_bytes()).hexdigest() == data["base_checker_sha256"]

    _, _, fan_of, fixed = fixed_parts(module)
    incidence = {tuple(pair) for pair in data["last_model_incidence_edges"]}
    cross = {tuple(pair) for pair in data["last_model_cross_fan_edges"]}
    assert len(incidence) == 81
    assert len(cross) == 28
    assert not (incidence & cross)
    for x, y in incidence:
        assert (x in module.U and y in fan_of) or (y in module.U and x in fan_of)
    for x, y in cross:
        assert x in fan_of and y in fan_of and fan_of[x] != fan_of[y]

    edges = fixed | incidence | cross
    canonical = ";".join(f"{x}-{y}" for x, y in sorted(edges))
    assert hashlib.sha256(canonical.encode()).hexdigest() == data["last_model_edge_sha256"]
    assert len(incidence) + len(cross) == data["last_model_variable_edges"]
    adj = adjacency(module.N, edges)

    degrees = [len(adj[v]) for v in range(module.N)]
    assert min(degrees) >= 5 and max(degrees) <= 9
    assert all(y in adj[x] for x, y in itertools.combinations(module.M, 2))
    assert not any(
        all(y in adj[x] for x, y in itertools.combinations(five, 2))
        for five in itertools.combinations(range(module.N), 5)
    )

    cuts = []
    singleton_counts = []
    residual_alphas = []
    residual_witnesses = []
    seeded_failures = []
    for fan in module.FANS:
        fan_set = set(fan)
        residual = tuple(module.U) + tuple(fan)
        cuts.append(sum(len(adj[u] & fan_set) for u in module.U))
        assert all(adj[u] & fan_set for u in module.U)
        fibre_counts = {a: 0 for a in fan}
        for u in module.U:
            neighbours = adj[u] & fan_set
            if len(neighbours) == 1:
                a = next(iter(neighbours))
                fibre_counts[a] += 1
                assert ambient_maximal_edge(u, a, adj)
        assert max(fibre_counts.values()) <= 1
        singleton_counts.append(sum(fibre_counts.values()))

        assert not any(
            all(y in adj[x] for x, y in itertools.combinations(triple, 2))
            for triple in itertools.combinations(residual, 3)
        )
        witness = maximum_independent_set(residual, adj)
        residual_alphas.append(len(witness))
        residual_witnesses.append(witness)

        failures = 0
        for seed in itertools.combinations(residual, 6):
            if not independent(seed, adj):
                continue
            seed_set = set(seed)
            for z in set(module.U) - seed_set:
                if not any(ambient_maximal_edge(z, x, adj) for x in seed):
                    failures += 1
                    break
        seeded_failures.append(failures)

    assert sorted(cuts) == [20, 20, 20, 21]
    assert residual_alphas == data["last_model_residual_alphas"] == [6, 6, 6, 6]
    assert [list(w) for w in residual_witnesses] == data["last_model_residual_alpha_witnesses"]

    global_witness = maximum_independent_set(range(module.N), adj)
    assert len(global_witness) == data["last_model_global_alpha"] == 11
    assert list(global_witness) == data["last_model_global_alpha_witness"]
    assert independent(global_witness, adj)
    assert seeded_failures == [29, 36, 18, 49]
    return {
        "degrees": (min(degrees), max(degrees)),
        "cuts": cuts,
        "singletons": singleton_counts,
        "residual_alphas": residual_alphas,
        "global_alpha": len(global_witness),
        "seeded_failures": seeded_failures,
    }


def main():
    module = load_base()
    fatal, protected, blocked = check_fixed_witness_obstruction(module)
    outer = check_stored_outer_model(module)
    print("fixed-witness fatal ten-set:", fatal)
    print("protected singleton-fibre edges:", len(protected))
    print("blocked different-fan pairs inside fatal set:", len(blocked))
    print("last outer-model degree interval:", outer["degrees"])
    print("last outer-model cuts:", outer["cuts"])
    print("last outer-model singleton counts:", outer["singletons"])
    print("last outer-model residual alphas:", outer["residual_alphas"])
    print("last outer-model global alpha (required <=9):", outer["global_alpha"])
    print("last outer-model H3 seeded failures:", outer["seeded_failures"])
    print("status: VERIFIED_BOUNDED_NO_CONCLUSION")


if __name__ == "__main__":
    main()
