# Erdős #742 — unrestricted order-25 candidate-first attack

## Outcome

No counterexample was found, and this work does not prove any new case of the
Murty–Simon conjecture.  The unrestricted target at order 25 is a graph with
exactly 157 edges.  Across the serious guided portfolio, the best graph still
had 25 removable edges.  No state below that threshold, and therefore no
quantified target-preserving repair path, was found.  The candidate-search
hard gate is met: stop this heuristic family rather than launch another large
symmetry exclusion or uncertified UNSAT computation.

The useful outcome is a corrected local baseline, an exact edit-radius audit,
an unrestricted graph-state search implementation, and a standalone second
definition checker.

## Published facts and live audit (not new results)

1. The statement asks whether every finite simple graph of diameter exactly
   two for which deleting any edge destroys diameter two has at most
   `floor(n^2/4)` edges.
2. The [live Erdős Problems entry](https://www.erdosproblems.com/742) was
   indexed on 2026-08-03 as **DECIDABLE — resolved up to a finite check**, not
   as fully proved or disproved.  The indexed page exposed no named person as
   currently working on it.  Search non-discovery is not a priority claim.
3. Fan proved the conjectured inequality through order 24 and at order 26.
   His strict general bound

   ```text
   m < n^2/4 + (n^2 - 16.2n + 56)/320
   ```

   is `m < 157.1125` at `n=25`.  Thus an order-25 counterexample has exactly
   157 edges.  Füredi's sufficiently-large-order theorem leaves a finite but
   impractically large middle range.
4. Published reductions imply that an order-25 counterexample is
   nonbipartite, has maximum degree at most 17, and has no dominating edge.
5. In the complement formulation it would be a 143-edge, order-25
   3-total-domination-edge-critical graph.  The no-dominating-edge reduction
   places the complement in the diameter-two rather than diameter-three case.
6. Dailly–Foucaud–Hansberg conjecture the much stronger nonbipartite bound
   `floor((n-1)^2/4)+1`, which is 145 at order 25, with the large extremal
   family formed by `C5` twin expansions.  This is a conjecture, not a usable
   exclusion of the 157-edge slice.
7. Brian Li's public order-25 CNF at commit
   [`57fd4b4`](https://github.com/BrianLi009/diameter2critical/commit/57fd4b41913670227f7bc86708297d695af7823e)
   contains no published SAT/UNSAT conclusion for the counterexample slice.
   All locally recorded order-25 and order-27–30 solver PIDs were stale at the
   start of this lane; no active process was replaced or duplicated.
8. The latest directly relevant paper found was the restricted 2025
   Lin–Wang high-density/`C5`-free classification, which still treats the full
   statement as the longstanding conjecture.
9. The Erdős–Faudree–Rousseau triangular-edge theorem forces every graph with
   more than `floor(n^2/4)` edges to have at least
   `2 floor(n/2)+1` edges lying in triangles.  At order 25 this is exactly 25.
   The 157-edge radius-one baseline attains equality: its twelve triangles
   form a book around the added internal edge and their union has 25 edges.

Primary references are Fan ([DOI](https://doi.org/10.1016/0012-365X(87)90174-9)),
Dailly–Foucaud–Hansberg ([arXiv:1812.08420](https://arxiv.org/abs/1812.08420)),
the maximum-degree theorem of Haynes–Henning–van der Merwe–Yeo
([DOI](https://doi.org/10.2478/s11533-014-0449-3)), and Lin–Wang
([DOI](https://doi.org/10.1016/j.dam.2025.06.025)).  A modern primary source
restating the exact Erdős–Faudree–Rousseau theorem is
[arXiv:2406.13176](https://arxiv.org/abs/2406.13176).

## Exact computational setup (search evidence only)

Fix a labelled `12+13` partition.  Relative to `K12,13`, every 157-edge graph
has `k` internal edges and exactly `k-1` deleted cross-edges, since

```text
156 + k - (k-1) = 157.
```

This is a parametrization of every labelled graph on the target slice for the
fixed partition, not a near-bipartite restriction.  The guided search also
uses raw arbitrary edge swaps and therefore does not depend on remaining near
that partition.

The fast checker uses the exact local characterization for an edge `uv` in a
diameter-two graph.  The edge is critical exactly when at least one of these
holds:

1. `u` and `v` have no common neighbour;
2. some `x in N(u) \ (N(v) union {v})` has `N(x) intersect N(v) = {u}`;
3. the symmetric condition holds.

The reported objective is

```text
(nonedges lacking a two-path,
 present edges failing the criticality test,
 surrogate certificate-defect sum).
```

The third coordinate guides the walk but is **not** claimed to be an edit
distance.  Acceptance gives diameter failures finite weight so the walk can
cross temporary distance-three states.

### A rigorous target-slice reduction from triangular edges

Call a nonedge a *one-common-neighbour pair* when its endpoints have exactly
one common neighbour.  Every critical edge lying in a triangle must use the
second or third local certificate above, because its endpoints already have a
common neighbour.  Such a certificate selects a one-common-neighbour nonedge.
Conversely, one such nonedge, with unique common neighbour `u`, can certify at
most its two incident edges through `u`.

The triangular-edge theorem therefore gives the following necessary condition
for an order-25, 157-edge candidate:

```text
at least 25 present edges lie in triangles;
at least ceil(25/2) = 13 nonedges have exactly one common neighbour.
```

Moreover, if nonadjacent `x,y` have unique common neighbour `u`, then
`N(x) union N(y)` lies in the other 23 vertices and has size
`d(x)+d(y)-1`.  Hence `d(x)+d(y) <= 24`.  So the candidate needs at least 13
distinct low-degree-sum nonedges of this exact type.  This is an elementary
sound reduction, not a solution; it sharpens the concrete order-25 search
specification and suggests a complement-side capacity argument.

Equivalently, in the 143-edge complement these are at least 13 edges whose
endpoints jointly totally dominate every vertex except one, and whose
complement-degree sum is at least 24.  This is the natural quasi-edge skeleton
on which a future complement/total-domination construction or counting proof
should start.

A second implementation, `independent_bfs_verifier.py`, imports neither
searcher.  It builds adjacency sets, performs all-source BFS, then repeats the
diameter computation after deleting each edge.  Its controls verify:

| graph | edges | definition result |
|---|---:|---|
| `K12,13` | 156 | diameter-2-critical |
| a split `C5+` construction | 145 | diameter-2-critical |
| `K12,13` plus one internal edge | 157 | invalid; 25 removable edges |

Any actual candidate would have to pass both the local implementation and this
standalone BFS implementation.  No candidate reached that gate.

## Exhaustive radius audit

There are two radius-one orbits because the two parts have different sizes:

| added internal edge | objective | independent removable-edge count |
|---|---:|---:|
| in the 12-vertex side | `(0,27,39)` | 27 |
| in the 13-vertex side | `(0,25,36)` | 25 |

The latter is the true local baseline.  If its internal edge is `xy`, its 25
failures are exactly the internal edge plus the 24 cross-edges incident with
`x` or `y`.  The 24 cross-edge surrogate defects are one each; the internal
edge's current-state surrogate defect is 12.

Adding two internal edges and deleting one cross-edge has 14 orbits: an
adjacent pair or matching in either side, plus one edge in each side, with all
incidence roles for the deleted cross-edge.  All 14 were evaluated.  The best
diameter-two representative is a path in the 13-side supported at its middle
vertex, with objective `(0,35,46)`.  Several incidence roles already fail
diameter two.  Hence the smallest fixed-edge-count perturbations do not expose
a repair of the 25-failure baseline.  The complete orbit table is retained in
`run_summary.json`.

## Guided unrestricted portfolio

Move generation targeted failed unique-two-path certificates, sampled
compensating additions that repair newly broken distance pairs, and always
included unrestricted random edge swaps.  Restarts cycled through:

- the `K12,13` local baseline;
- arbitrary random 157-edge graphs;
- random dense graphs greedily deleted to 157 edges while preserving diameter
  two where possible;
- the 145-edge subdivided-bipartite/`C5+` construction augmented by 12 random
  edges.

The first portfolio ran for 120 seconds over seeds 742–744: 1,378 iterations,
1,265 accepted moves, and 14 restarts.  It tracked the selected beam moves and
never beat `(0,25,36)`.

An audit then found that best-state reporting should inspect every generated
neighbour, not only the neighbour selected by scalar energy.  After that was
fixed, seeds 745–746 ran for 90 seconds: 1,498 iterations, 1,436 accepted
moves, 15 diversified restarts, and every scored neighbour included in the
best-objective audit.  The result remained `(0,25,36)`.  The lowest scalar
state was also the same radius-one graph.

Combined serious walk time was 210 seconds, 2,876 iterations, 2,701 accepted
moves, and 29 restarts.  These numbers measure a bounded heuristic search;
they do not exclude any graph.

## Structural bridge to the 145-edge family

Start with the best baseline `K12,13 + xy`, where `x,y` lie in the 13-side.
For each of the 12 opposite-side vertices `a`, delete exactly one of `ax` and
`ay`, using both choices at least once.  The resulting graph has 145 edges,
diameter two, and every edge is critical.  The standalone BFS verifier checks
this construction directly.  It is the familiar `C5+`/subdivided-bipartite
extremal family predicted by the stronger conjecture.

This explains the landscape but is not a bound: the natural coordinated
nonbipartite repair sheds 12 edges, whereas a counterexample would have to
recover all 12 net edges through a different global witness system.  Random
and certificate-guided 12-edge augmentations did not do so.  There is no proof
that every possible augmentation fails.

## Speculation and recommended next gate

The search evidence points away from a counterexample at order 25, but 25
removable edges is not a near-candidate.  More blind stochastic time is not
justified by this landscape.  A worthwhile next attack needs a new structural
compression, for example a complement-side quasi-edge capacity lemma using
the forced 143-edge, minimum-complement-degree, diameter-two regime.  Only
after such a lemma reduces the unrestricted space substantially would a
certified finite computation be proportionate.

In particular, do not revive the already-falsified blanket injection from
maximum-cut internal edges to cross nonedges, and do not turn an uncertified
solver `UNSAT` response into a theorem.

## Files

- `direct_candidate_search.py` — all-slice parametrization, local checker,
  two radius-one and fourteen radius-two orbit audits, simple annealer.
- `guided_swap_search.py` — unrestricted certificate-guided edge-swap search.
- `independent_bfs_verifier.py` — standalone definition checker and controls.
- `run_summary.json` — exact retained objectives and run counts.
