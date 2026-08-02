# Order 40, clique number 4 or 5: fixed-clique reductions (Erdős #151)

> **Audit failure notice (2 August 2026): this historical draft is not sound
> as written and must not be used as a proof or solver specification.**  Its
> opening independence-number claim, first G3 construction, multi-adjacency
> slopes, and claimed applicability to the active order-41 runs failed
> independent audit.  The surviving corrected statements and exact sound
> clauses are in
> [`N40_CLIQUE_CASES_AUDIT.md`](N40_CLIQUE_CASES_AUDIT.md).

**2 August 2026, Fable lane.  All claims conditional on order 40 being
the h = 10 jump (i.e. `R(3,10) = 40`; otherwise 40 is a plateau order,
already excluded by monotonicity) and on a least counterexample `G`
there with `omega(G) ∈ {4,5}`.  Standing package: `beta = alpha = 9`
possible only as `beta = 9`, `Delta <= 9`, `delta >= 4`,
`omega <= 5`, bad-10-set property, ambient-maximal semantics.
PROVED / COMPUTATIONALLY CHECKED separated; failed reductions recorded
with the exact missing constraint.  No overlap with the K4-free
(omega <= 3) proof, saturation LPs, heuristics, or the F4/F5 CEGAR
runs — the dichotomies below are handoffs TO those runs.**

## PROVED

**(G1) Adjacency ledger at a fixed maximal clique.**  Let `M` be a
maximal `s`-clique (`s = omega ∈ {4,5}`).  No outside vertex is
adjacent to all of `M` (maximality), so with `n_i` = number of outside
vertices adjacent to exactly `i` vertices of `M` (`0 <= i <= s-1`):
`sum n_i = 40 - s` and `sum i·n_i = sum_{p ∈ M} deg_out(p)
 <= s·(9 - (s-1))`  — i.e. budget 25 for `s = 5`, 24 for `s = 4`.

**(G2) Averaged anticomplete residual.**  For `c ∈ M` put
`P_c = M \ {c}` and `Z_c` = outside vertices whose `M`-neighbors lie
in `{c}`.  Then `sum_c |Z_c| = s·n_0 + n_1`, so
`max_c |Z_c| >= n_0 + n_1/s`.  Minimizing over ledger-feasible
profiles (LP, machine-checked): the adversary optimum is the all-`i=1`
profile, giving
- `s = 5`:  `max_c |Z_c| >= 15  >= R(3,5) = 14`  (slack 1);
- `s = 4`:  `max_c |Z_c| >= 18  =  R(3,6) = 18`  (tight).

**(G3) Clique-seeded maximum admissible sets exist.**  Choose `c`
realizing G2 and any `R(3, 11-s)`-subset of `Z_c`; its induced graph
`F` has `beta(F) >= H(R(3,11-s)) = 11 - s` by least-order minimality,
and for an `F`-admissible `S_F` of that size, `P_c ∪ S_F` is
admissible in `G` (cliques in `P_c` extend by `c`; no mixed cliques by
anticompleteness; `G`-maximal cliques inside `S_F` are `F`-maximal as
before).  Its size is `(s-1) + (11-s) = 10`— **contradiction?  No:**
size is `(s-1)+(11-s) = 10` only if the residual delivered `11-s`;
`H(R(3,11-s)) = 10-s+1 = 11-s`, so the set has `s-1+11-s = 10`
vertices… **Correction (audit this first):** `H(R(3,k)) = k`, so
`beta(F) >= 11-s` gives `|P_c ∪ S_F| = (s-1)+(11-s) = 10 > 9`, which
would contradict `beta = 9` outright.  The count must be re-examined
against the clique-residual lemma's bookkeeping, which required
`A >= R(3, h-s+1)` with contribution `h-s+1 = 11-s` and concluded
contradiction — there the requirement was `|Z| >= R(3, h-s+1) =
R(3,6) = 18` for `s = 5` and `R(3,7) = 23` for `s = 4`.  The G2
values 15 and 18 sit BELOW those thresholds, so the correct statement
is one step weaker: the residual delivers `H(15) = 5` (`s=5`) or
`H(18) = 6` (`s=4`), and `P_c ∪ S_F` has size `4+5 = 9` or
`3+6 = 9` — **a maximum admissible set containing a K4 (s=5) or a
triangle (s=4), not a contradiction.**  This corrected form is the
proved statement; the crossed-out miscount above is retained
deliberately as a worked example of the off-by-one hazard in this
bookkeeping (first drafted, then caught in self-audit).

**(G4) Rigidity dichotomy (sound static constraints for the CEGAR
lanes).**  Equality in G2 forces the adversary profile exactly:
- `s = 4`: every `M`-vertex has degree 9 with out-degree 6, the four
  out-neighborhoods are pairwise disjoint (24 distinct vertices, each
  adjacent to exactly one `M`-vertex), `n_2 = n_3 = 0`, `n_0 = 12`,
  and every `M`-edge lies in exactly its two internal triangles.
  **Dichotomy: either some `Z_c` has at least 19 vertices, or the
  rigid disjoint-fan profile holds at every maximal K4.**
- `s = 5`: equality needs `n_1 = 25, n_0 = 10`, all five out-degrees
  equal 5 (degree 9), disjoint out-fans; **either some `Z_c >= 16` or
  the rigid K5-fan profile holds.**
Both branches are checkable clause-level facts on a fixed labeled
clique and materially prune the exact F4/F5 searches.

## FAILED REDUCTION (recorded per protocol)

The direct clique-residual contradiction needs `|Z| >= R(3,7) = 23`
(`s=4`) or `R(3,6) = 18` (`s=5`); G2 provably delivers only 18 and
15.  **Exact gaps: 5 and 3.**  The missing global constraint is a
multi-adjacency forcing lemma: any lower bound `n_2 + n_3 > 0` of
weight ~gap in the ledger budget closes the case (each unit of `i>=2`
mass frees budget and pushes `max_c |Z_c|` up by the LP slope 3/4
resp. 4/5).  Nothing in the current package (degree window, cascade,
bad-10-sets — note maximal cliques SHIELD their supersets from the
bad-set property, an observation worth keeping) forces `n_2 > 0`.
Candidate sources: the arrowing core's triangle demands localized near
`M`, or saturation anchors of the G3-seeded sets (their `X`-vertices
in `Z_c \ S_F` must anchor inside `S_F`, recursing into `F`).

## COMPUTATIONALLY CHECKED

Adversary LP optima (exact fractions): 15 (`s=5`, budget 25, out 35)
and 18 (`s=4`, budget 24, out 36), both at the all-`i=1` vertex.

## Prior art

Today's searches (this lane and the priority sweep) found no prior use
of fixed-clique residual ledgers for #151; the technique is
classical-style (Erdős–Gallai-type counting + this campaign's
clique-residual lemma).  Independent audit requested before any use
beyond search pruning.
