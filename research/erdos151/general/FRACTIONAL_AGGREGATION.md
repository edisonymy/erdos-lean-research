# Fractional aggregation over all maximum admissible sets (Erdős #151)

**2 August 2026, Fable lane.  PROVED / COMPUTATIONALLY CHECKED /
CONJECTURAL strictly separated; no publication before an independent
audit of the full quantifier chain.**  Setting: `G` a least
counterexample at the jump `n = R(3,h)`, `r = h - 1`,
`𝒮` = all maximum admissible `r`-sets (E0 of
[`SATURATION_EXCHANGE.md`](SATURATION_EXCHANGE.md)).  Post-audit
corrections respected throughout: no anchor uniqueness/disjointness,
no `c`-concentration claim (the `h = 10` average bound is `81/31` or
`81/32`, not below 2.4), E6 only in its clean singleton form.

## PROVED

**(F1) The L-graph bridge.**  Let `L` be the set of edges of `G` in no
triangle (maximal 2-cliques).  Then `(V, L)` is triangle-free (a
triangle among `L`-edges would put each of its edges in a triangle),
so `alpha((V,L)) >= H(n) = h` and `L`-independent `h`-sets exist.
Every `S ∈ 𝒮` is `L`-independent, and **every `L`-independent `h`-set
contains an ambient-maximal clique of size ≥ 3** (it contains a
maximal clique since `beta = r < h`; a size-2 one would be an `L`-edge
inside it).  This couples global `L`-sparsity to triangle-richness on
*all* `h`-sets at once — the first constraint here that goes beyond
sets of the form `S ∪ {v}`.

**(F2) Layered coverage inequalities.**  Let `N_k` be the number of
ambient-maximal `k`-cliques.  Counting `h`-sets against the maximal
cliques they must contain:
`sum_k N_k · C(n-k, h-k) >= C(n, h)`,
and, restricting to `L`-independent `h`-sets via F1 and a union bound,
`N_3 · C(n-3, h-3) + N_4 · C(n-4, h-4) >= C(n,h) - N_2 · C(n-2, h-2)`
(with higher `N_k` added if `omega` permits).  Valid unconditionally
for any graph with `beta <= r` at order `n`.  **Audit clarification:**
after moving the `N_2` term to the left, the displayed `L`-independent
union-bound form is algebraically identical to the ordinary first-order
coverage inequality when every allowed clique size is included.  It is a
useful reinterpretation, not a stronger inequality.  A genuine improvement
needs a sharper count of `L`-independent `h`-sets, overlap information, or
additional exchange constraints.

**(F3) A projected h = 8 coverage comparison (exact constants, but an
infeasible corner).**  At
`n = 28, h = 8` the normalized coefficients are `1/13.5, 1/58.5,
1/292.5` for `N_2, N_3, N_4`.  In the corner where `G` is 7-regular
with `omega = 3` (all maximal cliques are edges or triangles) and
`L = ∅`:  F2 forces `N_3 >= 59`, while the audited 7-regular two-walk
bound `t_v <= 7` forces `N_3 = (1/3)·sum t_v <= 65`.  The numerical
projection is therefore `59<=N_3<=65`.

**Audit correction:** this is not a realizable corner under the full
two-walk package.  If `L=∅`, every link has `l_v=0`; the already-audited
inequalities `u_v>=2t_v-2` and `u_v<=6l_v` give `t_v<=1`.  But `L=∅`
also makes every vertex of the 7-vertex link nonisolated, giving
`t_v>=ceil(7/2)=4`.  Thus the corner is immediately contradictory.
The `59..65` comparison remains a correct check of the weaker projected
coverage inequalities after the `(u_v,l_v)` constraints are discarded,
but it is not a genuine residual case.  A nonempty `L` relaxes the isolated
coverage right-hand side while simultaneously strengthening the local
two-walk restrictions, so no monotonic statement about the **net** slack is
justified.  In a mixed degree profile the raw `t_v<=11` two-walk cap
applies only at degree-7 vertices; degree-5/6 vertices instead need their
separate link bounds (for example the `omega<=4` Turán caps 8 and 12).

