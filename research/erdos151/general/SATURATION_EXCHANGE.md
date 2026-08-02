# Saturation–exchange theory at a Ramsey jump (Erdős #151)

**2 August 2026, Fable lane.  PROVED / COMPUTATIONALLY CHECKED /
CONJECTURAL kept strictly separate.  Nothing here is a claimed
resolution; no publication before an independent audit of the full
quantifier chain.**  Standing hypotheses for the PROVED section:
`G` is a least-order counterexample; by the audited monotonicity lemma
and least-order minimality it sits at a Ramsey jump `n = R(3,h)`;
write `r := h - 1`.  All preceding orders are cleared (through-39
package, provisionally verified upstream, is used only through the
statement "the conjecture holds below `n`").

## PROVED

**(E0) Exact beta and exact maximum sets.**  `beta(G) = r`, and every
maximum admissible set has exactly `r` vertices.
*Proof.*  For any vertex `v`, `G - v` has `n - 1 in
[R(3,r), R(3,h) - 1]` vertices, so `H(n-1) = r`; minimality gives
`beta(G - v) >= r`, and induced-subgraph monotonicity gives
`beta(G) >= beta(G - v) >= r`.  A counterexample has `beta <= r`.  ∎

Fix a maximum admissible set `S`, `|S| = r`, and let `X := V \ S`,
`|X| = R(3,h) - r`  (21, 28, and `R(3,10) - 9 ∈ {31, 32}` at
`h = 8, 9, 10`).  For `v ∈ X` write `c(v) := |N(v) ∩ S|`.

**(E1) Anchor existence (no uniqueness or disjointness claimed).**
For every `v ∈ X` the anchor system
`A(v) := { A ⊆ N(v) ∩ S : A ≠ ∅, A ∪ {v} is an ambient-maximal
clique }` is nonempty.  In particular `c(v) >= 1`: `S` is dominating.
*Proof.*  `S ∪ {v}` has `h` vertices; since `beta = r < h`, it
contains an ambient-maximal clique `K` with `|K| >= 2`; `K ⊄ S`
(admissibility), so `v ∈ K` and `A := K \ {v}` qualifies.  ∎
A single clique `A` may anchor many outside vertices, and one `v` may
have many anchors; none of this is excluded.

**(E2) Anchored-set independence.**  For a fixed clique `A ⊆ S`, the
set `X_A := { v ∈ X : A ∈ A(v) }` is independent in `G`.
*Proof.*  If `v ≠ v' ∈ X_A` were adjacent, `v'` would be adjacent to
every vertex of `A ∪ {v}` (to `A` since `A ∈ A(v')`, to `v` by
assumption), contradicting maximality of `A ∪ {v}`.  ∎
Hence `|X_A| <= alpha(G) <= r` for every `A`, and the family
`{X_A : A a clique in S}` **covers** `X` (by E1).

**(E3) Singleton anchors are triangle-free edges.**  If
`{a} ∈ A(v)` then the edge `va` lies in no triangle of `G`.
In particular if `c(v) = 1` with `N(v) ∩ S = {a}`, then `va` is a
maximal 2-clique.
*Proof.*  `{v,a}` maximal means no common neighbor.  ∎

**(E4) One-vertex exchange criterion.**  For `v ∈ X` and `a ∈ S`, the
set `S' := (S \ {a}) ∪ {v}` is again a maximum admissible set
**iff** `a ∈ A` for every `A ∈ A(v)`.
*Proof.*  `S'` fails admissibility iff some ambient-maximal clique
`K ⊆ S'` exists.  If `v ∉ K` then `K ⊆ S`, impossible.  If `v ∈ K`
then `K \ {v}` is nonempty because the witnessing clique is nontrivial,
and `K \ {v} ⊆ (S \ {a}) ∩ N(v)`, i.e. `K \ {v} ∈ A(v)` avoiding `a`.
So inadmissibility ⇔ some anchor avoids `a`.  `|S'| = r` keeps it
maximum.  ∎
Corollary: every `c(v) = 1` vertex is swappable (its unique possible
anchor is `{a}`).  Exchanges generate a web of maximum admissible
sets; all results above apply to every one of them simultaneously.

**(E5) Edge budget between X and S.**
`sum_{v ∈ X} c(v) = e(X, S) = sum_{a ∈ S} deg(a) - 2 e(S)
 <= r^2 - 2 e(S)`.
With (E1), `e(S) <= (r^2 - |X|) / 2`, and the average of `c(v)` is at
most `(r^2 - 2e(S)) / |X|`.  With `e(S) = 0` this upper bound is
`49/21 = 7/3` at `h = 8`, `64/28 = 16/7` at `h = 9`, and either
`81/31` or `81/32` at `h = 10`.  Thus the originally reported
"below 2.4 at every `h <= 10`" assertion was false at `h = 10`, and
the edge budget alone does **not** prove that most outside vertices
have `c(v) ∈ {1,2}` there.  Low-`c` vertices remain important because
the average is small, but any concentration statement needs another
argument.

**(E6) Clean singleton two-swap.**  If nonadjacent `v,v' ∈ X` have
`N(v) ∩ S = {a}` and `N(v') ∩ S = {b}` for distinct `a,b ∈ S`, then
`S'' := (S \ {a,b}) ∪ {v,v'}` is a maximum admissible set.  This is
the only two-swap statement established here; the earlier broad
"if and only if" formulation involving moving anchor systems was not
proved and is withdrawn.  *Proof:* any maximal
`K ⊆ S''` with `K ∩ {v,v'} ≠ ∅`, say `v ∈ K`: `K \ {v} ⊆
((S \ {a,b}) ∪ {v'}) ∩ N(v) ⊆ {v'} ∪ (N(v) ∩ S \ {a})`; since
`N(v) ∩ S = {a}` and `vv' ∉ E`, `K \ {v} = ∅`, impossible.  ∎

