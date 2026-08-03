"""Faithful finite s=3 probe of Morris--Sahasrabudhe--Verstraete.

Primary source: arXiv:2607.16118v1, Definition 2.1, equations (10)--(14),
Observation 2.2 and Lemma 2.3.  This file deliberately keeps the paper's
two independent random partitions, indexed copies sampled with replacement,
and both deletion steps.  Parameters are finite and tunable; the asymptotic
constants in equation (10) are not claimed to be useful at these orders.

The program only treats s=3.  It searches for a K4-free graph G with
tf_3(G) < h, where h is a certified lower bound for H(n).  Heuristic searches
only produce *lower* bounds on tf_3; a heuristic stall is never a certificate.

Usage:
  .venv\\Scripts\\python.exe -X utf8 msv_s3_probe.py --smoke
  .venv\\Scripts\\python.exe -X utf8 msv_s3_probe.py --sweep RESULTS.json
  .venv\\Scripts\\python.exe -X utf8 msv_s3_probe.py --boundary-sweep BOUNDARY_RESULTS.json
  .venv\\Scripts\\python.exe -X utf8 msv_s3_probe.py --one N R Q M SEED
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SOURCE = {
    "paper": "Morris--Sahasrabudhe--Verstraete, On the Erdos--Rogers function",
    "arxiv": "2607.16118v1",
    "submitted": "2026-07-17",
    "construction_location": "Definition 2.1, equations (10)--(14), Observation 2.2, Lemma 2.3",
    "ramsey_survey": "Radziszowski, Small Ramsey Numbers, DS1.18, 2026-04-24",
}

# Exact values followed by the published April 2026 upper bounds.  For k>23
# we also use the elementary recurrence R(3,k)<=R(3,k-1)+k and the audited
# Shearer certificate used elsewhere in this campaign.
R3_EXACT = {2: 3, 3: 6, 4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36}
R3_UPPER_2026 = {
    10: 41,
    11: 50,
    12: 59,
    13: 68,
    14: 77,
    15: 87,
    16: 97,
    17: 109,
    18: 120,
    19: 132,
    20: 145,
    21: 157,
    22: 171,
    23: 185,
}


def shearer_f(d: float) -> float:
    return (d * math.log(d) - d + 1.0) / ((d - 1.0) ** 2)


def shearer_upper(k: int) -> int:
    """Certified R(3,k) upper bound from the campaign's audited lemma."""
    return math.ceil(k / shearer_f(k - 1.0))


_R3_CACHE: dict[int, int] = {}


def r3_certified_upper(k: int) -> int:
    """Best upper bound used here, with its ingredients kept explicit."""
    if k in _R3_CACHE:
        return _R3_CACHE[k]
    if k in R3_EXACT:
        ans = R3_EXACT[k]
    else:
        candidates = [shearer_upper(k)]
        if k in R3_UPPER_2026:
            candidates.append(R3_UPPER_2026[k])
        if k > 3:
            candidates.append(r3_certified_upper(k - 1) + k)
        ans = min(candidates)
    _R3_CACHE[k] = ans
    return ans


def h_certified(n: int) -> int:
    """A proved lower bound on H(n)=max{k:R(3,k)<=n}."""
    h = 2
    while r3_certified_upper(h + 1) <= n:
        h += 1
    return h


def h_certificate(n: int) -> dict:
    h = h_certified(n)
    return {
        "n": n,
        "h": h,
        "R3_h_upper": r3_certified_upper(h),
        "R3_h_plus_1_upper": r3_certified_upper(h + 1),
        "logic": "R(3,h)<=n implies H(n)>=h",
    }


def derive_seed(seed: int, label: str) -> int:
    data = f"msv151-v1|{seed}|{label}".encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def edge_code(n: int, u: int, v: int) -> int:
    if u > v:
        u, v = v, u
    return u * n + v


def decode_edge(n: int, code: int) -> tuple[int, int]:
    return divmod(code, n)


