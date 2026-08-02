# Erdős 151: general structure — the Folkman reduction and the window package

**Status of this note (2 August 2026, Claude Fable 5 lane).**  Everything
proved here is unconditional and self-contained given the stated Ramsey
values, except where a claim explicitly cites the through-27 files.  The
note has not yet been independently audited; treat it as a research note
awaiting the same adversarial review the order-23/24 files received.
Notation follows [`../README.md`](../README.md): maximal always means
inclusion-maximal, a set is *admissible* if it contains no maximal clique
of the ambient graph on at least two vertices, `beta(G)` is the largest
admissible size, `tau(G) = n - beta(G)`, and `H(n)` is the minimum
independence number over triangle-free graphs on `n` vertices, so
`H(n) = h` exactly when `R(3,h) <= n < R(3,h+1)`.  The conjecture
(Erdős #151, Erdős–Gallai–Tuza Problem 1) is `beta(G) >= H(n)` for every
graph `G` on `n` vertices.

The through-27 campaign files prove the conjecture for `n <= 27`.  This
note asks what the mechanism gives for *all* `n`.

---

## Theorem A (Folkman reduction; fully general)

Write `G -> (3,3)` for the edge-arrowing relation: every red/blue
coloring of `E(G)` contains a monochromatic triangle.

**Theorem A.**  Let `G` be any graph on `n` vertices with
`G -/-> (3,3)`.  Then `beta(G) >= H(n)`; equivalently
`tau(G) <= n - H(n)`.

Consequently, **every counterexample to Erdős #151 edge-arrows
`(3,3)`** — it is an edge-Folkman graph.

**Proof.**  Fix a coloring of `E(G)` with no monochromatic triangle; let
`M` be its red class, so `M` is triangle-free and every triangle of `G`
contains at least one `M`-edge (it is not all blue) and at least one
blue edge (it is not all red).  Let `L` be the set of edges of `G` lying
in no triangle of `G`; these are exactly the maximal 2-cliques.  Put
`J = L ∪ M`, a spanning subgraph of `G`.

*`J` is triangle-free.*  A triangle of `J` is a triangle of `G`; none of
its edges lies in `L` (each lies in a triangle), so all three lie in
`M`, contradicting the triangle-freeness of `M`.

Since `J` has `n` vertices and is triangle-free, `alpha(J) >= H(n)` by
the definition of `H`.  Let `S` be a `J`-independent set of size `H(n)`.

*`S` is admissible in `G`.*  Let `K` be a maximal clique of `G` with
`|K| >= 2`.  If `|K| = 2`, its edge lies in no triangle, hence lies in
`L ⊆ J`, so both endpoints cannot lie in the `J`-independent `S`.  If
`|K| >= 3`, then `K` contains a triangle of `G`, which contains an edge
of `M ⊆ J` with both endpoints in `K`; again `K ⊄ S`.

Hence `beta(G) >= |S| = H(n)`.  ∎

**Remarks.**

1. Theorem A needs no minimality, no degree bound, no window: the
   order-24 file's finish ([`../order24.md`](../order24.md), "Ramsey
   finish") is this argument specialized to a 6-regular 24-vertex graph;
   the observation here is that all its hypotheses except the coloring
   are removable.
2. Combined with the triangle-edge-coloring lemma
   ([`../order24.md`](../order24.md), Lemma 2 — every graph in which
   each vertex lies in at most three triangles admits such a coloring),
   Theorem A already reproves the conjecture for every graph with all
   vertex triangle-counts at most three, on every order.
3. A counterexample contains an edge-minimal edge-Folkman core `Q`.
   Every edge of `Q` lies in at least two `Q`-triangles, and the ambient
   counterexample has some vertex in at least four triangles (by Lemma 2).
   The first statement is about the minimal core, not every ambient edge:
   an ambient arrowing graph can have irrelevant triangle-free edges.  The
   conjecture is thereby reduced to graphs containing a triangle-rich core,
   while Theorem B below forces the ambient counterexample to be globally
   sparse.  The tension between these two is now the entire problem.

## Theorem B (window package for a first counterexample)

Let `n` be the **least** order carrying a counterexample, let `G` be one
on `n` vertices, and let `h = H(n)`, so `beta(G) <= h - 1`.  Recall two
elementary facts from the campaign files (both are reproved trivially):
`beta >= Delta` (an open neighborhood is admissible) and the recurrence
`beta(G) >= |I| + beta(G - N[I])` for every independent set `I`
([`../README.md`](../README.md); Lean-verified recurrence).  Since any
independent set is admissible, also `beta(G) >= alpha(G)`.

Then:

- **(W1) Window.**  `R(3,h) <= n <= R(3,h-1) + h - 1`.
- **(W2) Ramsey-type sparsity.**  `alpha(G) <= h - 1` and
  `Delta(G) <= h - 1`.
- **(W3) Degree floor.**  Every vertex has
  `deg(v) >= n - R(3,h-1)`, so
  `delta(G) >= R(3,h) - R(3,h-1)`; at the top of the window
  (`n = R(3,h-1) + h - 1`) the graph is exactly `(h-1)`-regular.
- **(W4) Domination cascade.**  For every independent set `I` with
  `1 <= |I| = k <= h - 2`:  `|N[I]| >= n - R(3,h-k) + 1`.
- **(W5) Local swap structure.**  If `deg(v) = h - 1` and
  `x ∉ N[v]`, then `v` and `x` have a common neighbor; if the common
  neighbor `a` is unique, then neither `va` nor `xa` lies in a triangle.
- **(W6) Two-walk triangle bound.**  If `G` is `(h-1)`-regular, then for
  every vertex `v`, writing `t_v` for the number of triangles on `v`:
  `t_v <= ((h-1)(h-2) - (n-h)) / 2`.
- **(W7) Folkman.**  `G -> (3,3)`  (Theorem A).

**Proofs.**

*(W1).*  `n >= R(3,h)` restates `H(n) = h`.  For the upper end, pick any
vertex `v`; minimality gives `beta(G - N[v]) >= H(n - 1 - deg v)`, so by
the recurrence `h - 1 >= beta(G) >= 1 + H(n - 1 - deg v)`, forcing
`H(n - 1 - deg v) <= h - 2`, i.e. `n - 1 - deg(v) <= R(3,h-1) - 1`.
With `deg(v) <= Delta <= beta <= h - 1` this gives
`n <= R(3,h-1) + h - 1`.

*(W2).*  `alpha <= beta <= h - 1` and `Delta <= beta <= h - 1`.

*(W3).*  The displayed inequality in (W1)'s proof holds for every `v`:
`deg(v) >= n - R(3,h-1)`.  At the top of the window this floor equals
`h - 1`, meeting the (W2) ceiling.

*(W4).*  By the recurrence and minimality,
`h - 1 >= beta(G) >= k + H(n - |N[I]|)`; if
`n - |N[I]| >= R(3,h-k)` the right side would be `>= k + (h - k) = h`.
(For `k = h - 1` the statement is vacuous.)

*(W5).*  `beta <= h - 1` means every `h`-subset contains a maximal
clique of `G` (the bad-`h`-set property).  Apply it to
`S = {x} ∪ N(v)`, `|S| = h`: the maximal clique `K ⊆ S` cannot avoid
`x` (else `K ⊆ N(v)` extends by `v`), so `x ∈ K` and
`K \ {x} ⊆ N(v) ∩ N(x)`, nonempty since `|K| >= 2`.  If
`N(v) ∩ N(x) = {a}` then `K = {x,a}` is maximal, i.e. `xa` lies in no
triangle.  The same conclusion for `va` follows only if `deg(x)=h-1` as
well; the regular-graph application in (W6) has this extra hypothesis.

*(W6).*  Exactly as in [`../order24.md`](../order24.md) (6): counting
two-walks from `v` landing outside `N[v]`,
`sum_{x ∉ N[v]} c(v,x) = (h-1)(h-2) - 2 t_v`, and by (W5) every one of
the `n - h` summands is at least 1.

∎

**Consistency check at `h = 7`.**  (W1) gives `23 <= n <= 24`; (W3) top
gives 6-regularity at `n = 24`; (W6) gives `t_v <= (30 - 17)/2`, i.e.
`t_v <= 6` — the order-24 file sharpens this to `t_v <= 3` using the
common-neighbor cap (4) and the `u_v <= 5 l_v` count, which need the
exact equality structure; the general package deliberately records only
the hypothesis-free part.

## What the package says about the next interval (h = 8, n = 28..30)

By (W1) with `R(3,8) = 28`, `R(3,7) = 23`: the next possible first
counterexample lives at `n ∈ {28, 29, 30}`.  By (W2)–(W7) it satisfies:

- `alpha(G) <= 7`, `Delta(G) <= 7`;
- `delta(G) >= n - 23` (so `>= 5, 6, 7` at `n = 28, 29, 30`; at
  `n = 30`, exactly 7-regular);
- every independent pair dominates all but at most `R(3,6) - 1 = 17`
  vertices; every independent triple all but at most `R(3,5) - 1 = 13`;
  every independent 6-set all but at most `R(3,2) - 1 = 2`;
- `G -> (3,3)`, it contains an edge-minimal arrowing core in which every
  core edge lies in at least two core triangles, and some ambient vertex
  lies in at least four triangles;
- every 8-subset of `V(G)` contains an inclusion-maximal clique of `G`.

Two consequences worth acting on:

1. **The interval is a finite, SAT-shaped question.**  "Does there exist
   `G` on 28 vertices with `Delta <= 7` and `beta(G) <= 7`?" is a
   monotone-free finite search with a natural lazy encoding: the
   admissible-8-set condition is a separation oracle (given a candidate
   `G`, find an admissible 8-set; add the blocking constraint),
   structurally identical to the campaign's existing CEGAR machinery.
   The `alpha <= 7`, degree, domination, and triangle-richness
   constraints above are static pruning.  If SAT: **that model is a full
   negative resolution of Erdős #151** (after the two independent
   definition-level checkers).  If UNSAT at 28, 29, 30 with replayable
   certificates: the conjecture holds through order 35
   (`R(3,9) = 36`), and the window recurrence advances to the next
   interval.
