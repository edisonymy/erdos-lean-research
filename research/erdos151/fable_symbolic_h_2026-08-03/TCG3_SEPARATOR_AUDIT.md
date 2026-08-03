# V1 / TCG-3 separator audit

Date: 2026-08-03

Status: **PASS as a standalone, future-successor-only separator.**  Neither
live CEGAR process was changed, stopped, or restarted.

## Finding

`cegar_face_matching3.py` has no triangle-free two-partition separator.  Its
model loop reconstructs the graph, invokes only `oracle_admissible`, and adds
the fixed-size admissible-set cut made from triangle witnesses and maximal-edge
witnesses.  Its `triangle_var` helper supplies reusable one-way triangle
witnesses, but there is no triangle-hypergraph two-coloring oracle and no cut
over triples internal to the two sides of a vertex partition.  Thus the
existing terminal admissible-set test is not an implementation of V1/TCG-3.

## Soundness

Let `V=A union B`, with both `G[A]` and `G[B]` triangle-free.  Color an edge
red when it crosses the partition and blue when it is internal.  A triangle
has either zero or two crossing edges, so it cannot be all red.  An all-blue
triangle would be contained in one side, which the hypothesis excludes.
Therefore the partition certifies `G` does not edge-arrow `(3,3)`.

For a partition found in a rejected model, the future CEGAR cut is

```text
OR { y_t : t is a triple contained in A or contained in B }.
```

The inherited definition is only one-way:

```text
y_{abc} -> e_ab,  y_{abc} -> e_ac,  y_{abc} -> e_bc.
```

This is sufficient and exact for the cut.  Under a fixed graph, a nontriangle
forces its witness false, while a triangle permits its witness to be true.
Consequently the disjunction is satisfiable exactly when one of the two sides
contains a triangle.  The rejected graph has none.  Every edge-arrowing target
has at least one for this fixed partition, so no target is removed.  Reverse
edge-to-witness implications are unnecessary.

This is a one-way obstruction: failure to find a triangle-free two-partition
does not itself prove that a graph edge-arrows `(3,3)`.

## Implementation and exhaustive audit

`tcg3_separator.py` provides:

- exact triangle enumeration;
- an exact two-colorability SAT oracle for the triangle hypergraph;
- independent partition validation; and
- construction of the inherited-`y_t` CEGAR clause.

`audit_tcg3_separator.py` passed all of the following:

- all 8 side assignments of a single triangle, verifying the V1 coloring
  argument;
- all 32,768 labeled graphs on 6 vertices, with the SAT oracle agreeing with
  brute-force partition enumeration in every case (32,596 partitionable and
  172 nonpartitionable); and
- 16,384 fixed-graph/fixed-partition checks on 5 vertices, verifying directly
  that the actual `tcg3_cut` plus the inherited three one-way clauses is SAT
  exactly when an internal triple is a triangle.

The audit also compiles both Python files and statically confirms that the
matching-3 successor does not call the new separator.  The absence conclusion
was additionally checked by inspecting its model loop: its sole structural
oracle call is `oracle_admissible`.

## Order-50 cost and recommendation

For a reconstructed order-50 graph, the exact oracle uses 50 Boolean variables
and two clauses per actual triangle, at most 39,200 clauses.  A partition with
side sizes `a` and `50-a` produces

```text
C(a,3) + C(50-a,3)
```

cut literals: 4,600 for a 25/25 partition and at most 19,600.  The incremental
solver receives one long cut clause and at most three new implication clauses
per previously unseen triangle witness; witnesses already created by the
admissible-set cuts are reused.

**Recommendation: yes, it is worth a bounded later successor pilot, but not a
restart of either live run.**  The oracle is exact and small, and the cut
captures a qualitatively global obstruction.  Runtime benefit is not yet
established: a long disjunction may propagate weakly, an arbitrary SAT
partition may be unbalanced, and early rounds may have to define many new
`y_t` witnesses.  A future flag-gated A/B pilot should add at most one TCG-3
cut per model, prefer a near-balanced satisfying partition when possible, and
compare equal-seed/equal-budget throughput and convergence before a production
relaunch.

No order-50 run using this separator was performed, and no claim about its hit
rate or speedup is made.

## Reproducibility

Run from the workspace root:

```powershell
.venv\Scripts\python.exe -m py_compile `
  research/erdos151/fable_symbolic_h_2026-08-03/tcg3_separator.py `
  research/erdos151/fable_symbolic_h_2026-08-03/audit_tcg3_separator.py
.venv\Scripts\python.exe `
  research/erdos151/fable_symbolic_h_2026-08-03/audit_tcg3_separator.py
```

SHA-256:

```text
66767EFAC9779E5C743683A0955AE7A5CD4B5EA8650C72635ECA4B80880C952F  tcg3_separator.py
C91BE4F992FC0CECC25B2BD7E09A7DEF1AB999F79028D70A45F9647EA28897AA  audit_tcg3_separator.py
9F419A4288365CBFE08C9726FDC21DC01F21B65D5245A4CD9008A6FE4FF92DEF  audit_tcg3_separator.result.json
```
