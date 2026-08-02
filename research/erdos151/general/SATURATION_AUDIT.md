# Independent audit of the saturation–exchange lane

**Status: audited structural progress, not a solution of Erdős #151.**
This note was reconstructed independently on 2 August 2026.  It assumes a
least counterexample at the next Ramsey jump `n = R(3,10) ∈ {40,41}`, the
verified through-order-39 result, and the standard consequences
`beta(G)=9`, `Delta(G)<=9`, `alpha(G)<=9`, and `omega(G)<=5`.

The companion Fable note `SATURATION_EXCHANGE.md` originally contained two
overstatements.  They have been corrected in place:

1. The edge-budget average is not below `2.4` at `h=10`: its zero-internal-
   edge upper bound is `81/31` at order 40 and `81/32` at order 41.  The
   budget alone does not show that most outside vertices have one or two
   neighbors in `S`.
2. Only the clean singleton two-swap lemma was proved.  The broader claimed
   two-swap equivalence was withdrawn.

## Reconstructed base lemmas

Let `S` be a maximum admissible 9-set and `O=V(G)\S`.  An `S`-anchor of
`v∈O` is a nonempty `A⊆S` such that `{v}∪A` is an ambient-maximal clique.

- `beta(G)=9`, and every maximum admissible set has size 9.
- Every outside vertex has at least one anchor.
- For a fixed anchor `A`, the vertices anchored by `A` form an independent
  set: two adjacent such vertices would extend each other's claimed maximal
  clique.
- `(S\{a})∪{v}` is admissible exactly when every anchor of `v` contains
  `a`.  A nontrivial maximal clique witnessing failure must contain `v`,
  and its remaining vertices are precisely an anchor avoiding `a`.
- If nonadjacent `v,w` have exact `S`-neighborhoods `{a}` and `{b}` with
  `a≠b`, then `(S\{a,b})∪{v,w}` is admissible.  Both inserted vertices are
  anticomplete to the remaining part of `S` and to each other.

These arguments use ambient maximality throughout; they do not replace it
with maximality inside an induced subgraph.

## Stronger consequences

### Exact fibers

For nonempty `A⊆S`, put

`P_A={v∈O : N(v)∩S=A}`.

Then `P_A` is independent and `|P_A|<=|A|`.  For independence, choose any
anchor `B⊆A` of one fiber vertex; an adjacent second fiber vertex would
extend `{v}∪B`.  If `|P_A|>=|A|+1`, then `S\A` together with `|A|+1`
fiber vertices is an admissible 10-set.

### Hall–beta expansion

For every `Y⊆O`,

`beta(G[Y]) <= |N_S(Y)|`.

Indeed, if `T` is admissible in `G[Y]`, then
`(S\N_S(Y))∪T` is ambient-admissible.  A nontrivial ambient-maximal clique
inside this union lies wholly in one anticomplete part.  The `S` case is
impossible; in the `T` case it is also maximal in `G[Y]`, contradicting the
choice of `T`.

Least-order minimality then gives

`|Y| <= R(3,|N_S(Y)|+1)-1`.

Equivalently, for `A⊆S`,

`|{v∈O : N_S(v)⊆A}| <= R(3,|A|+1)-1`.

The Ramsey-number corollary uses the least-counterexample hypothesis; it is
not a free consequence of the Hall–beta inequality for an arbitrary graph.

### Minimum-internal-edge choice

Now choose `S` among maximum admissible sets to minimize `e(G[S])`.  Write
`z` for the number of isolated vertices of `G[S]`, `m=|O|`, and
`C=e(S,O)`.

An exact one-neighbor vertex attached at `s` is swappable.  Minimality forces
`s` to be isolated in `G[S]`, and the exact-fiber lemma allows at most one
such vertex per isolated `s`.  Consequently

`2m-z <= C <= 81-2e(G[S])`,

while `e(G[S]) <= binom(9-z,2)`.  Optimizing over integral `z` gives

- `e(G[S])<=11` at order 40;
- `e(G[S])<=10` at order 41.

### All-removal-set anchor shadow

For `R0⊆S`, define

`B_R0={v∈O : every S-anchor of v meets R0}`.

Then

