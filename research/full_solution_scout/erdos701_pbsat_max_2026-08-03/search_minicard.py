#!/usr/bin/env python3
"""Native-cardinality SAT search for an Erdős #701 counterexample on [8].

This encoder is intentionally independent of the CP-SAT and Z3 encoders in
the sibling directory.  Its ordinary constraints are CNF clauses and its
counting constraints are MiniCard native AtMost constraints.

The sought objects are a downset F and an intersecting A subset F such that
|A| > |F_x| for every x in [8].  In the strong (default) mode we use three
lossless normalizations:

* F = down(A).  Given a counterexample, first replace F by down(A) plus the
  eight singletons.  Replacing A by a maximal intersecting extension inside
  that smaller F preserves the strict inequalities.  If union(A)=[8], every
  singleton already lies in down(A), so the ``plus singletons'' is redundant.
* A is maximal intersecting inside F.  Every omitted T in F then has a member
  of A disjoint from T.
* union(A)=[8].  Otherwise the same counterexample lives on at most seven
  points, which is ruled out by the separately established n<=7 result.

No normalization is needed to decode or verify a SAT answer: the output is
checked directly against the original definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from pysat.formula import CNFPlus, IDPool
from pysat.solvers import Solver


N = 8
M = 1 << N
FULL = M - 1


def subsets_immediate(mask: int):
    """Yield masks obtained by deleting one element."""
    bit = 1
    while bit < M:
        if mask & bit:
            yield mask ^ bit
        bit <<= 1


def supersets(mask: int):
    outside = FULL ^ mask
    add = outside
    while True:
        yield mask | add
        if add == 0:
            break
        add = (add - 1) & outside


def build_formula(args: argparse.Namespace):
    pool = IDPool()
    f = [pool.id(("F", s)) for s in range(M)]
    a = [pool.id(("A", s)) for s in range(M)]
    formula = CNFPlus()
    counts = {
        "units": 0,
        "downward_immediate": 0,
        "A_subset_F": 0,
        "A_intersecting": 0,
        "normal_form_reverse": 0,
        "full_support": 0,
        "maximal_intersecting": 0,
        "upward_closure_redundant_strengthening": 0,
        "minimum_member_branch": 0,
        "star_order_native": 0,
        "strict_gap_native": 0,
        "threshold_native": 0,
    }

    def clause(lits):
        formula.append(list(lits))

    def unit(lit: int):
        clause([lit])
        counts["units"] += 1

    # Definition-level conventions.  A nonempty downset on the stated ground
    # set contains the empty set and every singleton.  The empty set cannot be
    # a member of a non-vacuously intersecting witness.
    unit(f[0])
    unit(-a[0])
    for x in range(N):
        unit(f[1 << x])

    # Immediate-subset implications are equivalent to downward closure.
    for s in range(1, M):
        for t in subsets_immediate(s):
            clause([-f[s], f[t]])
            counts["downward_immediate"] += 1

    for s in range(M):
        clause([-a[s], f[s]])
        counts["A_subset_F"] += 1

    # A is pairwise intersecting.
    for s in range(1, M):
        for t in range(s + 1, M):
            if (s & t) == 0:
                clause([-a[s], -a[t]])
                counts["A_intersecting"] += 1

    strong = not args.bare
    if strong:
        # A singleton witness is contained in that singleton's star and hence
        # cannot beat it.  These units are redundant but propagationally useful.
        for x in range(N):
            unit(-a[1 << x])

        # union(A)=[8].
        for x in range(N):
            clause(a[s] for s in range(1, M) if s & (1 << x))
            counts["full_support"] += 1

        # Reverse implication for F=down(A).  The forward implication follows
        # from A subset F and downward closure.  Full support supplies the
        # singleton cases; the empty-set case is fixed above.
        for s in range(M):
            if s.bit_count() >= 2:
                clause([-f[s], *(a[t] for t in supersets(s))])
                counts["normal_form_reverse"] += 1

        # Maximality of A within F: if T belongs to F but not A, at least one
        # selected set is disjoint from T.  This includes T=empty and thus also
        # explicitly forces A nonempty.
        for t in range(M):
            blockers = [a[s] for s in range(1, M) if (s & t) == 0]
            clause([-f[t], a[t], *blockers])
            counts["maximal_intersecting"] += 1

        if args.upclosure:
            # Logically entailed by maximality, included only as a CDCL aid.
            for s in range(1, M):
                for t in supersets(s):
                    if t != s:
                        clause([-a[s], -f[t], a[t]])
                        counts["upward_closure_redundant_strengthening"] += 1

    if args.min_member is not None:
        if not strong:
            raise ValueError("--min-member is implemented only in strong mode")
        r = args.min_member
        if not 2 <= r <= N:
            raise ValueError("--min-member must be in [2,8]")
        chosen = (1 << r) - 1
        unit(a[chosen])
        counts["minimum_member_branch"] += 1
        for s in range(1, M):
            if s.bit_count() < r:
                unit(-a[s])
                counts["minimum_member_branch"] += 1

    # Native cardinality comparisons.  MiniCard accepts signed literals.
    # |A| >= |F_x|+1  iff  |F_x| + sum_s (not A_s) <= 255.
    if args.threshold is None:
        neg_a = [-a[s] for s in range(M)]
        for x in range(N):
            fstar = [f[s] for s in range(M) if s & (1 << x)]
            formula.append([[*fstar, *neg_a], M - 1], is_atmost=True)
            counts["strict_gap_native"] += 1
    else:
        k = args.threshold
        if not 1 <= k <= 128:
            raise ValueError("--threshold must be in [1,128]")
        # A counterexample exists with |A|=K and max star m<K iff it satisfies
        # this split formulation for some k in [m+1,K].
        formula.append([[-a[s] for s in range(M)], M - k], is_atmost=True)
        counts["threshold_native"] += 1
        for x in range(N):
            fstar = [f[s] for s in range(M) if s & (1 << x)]
            formula.append([fstar, k - 1], is_atmost=True)
            counts["threshold_native"] += 1

    # Element relabelling symmetry.  Without a fixed minimum member we may
    # order all stars.  In an r-branch, only permutations within the chosen
    # prefix and within its complement stabilize the branch.
    if strong and args.star_order:
        groups = [list(range(N))]
        if args.min_member is not None:
            r = args.min_member
            groups = [list(range(r)), list(range(r, N))]
        for group in groups:
            for x, y in zip(group, group[1:]):
                # |F_x| >= |F_y| after cancelling sets containing both:
                # |F_{y\not x}| + sum_{S in F_{x\not y}} (not F_S) <= 64.
                yon = [f[s] for s in range(M)
                       if (s & (1 << y)) and not (s & (1 << x))]
                xoff = [-f[s] for s in range(M)
                        if (s & (1 << x)) and not (s & (1 << y))]
                assert len(yon) == len(xoff) == 64
                formula.append([[*yon, *xoff], 64], is_atmost=True)
                counts["star_order_native"] += 1

    metadata = {
        "variables_before_solver": pool.top,
        "ordinary_clauses": len(formula.clauses),
        "native_atmost_constraints": len(formula.atmosts),
        "constraint_counts": counts,
    }
    return pool, f, a, formula, metadata


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=180.0)
    ap.add_argument("--seed", type=int, default=701080301)
    ap.add_argument("--bare", action="store_true")
    ap.add_argument("--upclosure", action="store_true")
    ap.add_argument("--star-order", action="store_true")
    ap.add_argument("--threshold", type=int)
    ap.add_argument("--min-member", type=int)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    # MiniCard's native-cardinality backend does not reliably honor PySAT's
    # asynchronous interrupt.  Enforce the wall-clock limit from a parent
    # process so a timed-out native solve cannot linger in the background.
    if not args.worker:
        command = [sys.executable, *sys.argv, "--worker"]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            output, _ = proc.communicate(timeout=args.seconds + 5.0)
            print(output, end="")
            return proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            output, _ = proc.communicate()
            if output:
                print(output, end="")
            _, _, _, formula, metadata = build_formula(args)
            payload = {
                "schema": "erdos701-n8-minicard-v1",
                "engine": "PySAT MiniCard native cardinality",
                "status": "UNKNOWN_TIMEOUT",
                "parameters": {
                    "seconds": args.seconds,
                    "seed_provenance_only": args.seed,
                    "bare": args.bare,
                    "upclosure": args.upclosure,
                    "star_order": args.star_order,
                    "threshold": args.threshold,
                    "min_member": args.min_member,
                },
                "encoding": metadata,
                "family_masks": None,
                "witness_masks": None,
                "family_size": None,
                "witness_size": None,
                "star_sizes": None,
                "minimum_gap": None,
                "watchdog": "parent process killed worker after wall-clock budget",
                "claim_boundary": "timeout proves nothing",
            }
            encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_bytes(encoded)
            print(json.dumps({
                "event": "result", "status": "UNKNOWN_TIMEOUT",
                "sha256": hashlib.sha256(encoded).hexdigest(),
            }, sort_keys=True), flush=True)
            return 0

    started = time.monotonic()
    pool, f, a, formula, metadata = build_formula(args)
    built = time.monotonic()
    print(json.dumps({"event": "built", **metadata,
                      "build_seconds": built - started}), flush=True)

    # MiniCard is deterministic for a fixed formula in this PySAT build; seed
    # is retained as provenance and for parity with the two sibling encoders.
    with Solver(name="minicard", bootstrap_with=formula, use_timer=True) as solver:
        # The parent process is the hard wall-clock watchdog.
        answer = solver.solve()
        elapsed = time.monotonic() - built
        status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN_TIMEOUT"
        family = witness = stars = None
        if answer is True:
            positive = {lit for lit in solver.get_model() if lit > 0}
            family = [s for s in range(M) if f[s] in positive]
            witness = [s for s in range(M) if a[s] in positive]
            stars = [sum(bool(s & (1 << x)) for s in family) for x in range(N)]
        payload = {
            "schema": "erdos701-n8-minicard-v1",
            "engine": "PySAT MiniCard native cardinality",
            "status": status,
            "parameters": {
                "seconds": args.seconds,
                "seed_provenance_only": args.seed,
                "bare": args.bare,
                "upclosure": args.upclosure,
                "star_order": args.star_order,
                "threshold": args.threshold,
                "min_member": args.min_member,
            },
            "encoding": metadata,
            "build_seconds": built - started,
            "solve_seconds": elapsed,
            "solver_statistics": solver.accum_stats(),
            "family_masks": family,
            "witness_masks": witness,
            "family_size": None if family is None else len(family),
            "witness_size": None if witness is None else len(witness),
            "star_sizes": stars,
            "minimum_gap": None if witness is None else min(len(witness) - z for z in stars),
            "claim_boundary": (
                "SAT is a candidate full negative resolution, subject to independent verification; "
                "UNSAT concerns n=8 and the selected lossless branch only; timeout proves nothing"
            ),
        }
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(encoded)
        print(json.dumps({
            "event": "result", "status": status, "solve_seconds": elapsed,
            "family_size": payload["family_size"],
            "witness_size": payload["witness_size"],
            "minimum_gap": payload["minimum_gap"],
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }, sort_keys=True), flush=True)
        return 10 if answer is True else 20 if answer is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
