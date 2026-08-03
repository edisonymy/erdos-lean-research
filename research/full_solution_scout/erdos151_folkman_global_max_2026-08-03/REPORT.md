# Erdős #151: global/Folkman construction audit

Date: 2026-08-03 (Europe/London)

## Outcome

This lane found **no full proof and no counterexample** to Erdős #151.  It did
find a rigorous pruning theorem that retrospectively rules out the entire
"triangle-free Ramsey base plus one or two vertices" construction family.
That is useful campaign infrastructure, but it is probably folklore rather
than a publishable theorem.

The allocation verdict is **KILL as a full-thrust one-week lane; retain only
maintenance effort**.  Every genuinely global continuation located here
bottoms out in one of three hard problems:

1. a leading-constant comparison for the Erdős--Rogers function
   `f_{3,4}(n)`;
2. a new sparse edge-Folkman construction simultaneously controlling maximum
   degree, independence number, and maximal-clique avoidance; or
3. a months-scale certified enumeration.

This is not a recommendation to abandon #151.  It is a recommendation not to
mistake accumulated local structure for proximity to a full resolution.

## Definitions used

For a graph `G`, `beta(G)` is the largest cardinality of a vertex set that
contains no nontrivial inclusion-maximal clique of the ambient graph `G`.
`H(n)` is the minimum independence number among triangle-free graphs on `n`
vertices.  The conjecture is `beta(G) >= H(|G|)`.

Write `G ->_e (3,3)` when every red/blue edge-colouring of `G` has a
monochromatic triangle, and `G ->_v (3,3)` when every red/blue vertex-colouring
has a monochromatic triangle.

## Proved statements

### P1. Exact edge-Folkman reduction

If `G` does **not** edge-arrow `(3,3)`, then `beta(G) >= H(n)`.
Consequently every counterexample to #151 must satisfy `G ->_e (3,3)`.

Proof.  Fix a red/blue edge-colouring with no monochromatic triangle.  Let `M`
be the red-edge graph and let `L` consist of the edges of `G` that lie in no
triangle of `G`.  The graph `J = M union L` is triangle-free: a triangle using
an edge of `L` is impossible, and a triangle using only `M` would be red
monochromatic.  Every nontrivial maximal clique of `G` contains a `J`-edge.
A maximal clique of size two is an edge in `L`; a larger maximal clique
contains a triangle, and every triangle contains a red edge.  Since `J` is a
triangle-free `n`-vertex graph, it has an independent set `S` of size at least
`H(n)`.  Such an `S` cannot contain a maximal clique of `G`, because every such
clique contains a `J`-edge.  Thus `S` is admissible and
`beta(G) >= |S| >= H(n)`.  QED.

### P2. Edge-arrowing forces vertex-arrowing for triangles

`G ->_e (3,3)` implies `G ->_v (3,3)`.

Proof.  Suppose `V(G)=A union B` and both induced graphs `G[A]` and `G[B]`
are triangle-free.  Colour an edge red when both endpoints lie in the same
part, and blue when its endpoints lie in different parts.  A red triangle
would lie wholly in `A` or wholly in `B`, impossible.  A blue triangle would
have three vertices pairwise in different parts, impossible with two parts.
This is a red/blue edge-colouring with no monochromatic triangle.  Taking the
contrapositive proves the assertion.  QED.

The converse is false: `K5 ->_v (3,3)` by pigeonhole, while `K5` has a
red/blue edge-colouring with no monochromatic triangle because `R(3,3)=6`.

This proof specifically colours the internal edges of **both** parts the same
colour.  Colouring the two internal edge sets oppositely is unnecessary and
would obscure the argument.

### P3. Triangle-deletion and attachment obstruction

Every counterexample to #151 has triangle vertex-deletion number at least
three.  More generally, it cannot have its vertex set partitioned into two
triangle-free induced subgraphs.

Indeed, if deleting a set `D` of at most two vertices leaves a triangle-free
graph, then `G[D]` is also triangle-free.  Apply P2 to the partition
`D, V(G)-D`, then P1.

