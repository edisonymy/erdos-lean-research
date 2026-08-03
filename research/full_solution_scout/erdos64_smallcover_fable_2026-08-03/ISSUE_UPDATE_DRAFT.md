# Draft public update for issue #9 (post at wrap-up; fill FINAL numbers)

> **WITHDRAWN DRAFT — DO NOT POST.**  It predates the Royle/F038A and
> McKay--Afzaly priority corrections, contains an incorrect order range, and
> omits the successor certificate results.  Use a new update derived from
> `root_independent_audit_2026-08-03/` and the certified σ=19 handover.

## 2026-08-04 update — small-cover and bipartite two-defect lanes (not a solution)

This update reports two new finite counterexample families for #64, one
DRAT-certified structural theorem, and bounded exclusions.  **No
counterexample and no universal proof; this is not a solution.**
Packet: `research/full_solution_scout/erdos64_smallcover_fable_2026-08-03/`
(LEDGER.md is the append-only log; REPORT.md the summary).

**1. Mersenne-free bipartite marked edges.**  For a bipartite cubic host
H with marked edge e, the campaign's marked-edge criterion simplifies:
the Mersenne condition (no (2^k - 1)-cycle through e) holds vacuously.
Equivalently, define a *two-defect block*: bipartite F, exactly one
degree-2 vertex in each side, all other degrees 3, and no C4/C8/C16/C32.
Two copies of F, each with a midpoint joining its two defects, connected
by a bridge, form a cubic graph with no power-of-two cycle.  A same-side
defect pair is impossible mod 3.  |E(F)| is exactly one more than the
Győri–Li–Salia–Tompkins–Varga–Zhu maximum for 0-mod-4-cycle-free graphs.

**2. Exclusion.**  SAT with static quadrilateral clauses and C16/C32
CEGAR excludes two-defect blocks for every even order n_F = 24..[42/44],
killing the bipartite marked-edge mechanism for hosts through order
[42/44].  The campaign census previously gave 24.  Calibration: every
(3,10)-cage minus an edge is a C4/C8-free two-defect block on 70
vertices (each cage contains C16, checked), so the C8-part of this
ladder flips somewhere in (44, 70] — that window, with the C16/C32
battle, is the lane's continuation.

**3. Certified small-side theorem.**  DRAT-certified (kissat-4.0.4 +
drat-trim, hashes in the packet): for sigma <= [17/18/19], no linear
hypergraph on sigma points with point-degrees >= 3 and edge sizes >= 3
has a C8-free incidence graph.  Equivalently, **every bipartite graph
with minimum degree >= 3, no C4 and no C8 has at least [18/19/20]
vertices on each side.**  Corollary: every bipartite counterexample to
#64 has both sides >= [18/19/20], already from its C4/C8 conditions
(compare the published total-order bound of 32).  The extremal threshold
lies in [[18/19/20], 35]: side 35 is realized by the (3,10)-cages.
C6 (triangles of lines) is allowed throughout — this
"triangle-permitting, quadrilateral-free" family appears to be
unstudied; a Z_9 Heawood lift on 63+63 vertices gives a C6-rich C8-free
specimen (frozen and independently checked in the packet).

**4. Small-cover family.**  Any min-degree-3 graph with an independent
set of co-size sigma <= 15 has all cycles of length <= 30, so it needs
only C4/C8/C16 avoidance to refute #64; the family is finite (n <= 50)
and lies beyond the public SMS frontier (n <= 31).  The bipartite case
is closed by the theorem above.  The general case (edges inside the
cover) ran with exact static C8 shapes for [status at wrap-up].

Verification pipeline: independent stdlib cycle checker, positive
controls (encodings go SAT when the C8 clauses are removed, with
verified C8-present models), one encoding leak found by CEGAR histogram
and fixed with proven-exact degeneracy excuses, one of my own counting
lemmas found wrong and corrected (LEDGER entries 4-5).  Priority checks
on 2026-08-03 found no prior statement of the small-side theorem or the
two-defect reduction; that is search-relative, not a guarantee.