2. **Erdős's own doubt points at the negative direction.**  The problem
   page records Erdős calling the conjecture "perhaps completely
   wrongheaded" and that Erdős–Gallai could not progress even for
   `K4`-free graphs.  The right posture for the interval is
   candidate-first (hunt the SAT model), with the UNSAT certificates as
   the consolation theorem — not the other way round.

## Where the general problem actually stands

The present method cannot reduce the full conjecture to finitely many
intervals.  The window (W1) is nonempty whenever
`R(3,h)-R(3,h-1)<=h-1`, and this occurs for infinitely many `h`: if all
sufficiently late gaps were at least `h`, summing them would force
`R(3,h)=Omega(h^2)`, contradicting the standard
`R(3,h)=O(h^2/log h)` upper bound.  This does not assert a pointwise
`O(h/log h)` bound on every consecutive gap.  A general proof must kill
the surviving windows uniformly.  The mechanism's uniform residue after
Theorems A and B is exactly:

> show that no graph can simultaneously satisfy (W2)-(W6) — global
> sparsity at the Ramsey threshold — and (W7) — edge-Folkman
> triangle-richness.

At small `h` the two collide numerically (`t_v <= 3` versus Lemma 2's
threshold — this is precisely the through-27 proof).  At large `h` the
two-walk bound (W6) weakens to `t_v = O(h^2)`, far above any coloring
threshold, and the collision must instead come from sparse-Ramsey
constants: `alpha(G) <= h - 1` with `Delta <= h - 1` on
`n >= R(3,h) = Theta(h^2 / log h)` vertices sits within a constant
factor of the best known `K_r`-free independence bounds
(Shearer-type `alpha >= c n log Delta / Delta` for triangle-free;
weaker for bounded clique number).  Improving those constants for
triangle-*rich* Folkman-type graphs is a genuine research program, not a
week-scale computation; conversely, a large-`h` counterexample would
need a sparse, small-independence edge-Folkman graph — no known
construction is close, but nothing excludes one, consistent with
Erdős's recorded doubt.  Both directions should be treated as live.

## Priority caution

Theorem A's ingredients (the `L ∪ M` splitting and the coloring lemma)
are elementary and natural; the specialization-free statement may exist
in the clique-transversal literature (Tuza's surveys, or work citing
Erdős–Gallai–Tuza 1992).  Before any public use of Theorem A it must get
its own targeted priority search ("clique transversal" + "Ramsey" +
"monochromatic triangle" + "Folkman"), beyond the searches recorded in
[`../literature.md`](../literature.md), which did not target this
reduction.