Consequently, **adding one or two arbitrary vertices to any triangle-free
graph can never produce a counterexample to #151**.  This makes every
one-vertex extension of the 27-vertex Ramsey `(3,8)` catalogue, and every
two-vertex extension of a triangle-free base, a logically impossible
counterexample family.  The earlier zero-hit one-vertex attachment sweep was
therefore inevitable.  Three-vertex extensions are killed too unless the
three added vertices induce a triangle (or another triangle-free bipartition
exists).

### P4. Neighbourhood and cone obstruction

For every vertex `v`, its open neighbourhood `N(v)` is admissible: if it
contained a maximal clique `K` of `G`, then `K union {v}` would be a larger
clique.  Hence

`beta(G) >= Delta(G)`.

In particular, if `G = K1 join H` is a cone over a nonempty graph `H`, every
maximal clique contains the apex and `V(H)` is admissible.  Since the full
vertex set contains a nontrivial maximal clique,

`beta(K1 join H) = |V(H)| = |V(G)|-1`.

Thus cone-based Folkman constructions cannot be #151 counterexamples.

### P5. One-edge stability of beta

For every edge `e=uv`,

`beta(G-e) <= beta(G)+1`.

Proof.  Let `S` be admissible in `G-e`.  If it is admissible in `G`, there is
nothing to prove.  Otherwise it contains a maximal clique `K` of `G`.  Such a
`K` must contain both `u` and `v`: if it did not use `e`, it would remain a
clique in `G-e`, and any extension there would also extend it in `G`, contrary
to maximality in `G`.  Therefore every maximal clique of `G` contained in `S`
uses `e`, so `S-{u}` is admissible in `G`.  Taking a maximum `S` gives the
inequality.  QED.

Corollary.  If `H(n)=h` and `G` is edge-minimal among `n`-vertex
counterexamples, then `beta(G)=h-1`, `beta(G-e)=h` for every edge, and every
admissible `h`-set in `G-e` contains both endpoints of `e`.  This is exact
criticality structure, but by itself it does not close a new case.

### P6. The K4-free Erdős--Rogers gateway

Let `alpha_3(G)` be the largest order of an induced triangle-free subgraph.
In a `K4`-free graph every triangle is an ambient maximal clique, so every
admissible set is triangle-free and

`beta(G) <= alpha_3(G)`.

Therefore a strict inequality

`f_{3,4}(n) < H(n)`

at any `n`, where `f_{3,4}` is the minimum possible `alpha_3` over `K4`-free
`n`-vertex graphs, would immediately provide a full counterexample to #151.
This is a correct global counterexample gateway, not a result establishing the
needed inequality.

## Computationally checked

`audit_small_graphs.py` exhaustively enumerates every labelled simple graph on
one through six vertices, with no external package.  Under Python 3.12.4 it
checked:

* 33,867 graphs in total;
* the explicit P2 partition-to-edge-colouring construction on every
  non-vertex-arrowing graph;
* no violation of edge-arrowing implying vertex-arrowing;
* no edge-arrowing graph with triangle-deletion number at most two;
* all 251,085 pairs `(G,e)` with `e` present for P5;
* `K5 ->_v (3,3)`, `K5` not `->_e (3,3)`, and `K6 ->_e (3,3)`.

There were zero violations.  The exact output is in
`audit_small_graphs.result.json`.  This computation is a regression/audit,
not the proof of P1--P6.

Reproduce from the repository root with:

```powershell
python .\research\full_solution_scout\erdos151_folkman_global_max_2026-08-03\audit_small_graphs.py
```

## Construction audit

| Construction route | Exact obstruction / status |
|---|---|
| Triangle-free base plus one or two vertices | Impossible by P2--P3, regardless of attachment edges. Do not restart this search. |
| Cone or universal-apex Folkman construction | `beta=n-1` by P4. |
| Dense known edge-Folkman graphs | Any instance with `Delta >= H(n)` is killed immediately by `beta >= Delta`; this is what happens to the internally checked dense catalogue examples. |
| Disjoint copies of a fixed graph | `beta` is additive over components, hence grows linearly in the number of copies, whereas `H(n)=Theta(sqrt(n log n))`. This is asymptotically the wrong direction. |
| Fixed-pattern balanced blow-ups | Even if arrowing is preserved, any base edge produces degree linear in the blow-up factor, while `H` is sublinear; P4 kills sufficiently large blow-ups. |
| K4-free pseudorandom construction | This is precisely the constant-sensitive P6 gateway. Current asymptotics do not supply the needed strict comparison. |
| Signal-sender / degree-splitting transformation | No sound transformation was found that preserves edge-arrowing while controlling `Delta`, `alpha`, and `beta`. Establishing one is a new research programme, not a one-week continuation. |