**(F4) Potential-minimizing base and one-swap inequalities.**  Choose
`S ∈ 𝒮` minimizing the potential `Φ(S) := e(G[S])` (not the anchor
count).  If `v ∈ X` has `c(v) = 1` with attachment `a`, the E4-swap
`S' = (S \ {a}) ∪ {v}` is again in `𝒮`, and since `N(v) ∩ S = {a}`,
`e(G[S']) = e(G[S]) - deg_S(a)`.  Minimality forces
`deg_S(a) = 0`: **at an edge-minimizing maximum admissible set, every
`c = 1` attachment point is isolated inside `S`.**  Consequently such
`a` has all its neighbors in `X`, `X_{\{a\}}` is independent (E2), and
`va ∈ L` (E3).  The clean two-swap (E6) adds
`deg_S(a) + deg_S(b) <= [ab ∈ E]`, which is implied; multi-swap
potentials sharper than `e(S)` are open (see T″).

## COMPUTATIONALLY CHECKED

- Exact constants for the projected F3 calculation (`python`, 2 Aug):
  `C(26,6)/C(28,8) = 1/13.5`,
  `C(25,5)/C(28,8) = 1/58.5`, `C(24,4)/C(28,8) = 1/292.5`; corner
  bound `N_3 >= 58.5`, regular cap `N_3 <= 65.33`.
- `h = 10` average-`c` values `81/31 ≈ 2.61`, `81/32 ≈ 2.53`
  (consistent with the audited E5 correction).

## PROVED LIMITATION (why this is not yet uniform)

In the triangle-only projection `N_2=N_k=0` for `k>=4`, asymptotically
`n = R(3,h) = Θ(h²/log h)` and the F2 requirement scales as
`N_3 ≳ (n/h)³ = Θ((h/log h)³)` while the two-walk supply cap scales
as `n · t_max / 3` with `t_max = Θ(h²)`, i.e. supply
`Θ(h⁴/log h) ≫ demand`.  Thus this raw triangle-coverage versus generic
two-walk-cap comparison cannot give a uniform contradiction.  It does not
rule out every first-order LP enriched by exchange or other structural
constraints, and general F2 does not force triangles when other maximal
clique layers are available.  Uniformity, if achievable on this route, must
use additional aggregation over `𝒮` or comparably strong structure.

## CONJECTURAL

**(T″) The (S, v, A)-incidence program.**  Over the tensor of
incidences `{(S, v, A) : S ∈ 𝒮, v ∉ S, A ∈ A_S(v)}`, the proved
constraints — E1 (each `(S,v)` fiber nonempty), E2 (each `(S,A)` fiber
independent, hence `<= r` and pairwise-nonadjacent inside), E4/F4
(exchange-closure of `𝒮` with the potential inequalities), E5 (edge
budgets per `S`), F1–F2 (global coverage), plus `alpha, Delta <= r`
and the cascade — should admit an LP-dual certificate of
infeasibility, uniformly in `h` or at least at `h = 8` beyond the F3
corner.  Design note for the next session: formulate with variables =
densities of (attachment-type, degree-class) pairs and dual weights on
(E2-independence, coverage, two-walk) constraints; test first as a
small numeric LP at `h = 8` (this is an LP over count-variables, NOT
another graph SAT probe — no overlap with the running anchor-shadow /
CEGAR / catalogue / audit lanes).
**(T‴) Withdrawn after audit.**  The proposed Bonferroni attack on the
7-regular `omega=3, L=∅` corner is unnecessary because that corner is
already impossible from `u_v>=2t_v-2`, `u_v<=6l_v`, and link minimum
degree.  A second-order calculation was independently checked and, in a
weaker projection omitting those constraints, improves `59..65` to
`64..65`; it is an arithmetic lemma about the projection, not progress on
a live graph case.  Any replacement aggregation target must retain and
exploit the forced nonempty `L`-graph.

## INDEPENDENT AUDIT

The reconstruction and executable arithmetic/LP audit are in
[`../../../experiments/erdos151_siege/fractional_lp/README.md`](../../../experiments/erdos151_siege/fractional_lp/README.md)
and `audit_fractional_lp.py`.  The checker independently confirms the sharp
8-vertex cap 15, every coverage coefficient, the projection-only `64..65`
remainder, and the immediate full-package contradiction at `L=∅`.  It also
shows that the proposed `(attachment size, degree class)` marginal LP is
feasible over both real and integral count variables.  Such marginals do not
encode anchor-fibre adjacency, ambient maximality, domination, or rebased
types after exchange, so T″ needs substantially richer correlation variables
before a dual-infeasibility search would be meaningful.
