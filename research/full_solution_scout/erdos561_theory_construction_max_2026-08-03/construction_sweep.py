#!/usr/bin/env python3
"""Targeted construction search for a counterexample to Erdos problem 561.

This is deliberately *not* an enumeration of all unlabelled graphs.  It
constructs named sparse host families (complete multipartite graphs, theta
graphs, wheels/fans, windmills, and small disjoint unions of such atoms) and
tests the first small parameter pairs outside the published special cases.

For a target star forest with leaf demands d_1,...,d_s, embeddings are
generated exactly.  After choosing distinct centres, the leaf choices are a
capacitated bipartite matching problem.  The recursive implementation below
enumerates the corresponding edge masks while enforcing disjoint vertices.
An avoiding red/blue colouring is then a SAT instance:

  * every red-target embedding has a blue edge;
  * every blue-target embedding has a red edge.

Thus UNSAT means that the host arrows the ordered pair.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
OUT = HERE / "construction_sweep_result.json"


def canon_edges(g: nx.Graph) -> tuple[tuple[int, int], ...]:
    g = nx.convert_node_labels_to_integers(g, ordering="sorted")
    return tuple(sorted((min(u, v), max(u, v)) for u, v in g.edges()))


def graph_from_edges(edges: tuple[tuple[int, int], ...]) -> nx.Graph:
    g = nx.Graph()
    g.add_edges_from(edges)
    return g


def graph_key(g: nx.Graph) -> str:
    """WL hash plus exact invariants; collisions are resolved by isomorphism."""
    h = nx.weisfeiler_lehman_graph_hash(g)
    ds = ",".join(map(str, sorted(dict(g.degree()).values())))
    return f"{g.number_of_nodes()}:{g.number_of_edges()}:{ds}:{h}"


def add_unique(bucket: dict[str, list[tuple[str, nx.Graph]]], name: str, g: nx.Graph) -> None:
    g = nx.convert_node_labels_to_integers(g)
    g.remove_nodes_from(list(nx.isolates(g)))
    if not g.edges:
        return
    key = graph_key(g)
    for _, old in bucket[key]:
        if nx.is_isomorphic(g, old):
            return
    bucket[key].append((name, g.copy()))


def theta_graph(lengths: tuple[int, ...]) -> nx.Graph:
    """Internally vertex-disjoint paths of prescribed lengths with common ends."""
    assert len(lengths) >= 2 and min(lengths) >= 1
    g = nx.Graph()
    left, right = 0, 1
    nxt = 2
    for length in lengths:
        if length == 1:
            g.add_edge(left, right)
            continue
        path = [left] + list(range(nxt, nxt + length - 1)) + [right]
        nxt += length - 1
        g.add_edges_from(zip(path, path[1:]))
    return g


def windmill_graph(petals: int, clique_size: int) -> nx.Graph:
    """petals copies of K_clique_size sharing exactly one hub."""
    g = nx.Graph()
    hub = 0
    nxt = 1
    for _ in range(petals):
        verts = [hub] + list(range(nxt, nxt + clique_size - 1))
        nxt += clique_size - 1
        g.add_edges_from(itertools.combinations(verts, 2))
    return g


def fan_graph(path_vertices: int) -> nx.Graph:
    g = nx.path_graph(path_vertices)
    hub = path_vertices
    g.add_edges_from((hub, v) for v in range(path_vertices))
    return g


def named_connected_hosts(max_edges: int) -> list[tuple[str, nx.Graph]]:
    bucket: dict[str, list[tuple[str, nx.Graph]]] = defaultdict(list)

    # Paths, cycles, stars, cliques, wheels, fans.
    for m in range(1, max_edges + 1):
        add_unique(bucket, f"P{m + 1}", nx.path_graph(m + 1))
        add_unique(bucket, f"K1,{m}", nx.star_graph(m))
        if m >= 3:
            add_unique(bucket, f"C{m}", nx.cycle_graph(m))
    for n in range(3, 10):
        for name, g in (
            (f"K{n}", nx.complete_graph(n)),
            (f"W{n}", nx.wheel_graph(n)),
            (f"Fan{n}", fan_graph(n)),
        ):
            if g.number_of_edges() <= max_edges:
                add_unique(bucket, name, g)

    # Complete bipartite and complete multipartite graphs.
    for a in range(1, 8):
        for b in range(a, 11):
            g = nx.complete_bipartite_graph(a, b)
            if g.number_of_edges() <= max_edges:
                add_unique(bucket, f"K{a},{b}", g)
    for parts_n in range(3, 6):
        for parts in itertools.combinations_with_replacement(range(1, 6), parts_n):
            g = nx.complete_multipartite_graph(*parts)
            if g.number_of_edges() <= max_edges:
                add_unique(bucket, "K(" + ",".join(map(str, parts)) + ")", g)

    # Theta graphs with 3--5 branches.  Parallel length-one paths would make
    # duplicate edges, so at most one branch has length one.
    for branches in range(3, 6):
        for lengths in itertools.combinations_with_replacement(range(1, max_edges), branches):
            if sum(lengths) > max_edges or lengths.count(1) > 1:
                continue
            add_unique(bucket, "Theta(" + ",".join(map(str, lengths)) + ")", theta_graph(lengths))

    # Friendship/windmill graphs and clique-with-pendant-leaf constructions.
    for k in range(3, 6):
        for petals in range(2, 8):
            g = windmill_graph(petals, k)
            if g.number_of_edges() <= max_edges:
                add_unique(bucket, f"Windmill({petals},K{k})", g)
    for core_n in range(2, 7):
        base = nx.complete_graph(core_n)
        for leaf_counts in itertools.product(range(4), repeat=core_n):
            g = base.copy()
            nxt = core_n
            for v, count in enumerate(leaf_counts):
                for _ in range(count):
                    g.add_edge(v, nxt)
                    nxt += 1
            if g.number_of_edges() <= max_edges:
                add_unique(bucket, f"K{core_n}+leaves{leaf_counts}", g)

    ans = [item for values in bucket.values() for item in values]
    ans.sort(key=lambda x: (x[1].number_of_edges(), x[1].number_of_nodes(), x[0]))
    return ans


def disjoint_union_catalogue(
    connected: list[tuple[str, nx.Graph]], max_edges: int, max_components: int = 4
) -> list[tuple[str, nx.Graph]]:
    """Small multiset closure of low-complexity connected atoms."""
    # Restrict atoms so this remains a construction sweep, not an accidental
    # general graph catalogue.
    atoms = [(n, g) for n, g in connected if g.number_of_edges() <= max_edges]
    atoms.sort(key=lambda x: (x[1].number_of_edges(), x[0]))
    bucket: dict[str, list[tuple[str, nx.Graph]]] = defaultdict(list)

    def rec(start: int, chosen: list[tuple[str, nx.Graph]], used: int) -> None:
        if len(chosen) >= 2:
            g = nx.disjoint_union_all([x[1] for x in chosen])
            add_unique(bucket, "+".join(x[0] for x in chosen), g)
        if len(chosen) == max_components:
            return
        for i in range(start, len(atoms)):
            name, g = atoms[i]
            m = g.number_of_edges()
            if used + m > max_edges:
                continue
            chosen.append((name, g))
            rec(i, chosen, used + m)
            chosen.pop()

    rec(0, [], 0)
    ans = [item for values in bucket.values() for item in values]
    ans.sort(key=lambda x: (x[1].number_of_edges(), x[1].number_of_nodes(), x[0]))
    return ans


def embedding_masks(g: nx.Graph, demands: tuple[int, ...]) -> tuple[int, ...]:
    """All edge masks of (not necessarily induced) copies of a star forest."""
    nodes = tuple(g.nodes())
    edges = canon_edges(g)
    eidx = {e: i for i, e in enumerate(edges)}
    adj = {v: set(g.neighbors(v)) for v in nodes}
    masks: set[int] = set()

    # Assign larger demands first, and quotient equal-demand permutations by
    # requiring increasing centre labels within each equality block.
    for centers in itertools.permutations(nodes, len(demands)):
        if any(demands[i] == demands[i - 1] and centers[i] < centers[i - 1]
               for i in range(1, len(demands))):
            continue
        center_set = set(centers)
        options: list[list[tuple[frozenset[int], int]]] = []
        feasible = True
        for c, need in zip(centers, demands):
            leaves = sorted(adj[c] - center_set)
            if len(leaves) < need:
                feasible = False
                break
            here: list[tuple[frozenset[int], int]] = []
            for choice in itertools.combinations(leaves, need):
                mask = 0
                for leaf in choice:
                    e = (min(c, leaf), max(c, leaf))
                    mask |= 1 << eidx[e]
                here.append((frozenset(choice), mask))
            options.append(here)
        if not feasible:
            continue

        def choose(i: int, used_vertices: frozenset[int], mask: int) -> None:
            if i == len(options):
                masks.add(mask)
                return
            for leaves, emask in options[i]:
                if leaves.isdisjoint(used_vertices):
                    choose(i + 1, used_vertices | leaves, mask | emask)

        choose(0, frozenset(center_set), 0)
    return tuple(sorted(masks))


def arrows(
    g: nx.Graph, red_target: tuple[int, ...], blue_target: tuple[int, ...]
) -> tuple[bool, int | None, dict[str, int]]:
    edges = canon_edges(g)
    red_emb = embedding_masks(g, red_target)
    blue_emb = embedding_masks(g, blue_target)
    with Solver(name="g4") as solver:
        for mask in red_emb:
            solver.add_clause([-(i + 1) for i in range(len(edges)) if mask >> i & 1])
        for mask in blue_emb:
            solver.add_clause([(i + 1) for i in range(len(edges)) if mask >> i & 1])
        sat = solver.solve()
        if sat:
            model = set(x for x in solver.get_model() if x > 0)
            red_mask = sum(1 << i for i in range(len(edges)) if i + 1 in model)
        else:
            red_mask = None
    return (not sat, red_mask, {"red_embeddings": len(red_emb), "blue_embeddings": len(blue_emb)})


def formula(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, list[int]]:
    ls: list[int] = []
    for k in range(2, len(a) + len(b) + 1):
        vals = [a[i - 1] + b[j - 1] - 1
                for i in range(1, len(a) + 1)
                for j in range(1, len(b) + 1) if i + j == k]
        ls.append(max(vals))
    return sum(ls), ls


def likely_covered(a: tuple[int, ...], b: tuple[int, ...]) -> list[str]:
    """Conservative published-case filter used only for target selection."""
    why: list[str] = []
    if len(a) == 1 or len(b) == 1:
        why.append("DJKR:s=1_by_symmetry")
    if len(a) == 2 and a[0] == a[1]:
        why.append("DJKR:two_equal_first")
    if len(b) == 2 and b[0] == b[1]:
        why.append("DJKR:two_equal_second_by_symmetry")
    if len(set(a)) == 1 and len(set(b)) == 1:
        why.append("BEFRS:uniform_pair")
    if all(x % 2 for x in a + b):
        why.append("DJKR:all_odd")
    if all(x == 1 for x in a[1:]) and all(x == 1 for x in b[1:]):
        why.append("Cheng:all_tails_one")
    # Theorem 2.6 and its color-swapped form.  We mark only the literal
    # parameter range visible in the primary source (other-side entries >=2).
    if len(set(a)) == 1 and a[0] % 2 == 1 and b[0] % 2 == 1 and min(b) >= 2:
        why.append("DJKR:uniform_odd_vs_odd_leader")
    if len(set(b)) == 1 and b[0] % 2 == 1 and a[0] % 2 == 1 and min(a) >= 2:
        why.append("DJKR:uniform_odd_vs_odd_leader_symmetry")
    B, ls = formula(a, b)
    if all(x * (x - 1) // 2 > sum(ls[i:]) for i, x in enumerate(ls)):
        why.append("Gyori-Schelp")
    return why


def target_catalogue(max_degree: int = 5, max_len: int = 3, max_bound: int = 16):
    seqs: list[tuple[int, ...]] = []
    for s in range(2, max_len + 1):
        seqs.extend(itertools.combinations_with_replacement(range(1, max_degree + 1), s))
    seqs = [tuple(reversed(x)) for x in seqs]
    rows = []
    for i, a in enumerate(seqs):
        for b in seqs[i:]:
            B, ls = formula(a, b)
            covered = likely_covered(a, b)
            if B <= max_bound and not covered:
                rows.append((B, sum(a) + sum(b), a, b, ls))
    rows.sort()
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-bound", type=int, default=14)
    ap.add_argument("--max-targets", type=int, default=20)
    ap.add_argument("--all-edge-levels", action="store_true",
                    help="test hosts at every m<B, rather than only B-1 and B-2")
    args = ap.parse_args()

    targets = target_catalogue(max_bound=args.max_bound)[: args.max_targets]
    max_edges = max(B - 1 for B, *_ in targets)
    connected = named_connected_hosts(max_edges)
    # Disjoint unions use a deliberately small atom basis.  Larger structured
    # connected families remain in the connected catalogue.
    atom_names = {name for name, g in connected
                  if (name.startswith(("K1,", "C", "P", "K2,", "Theta"))
                      and g.number_of_edges() <= 8)}
    atoms = [(n, g) for n, g in connected if n in atom_names]
    disconnected = disjoint_union_catalogue(atoms, max_edges, max_components=4)
    hosts = connected + disconnected

    results = []
    hits = []
    for B, _, a, b, ls in targets:
        tested = 0
        level_counts: dict[str, int] = defaultdict(int)
        for name, g in hosts:
            m = g.number_of_edges()
            if m >= B:
                continue
            if not args.all_edge_levels and m < B - 2:
                continue
            # Both target forests need no more vertices than the host.
            if g.number_of_nodes() < min(sum(a) + len(a), sum(b) + len(b)):
                continue
            tested += 1
            level_counts[str(m)] += 1
            hit, witness, counts = arrows(g, a, b)
            if hit:
                row = {
                    "red_target": list(a), "blue_target": list(b),
                    "formula_bound": B, "l_values": ls,
                    "host_name": name, "n": g.number_of_nodes(), "m": m,
                    "edges": [list(e) for e in canon_edges(g)],
                    **counts,
                }
                hits.append(row)
                print("CANDIDATE", json.dumps(row, sort_keys=True), flush=True)
            # Symmetry can fail for distinct target sequences.
            if a != b:
                hit2, witness2, counts2 = arrows(g, b, a)
                if hit2:
                    row = {
                        "red_target": list(b), "blue_target": list(a),
                        "formula_bound": B, "l_values": ls,
                        "host_name": name, "n": g.number_of_nodes(), "m": m,
                        "edges": [list(e) for e in canon_edges(g)],
                        **counts2,
                    }
                    hits.append(row)
                    print("CANDIDATE", json.dumps(row, sort_keys=True), flush=True)
        results.append({
            "a": list(a), "b": list(b), "bound": B, "l_values": ls,
            "hosts_tested": tested, "host_counts_by_edges": dict(level_counts),
        })
        print(f"target {a} vs {b}: B={B}, tested={tested}, hits={len(hits)}", flush=True)

    payload = {
        "scope": "targeted named-family construction search, not exhaustive graph search",
        "target_filter": "small tuples not matched by conservative published-case rules",
        "connected_named_hosts": len(connected),
        "disconnected_named_hosts": len(disconnected),
        "targets": results,
        "candidates": hits,
        "outcome": "CANDIDATE_FOUND" if hits else "NO_CANDIDATE_IN_NAMED_FAMILIES",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": payload["outcome"], "candidates": len(hits),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