The existing local catalogue reports and exact searches were audited rather
than rerun.  In particular, this lane did not repeat the stopped order-41
residual CEGAR, the Ramsey `(3,8,27)` attachment sweep, or the incremental
saturation encodings.

## Fresh priority check (2026-08-03)

The check used primary papers where available and treated the Erdős Problems
status page only as an index, not as proof of openness.

* The live #151 page still labels the problem open and showed no linked proof:
  <https://www.erdosproblems.com/151>.
* Morris--Sahasrabudhe--Verstraëte, *On the Erdős--Rogers function*, posted
  2026-07-17, proves `f_{s,s+1}(n)=Theta(sqrt(n log n))` for fixed `s`:
  <https://arxiv.org/abs/2607.16118>.  For P6 this matches the order of `H(n)`
  but the available constants do not establish `f_{3,4}(n)<H(n)`.
* Joret--Micek--Reed--Smid, *Clique coloring of graphs with maximum degree*,
  gives an asymptotic `O(Delta/log Delta)` clique-colouring theorem:
  <https://arxiv.org/abs/2006.11353>.  A colour class is admissible, but the
  theorem does not provide the sharp constant needed to reach `beta>=H` in
  the Ramsey-jump regime.
* Hassan--Radziszowski--Van Overberghe, *On Small Folkman Graphs Arrowing K2
  or K3*, posted 2026-05-15, is the freshest directly adjacent construction
  paper located: <https://arxiv.org/abs/2605.16542>.  It does not provide the
  simultaneous low-degree/low-beta transformation required here.
* Cooper--Hollars, *Hitting all maximal independent sets in c-hollow graphs*,
  posted 2026-07-16 and revised 2026-07-21, is complement-adjacent but its
  bounds do not imply #151: <https://arxiv.org/abs/2607.15486>.
* Bikov--Nenov, *The edge Folkman number F_e(3,3;4) is greater than 19*, gives
  background and the then-known construction bounds:
  <https://arxiv.org/abs/1609.03468>.

Targeted searches found no paper claiming #151, the P6 constant comparison,
or a catalogue-to-low-beta transformation.  This is negative search evidence,
not a proof that no such result exists.  P2 is elementary and should be cited
as folklore/observed here unless a more exhaustive bibliographic check finds
an attribution; it should not be announced as a novelty claim.

## What remains conjectural or open

* Erdős #151 itself remains unresolved by this lane.
* No graph with `beta(G)<H(|G|)` was found.
* No leading-constant inequality `f_{3,4}(n)<H(n)` was proved at any new
  order.
* No degree-splitting or signal-sender construction with controlled beta was
  proved.
* No global clique-colouring/decomposition theorem sharp enough for #151 was
  proved.
* The small-graph audit is not evidence for the conjecture at orders beyond
  six; its purpose is only to adversarially check the structural lemmas.

## Allocation recommendation

Allocate at most the campaign's previously discussed **15--25% maintenance
share** to #151, mainly to preserve checked artefacts and exploit genuinely
new external inputs.  Do not launch more variants of the triangle-free-base
attachment search, and do not resume the stopped residual-first CEGAR merely
because it has accumulated many cuts.

Renew full thrust only if at least one of these concrete signals appears:

1. an explicit graph passes independent checks for `beta(G)<H(|G|)`;
2. a primary theorem or a certified finite computation establishes the P6
   strict constant comparison at some order;
3. a new low-degree edge-Folkman catalogue becomes available in the candidate
   `Delta,alpha < H(n)` regime; or
4. a decomposition theorem improves the current clique-colouring bound to the
   sharp Ramsey-scale constant rather than only the correct asymptotic order.

Absent one of those signals, the highest probability of solving at least one
Erdős problem within a week comes from reallocating the majority of research
capacity to fresh counterexample-friendly targets while keeping #151 warm.
