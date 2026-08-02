# Independent audit of the order-41 `omega=5` double-spoke saturation argument

**Date:** 2 August 2026. **Verdict: PASS.**

The unconditional analytic part is sound: the shared vertex `w` causes no
exception to the singleton-fibre proof, every one of the five spokes has at
least 19 `U`-edges, the duplicated `U-w` incidence is corrected exactly
once, `r<=7`, and the global degree budget forces `e(U)<=10`.  Conditional on
completeness of the pinned Ramsey `(3,6;17)` catalogue, the repaired and
independently re-audited overlap enumeration forces the common core to have
20, 21, or 22 edges, so row D is impossible.

The PASS verdict confirms that the source states this conditionality
correctly.  It does not prove catalogue completeness, a full order-41
theorem, or Erdős problem #151, and it makes no Git, publication, novelty,
priority, or whole-graph UNSAT claim.  No source proof or checker was edited.

## Audited inputs and bindings

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_DOUBLE_SATURATION.md` | `277b65c4956b56298c76a5e08ed3daf31af040033b4fb001550db3831f7955ca` |
| `checks/double_saturation/check_double_saturation.py` | `be3cf20744516eaac13e0bb29dee47377ea4b66a33269c659dd0639a8a865951` |
| repaired `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| `ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json` | `02452b459e79c672b79089c550fd48b1f0eba7cf6257b90c0e891f01efc9d987` |
| repaired overlap checker | `d4eee390c83862f5b166b9bbd6c71415929d0bf428e7f62aeec2817ba3cc3d95` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.md` | `d5e7b337867bf449f946472e690ce3119f1f6f8c4e351d583567bb5f2d02896f` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json` | `c015740e97888f230bb0e769ea887eb27d8ac86154a115a297f3fb1c50dee4db` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.md` | `05152283f4377073664d2d8e33a922c6cd49ed7aa32ce69a2d07a25bdaee97a9` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.json` | `e5e35724f2d031e78b130f20fc022cc530675aac716cbcca4696b70bcdee7d3c` |
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |

The re-audit JSON correctly binds its Markdown, the repaired note, result,
checker, remediation pair, original immutable FAIL audit, and pinned
dependencies.  All relevant current hashes match that binding.  The pinned
file contains seven records; its claimed completeness remains an external
premise rather than a fact certified by these hashes.

## Reconstruction of row D

The outside vertices are `U`, the double-neighbour vertex `w`, and five
unique-neighbour fans.  Here `|U|=12`, `N_M(w)={p,q}`,
`|A_p|=|A_q|=4`, and the other three fans have order five.  Define

```text
B_p=A_p union {w},   B_q=A_q union {w},
B_c=A_c for the other three clique vertices.
```

Every `B_c` has order five and

```text
N(c)=(M-{c}) union B_c.
```

All five clique vertices have degree nine, so these neighbourhoods are
maximum ambient-admissible 9-sets.  Their saturation makes every `B_c`
dominate `U`.  Vertices of `U` are anticomplete to all of `M`, and
`Delta(G)<=beta(G)=9`.

## Claim-by-claim audit

### 1. Singleton fibres, including the shared `w` — PASS

For `a in B_c`, put

```text
P_c(a)={u in U:N(u) intersect B_c={a}}.
```

For `u in P_c(a)`, the only neighbour of `u` in `S_c=N(c)` is `a`.
The inadmissible ten-set `S_c union {u}` must therefore be witnessed by the
ambient-maximal edge `ua`.  Two vertices in the same fibre cannot be
adjacent, because either one would extend `ua` to a triangle with `a`; if
they are nonadjacent, replacing `a` in `S_c` by the two vertices makes them
isolated and leaves every other clique extendable by `c`.  This would be an
admissible ten-set.  Hence `|P_c(a)|<=1`.

For `c=p,a=w`, the edge `qw` does not spoil the argument.  A vertex of `U`
is nonadjacent to `q` and every other member of `M`; after removing `w` from
`N(p)`, the inserted fibre vertices are anticomplete to the whole remaining
set.  The argument at `q` is identical.  A single `u` may lie in both
`P_p(w)` and `P_q(w)`; the proof only asserts the separate pointwise caps,
and the subsequent sum corrects the duplicated edge explicitly.

### 2. Five cut bounds — PASS

For a fixed five-vertex spoke, domination gives twelve nonempty neighbour
sets.  If `s_c` are singletons, the five fibre caps give `s_c<=5`; hence

```text
e_c=e(U,B_c)>=s_c+2(12-s_c)=24-s_c>=19.
```

An independent set-system dynamic program exhausted the 31 possible
nonempty neighbour sets per `U` vertex and confirmed the one-spoke minimum
19.  A second dynamic program treated `B_p` and `B_q` simultaneously,
requiring the `w` bit to agree in both spokes and tracking the two sets of
singleton labels.  Under `r<=7`, the exact minimum actual pair cost was

```text
e_p+e_q-r=31,
```

attained with `e_p=e_q=19` and `r=7`.  Thus the separate cut bounds and the
shared correction are jointly feasible and sharp; no hidden disjoint-spoke
assumption strengthens the claimed inequality accidentally.

