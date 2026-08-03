"""Whole-graph, degree-preserving construction search for Erdos #151.

This is deliberately not an edge-variable CEGAR encoding.  It starts from
the published-Ramsey order-41 near misses in ``ramsey39_perturbation`` and
walks the entire labelled 2-switch component of their degree sequence.  The
compact Folkman core is *not* fixed.  Persistent semantic witnesses guide the
walk toward three simultaneous conditions:

* no ambient-admissible 10-set (equivalently beta <= 9);
* no proper 5-colouring (a cheap necessary condition for arrowing (3,3));
* no red/blue edge-colouring avoiding a monochromatic triangle.

Every state has the seed's degree at each labelled vertex (degrees 8 or 9),
and states with a K5 are strongly rejected.  Exact separators are called
after every local-search round.  A possible counterexample is exported from
its raw edge list and checked by the two independent validators from the
earlier constructive lane.

The search is stochastic and bounded.  Failure is evidence only for the
recorded trajectory, never an exhaustion claim.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import itertools
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONSTRUCTIVE = ROOT / "experiments" / "erdos151_siege" / "n41_candidate_heuristic"
PERTURBATION = ROOT / "experiments" / "erdos151_siege" / "ramsey39_perturbation"
sys.path.insert(0, str(CONSTRUCTIVE))

from common import (  # noqa: E402
    N,
    PAIR_ORDER,
    admissible_set_witnesses,
    canonical_edges,
    color_of,
    edge_sha256,
    extend_to_total_coloring,
    mask_of,
    maximal_cliques_nx,
    norm_edge,
    set_is_admissible,
    triangle_avoiding_colorings,
    triangles,
)


SCHEMA = "erdos151-whole-switch-run-v1"
CANDIDATE_SCHEMA = "erdos151-n41-candidate-v1"


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_graph(path: Path) -> nx.Graph:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("n") != N:
        raise ValueError(f"seed order is {raw.get('n')}, expected {N}")
    graph = nx.Graph()
    graph.add_nodes_from(range(N))
    edges: list[tuple[int, int]] = []
    for item in raw.get("edges", []):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("malformed seed edge")
        u, v = map(int, item)
        if not 0 <= u < v < N:
            raise ValueError("noncanonical seed edge")
        edges.append((u, v))
    if len(edges) != len(set(edges)):
        raise ValueError("duplicate seed edge")
    graph.add_edges_from(edges)
    degrees = sorted(dict(graph.degree()).values())
    if degrees != [8] + [9] * 40:
        raise ValueError(f"unexpected seed degree sequence {degrees}")
    return graph


def five_colorings(graph: nx.Graph, limit: int) -> list[tuple[int, ...]]:
    """Return up to ``limit`` proper 5-colourings, with colour symmetry fixed."""
    if limit <= 0:
        return []
    k = 5

    def var(vertex: int, colour: int) -> int:
        return vertex * k + colour + 1

    clauses: list[list[int]] = []
    for vertex in range(N):
        clauses.append([var(vertex, colour) for colour in range(k)])
        for first, second in itertools.combinations(range(k), 2):
            clauses.append([-var(vertex, first), -var(vertex, second)])
    for u, v in graph.edges():
        for colour in range(k):
            clauses.append([-var(u, colour), -var(v, colour)])
    clauses.append([var(0, 0)])

    result: list[tuple[int, ...]] = []
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        while len(result) < limit and solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            colouring = tuple(
                next(colour for colour in range(k) if var(vertex, colour) in positive)
                for vertex in range(N)
            )
            result.append(colouring)
            solver.add_clause([-var(vertex, colouring[vertex]) for vertex in range(N)])
    return result


def independent_sets(graph: nx.Graph, size: int, limit: int) -> list[tuple[int, ...]]:
    """Enumerate exact independent sets; these are high-value beta witnesses."""
    if limit <= 0:
        return []
    clauses = [[-(u + 1), -(v + 1)] for u, v in graph.edges()]
    pool = IDPool(start_from=N + 1)
    clauses.extend(
        CardEnc.equals(
            list(range(1, N + 1)),
            bound=size,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    result: list[tuple[int, ...]] = []
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        while len(result) < limit and solver.solve():
            positive = {lit for lit in solver.get_model() if lit > 0}
            witness = tuple(vertex for vertex in range(N) if vertex + 1 in positive)
            if len(witness) != size:
                raise AssertionError("independence cardinality encoder failed")
            result.append(witness)
            solver.add_clause([-(vertex + 1) for vertex in witness])
    return result


def colouring_is_proper(graph: nx.Graph, colouring: Sequence[int]) -> bool:
    return all(colouring[u] != colouring[v] for u, v in graph.edges())


def edge_colouring_is_killed(
    total_colouring: int, graph_triangles: Sequence[tuple[int, int, int]]
) -> bool:
    for a, b, c in graph_triangles:
        colour = color_of(total_colouring, a, b)
        if colour == color_of(total_colouring, a, c) == color_of(total_colouring, b, c):
            return True
    return False


@dataclasses.dataclass(frozen=True)
class Pools:
    independent: tuple[int, ...]
    beta: tuple[int, ...]
    vertex: tuple[tuple[int, ...], ...]
    edge: tuple[int, ...]


@dataclasses.dataclass(frozen=True)
class Score:
    omega: int
    independent_bad: tuple[int, ...]
    beta_bad: tuple[int, ...]
    vertex_bad: tuple[int, ...]
    edge_bad: tuple[int, ...]
    clique_count: int
    maximal_edges: int
    triangle_count: int

    @property
    def hard_penalty(self) -> int:
        return 1_000_000 * max(0, self.omega - 4)

    @property
    def semantic_penalty(self) -> int:
        # Beta is the actual target.  Non-5-colourability is a reusable,
        # inexpensive bridge toward arrowing; edge-colouring witnesses remain
        # in the objective from the start rather than being postponed.
        return (
            200 * len(self.independent_bad)
            + 40 * len(self.beta_bad)
            + 8 * len(self.vertex_bad)
            + len(self.edge_bad)
        )

    @property
    def penalty(self) -> int:
        return self.hard_penalty + self.semantic_penalty

    @property
    def key(self) -> tuple[int, int, int, int]:
        return (
            self.penalty,
            len(self.independent_bad),
            len(self.beta_bad),
            len(self.vertex_bad),
            len(self.edge_bad),
        )


def score_graph(graph: nx.Graph, pools: Pools) -> Score:
    cliques = maximal_cliques_nx(graph)
    clique_masks = tuple(mask_of(clique) for clique in cliques)
    graph_triangles = triangles(graph)
    return Score(
        omega=max((len(clique) for clique in cliques), default=1),
        independent_bad=tuple(
            index
            for index, witness in enumerate(pools.independent)
            if all(not (witness & (1 << u) and witness & (1 << v)) for u, v in graph.edges())
        ),
        beta_bad=tuple(
            index
            for index, witness in enumerate(pools.beta)
            if set_is_admissible(witness, clique_masks)
        ),
        vertex_bad=tuple(
            index
            for index, colouring in enumerate(pools.vertex)
            if colouring_is_proper(graph, colouring)
        ),
        edge_bad=tuple(
            index
            for index, colouring in enumerate(pools.edge)
            if not edge_colouring_is_killed(colouring, graph_triangles)
        ),
        clique_count=len(cliques),
        maximal_edges=sum(len(clique) == 2 for clique in cliques),
        triangle_count=len(graph_triangles),
    )


def newest_unique(existing: Iterable, additions: Iterable, limit: int) -> tuple:
    values = list(existing)
    known = set(values)
    for value in additions:
        if value not in known:
            known.add(value)
            values.append(value)
    return tuple(values[-limit:])


def add_exact_witnesses(
    graph: nx.Graph,
    pools: Pools,
    *,
    independent_batch: int,
    beta_batch: int,
    vertex_batch: int,
    edge_batch: int,
    independent_cap: int,
    beta_cap: int,
    vertex_cap: int,
    edge_cap: int,
    domain: str,
) -> tuple[Pools, dict]:
    independent_models = independent_sets(graph, 10, independent_batch)
    beta_models = admissible_set_witnesses(graph, 10, beta_batch)
    vertex_models = five_colorings(graph, vertex_batch)
    edge_models = triangle_avoiding_colorings(graph, edge_batch)
    extended_edges = []
    graph_hash = edge_sha256(N, canonical_edges(graph))
    for index, partial in enumerate(edge_models):
        extended_edges.append(
            extend_to_total_coloring(
                partial, f"{domain};graph={graph_hash};edge-model={index}"
            )
        )
    updated = Pools(
        independent=newest_unique(
            pools.independent,
            (mask_of(model) for model in independent_models),
            independent_cap,
        ),
        beta=newest_unique(pools.beta, (mask_of(model) for model in beta_models), beta_cap),
        vertex=newest_unique(pools.vertex, vertex_models, vertex_cap),
        edge=newest_unique(pools.edge, extended_edges, edge_cap),
    )
    return updated, {
        "alpha_pass": not independent_models,
        "beta_pass": not beta_models,
        "five_chromatic_pass": not vertex_models,
        "arrow_pass": not edge_models,
        "new_independent_10_sets": len(independent_models),
        "new_beta_witnesses": len(beta_models),
        "new_five_colourings": len(vertex_models),
        "new_edge_colourings": len(edge_models),
    }


def switch_options_for_target(
    graph: nx.Graph, target: tuple[int, int], rng: random.Random, cap: int = 80
) -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]]:
    """2-switches which insert ``target`` and preserve every vertex degree."""
    u, v = norm_edge(*target)
    if graph.has_edge(u, v):
        return []
    choices: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]] = []
    left = list(graph[u])
    right = list(graph[v])
    rng.shuffle(left)
    rng.shuffle(right)
    for a in left:
        for b in right:
            if len({u, v, a, b}) != 4 or graph.has_edge(a, b):
                continue
            choices.append((norm_edge(u, a), norm_edge(v, b), (u, v), norm_edge(a, b)))
    rng.shuffle(choices)
    return choices[:cap]


def random_switch(
    graph: nx.Graph, rng: random.Random
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]] | None:
    edges = list(canonical_edges(graph))
    for _ in range(80):
        first, second = rng.sample(edges, 2)
        a, b = first
        c, d = second
        if len({a, b, c, d}) != 4:
            continue
        alternatives = [
            (norm_edge(a, c), norm_edge(b, d)),
            (norm_edge(a, d), norm_edge(b, c)),
        ]
        rng.shuffle(alternatives)
        for third, fourth in alternatives:
            if third == fourth or graph.has_edge(*third) or graph.has_edge(*fourth):
                continue
            return first, second, third, fourth
    return None


def beta_targets(graph: nx.Graph, pools: Pools, score: Score, rng: random.Random) -> list[tuple[int, int]]:
    witness = pools.beta[rng.choice(score.beta_bad)]
    vertices = [vertex for vertex in range(N) if witness & (1 << vertex)]
    pairs = [pair for pair in itertools.combinations(vertices, 2) if not graph.has_edge(*pair)]
    # An inserted edge with a small common neighbourhood is more likely to be
    # an ambient maximal edge, which kills the admissible-set witness outright.
    pairs.sort(key=lambda pair: (len(set(graph[pair[0]]) & set(graph[pair[1]])), rng.random()))
    return pairs[:24]


def independent_targets(
    graph: nx.Graph, pools: Pools, score: Score, rng: random.Random
) -> list[tuple[int, int]]:
    witness = pools.independent[rng.choice(score.independent_bad)]
    vertices = [vertex for vertex in range(N) if witness & (1 << vertex)]
    pairs = list(itertools.combinations(vertices, 2))
    rng.shuffle(pairs)
    return pairs[:32]


def vertex_targets(graph: nx.Graph, pools: Pools, score: Score, rng: random.Random) -> list[tuple[int, int]]:
    colouring = pools.vertex[rng.choice(score.vertex_bad)]
    pairs = [
        pair
        for pair in itertools.combinations(range(N), 2)
        if colouring[pair[0]] == colouring[pair[1]] and not graph.has_edge(*pair)
    ]
    rng.shuffle(pairs)
    return pairs[:32]


def edge_targets(graph: nx.Graph, pools: Pools, score: Score, rng: random.Random) -> list[tuple[int, int]]:
    colouring = pools.edge[rng.choice(score.edge_bad)]
    targets: set[tuple[int, int]] = set()
    for u, v in itertools.combinations(range(N), 2):
        if graph.has_edge(u, v):
            continue
        uv = color_of(colouring, u, v)
        for middle in set(graph[u]) & set(graph[v]):
            if uv == color_of(colouring, u, middle) == color_of(colouring, v, middle):
                targets.add((u, v))
                break
    result = list(targets)
    rng.shuffle(result)
    return result[:32]


def targeted_switch(graph: nx.Graph, pools: Pools, score: Score, rng: random.Random):
    kinds: list[str] = []
    if score.independent_bad:
        kinds.extend(["independent"] * 9)
    if score.beta_bad:
        kinds.extend(["beta"] * 7)
    if score.vertex_bad:
        kinds.extend(["vertex"] * 4)
    if score.edge_bad:
        kinds.extend(["edge"] * 4)
    kinds.extend(["random"] * 3)
    rng.shuffle(kinds)
    for kind in kinds:
        if kind == "random":
            proposal = random_switch(graph, rng)
            if proposal is not None:
                return proposal, kind
            continue
        if kind == "independent":
            targets = independent_targets(graph, pools, score, rng)
        elif kind == "beta":
            targets = beta_targets(graph, pools, score, rng)
        elif kind == "vertex":
            targets = vertex_targets(graph, pools, score, rng)
        else:
            targets = edge_targets(graph, pools, score, rng)
        for target in targets:
            options = switch_options_for_target(graph, target, rng, cap=12)
            if options:
                return rng.choice(options), kind
    return None, "none"


def apply_switch(graph: nx.Graph, switch) -> None:
    first, second, third, fourth = switch
    graph.remove_edge(*first)
    graph.remove_edge(*second)
    graph.add_edge(*third)
    graph.add_edge(*fourth)


def undo_switch(graph: nx.Graph, switch) -> None:
    first, second, third, fourth = switch
    graph.remove_edge(*third)
    graph.remove_edge(*fourth)
    graph.add_edge(*first)
    graph.add_edge(*second)


def optimize(
    graph: nx.Graph,
    pools: Pools,
    rng: random.Random,
    moves: int,
    deadline: float,
) -> tuple[nx.Graph, Score, dict]:
    current = graph.copy()
    initial_degrees = dict(current.degree())
    current_score = score_graph(current, pools)
    best = current.copy()
    best_score = current_score
    accepted = 0
    attempted = 0
    alpha_rejected = 0
    kinds: dict[str, int] = {}
    for move_index in range(moves):
        if move_index % 32 == 0 and time.monotonic() >= deadline:
            break
        switch, kind = targeted_switch(current, pools, current_score, rng)
        if switch is None:
            continue
        attempted += 1
        kinds[kind] = kinds.get(kind, 0) + 1
        apply_switch(current, switch)
        if dict(current.degree()) != initial_degrees:
            raise AssertionError("2-switch changed a labelled degree")
        # Unlike a finite witness pool, this is an authoritative invariant:
        # once a Ramsey-valid seed is supplied, the walk never leaves
        # alpha <= 9.  This prevents the cheap fresh-independent-set drift
        # observed in the first whole-switch probe.
        if independent_sets(current, 10, 1):
            alpha_rejected += 1
            undo_switch(current, switch)
            continue
        proposed = score_graph(current, pools)
        delta = proposed.penalty - current_score.penalty
        fraction = move_index / max(1, moves - 1)
        temperature = 5.0 * (1.0 - fraction) + 0.08
        accept = delta <= 0 or rng.random() < math.exp(-delta / temperature)
        if accept:
            accepted += 1
            current_score = proposed
            if proposed.key < best_score.key:
                best = current.copy()
                best_score = proposed
                if proposed.semantic_penalty == 0 and proposed.omega <= 4:
                    break
        else:
            undo_switch(current, switch)
    return best, best_score, {
        "requested": moves,
        "attempted": attempted,
        "accepted": accepted,
        "alpha_rejected": alpha_rejected,
        "proposal_kinds": kinds,
    }


def artifact(graph: nx.Graph, provenance: dict) -> dict:
    edges = canonical_edges(graph)
    return {
        "schema": CANDIDATE_SCHEMA,
        "n": N,
        "edges": [list(edge) for edge in edges],
        "edge_sha256": edge_sha256(N, edges),
        "construction": {
            "family": "whole labelled degree-sequence 2-switch component",
            "degree_sequence": sorted(dict(graph.degree()).values()),
        },
        "provenance": provenance,
    }


def run_verifiers(path: Path) -> list[dict]:
    reports: list[dict] = []
    for verifier_name in ("verify_a.py", "verify_b.py"):
        verifier = CONSTRUCTIVE / verifier_name
        report = path.with_name(path.stem + f".{verifier.stem}.json")
        completed = subprocess.run(
            [sys.executable, str(verifier), str(path), "--report", str(report)],
            text=True,
            capture_output=True,
            check=False,
        )
        reports.append(
            {
                "verifier": verifier_name,
                "returncode": completed.returncode,
                "report": str(report),
                "stdout_tail": completed.stdout[-2000:],
                "stderr_tail": completed.stderr[-2000:],
            }
        )
    return reports


def checkpoint(path: Path, *, graph: nx.Graph, pools: Pools, state: dict) -> None:
    payload = dict(state)
    payload.update(
        {
            "schema": SCHEMA,
            "edges": [list(edge) for edge in canonical_edges(graph)],
            "pools": {
                "independent": [hex(value) for value in pools.independent],
                "beta": [hex(value) for value in pools.beta],
                "vertex": [list(value) for value in pools.vertex],
                "edge": [hex(value) for value in pools.edge],
            },
        }
    )
    atomic_json(path, payload)


def run(args: argparse.Namespace) -> int:
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    seed_path = args.seed_graph.resolve()
    graph = load_graph(seed_path)
    seed_degrees = dict(graph.degree())
    rng = random.Random(args.random_seed)
    pools = Pools((), (), (), ())
    deadline = time.monotonic() + args.time_limit_seconds

    metadata = {
        "schema": SCHEMA,
        "random_seed": args.random_seed,
        "seed_graph": str(seed_path),
        "seed_sha256": file_sha256(seed_path),
        "source_sha256": file_sha256(Path(__file__)),
        "rounds": args.rounds,
        "moves_per_round": args.moves_per_round,
        "batches": {
            "independent": args.independent_batch,
            "beta": args.beta_batch,
            "vertex": args.vertex_batch,
            "edge": args.edge_batch,
        },
        "pool_caps": {
            "independent": args.independent_cap,
            "beta": args.beta_cap,
            "vertex": args.vertex_cap,
            "edge": args.edge_cap,
        },
        "time_limit_seconds": args.time_limit_seconds,
        "claim_boundary": "bounded stochastic trajectory; not an exhaustion",
    }
    atomic_json(run_dir / "metadata.json", metadata)
    events = run_dir / "events.jsonl"
    best_graph = graph.copy()
    best_key: tuple | None = None
    exact_status: dict = {}

    for round_index in range(args.rounds):
        if time.monotonic() >= deadline:
            break
        pools, exact_status = add_exact_witnesses(
            graph,
            pools,
            independent_batch=args.independent_batch,
            beta_batch=args.beta_batch,
            vertex_batch=args.vertex_batch,
            edge_batch=args.edge_batch,
            independent_cap=args.independent_cap,
            beta_cap=args.beta_cap,
            vertex_cap=args.vertex_cap,
            edge_cap=args.edge_cap,
            domain=f"run={args.random_seed};round={round_index}",
        )
        before = score_graph(graph, pools)
        if dict(graph.degree()) != seed_degrees:
            raise AssertionError("degree sequence drift before optimization")
        event = {
            "round": round_index,
            "graph_sha256": edge_sha256(N, canonical_edges(graph)),
            "exact": exact_status,
            "pool_sizes": {
                "independent": len(pools.independent),
                "beta": len(pools.beta),
                "vertex": len(pools.vertex),
                "edge": len(pools.edge),
            },
            "before": dataclasses.asdict(before),
            "elapsed_seconds": args.time_limit_seconds - max(0.0, deadline - time.monotonic()),
        }
        print(json.dumps(event, sort_keys=True), flush=True)
        append_jsonl(events, event)

        if before.omega <= 4 and exact_status["beta_pass"] and exact_status["arrow_pass"]:
            hit = artifact(
                graph,
                {
                    "status": "SEARCH_SIDE_POSSIBLE_COUNTEREXAMPLE",
                    "run_dir": str(run_dir),
                    "round": round_index,
                    "random_seed": args.random_seed,
                },
            )
            hit_path = run_dir / f"candidate-{hit['edge_sha256']}.json"
            atomic_json(hit_path, hit)
            verification = run_verifiers(hit_path)
            result = {
                "status": "POSSIBLE_COUNTEREXAMPLE",
                "candidate": str(hit_path),
                "verification": verification,
            }
            if all(item["returncode"] == 0 for item in verification):
                result["status"] = "INDEPENDENTLY_VERIFIED_COUNTEREXAMPLE"
            atomic_json(run_dir / "result.json", result)
            return 0

        graph, after, move_stats = optimize(
            graph, pools, rng, args.moves_per_round, deadline
        )
        key = after.key + (-after.maximal_edges, after.triangle_count)
        if best_key is None or key < best_key:
            best_key = key
            best_graph = graph.copy()
        append_jsonl(
            events,
            {
                "round": round_index,
                "optimized_graph_sha256": edge_sha256(N, canonical_edges(graph)),
                "after": dataclasses.asdict(after),
                "moves": move_stats,
            },
        )
        checkpoint(
            run_dir / "checkpoint.json",
            graph=graph,
            pools=pools,
            state={
                "round_completed": round_index,
                "random_seed": args.random_seed,
                "exact_status_before_round": exact_status,
                "score_after_round": dataclasses.asdict(after),
            },
        )

    terminal = artifact(
        best_graph,
        {
            "status": "TERMINAL_NEAR_MISS",
            "run_dir": str(run_dir),
            "random_seed": args.random_seed,
            "completed_rounds": round_index + 1 if "round_index" in locals() else 0,
        },
    )
    terminal_path = run_dir / f"terminal-{terminal['edge_sha256']}.json"
    atomic_json(terminal_path, terminal)
    verification = run_verifiers(terminal_path)
    atomic_json(
        run_dir / "result.json",
        {
            "status": "BOUNDED_NO_COUNTEREXAMPLE",
            "scope": "only the recorded whole-graph 2-switch trajectory",
            "terminal_near_miss": str(terminal_path),
            "terminal_verification": verification,
            "last_exact_status": exact_status,
        },
    )
    return 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--run-dir", type=Path, required=True)
    result.add_argument(
        "--seed-graph",
        type=Path,
        default=PERTURBATION / "near_miss_low_beta.json",
    )
    result.add_argument("--random-seed", type=int, required=True)
    result.add_argument("--rounds", type=int, default=30)
    result.add_argument("--moves-per-round", type=int, default=2000)
    result.add_argument("--independent-batch", type=int, default=16)
    result.add_argument("--beta-batch", type=int, default=8)
    result.add_argument("--vertex-batch", type=int, default=8)
    result.add_argument("--edge-batch", type=int, default=4)
    result.add_argument("--independent-cap", type=int, default=1024)
    result.add_argument("--beta-cap", type=int, default=512)
    result.add_argument("--vertex-cap", type=int, default=512)
    result.add_argument("--edge-cap", type=int, default=256)
    result.add_argument("--time-limit-seconds", type=float, default=300.0)
    return result


def main() -> int:
    args = parser().parse_args()
    positive = (
        args.rounds,
        args.moves_per_round,
        args.independent_batch,
        args.beta_batch,
        args.vertex_batch,
        args.edge_batch,
        args.independent_cap,
        args.beta_cap,
        args.vertex_cap,
        args.edge_cap,
    )
    if min(positive) <= 0 or args.time_limit_seconds <= 0:
        raise SystemExit("all budgets must be positive")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