## CONSEQUENCES ASSEMBLED SO FAR (still PROVED, stated for use)

For every maximum admissible `S` simultaneously:
- `X` is covered by independent sets `X_A`, each of size `<= r`,
  indexed by cliques `A` inside `S` with `|A| <= omega - 1`;
- every `v` with `c(v) = 1` contributes a triangle-free edge into `S`
  and is exchangeable (E4), producing further maximum sets whose own
  (E1)–(E5) constraints must also hold;
- the load identity: `sum over nonempty cliques A ⊆ S of [A anchors]`
  counts each `v` at least once, while each `X_A` is independent and
  `alpha(G[X]) <= r`.

## CONJECTURAL (the counting target)

**(T) Saturation-counting contradiction.**  For every `h` (or all
large `h` plus finitely many base cases), no graph can satisfy E0–E6
together with `Delta <= r`, `alpha <= r`, the degree floor
`delta >= R(3,h) - R(3,r)`, the clique-residual `omega` bound, and the
`k`-set domination cascade.  Status: **open**; not yet provable by the
counts above alone (the adversarial track below exists precisely to
locate the missing realizability conditions or refute intermediate
lemma candidates).

## COMPUTATIONALLY CHECKED (adversarial track results, 2 Aug)

Probe at `h = 8` (`n = 28`, `r = 7`), `anchor_model.py`:

- **Stage 1** (A1 + A3 + A4 + lazy `omega <= 4`): SAT in 0.1 s — a
  degenerate 21-edge configuration (three `S`-vertices of degree 7,
  each anchoring seven `c = 1` outside vertices; all X-degrees 1).
  The anchor axioms alone are nearly vacuous.
- **Stage 2** (+ lazy `alpha <= 7`): **SAT** in 162 s after 4,690
  independent-8-set blocks and 6 `K5` blocks — an explicit 92-edge
  configuration (`runs/anchor_stage2.json`) with
  `c`-distribution `{1: 9, 2: 5, 3: 7}`, `S`-degrees 6–7, X-degrees
  5–7.  **This is an explicit falsifier of contradiction from the
  encoded local axioms A1+A2+A3+A4+W.**  It does not satisfy E0 or
  `beta<=7`: for example `{0,1,2,3,4,5,8,11}` is an admissible 8-set.

- **Stage 3** (+ degree floor `delta >= 5`): SAT in 87 s
  (`runs/anchor_stage3.json`, 94 edges, `c`-distribution
  `{1: 9, 2: 6, 3: 4, 4: 2}`) — as predicted, the floor is not the
  binding ingredient.  **The three coded single-`S` stages remain jointly
  satisfiable at `h = 8`.**  They are not a complete encoding of E0–E6.

**Missing-realizability diagnosis.**  The stage-2 witness satisfies local
admissibility and anchor conditions at one designated `S`; it does not make
`S` maximum.  A genuine counterexample must first satisfy `beta<=r`,
equivalently the bad-`h`-set property for **every** `h`-set.  With E0 this
also forces the E1–E5 structure on every maximum admissible set generated by
the exchange web.  The single-`S` model omits at least the global
bad-`h`-set quantifier, maximum-set status, and reimposition of the anchor
conditions after exchanges.  Stage 3 subsequently returned SAT as recorded
above, confirming only that the degree floor does not close this coded
abstract ladder.

**Revised CONJECTURAL target (T').  Exchange-closure counting.**
Impose E1–E5 not on one `S` but on the closure of `S` under E4
one-vertex exchanges (already forced by PROVED results); show this
web's combined incidence constraints are unsatisfiable under
`alpha, Delta <= r`, `omega` bounds, and the cascade.  Next probe:
encode the one-step closure (all swaps at `c = 1` vertices) and
re-run the ladder.  If even full closure is abstractly satisfiable,
the residual gap is the global quantifier itself, and the uniform
route should pivot to extremal counting over ALL maximum admissible
sets (fractional relaxation of the bad-`h`-set hypergraph).

## ADVERSARIAL TRACK (design; results recorded as they land)

`experiments/erdos151_siege/anchor_model.py` encodes, for a chosen
`h`, a graph on `n = R(3,h)` labeled vertices `S ∪ X` with a chosen
**subset** of axioms:
(A1) `Delta <= r`; (A1') degree floor; (A2) `alpha <= r` (lazy
blocking); (A3) `S` admissible in the full sense (every clique inside
`S` up to size `omega - 1` has an ambient extender; cliques of size
`omega` inside `S` are forbidden outright since they cannot extend);
(A4) every `v ∈ X` has an anchor (aux-encoded maximality).
Protocol: the implemented stages run A1+A3+A4+W, then add A2, then A1'.
A SAT witness is a **counterexample to contradiction from that explicitly
encoded local package**.  No present stage encodes the full problem or the
domination cascade.  Any UNSAT transition would require a replayable proof
certificate or an independent solver audit before it could be used.  This
track deliberately does NOT duplicate the
order-40/41 core-coloring or counterexample lanes: it works at the
abstract-axiom level, primarily at `h = 8` where the ground truth
(no counterexample at 28) is already known upstream, so SAT/UNSAT
transitions are informative about the *lemma*, not about #151 itself.