def iter_bits(mask: int) -> Iterable[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def has_edge_in_set(adj: Sequence[int], vertices: int) -> bool:
    rest = vertices
    while rest:
        bit = rest & -rest
        v = bit.bit_length() - 1
        rest ^= bit
        if adj[v] & rest:
            return True
    return False


def is_independent(adj: Sequence[int], vertices: int) -> bool:
    rest = vertices
    while rest:
        bit = rest & -rest
        v = bit.bit_length() - 1
        rest ^= bit
        if adj[v] & rest:
            return False
    return True


def is_triangle_free_induced(adj: Sequence[int], vertices: int) -> bool:
    rest = vertices
    while rest:
        bit = rest & -rest
        v = bit.bit_length() - 1
        rest ^= bit
        if has_edge_in_set(adj, adj[v] & rest):
            return False
    return True


def find_k4(adj: Sequence[int]) -> tuple[int, int, int, int] | None:
    """Independent exact audit: an edge inside a common neighbourhood."""
    n = len(adj)
    for u in range(n):
        later_u = adj[u] & ~((1 << (u + 1)) - 1)
        for v in iter_bits(later_u):
            common = adj[u] & adj[v]
            rest = common
            while rest:
                bit = rest & -rest
                w = bit.bit_length() - 1
                rest ^= bit
                xmask = adj[w] & rest
                if xmask:
                    x = (xmask & -xmask).bit_length() - 1
                    return (u, v, w, x)
    return None


def enumerate_triangles(adj: Sequence[int]) -> list[tuple[int, int, int]]:
    n = len(adj)
    out: list[tuple[int, int, int]] = []
    for u in range(n):
        later_u = adj[u] & ~((1 << (u + 1)) - 1)
        for v in iter_bits(later_u):
            common = adj[u] & adj[v] & ~((1 << (v + 1)) - 1)
            out.extend((u, v, w) for w in iter_bits(common))
    return out


def random_equipartition(n: int, r: int, rng: random.Random) -> list[list[int]]:
    vertices = list(range(n))
    rng.shuffle(vertices)
    return [vertices[i : i + r] for i in range(0, n, r)]


@dataclass
class Pregraph:
    n: int
    r: int
    q: int
    m: int
    seed: int
    membership: list[int]
    edge_colour: dict[int, int]
    edge_owner: dict[int, int]
    copy_part_masks: list[tuple[int, int, int]]
    gprime_adj: list[int]
    stats: dict


def build_pregraph(n: int, r: int, q: int, m: int, seed: int) -> Pregraph:
    """Build G' exactly through the paper's first deletion step."""
    if n <= 0 or r <= 0 or n % r:
        raise ValueError("require r|n")
    if q <= 0 or q % 3:
        raise ValueError("this probe requires q divisible by 3")
    N = n // r
    if q > N:
        raise ValueError("T3(q) does not fit in the base graph")
    if m <= 0:
        raise ValueError("m must be positive")

    partitions = [
        random_equipartition(n, r, random.Random(derive_seed(seed, "partition-A"))),
        random_equipartition(n, r, random.Random(derive_seed(seed, "partition-B"))),
    ]
    family_rng = [
        random.Random(derive_seed(seed, "family-A")),
        random.Random(derive_seed(seed, "family-B")),
    ]

    membership = [0] * n
    edges: dict[int, int] = {}
    copy_vertex_masks: list[int] = []
    copy_part_masks: list[tuple[int, int, int]] = []
    copy_part_sizes: list[list[int]] = []
    part_base_size = q // 3

    for colour in range(2):
        blocks = partitions[colour]
        rng = family_rng[colour]
        for j in range(m):
            # A shuffled q-subset followed by equal labelled chunks is
            # uniform over labelled balanced tripartitions, hence uniform
            # over unlabelled copies as each has the same 3! multiplicity.
            chosen = rng.sample(range(N), q)
            rng.shuffle(chosen)
            base_parts = [
                chosen[i * part_base_size : (i + 1) * part_base_size]
                for i in range(3)
            ]
            final_parts = [
                [v for b in base_part for v in blocks[b]]
                for base_part in base_parts
            ]
            copy_id = colour * m + j
            copy_bit = 1 << copy_id
            vertex_mask = 0
            for part in final_parts:
                for v in part:
                    membership[v] |= copy_bit
                    vertex_mask |= 1 << v
            copy_vertex_masks.append(vertex_mask)
            copy_part_masks.append(tuple(
                sum(1 << v for v in part) for part in final_parts
            ))
            copy_part_sizes.append([len(x) for x in final_parts])
            colour_bit = 1 << colour
            for a in range(3):
                for b in range(a + 1, 3):
                    for u in final_parts[a]:
                        for v in final_parts[b]:
                            code = edge_code(n, u, v)
                            edges[code] = edges.get(code, 0) | colour_bit

    gstar_edges = len(edges)
    d1: set[int] = set()
    surviving_colours: dict[int, int] = {}
    owner_ids: dict[int, int] = {}
    adj = [0] * n
    for code, colours in edges.items():
        u, v = decode_edge(n, code)
        common_copies = membership[u] & membership[v]
        count = common_copies.bit_count()
        if count >= 2:
            d1.add(code)
            continue
        if count != 1:
            raise AssertionError("generated edge has no containing indexed J*")
        if colours not in (1, 2):
            raise AssertionError("D1 left an edge with two colours")
        owner = (common_copies & -common_copies).bit_length() - 1
        expected_colour = 1 if owner < m else 2
        if colours != expected_colour:
            raise AssertionError("unique container colour disagrees with provenance")
        surviving_colours[code] = colours
        owner_ids[code] = owner
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    # Independent replay of the literal D1 predicate for all surviving edges.
    for code in surviving_colours:
        u, v = decode_edge(n, code)
        if (membership[u] & membership[v]).bit_count() != 1:
            raise AssertionError("D1 replay failed")

    stats = {
        "ell": q * r,
        "N": N,
        "copies_per_colour": m,
        "indexed_copies_total": 2 * m,
        "gstar_edges": gstar_edges,
        "d1_edges": len(d1),
        "gprime_edges": len(surviving_colours),
        "uncovered_vertices": sum(x == 0 for x in membership),
        "vertex_copy_incidence_min": min(x.bit_count() for x in membership),
        "vertex_copy_incidence_max": max(x.bit_count() for x in membership),
        "vertex_copy_incidence_mean": sum(x.bit_count() for x in membership) / n,
        "copy_part_sizes": copy_part_sizes[0] if copy_part_sizes else [],
        "literal_d1_replay": "PASS",
    }
    return Pregraph(
        n,
        r,
        q,
        m,
        seed,
        membership,
        surviving_colours,
        owner_ids,
        copy_part_masks,
        adj,
        stats,
    )


@dataclass
class TriangleLedger:
    total: int
    intrinsic: list[tuple[int, int, int]]
    extrinsic: list[tuple[tuple[int, int, int], int | None]]
    intrinsic_edge_counts: dict[int, int]


def build_triangle_ledger(pre: Pregraph) -> TriangleLedger:
    n = pre.n
    intrinsic: list[tuple[int, int, int]] = []
    extrinsic: list[tuple[tuple[int, int, int], int | None]] = []
    intrinsic_edge_counts: dict[int, int] = {}
    for u, v, w in enumerate_triangles(pre.gprime_adj):
        codes = (
            edge_code(n, u, v),
            edge_code(n, u, w),
            edge_code(n, v, w),
        )
        common = pre.membership[u] & pre.membership[v] & pre.membership[w]
        if common:
            intrinsic.append((u, v, w))
            for code in codes:
                intrinsic_edge_counts[code] = intrinsic_edge_counts.get(code, 0) + 1
            continue
        colours = [pre.edge_colour[c] for c in codes]
        count_a = colours.count(1)
        count_b = colours.count(2)
        forced: int | None = None
        if count_a == 1 and count_b == 2:
            forced = codes[colours.index(1)]
        elif count_b == 1 and count_a == 2:
            forced = codes[colours.index(2)]
        elif count_a not in (0, 3):
            raise AssertionError("extrinsic triangle has invalid post-D1 colours")
        extrinsic.append((codes, forced))
    return TriangleLedger(
        total=len(intrinsic) + len(extrinsic),
        intrinsic=intrinsic,
        extrinsic=extrinsic,
        intrinsic_edge_counts=intrinsic_edge_counts,
    )


def d2_random(pre: Pregraph, ledger: TriangleLedger) -> set[int]:
    rng = random.Random(derive_seed(pre.seed, "d2-paper-random"))
    deleted: set[int] = set()
    for codes, forced in ledger.extrinsic:
        deleted.add(forced if forced is not None else rng.choice(codes))
    return deleted


def d2_greedy_preserve(pre: Pregraph, ledger: TriangleLedger) -> set[int]:
    """A faithful global choice for the paper's arbitrary D2 decisions.

    Mixed triangles first force their minority-colour edge.  Remaining
    monochromatic extrinsic triangles are hit greedily, preferring high
    coverage and low destruction of intrinsic triangles.  A hitting set is
    exactly a simultaneous choice of one of the selected edges for each
    triangle, so this stays within Definition (14)'s second deletion step.
    """
    deleted = {forced for _, forced in ledger.extrinsic if forced is not None}
    remaining: list[tuple[int, int, int]] = []
    for codes, forced in ledger.extrinsic:
        if forced is None and not any(code in deleted for code in codes):
            remaining.append(codes)
    if not remaining:
        return deleted

    edge_to_triangles: dict[int, list[int]] = {}
    for tid, codes in enumerate(remaining):
        for code in codes:
            edge_to_triangles.setdefault(code, []).append(tid)
    active = [True] * len(remaining)
    active_count = len(remaining)
    heap: list[tuple[float, int, int, int]] = []

    def push(code: int) -> None:
        coverage = sum(active[tid] for tid in edge_to_triangles[code])
        if not coverage:
            return
        intrinsic_loss = ledger.intrinsic_edge_counts.get(code, 0)
        # Primary objective: reuse deletions.  The denominator is the exact
        # number of protected triangles directly destroyed plus one.
        score = coverage / (1 + intrinsic_loss)
        tie = derive_seed(pre.seed, f"d2-edge-{code}") & 0x7FFFFFFF
        heapq.heappush(heap, (-score, -coverage, intrinsic_loss, tie, code))

    for code in edge_to_triangles:
        push(code)
    while active_count:
        if not heap:
            raise AssertionError("D2 greedy cover exhausted its heap")
        _, neg_old_coverage, _, _, code = heapq.heappop(heap)
        live = [tid for tid in edge_to_triangles[code] if active[tid]]
        if not live:
            continue
        intrinsic_loss = ledger.intrinsic_edge_counts.get(code, 0)
        score = len(live) / (1 + intrinsic_loss)
        old_coverage = -neg_old_coverage
        # Lazy score repair after neighbouring triangle removals.
        if len(live) != old_coverage:
            tie = derive_seed(pre.seed, f"d2-edge-{code}") & 0x7FFFFFFF
            heapq.heappush(heap, (-score, -len(live), intrinsic_loss, tie, code))
            continue
        deleted.add(code)
        for tid in live:
            active[tid] = False
            active_count -= 1

    return deleted


def d2_rc2_weighted_preserve(pre: Pregraph, ledger: TriangleLedger) -> set[int]:
    """Exact weighted hitting set for the paper's simultaneous D2 choice.

    A Boolean variable says that an edge is put in D2.  Every extrinsic
    triangle is a hard hitting clause and every mixed triangle additionally
    forces its minority-colour edge.  Deleting edge e has cost 1 plus the
    number of intrinsic G'-triangles containing e.  RC2 minimizes that exact
    additive loss proxy.  This optimizes only a choice the paper leaves
    arbitrary; it does not alter either deletion rule.
    """
    try:
        from pysat.examples.rc2 import RC2
        from pysat.formula import WCNF
    except ImportError as exc:  # pragma: no cover - environment diagnostic
        raise RuntimeError("PySAT is required for rc2_weighted_preserve") from exc

    edge_codes = sorted({code for codes, _ in ledger.extrinsic for code in codes})
    var_of = {code: i + 1 for i, code in enumerate(edge_codes)}
    formula = WCNF()
    for codes, forced in ledger.extrinsic:
        formula.append([var_of[code] for code in codes])
        if forced is not None:
            formula.append([var_of[forced]])
    for code, var in var_of.items():
        cost = 1 + ledger.intrinsic_edge_counts.get(code, 0)
        formula.append([-var], weight=cost)
    with RC2(formula, solver="cadical195", adapt=True, exhaust=True) as rc2:
        model = rc2.compute()
        if model is None:
            raise AssertionError("D2 hitting formula unexpectedly UNSAT")
    positive = {lit for lit in model if lit > 0}
    deleted = {code for code, var in var_of.items() if var in positive}
    if any(not any(code in deleted for code in codes) for codes, _ in ledger.extrinsic):
        raise AssertionError("RC2 D2 model does not hit every extrinsic triangle")
    return deleted


class D2Infeasible(RuntimeError):
    """The requested faithful D2 side constraints admit no assignment."""


def d2_rc2_degree_capped_preserve(
    pre: Pregraph,
    ledger: TriangleLedger,
    exact_triangle_loss: bool = False,
) -> set[int]:
    """Choose D2 *assignments* globally while enforcing Delta < H(n).

    Unlike an unconstrained hitting-set formulation, a degree constraint may
    reward redundant selected edges.  A redundant hitting set need not be the
    union of choices of exactly one edge from each extrinsic triangle.  We
    therefore model the paper literally: x_(T,e) says triangle T chooses edge
    e, exactly one x is true for each T, and y_e is true iff some triangle
    chooses e.  Mixed triangles are restricted to their mandated minority
    edge.  Hard cardinality constraints on the y variables then make every
    final degree at most H(n)-1.  The soft objective first limits deletions and
    penalizes destruction of intrinsic triangles.

    This changes only the globally coordinated choice in Definition (14); it
    does not add arbitrary deletions or alter either deletion rule.
    """
    try:
        from pysat.card import CardEnc, EncType
        from pysat.examples.rc2 import RC2
        from pysat.formula import IDPool, WCNF
    except ImportError as exc:  # pragma: no cover - environment diagnostic
        raise RuntimeError(
            "PySAT is required for rc2_degree_capped_preserve"
        ) from exc

    formula = WCNF()
    pool = IDPool()
    edge_codes = sorted({code for codes, _ in ledger.extrinsic for code in codes})
    y_of = {code: pool.id(("deleted", code)) for code in edge_codes}
    occurrences: dict[int, list[int]] = {code: [] for code in edge_codes}

    for tid, (codes, forced) in enumerate(ledger.extrinsic):
        xvars = [pool.id(("choice", tid, pos)) for pos in range(3)]
        if forced is None:
            # Exactly one chosen edge, written directly to avoid auxiliary
            # variables in this ubiquitous three-literal constraint.
            formula.append(xvars)
            for i in range(3):
                for j in range(i + 1, 3):
                    formula.append([-xvars[i], -xvars[j]])
        else:
            forced_pos = codes.index(forced)
            for pos, var in enumerate(xvars):
                formula.append([var] if pos == forced_pos else [-var])
        for code, xvar in zip(codes, xvars):
            yvar = y_of[code]
            occurrences[code].append(xvar)
            formula.append([-xvar, yvar])

    # No edge can enter D2 unless some extrinsic triangle actually chooses it.
    for code, yvar in y_of.items():
        formula.append([-yvar, *occurrences[code]])

    h = h_certified(pre.n)
    for vertex in range(pre.n):
        degree = pre.gprime_adj[vertex].bit_count()
        required = max(0, degree - (h - 1))
        if not required:
            continue
        incident_y = [
            y_of[code]
            for code in edge_codes
            if vertex in decode_edge(pre.n, code)
        ]
        if len(incident_y) < required:
            raise D2Infeasible(
                f"vertex {vertex} needs {required} incident D2 deletions but "
                f"only {len(incident_y)} extrinsic-triangle edges are eligible"
            )
        card = CardEnc.atleast(
            lits=incident_y,
            bound=required,
            vpool=pool,
            encoding=EncType.totalizer,
        )
        for clause in card.clauses:
            formula.append(clause)

    if exact_triangle_loss:
        # An intrinsic triangle is destroyed once, even if two of its edges
        # enter D2.  Concentrating unavoidable deletions on already-destroyed
        # triangles can therefore outperform the additive edge proxy.  The
        # weight makes triangle survival lexicographically primary, with edge
        # count only a deterministic secondary objective.
        triangle_weight = len(edge_codes) + 1
        for tid, (u, v, w) in enumerate(ledger.intrinsic):
            deletable = [
                y_of[code]
                for code in (
                    edge_code(pre.n, u, v),
                    edge_code(pre.n, u, w),
                    edge_code(pre.n, v, w),
                )
                if code in y_of
            ]
            if not deletable:
                continue
            destroyed = pool.id(("intrinsic-destroyed", tid))
            for yvar in deletable:
                formula.append([-yvar, destroyed])
            formula.append([-destroyed], weight=triangle_weight)
        for yvar in y_of.values():
            formula.append([-yvar], weight=1)
    else:
        for code, yvar in y_of.items():
            cost = 1 + ledger.intrinsic_edge_counts.get(code, 0)
            formula.append([-yvar], weight=cost)

    with RC2(formula, solver="cadical195", adapt=True, exhaust=True) as rc2:
        model = rc2.compute()
        if model is None:
            raise D2Infeasible("faithful exactly-one D2 assignment cannot meet degree cap")
    positive = {lit for lit in model if lit > 0}
    deleted = {code for code, yvar in y_of.items() if yvar in positive}

    if any(not any(code in deleted for code in codes) for codes, _ in ledger.extrinsic):
        raise AssertionError("degree-capped D2 assignment left an extrinsic triangle")
    final_degrees = []
    for vertex in range(pre.n):
        removed = sum(vertex in decode_edge(pre.n, code) for code in deleted)
        final_degrees.append(pre.gprime_adj[vertex].bit_count() - removed)
    if max(final_degrees, default=0) >= h:
        raise AssertionError("degree-capped D2 assignment violated its hard cap")
    return deleted


def d2_rc2_degree_capped_exact_survival(
    pre: Pregraph, ledger: TriangleLedger
) -> set[int]:
    """Degree-capped exact-one D2 with exact intrinsic-triangle objective."""
    return d2_rc2_degree_capped_preserve(
        pre, ledger, exact_triangle_loss=True
    )


def finalize(pre: Pregraph, ledger: TriangleLedger, strategy: str) -> tuple[list[int], dict]:
    if strategy == "paper_random":
        d2 = d2_random(pre, ledger)
    elif strategy == "greedy_preserve":
        d2 = d2_greedy_preserve(pre, ledger)
    elif strategy == "rc2_weighted_preserve":
        d2 = d2_rc2_weighted_preserve(pre, ledger)
    elif strategy == "rc2_degree_capped_preserve":
        d2 = d2_rc2_degree_capped_preserve(pre, ledger)
    elif strategy == "rc2_degree_capped_exact_survival":
        d2 = d2_rc2_degree_capped_exact_survival(pre, ledger)
    else:
        raise ValueError(f"unknown D2 strategy {strategy}")

    # Literal simultaneous deletion from G'.
    adj = list(pre.gprime_adj)
    for code in d2:
        u, v = decode_edge(pre.n, code)
        adj[u] &= ~(1 << v)
        adj[v] &= ~(1 << u)

    unhit = [codes for codes, _ in ledger.extrinsic if not any(c in d2 for c in codes)]
    if unhit:
        raise AssertionError("D2 did not hit every extrinsic triangle")
    surviving_intrinsic = sum(
        not any(
            edge_code(pre.n, a, b) in d2
            for a, b in ((u, v), (u, w), (v, w))
        )
        for u, v, w in ledger.intrinsic
    )
    stats = {
        "d2_strategy": strategy,
        "gprime_triangles": ledger.total,
        "intrinsic_triangles_before_d2": len(ledger.intrinsic),
        "extrinsic_triangles": len(ledger.extrinsic),
        "mixed_extrinsic_triangles": sum(forced is not None for _, forced in ledger.extrinsic),
        "d2_distinct_edges": len(d2),
        "intrinsic_triangles_surviving_d2": surviving_intrinsic,
        "final_edges": sum(x.bit_count() for x in adj) // 2,
        "literal_d2_replay": "PASS",
    }
    return adj, stats


def owner_good_edge_colouring(pre: Pregraph, adj: Sequence[int]) -> dict[int, int]:
    """Explicit red/blue colouring proving every final graph is nonarrowing.

    D1 gives each surviving edge a unique owner T3 copy.  Within each owner,
    colour part pairs 01 and 12 red and pair 02 blue.  D2 guarantees that
    every final triangle is contained in a single owner; hence its three
    colours are red, red, blue.  This is also the computational replay of the
    general obstruction recorded in FOLKMAN_OBSTRUCTION.md.
    """
    colouring: dict[int, int] = {}
    for u in range(pre.n):
        for v in iter_bits(adj[u] & ~((1 << (u + 1)) - 1)):
            code = edge_code(pre.n, u, v)
            owner = pre.edge_owner[code]
            parts = pre.copy_part_masks[owner]
            u_parts = [i for i, mask in enumerate(parts) if (mask >> u) & 1]
            v_parts = [i for i, mask in enumerate(parts) if (mask >> v) & 1]
            if len(u_parts) != 1 or len(v_parts) != 1 or u_parts[0] == v_parts[0]:
                raise AssertionError("owner T3 part reconstruction failed")
            pair = {u_parts[0], v_parts[0]}
            colouring[code] = 2 if pair == {0, 2} else 1
    for u, v, w in enumerate_triangles(adj):
        colours = {
            colouring[edge_code(pre.n, u, v)],
            colouring[edge_code(pre.n, u, w)],
            colouring[edge_code(pre.n, v, w)],
        }
        if len(colours) != 2:
            raise AssertionError(f"owner colouring has monochromatic triangle {(u,v,w)}")
    return colouring


def greedy_independent_order(adj: Sequence[int], order: Sequence[int]) -> int:
    chosen = 0
    for v in order:
        if not (adj[v] & chosen):
            chosen |= 1 << v
    return chosen


def greedy_independent_min_degree(adj: Sequence[int], rng: random.Random) -> int:
    remaining = (1 << len(adj)) - 1
    chosen = 0
    while remaining:
        vertices = list(iter_bits(remaining))
        rng.shuffle(vertices)
        v = min(vertices, key=lambda x: (adj[x] & remaining).bit_count())
        chosen |= 1 << v
        remaining &= ~(adj[v] | (1 << v))
    return chosen


def greedy_tf_order(adj: Sequence[int], order: Sequence[int], start: int = 0) -> int:
    chosen = start
    for v in order:
        if (chosen >> v) & 1:
            continue
        common = adj[v] & chosen
        if not has_edge_in_set(adj, common):
            chosen |= 1 << v
    return chosen


def one_swap_tf_walk(
    adj: Sequence[int], start: int, rng: random.Random, steps: int
) -> int:
    """Sound plateau walk: every swap removes a vertex hitting every new triangle."""
    n = len(adj)
    current = start
    best = start
    for step in range(steps):
        v = rng.randrange(n)
        if (current >> v) & 1:
            continue
        common = adj[v] & current
        hitting: int | None = None
        rest = common
        while rest:
            bit = rest & -rest
            a = bit.bit_length() - 1
            rest ^= bit
            partners = adj[a] & rest
            for b in iter_bits(partners):
                endpoints = (1 << a) | (1 << b)
                hitting = endpoints if hitting is None else hitting & endpoints
                if not hitting:
                    break
            if hitting == 0:
                break
        if hitting is None:
            current |= 1 << v
        elif hitting:
            options = list(iter_bits(hitting))
            u = rng.choice(options)
            candidate = (current & ~(1 << u)) | (1 << v)
            if not is_triangle_free_induced(adj, candidate):
                raise AssertionError("one-swap logic produced a triangle")
            current = candidate
        if step % 37 == 0:
            order = list(range(n))
            rng.shuffle(order)
            current = greedy_tf_order(adj, order, current)
        if current.bit_count() > best.bit_count():
            best = current
    return best


def lower_bound_searches(
    adj: Sequence[int], h: int, seed: int, robust_restarts: int = 96
) -> dict:
    n = len(adj)
    deg = [x.bit_count() for x in adj]
    rng = random.Random(derive_seed(seed, "lower-bound-search"))
    base = list(range(n))

    alpha_methods: list[tuple[str, int]] = []
    order = list(base)
    rng.shuffle(order)
    alpha_methods.append(("random_order", greedy_independent_order(adj, order)))
    order = sorted(base, key=lambda v: (deg[v], rng.random()))
    alpha_methods.append(("static_low_degree", greedy_independent_order(adj, order)))
    alpha_methods.append(("dynamic_min_degree", greedy_independent_min_degree(adj, rng)))
    alpha_best_name, alpha_best = max(alpha_methods, key=lambda x: x[1].bit_count())

    tf_methods: list[tuple[str, int]] = []
    for mode in ("random_order", "static_low_degree", "static_high_degree"):
        order = list(base)
        if mode == "random_order":
            rng.shuffle(order)
        elif mode == "static_low_degree":
            order.sort(key=lambda v: (deg[v], rng.random()))
        else:
            order.sort(key=lambda v: (-deg[v], rng.random()))
        tf_methods.append((mode, greedy_tf_order(adj, order)))
    tf_best_name, tf_best = max(tf_methods, key=lambda x: x[1].bit_count())

    # If the mandatory diversified first pass has not already killed the
    # sample, make the stall robust before considering exact optimization.
    if tf_best.bit_count() < h:
        for restart in range(robust_restarts):
            order = list(base)
            mode = restart % 3
            if mode == 0:
                rng.shuffle(order)
            elif mode == 1:
                order.sort(key=lambda v: (deg[v], rng.random()))
            else:
                order.sort(key=lambda v: (-deg[v], rng.random()))
            candidate = greedy_tf_order(adj, order)
            if candidate.bit_count() > tf_best.bit_count():
                tf_best = candidate
                tf_best_name = f"robust_restart_{restart}_{mode}"
            if tf_best.bit_count() >= h:
                break
        if tf_best.bit_count() < h:
            walked = one_swap_tf_walk(adj, tf_best, rng, steps=max(5000, 20 * n))
            if walked.bit_count() > tf_best.bit_count():
                tf_best = walked
                tf_best_name = "sound_one_swap_walk"

    if not is_independent(adj, alpha_best):
        raise AssertionError("alpha lower-bound witness is not independent")
    if not is_triangle_free_induced(adj, tf_best):
        raise AssertionError("tf lower-bound witness is not triangle-free")
    return {
        "alpha_lower": alpha_best.bit_count(),
        "alpha_method": alpha_best_name,
        "alpha_witness": list(iter_bits(alpha_best)),
        "tf3_lower": tf_best.bit_count(),
        "tf3_method": tf_best_name,
        "tf3_witness": list(iter_bits(tf_best)),
        "alpha_methods": {name: mask.bit_count() for name, mask in alpha_methods},
        "tf3_initial_methods": {name: mask.bit_count() for name, mask in tf_methods},
        "witness_replay": "PASS",
    }


def evaluate_final(
    pre: Pregraph,
    ledger: TriangleLedger,
    strategy: str,
    robust_restarts: int = 96,
    include_edges: bool = False,
) -> dict:
    t0 = time.time()
    adj, final_stats = finalize(pre, ledger, strategy)
    hinfo = h_certificate(pre.n)
    h = hinfo["h"]
    k4 = find_k4(adj)
    if k4 is not None:
        raise AssertionError(f"paper construction failed independent K4 audit: {k4}")
    good_colouring = owner_good_edge_colouring(pre, adj)
    deg = [x.bit_count() for x in adj]
    max_degree = max(deg)
    max_vertex = deg.index(max_degree)
    neighbourhood = adj[max_vertex]
    if not is_triangle_free_induced(adj, neighbourhood):
        raise AssertionError("K4-free neighbourhood gate failed")

    result = {
        "parameters": {
            "n": pre.n,
            "r": pre.r,
            "q": pre.q,
            "ell": pre.q * pre.r,
            "m_per_colour": pre.m,
            "seed": pre.seed,
            "d2_strategy": strategy,
        },
        "h_certificate": hinfo,
        "pregraph": pre.stats,
        "final": final_stats,
        "audit": {
            "independent_k4_check": "PASS",
            "explicit_no_monochromatic_triangle_edge_colouring": "PASS",
            "folkman_obstruction": "G does not edge-arrow (3,3)",
            "max_degree_neighbourhood_triangle_free": "PASS",
        },
        "degree": {
            "min": min(deg),
            "max": max_degree,
            "mean": sum(deg) / pre.n,
            "max_vertex": max_vertex,
            "max_neighbourhood_witness": list(iter_bits(neighbourhood)),
        },
    }
    # A necessary covering condition independent of any heuristic search:
    # if every h-set contained a triangle, then the surviving triangles would
    # cover all C(n,h) h-sets.  Each one covers C(n-3,h-3) of them.
    surviving_triangles = final_stats["intrinsic_triangles_surviving_d2"]
    required_triangle_supply = math.ceil(
        math.comb(pre.n, 3) / math.comb(h, 3)
    )
    result["triangle_coverage_gate"] = {
        "surviving_triangles": surviving_triangles,
        "necessary_minimum": required_triangle_supply,
        "supply_ratio": (
            surviving_triangles * math.comb(h, 3) / math.comb(pre.n, 3)
        ),
        "logic": (
            "tau*C(n-3,h-3) >= C(n,h) is necessary for every h-set "
            "to contain a triangle"
        ),
        "passes_necessary_count": surviving_triangles >= required_triangle_supply,
    }
    if max_degree >= h:
        result["lower_bounds"] = {
            "tf3_lower": max_degree,
            "tf3_method": "maximum neighbourhood (triangle-free because K4-free)",
            "tf3_witness": list(iter_bits(neighbourhood)),
            "witness_replay": "PASS",
        }
        result["verdict"] = "REJECT_DELTA_GE_H"
    else:
        lower = lower_bound_searches(
            adj, h, derive_seed(pre.seed, f"search-{strategy}"), robust_restarts
        )
        result["lower_bounds"] = lower
        if lower["alpha_lower"] >= h:
            result["verdict"] = "REJECT_ALPHA_GE_H"
        elif lower["tf3_lower"] >= h:
            result["verdict"] = "REJECT_TF3_GE_H"
        else:
            result["verdict"] = "HEURISTIC_SURVIVOR_EXACT_REQUIRED"
    lower_tf = result["lower_bounds"]["tf3_lower"]
    result["metrics"] = {
        "delta_over_h": max_degree / h,
        "tf3_lower_over_h": lower_tf / h,
        "uncovered_over_h": pre.stats["uncovered_vertices"] / h,
        "intrinsic_triangle_survival_fraction": (
            final_stats["intrinsic_triangles_surviving_d2"]
            / max(1, final_stats["intrinsic_triangles_before_d2"])
        ),
        "triangle_coverage_supply_ratio": result["triangle_coverage_gate"][
            "supply_ratio"
        ],
    }
    result["elapsed_s"] = time.time() - t0
    if include_edges:
        result["graph"] = {
            "n": pre.n,
            "edges": [
                [u, v]
                for u in range(pre.n)
                for v in iter_bits(adj[u] & ~((1 << (u + 1)) - 1))
            ],
        }
        result["good_edge_colouring"] = [
            [*decode_edge(pre.n, code), "red" if colour == 1 else "blue"]
            for code, colour in sorted(good_colouring.items())
        ]
    return result


def run_pregraph_job(job: dict) -> list[dict]:
    t0 = time.time()
    pre = build_pregraph(job["n"], job["r"], job["q"], job["m"], job["seed"])
    h = h_certified(pre.n)
    # An uncovered vertex is isolated.  If there are h of them, both D2
    # policies are soundly dead before triangle enumeration.
    strategies = job.get("strategies", ("paper_random", "greedy_preserve"))
    if pre.stats["uncovered_vertices"] >= h:
        outputs = []
        for strategy in strategies:
            outputs.append({
                "parameters": {
                    "n": pre.n, "r": pre.r, "q": pre.q, "ell": pre.q * pre.r,
                    "m_per_colour": pre.m, "seed": pre.seed, "d2_strategy": strategy,
                },
                "h_certificate": h_certificate(pre.n),
                "pregraph": pre.stats,
                "verdict": "REJECT_UNCOVERED_GE_H",
                "lower_bounds": {
                    "tf3_lower": pre.stats["uncovered_vertices"],
                    "tf3_method": "isolated uncovered vertices",
                },
                "metrics": {
                    "tf3_lower_over_h": pre.stats["uncovered_vertices"] / h,
                    "uncovered_over_h": pre.stats["uncovered_vertices"] / h,
                },
                "elapsed_s": time.time() - t0,
            })
        return outputs
    ledger = build_triangle_ledger(pre)
    outputs = []
    for strategy in strategies:
        try:
            out = evaluate_final(
                pre, ledger, strategy, job.get("robust_restarts", 96)
            )
        except D2Infeasible as exc:
            out = {
                "parameters": {
                    "n": pre.n,
                    "r": pre.r,
                    "q": pre.q,
                    "ell": pre.q * pre.r,
                    "m_per_colour": pre.m,
                    "seed": pre.seed,
                    "d2_strategy": strategy,
                },
                "h_certificate": h_certificate(pre.n),
                "pregraph": pre.stats,
                "triangle_ledger": {
                    "gprime_triangles": ledger.total,
                    "intrinsic_triangles": len(ledger.intrinsic),
                    "extrinsic_triangles": len(ledger.extrinsic),
                },
                "verdict": "D2_DEGREE_CAP_INFEASIBLE",
                "obstruction": str(exc),
            }
        outputs.append(out)
    for out in outputs:
        out["pregraph_elapsed_s"] = time.time() - t0
    return outputs


def registered_grid() -> list[dict]:
    """Independent-audit core grid, updated to current H certificates."""
    rows = [
        (171, 1, 3, [92, 108, 124]),
        (288, 1, 3, [228, 267, 306]),
        (288, 1, 6, [50, 57, 65]),
        (288, 2, 3, [50, 57, 65]),
        (528, 1, 6, [125, 146, 168]),
        (528, 2, 3, [125, 146, 168]),
        (840, 1, 9, [116, 131, 148]),
        (840, 3, 3, [116, 131, 148]),
        (984, 1, 9, [145, 162, 182]),
        (984, 3, 3, [145, 162, 182]),
    ]
    jobs: list[dict] = []
    for n, r, q, ms in rows:
        for m in ms:
            for seed_index in range(2):
                seed = derive_seed(20260803 + seed_index, f"grid-{n}-{r}-{q}-{m}")
                jobs.append({
                    "n": n,
                    "r": r,
                    "q": q,
                    "m": m,
                    "seed": seed,
                    "robust_restarts": 96,
                })
    return jobs


def boundary_grid() -> list[dict]:
    """Changed second cycle: Ramsey jumps and the observed degree boundary.

    This is not an unchanged resampling pass.  It moves to every currently
    certified finite jump from 50 through 171, raises m until the mandatory
    Delta<h gate becomes active, tests both ell=3 and clustered ell=6 where
    useful, and adds an exact weighted-MaxSAT D2 optimizer.
    """
    orders = [50, 59, 68, 77, 87, 97, 109, 120, 132, 145, 157, 171]
    structures: list[tuple[int, int, int]] = [(n, 1, 3) for n in orders]
    structures.extend((n, 1, 6) for n in (68, 109, 171))
    structures.extend((n, 2, 3) for n in (68, 120))
    jobs: list[dict] = []
    for n, r, q in structures:
        h = h_certified(n)
        ell = r * q
        # Pre-D1 mean degree is approximately 4m ell^2/(3n).  Four
        # increasing targets bracket the observed Delta boundary.
        ms = sorted({
            max(2, round(frac * h * 3 * n / (4 * ell * ell)))
            for frac in (0.42, 0.52, 0.62, 0.72)
        })
        for m in ms:
            for seed_index in range(2):
                seed = derive_seed(
                    20260830 + seed_index, f"boundary-{n}-{r}-{q}-{m}"
                )
                jobs.append({
                    "n": n,
                    "r": r,
                    "q": q,
                    "m": m,
                    "seed": seed,
                    "robust_restarts": 96,
                    "strategies": [
                        "paper_random",
                        "greedy_preserve",
                        "rc2_weighted_preserve",
                    ],
                })
    return jobs


def degree_cap_grid() -> list[dict]:
    """Third cycle: denser pregraphs plus literal degree-constrained D2.

    The prior policies optimized edge count and intrinsic-triangle survival,
    but did not direct deletions toward high-degree vertices.  These values go
    beyond the observed Delta boundary at the four smallest Ramsey jumps and
    test a new global assignment mechanism.  Two ell=6 representations test
    whether larger intrinsic tripartite pieces benefit from the same control.
    """
    rows = [
        (50, 1, 3, [35, 40, 45, 50]),
        (59, 1, 3, [44, 50, 56, 62]),
        (68, 1, 3, [55, 63, 72, 82]),
        (77, 1, 3, [68, 78, 88, 98]),
        (50, 1, 6, [8, 10, 12, 14]),
        (68, 1, 6, [10, 14, 18, 22]),
        (68, 2, 3, [10, 14, 18, 22]),
    ]
    jobs: list[dict] = []
    for n, r, q, ms in rows:
        for m in ms:
            for seed_index in range(2):
                jobs.append({
                    "n": n,
                    "r": r,
                    "q": q,
                    "m": m,
                    "seed": derive_seed(
                        20260831 + seed_index,
                        f"degree-cap-{n}-{r}-{q}-{m}",
                    ),
                    "robust_restarts": 160,
                    "strategies": ["rc2_degree_capped_preserve"],
                })
    return jobs


def degree_cap_exact_grid() -> list[dict]:
    """Replay the identical third-cycle pregraphs with an exact loss model."""
    jobs = degree_cap_grid()
    for job in jobs:
        job["strategies"] = ["rc2_degree_capped_exact_survival"]
    return jobs


def smoke() -> dict:
    cases = []
    # Exhaustively compare the bitset K4 audit with combinations on small
    # outputs and replay both deletion invariants.
    import itertools

    for seed in range(12):
        pre = build_pregraph(24, 1, 3, 12, seed)
        ledger = build_triangle_ledger(pre)
        for strategy in ("paper_random", "greedy_preserve"):
            adj, stats = finalize(pre, ledger, strategy)
            owner_good_edge_colouring(pre, adj)
            fast = find_k4(adj)
            brute = None
            for quad in itertools.combinations(range(24), 4):
                if all((adj[u] >> v) & 1 for u, v in itertools.combinations(quad, 2)):
                    brute = quad
                    break
            if (fast is None) != (brute is None):
                raise AssertionError("independent K4 auditors disagree")
            if brute is not None:
                raise AssertionError(f"K4 unexpectedly survived: {brute}")
            cases.append({
                "seed": seed,
                "strategy": strategy,
                "explicit_nonarrowing_colouring": "PASS",
                **stats,
            })
    thresholds = {n: h_certificate(n) for n in (41, 50, 171, 288, 528, 840, 984)}
    if thresholds[171]["h"] != 22:
        raise AssertionError("current R(3,22)<=171 threshold was not applied")
    return {
        "status": "PASS",
        "small_final_graphs_checked": len(cases),
        "cases": cases,
        "thresholds": thresholds,
    }


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_sweep(output: Path, workers: int, jobs: list[dict], label: str) -> dict:
    grid_path = output.with_name("PARAMETER_GRID.json")
    if label != "registered_core":
        grid_path = output.with_name(f"{label.upper()}_GRID.json")
    strategies = sorted({s for job in jobs for s in job.get(
        "strategies", ("paper_random", "greedy_preserve")
    )})
    write_json(grid_path, {
        "registered_at": "2026-08-03",
        "label": label,
        "jobs": jobs,
        "pregraphs": len(jobs),
        "final_graphs": sum(len(job.get(
            "strategies", ("paper_random", "greedy_preserve")
        )) for job in jobs),
        "d2_strategies": strategies,
        "source": SOURCE,
    })
    t0 = time.time()
    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_pregraph_job, job): job for job in jobs}
        for index, future in enumerate(as_completed(futures), 1):
            job = futures[future]
            try:
                outputs = future.result()
            except Exception as exc:
                outputs = [{"parameters": job, "verdict": "ERROR", "error": repr(exc)}]
            results.extend(outputs)
            print(
                f"[{index}/{len(jobs)}] n={job['n']} r={job['r']} q={job['q']} "
                f"m={job['m']} -> {', '.join(x['verdict'] for x in outputs)}",
                flush=True,
            )
    results.sort(key=lambda x: (
        x.get("parameters", {}).get("n", 0),
        x.get("parameters", {}).get("r", 0),
        x.get("parameters", {}).get("q", 0),
        x.get("parameters", {}).get("m_per_colour", x.get("parameters", {}).get("m", 0)),
        x.get("parameters", {}).get("seed", 0),
        x.get("parameters", {}).get("d2_strategy", ""),
    ))
    nonerrors = [x for x in results if x.get("verdict") != "ERROR"]
    ranked = sorted(
        nonerrors,
        key=lambda x: (
            x.get("degree", {}).get("max", 10**9)
            >= x.get("h_certificate", {}).get("h", 0),
            x.get("metrics", {}).get("tf3_lower_over_h", 10**9),
            x.get("metrics", {}).get("delta_over_h", 10**9),
        ),
    )
    summary = {
        "status": "COMPLETE",
        "label": label,
        "source": SOURCE,
        "elapsed_s": time.time() - t0,
        "workers": workers,
        "pregraphs": len(jobs),
        "final_graphs": len(results),
        "verdict_counts": {
            verdict: sum(x.get("verdict") == verdict for x in results)
            for verdict in sorted({x.get("verdict", "MISSING") for x in results})
        },
        "best_ten": ranked[:10],
        "results": results,
    }
    write_json(output, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--sweep", type=Path)
    group.add_argument("--boundary-sweep", type=Path)
    group.add_argument("--degree-cap-sweep", type=Path)
    group.add_argument("--degree-cap-exact-sweep", type=Path)
    group.add_argument("--one", nargs=5, metavar=("N", "R", "Q", "M", "SEED"))
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--include-edges", action="store_true")
    parser.add_argument(
        "--strategy",
        action="append",
        choices=(
            "paper_random",
            "greedy_preserve",
            "rc2_weighted_preserve",
            "rc2_degree_capped_preserve",
            "rc2_degree_capped_exact_survival",
        ),
        help="D2 strategy for --one; repeat to compare several",
    )
    parser.add_argument("--output", type=Path, help="also write smoke/--one JSON")
    args = parser.parse_args()
    if args.smoke:
        result = smoke()
        if args.output:
            write_json(args.output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.sweep:
        summary = run_sweep(
            args.sweep, max(1, args.workers), registered_grid(), "registered_core"
        )
        print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    elif args.boundary_sweep:
        summary = run_sweep(
            args.boundary_sweep,
            max(1, args.workers),
            boundary_grid(),
            "jump_boundary_cycle",
        )
        print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    elif args.degree_cap_sweep:
        summary = run_sweep(
            args.degree_cap_sweep,
            max(1, args.workers),
            degree_cap_grid(),
            "degree_capped_d2_cycle",
        )
        print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    elif args.degree_cap_exact_sweep:
        summary = run_sweep(
            args.degree_cap_exact_sweep,
            max(1, args.workers),
            degree_cap_exact_grid(),
            "degree_capped_exact_survival_cycle",
        )
        print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    else:
        n, r, q, m, seed = map(int, args.one)
        pre = build_pregraph(n, r, q, m, seed)
        ledger = build_triangle_ledger(pre)
        strategies = args.strategy or ["paper_random", "greedy_preserve"]
        outputs = [
            evaluate_final(pre, ledger, strategy, include_edges=args.include_edges)
            for strategy in strategies
        ]
        if args.output:
            write_json(args.output, outputs)
        print(json.dumps(outputs, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
