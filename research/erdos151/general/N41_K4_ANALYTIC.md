# Order 41, maximal-K4 case: four-residual analysis (Erdős #151)

**2 August 2026, Fable lane.  Inputs: ONLY the audited facts of
`N40_CLIQUE_CASES_AUDIT.md` for n = 41:  `beta(G) = 9`,
degrees in `[5,9]`, `alpha <= 9`, and for a fixed maximal `K4` `M`
with residuals `Z_c` (`c ∈ M`): `beta(G[Z_c]) <= 6`, `|Z_c| <= 22`,
`sum_c |Z_c| = 76 + 3t + 2n_2 + 5n_3 <= 88`.  (Derivation re-verified:
`sum_c |Z_c| = 4 n_0 + n_1`, ledger `n_0+n_1+n_2+n_3 = 37`,
`n_1 + 2n_2 + 3n_3 = 24 - t`.)  Whole-graph SAT excluded by directive;
Codex owns CEGAR/catalog lanes.  Notation: `Z_0` = common anticomplete
core (`Z_c ∩ Z_{c'} = Z_0` for all pairs, since an `M`-neighbor set
contained in `{c}` and `{c'}` is empty), fans `F_c` (`|F_c| = f_c`,
`sum f_c = n_1`), `W_c := G[Z_c]`, `W_0 := G[Z_0]`.**

## PROVED

**(H1) Conservation law.**  With deficiencies `d_c := 22 - |Z_c| >= 0`:
`sum_c d_c + 3t + 2n_2 + 5n_3 = 12`.
Corollaries: `t <= 4`, `n_2 <= 6`, `n_3 <= 2`, `n_0 >= 13`, and at
most two residuals have `|Z_c| <= 17` (`d_c >= 5` twice exhausts 10 of
12; three times is impossible).  Hence **at least two `W_c` satisfy
`|Z_c| ∈ [18, 22]` and are H-extremal: `beta(W_c) = 6 = H(|Z_c|)`
exactly** (lower bound from least-order minimality, upper from the
audited fact).

**(H2) Seeded maximum sets, one per large residual.**  For each `c`
with `|Z_c| >= 18`: any `W_c`-admissible 6-set `S_F(c)` gives the
maximum admissible set `S_c = P_c ∪ S_F(c)` of `G` (anticompleteness
kills mixed cliques; `P_c` extends by `c`; `W_c`-admissible implies
`G`-admissible for subsets of `Z_c` by the audited monotonicity
argument).  By H1 there are at least two such `c`, with `S_c`
containing two different triangles of `M`.

**(H3) Recursive domination of the core.**  Fix such a `c` and apply
E1-saturation to `S_c`: any `z ∈ Z_0 \ S_F(c)` is anticomplete to
`P_c`, so its anchors satisfy `∅ ≠ A ⊆ N(z) ∩ S_F(c)` with
`A ∪ {z}` **ambient**-maximal and contained in `Z_c`.  Hence every
`W_c`-maximum admissible 6-set `S_F(c)` dominates `Z_0 \ S_F(c)`
through `G`-maximal cliques lying inside `Z_c` — simultaneously for
every large residual and every choice of `S_F(c)` (the exchange web of
`W_c` included).  Also `alpha(W_c) <= beta(W_c) <= 6` and
`omega(W_c) <= 4`.

## NUMERICALLY FEASIBLE LEDGER PROFILE (not a certified H3 realization)

Toy profile: `t = n_2 = n_3 = 0`, `f_c = 6` for all four `c`,
`n_0 = 13`: then `sum_c |Z_c| = 4·13 + 24 = 76`, each `|Z_c| = 19`,
`d_c = 3`, conservation `12 = 12` ✓, and all H1 numerical
corollaries are met.  This proves that the ledger alone has no numerical
contradiction.  It is **not** an explicit graph or set-system realization
of all H3 ambient-anchor conditions; constructing such a realization, or
proving that none exists, is part of the missing global problem below.
Per the stopping rule, no further pure ledger-counting lemma is proposed at
this level.

## THE MISSING GLOBAL CONSTRAINT (named precisely)

Two ambient ingredients are absent from the abstraction:

1. **Cross-residual ambient maximality.**  H3's anchor cliques are
   maximal in `G`, not merely in `W_c`: their non-extendability is
   witnessed against fan vertices of *other* `c'` and against `M` —
   the abstraction treats the four `W_c` as coupled only through
   `|Z_0|`, which is exactly why it is satisfiable.
2. **Arrowing-core triangle localization.**  `G` arrows `(3,3)`
   (Theorem A) with an edge-minimal core `Q`: every `Q`-edge in `>= 2`
   `Q`-triangles, `t_Q(v) >= d_Q(v)+1`, `chi(Q) >= 6`, `omega(Q) <= 4`.
   `M` supplies only its four internal triangles (few, and only `2` per
   `M`-edge when `n_2 = 0`), so the core's triangle mass must live in
   the fans/residuals — precisely where H-extremal `W_c` structure is
   Ramsey-graph-like (triangle-poor at `alpha <= 6` on `18..22`
   vertices).

**Isolated exact finite lemma (handoff, decidable at order <= 22,
NOT run here per directive):**

> **L\*.**  Determine `T*(m)` = the maximum, over graphs `W` on
> `m ∈ [18,22]` vertices with `omega(W) <= 4`, `alpha(W) <= 6`,
> `beta(W) = 6`, of the triangle count of `W` (and the variant with
> every maximum admissible 6-set dominating a fixed `>= 13`-subset).
> If `T*` is small enough that four such residuals plus `M` plus fan
> edges cannot host any `K5`-free graph with `chi >= 6` whose every
> edge lies in two of its triangles, the order-41 `K4` case is closed.

A countermodel hunt for the *naive* version of L\* (dropping the
domination condition) should start from the cyclic Ramsey `(3,7)`
graphs on 22 vertices plus one edge — expected to keep `beta = 6`
while creating triangles; the domination-constrained version is the
one that matters.  Recorded per protocol as the surviving open lemma;
everything above it is proved from the audited inputs alone.
