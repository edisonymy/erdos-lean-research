# T‴: projection-only second-moment calculation (corner infeasible)

**2 August 2026, Fable lane, corrected after independent audit.**  The
nominal F3 assumptions (least counterexample at n = 28, 7-regular,
`omega = 3`, `L = ∅`) are themselves inconsistent: `L=∅` gives
`l_v=0`, so the audited inequalities `u_v>=2t_v-2` and `u_v<=6l_v`
force `t_v<=1`, while every vertex of the 7-vertex link is nonisolated
and hence `t_v>=4`.  Independently, the through-39 proof forces a
maximal `K4`, contradicting `omega=3`.

The calculation below remains a correct **counterfactual projection** after
discarding those stronger constraints.  It is useful for checking the
second-moment machinery, but it is not a live structural theorem, does not
reopen order 28, and does not resolve #151.  Checker:
`experiments/erdos151_siege/bonferroni_check.py` (exact integer
arithmetic + exact MaxSAT for the local maxima).

## Setting

In the corner all maximal cliques are triangles, so the bad-8-set
property says every 8-set contains a triangle.  Let `N = N_3` be the
triangle count, `m_e` / `t_v` triangles through an edge / vertex, and
for an 8-set `T`, `m_T` = triangles inside `T`.  7-regularity gives 98
edges; `L = ∅` gives `m_e >= 1`; the audited two-walk bound gives
`t_v <= 7`.

## PROVED (audit of the proposed chain — every step verified)

1. **First moment.**  `I = sum_T m_T = N·C(25,5)`, and
   `D := I - C(28,8) = sum_T (m_T - 1) >= 0` since `m_T >= 1`.
2. **Second-moment minorant.**  On 8 vertices a `K4`-free graph has at
   most 18 triangles (Zykov; extremal `K(3,3,2)`; re-verified by exact
   MaxSAT), and for `1 <= m <= 18`:  `m - 1 >= C(m,2)/9`
   (equivalent to `m <= 18`).  Hence `D >= (1/9) sum_T C(m_T,2)`.
3. **Exact pair classification.**  With `A := sum_e C(m_e,2)` and
   `V := sum_v C(t_v,2)` (so an edge-sharing triangle pair is counted
   at both shared vertices), classifying triangle pairs by union size
   4/5/6 with 8-set counts `C(24,4), C(23,3), C(22,2)`:
   `sum_T C(m_T,2) = 7315·A + 1540·V + 231·C(N,2)`.
   (Identity check: `10626 - 231 = 7315 + 2·(1771 - 231)`.)
4. **Convex minima.**  `sum_e m_e = 3N` over 98 edges each `>= 1`
   gives `A >= 3N - 98` (valid while `3N <= 196`); `sum_v t_v = 3N`
   over 28 vertices gives `V >= 18N - 588` (even spread over
   `{6, 7}`, valid for `N >= 56`; consistent with `t_v <= 7`).
5. **Base squeeze.**  Combining 1–4:
   `53130·N - 3108105 >= (1/9)(7315(3N-98) + 1540(18N-588) + 231·C(N,2))`,
   a quadratic whose relevant root is `≈ 62.51`.  **So `N <= 62` is
   impossible: `63 <= N_3 <= 65` in the corner.**  This reproduces the
   proposed calculation exactly; all coefficients and inequality
   directions verified.

## PROVED SHARPENING (new): the capped local maximum is 15

`K(3,3,2)` has its 2-part vertices in **9** internal triangles, so it
violates the corner's `t_v <= 7` cap.  Exact MaxSAT over all
`K4`-free 8-vertex graphs with every vertex in at most 7 triangles
gives maximum **`M = 15`** (uncapped control run returns 18, matching
Zykov).  Since every induced `G[T]` inherits both constraints,
`m_T <= 15`, and for `1 <= m <= 15`:  `m - 1 >= (2/15)·C(m,2)`.
Rerunning step 5 with factor `2/15` (exact rational comparison):

**`N = 63` is impossible.  The corner window is `64 <= N_3 <= 65`.**

## Projection-only remainder 64 and 65

- The per-`T` route alone cannot kill 64: it would need `M <= 13`
  while `M = 15` exactly.
- In the weakened projection, a possible stability lever would be that
  near-tightness forces the
  `m_T`-distribution toward the bimodal `{1, 15}` shape (equality
  points of step 2'), while the mean is only `~ 1.09–1.11`; and the
  convexity equalities force `m_e ≈ 2` everywhere with
  `t_v ∈ {6,7}` — note `3N = 2·98` has no integer solution, so
  `m_e = 2` everywhere is impossible, and the coupled per-vertex
  identity `sum_{e ∋ v} m_e = 2 t_v` links the `A` and `V` minima
  beyond independent convexity.  No effort should be spent attacking
  `{64,65}` as graph cases, because the full F3 assumptions are already
  contradictory.

## COMPUTATIONALLY CHECKED

`bonferroni_check.py`: coefficient identity; base window `{63,64,65}`;
uncapped maximum 18; capped maximum 15; refined window `{64, 65}`.
All comparisons in exact integer arithmetic.

## Status

Verified arithmetic lemma about a weakened projection only.  The nominal
corner is infeasible under the full audited package, so this is not a
conditional structural theorem about a realizable graph class.  Order 28's
upstream disposition is unaffected and there is no claim about #151.  The
independent audit and a separate exact checker are recorded in
`experiments/erdos151_siege/fractional_lp/`.