`alpha(G[B_R0]) <= |R0|`.

Otherwise `(S\R0)` together with an independent `(|R0|+1)`-set in
`B_R0` is an admissible 10-set.  In particular, `B_{s}` is a clique and
every member is adjacent to `s`, so `|B_{s}|<=4`.

### Exact two-neighbor vertices

Suppose `N_S(v)={a,b}`.

- If `ab` is an edge, `vab` is the only possible anchor clique.  Both
  one-vertex swaps are admissible, so minimality makes `ab` an isolated
  `K2` component of `G[S]`.  There is at most one vertex over this pair:
  two exact-fiber vertices are nonadjacent, and replacing both endpoints of
  the `K2` would strictly reduce the internal-edge count.
- If `ab` is not an edge and two vertices have this exact neighborhood,
  replacing `a,b` by both independent fiber vertices forces both `a` and
  `b` to be isolated in `G[S]`.
- If exactly one spoke, say `av`, is maximal, then `{a}` is the sole anchor
  of `v`.  The singleton shadow `B_{a}` contains no other vertex, since it
  is a clique and any neighbor of both `a` and `v` would extend the maximal
  edge.  There are at most nine such vertices in total.
- Adjacent-pair cases lie over distinct isolated `K2` components, so there
  are at most four of them.

For every remaining exact-two-neighbor vertex, the pair is nonadjacent and
both spokes are maximal.  If there are `b` such vertices, then `b<=28`.
For each 4-set `R0⊆S`, the vertices whose anchor pair lies in `R0` have
independence number at most 4, and hence span at least `|X_R0|-4` edges.
Adjacent vertices in this class have disjoint anchor pairs, so each internal
edge is counted for exactly one 4-set, whereas each vertex is counted in
`binom(7,2)=21` four-sets.  Thus

`e(B) >= 21b-4*binom(9,4)=21b-504`.

The degree ceiling gives `e(B)<=7b/2`, whence `35b<=1008` and `b<=28`.
This is a genuine restriction, but not yet a contradiction at order 40 or
41.

## Independent verification of the abstract SAT witnesses

`experiments/erdos151_siege/verify_anchor_model.py` uses only the Python
standard library and shares no encoding implementation with the PySAT
generator.  It reconstructs the edge list and verifies degree bounds,
clique and independence bounds, ambient admissibility of the designated
`S`, every outside anchor, and all recorded statistics.

The checker hash at this audit revision is:

`e60c9063a2911d0b566514a44e760c1ec9927d4b2f32e5b188bc57145a0300b5`.

It returned `VERIFIED` on all three witnesses:

| stage | meaning added | edges | witness SHA-256 |
|---|---|---:|---|
| 1 | local degree/clique/admissibility/anchor axioms | 21 | `783821e74beb48a63aad1b28f7523d2f056af48b77ee727ba7e7d0b84fa80af3` |
| 2 | plus `alpha<=7` | 92 | `48dc7241542b623dcba714e0681099f1c91302d8e9013c108d6123b5a1c0bb0b` |
| 3 | plus `delta>=5` | 94 | `ad9efb54b69e44e77f95d711bb1034b5f5cfbc74074dafec7a81a3eb8de5f5e5` |

These are counterexamples to progressively stronger **abstract local
counting lemmas**, not counterexamples to Erdős #151.  They do not impose
the bad-10-set condition globally or saturation across all maximum
admissible sets.  The checker also validates an explicit admissible 8-set in
each graph, proving directly that none of the witnesses has `beta<=7` and
that E0/E4's maximum-set conclusion is absent from the encoding.

The next exact probe, `anchor_swap_closure_model.py`, adds the proved
`alpha(G[B_R0])<=|R0|` constraints for every `R0⊆S`.  Its first bounded run
was stopped after approximately one CPU-hour with **no conclusion** and no
result file; the exact disposition is recorded in
`experiments/erdos151_siege/runs/anchor_stage4.stopped.json`.  It produced no
SAT model, UNSAT answer, or certificate.  A future SAT outcome can be checked
by the present independent verifier.  An UNSAT outcome instead needs proof
logging and certificate checking, or a genuinely independent solver path;
the witness verifier cannot establish UNSAT.
