# Erdős #701 native-cardinality lane — prior-art collision

Status: **STOPPED / PRIOR_ART_COLLISION**  
Scope: ground set of size exactly 8  
Stopped: 2026-08-03T06:54:14+01:00

## Outcome

No counterexample and no UNSAT result are claimed.  The solver pulse was
stopped before completion as soon as a 2025 public dissertation was found to
have already run an exact order-8 computation.  This lane therefore has no
plausible priority value for the campaign's goal.

Leon Eifler's dissertation, *Algorithms and Certificates for Exact Mixed
Integer Programming* (TU Berlin, 2025), says in its overview that the improved
exact-MIP machinery proves Chvátal's conjecture for ground sets of size at
most 8.  Table 8.1 records exact SCIP solving `Pred(8)` in `450.0k` seconds,
and the text describes this as roughly 5.2 days.  The same passage explicitly
says certification was disabled because the projected VIPR certificate would
exceed 1 TB.  Thus the thesis is clear prior art for the mathematical/computational
order-8 claim, while its lack of a published solver-independent certificate is
an important reproducibility qualification.

Primary source (checked 2026-08-03):

https://d-nb.info/1370379641/34

Relevant locations in the PDF are the overview on PDF page 10 and Section
8.1.2 / Table 8.1 on PDF pages 133–134.

## Preserved independent formulation

`search_minicard.py` is a third, solver-native formulation, independent of the
sibling CP-SAT and Z3 implementations.  It uses 256 membership variables for
the downset `F`, 256 for the intersecting witness `A`, ordinary CNF clauses,
and MiniCard native cardinality constraints.  The direct strict inequality is

```text
|F_x| + sum_S (not A_S) <= 255,
```

which is exactly `|A| >= |F_x| + 1`.  An alternative threshold split uses
`|A| >= k` and `|F_x| <= k-1` for all eight elements.

The default strong formulation uses the following lossless normal form:

1. Starting with any counterexample `(F,A)`, replace `F` by `down(A)` plus all
   singletons.  This can only decrease stars.
2. Extend `A` to a maximal intersecting family inside the new `F`; this can
   only increase `|A|`.
3. A counterexample at the first unhandled order has `union(A)=[8]`; otherwise
   it is a counterexample on at most seven points.  Consequently every
   singleton is already in `down(A)`, so `F=down(A)` exactly.

The encoder also supports lossless minimum-member branches: choose a
minimum-cardinality member of `A`, relabel it to an initial segment, and order
stars only within the branch stabilizer.  The root agent independently audited
the direct inequality, threshold split, star-order cancellation, minimum-member
branch, and normal-form argument as sound before the prior-art stop.

`verify_independent.py` checks any future SAT output solely from the original
definitions: mask range, empty-set conventions, ground-set union, downward
closure, `A subset F`, pairwise intersection, and strict domination of all
eight stars.  The normal form and maximality are reported only as diagnostics.

## Execution record and boundary

A two-second smoke attempt at threshold `k=106` built the intended formula:

- 512 primary variables;
- 4,834 ordinary clauses;
- 16 native AtMost constraints;
- 3,025 disjoint-pair clauses;
- 1,024 immediate down-closure clauses;
- 247 reverse normal-form clauses;
- 256 maximality clauses;
- 7 star-order constraints and 9 threshold constraints.

The installed MiniCard backend did not honor the asynchronous interrupt.  The
exact process launched by this lane was identified and stopped; it produced no
result file and no logical status.  The preserved script was then repaired to
enforce future limits with a parent-process watchdog, but it was not run again
after the priority collision.  No other process was stopped.

This package must not be cited as evidence for or against Erdős #701, nor as a
new order-8 result.  It is retained only as audited search infrastructure and
as a campaign record of the priority-gate stop.