### 3. `r<=7` and exact double-counting — PASS

Let `r=|N(w) intersect U|` and `f_c=e(U,A_c)`.  Since `w` already meets
`p,q` and has degree at most nine, `r<=7` even if it has no other
neighbours.  The two shared spoke cuts satisfy

```text
e_p=f_p+r,       e_q=f_q+r,
sum_c e_c=sum_c f_c+2r.
```

The true sum of the degrees of `U` counts a `U-w` edge once, not twice, so

```text
sum_{u in U}d_G(u)
 =2e(U)+sum_c f_c+r
 =2e(U)+sum_c e_c-r.
```

This is an identity, independent of any inequality or catalogue input.  It
counts every `U-U` edge twice, every `U-A_c` edge once, every `U-w` edge
once, and no `U-M` edge.

### 4. The global degree consequence — PASS

The twelve degree-nine ceilings give

```text
108 >= 2e(U)+sum_c e_c-r
    >= 2e(U)+5*19-7
     = 2e(U)+88.
```

Therefore `e(U)<=10`.  A separate scalar exhaustion over all five cut sizes
at least 19 and all `0<=r<=7` confirmed that 10 is the largest feasible
integer value.  The residual fact `beta=5` also gives `alpha(U)<=5`; Turán's
theorem correctly yields the optional lower bound

```text
e(U)>=C(12,2)-ex(12,K6)=66-57=9,
```

because `T_5(12)` has part sizes `3,3,2,2,2` and 57 edges.  Thus the
unconditional analytic package narrows the core to nine or ten edges.

### 5. Re-audited D17 edge range — PASS, catalogue-conditional

The repaired overlap computation uses the three full order-17 residuals.
Conditional on completeness of the pinned `(3,6;17)` catalogue, every real
row-D core occurs among the 17 necessary-condition survivors.  The
post-remediation re-audit independently reconstructed the automorphism
closures and exact common-core enumeration and passed the repaired totals
`4368`, `786`, `1963`, and 17.

This audit also decoded the 17 graph6 representatives from the bound result
JSON with a separate short-form parser.  They are distinct 12-vertex graphs,
with edge histogram

```text
20 edges: 3 cores
21 edges: 9 cores
22 edges: 5 cores.
```

Thus every conditional survivor has `e(U) in {20,21,22}`, exactly as used.
A fresh replay of the repaired overlap checker exited zero and again
reported 17 D cores and the same individual edge counts.

### 6. No circularity — PASS

The repaired overlap check constructs each D survivor from a common
12-vertex induced graph of three catalogue residuals and their aligned
cross-degree vectors.  Its D filter then uses only pre-existing necessary
degree conditions: at least one remaining degree unit per `U` vertex,
forced adjacency to `w` when exactly one unit remains, and at most seven
forced `w` neighbours.  The code does not use the singleton-fibre cap, the
19-edge spoke bound, or `e(U)<=10`; indeed it emits cores with 20–22 edges,
which such a filter would have removed.

The overlap filter and the new inequality both use the already-known fact
`r<=7`.  Reusing one necessary fact in two downstream deductions is not
circular.  The logical chain is

```text
catalogue completeness + repaired overlap enumeration
    => every real D core lies among the 17 survivors
    => e(U)>=20,

row-D saturation + degree budget
    => e(U)<=10.
```

The two branches meet only at the final contradiction.

## Shipped checker replay and coverage

The double-saturation checker replayed in a fresh `-B` process and printed

```text
status: CHECKED
shared_w_identity_cases: 16384
minimum_U_degree_sums: e20->128, e21->130, e22->132
available_U_degree_budget: 108
feasible_states: 0
```

The arithmetic is correct.  It exhausts dummy values for the accounting
identity and all `e(U) in {20,21,22}`, `0<=r<=7` for the final inequality.

It intentionally does not check the row-D profile, domination, the
ambient-maximality proof, singleton fibres, the 19-edge cut derivation,
consistency of the shared `w` adjacency across both spokes, Turán's theorem,
the 17 graph6 records, their hashes, the repaired enumeration, or catalogue
completeness.  It hard-codes the D17 edge range and has no source-hash
binding or checked-output JSON.  These limitations are accurately described
by the source as an isolated arithmetic guard and are not blockers; the
missing finite and dependency checks were performed independently above.

## Conditionality, verdict, and blockers

Unconditionally under the standing row-D hypotheses, the audit confirms the
singleton-fibre bounds, all five cut bounds, the exact shared-edge identity,
`r<=7`, and `e(U)<=10` (with the optional `9<=e(U)`).  The exclusion of row D
is conditional on the external completeness of the pinned seven-record
Ramsey `(3,6;17)` catalogue.  The repository verifies the pinned bytes and
the repaired enumeration, but not that external completeness theorem.

**PASS.**  The source preserves this boundary and contains no circular use
of the D17 range.  The exact blocker list is empty; catalogue completeness
is an explicit premise of the conditional conclusion, not an unaudited
unconditional claim.
