# Erdős #64 theory milestone 1: hostile-audit version

Date: 2026-08-03

This note freezes three claims for independent audit.  It deliberately distinguishes
mathematical proof, imported literature, and computation.

## Status vocabulary

- **PROVED HERE**: the argument below is self-contained.
- **PROVED, ONE LITERATURE DEPENDENCY**: the local reduction is proved here and the
  named published theorem is the only imported assertion.
- **COMPUTATIONALLY CHECKED, CONDITIONAL SCOPE**: the code exhausts the explicitly
  identified records/operations, but upstream census completeness is a separate
  dependency.

Throughout, a *dyadic length* means `2^k` with `k >= 2`, so the first forbidden
length is 4.  All graphs are finite and simple, and all cycles are simple.

## 1. Exact minimality convention

Assume a counterexample exists.  Choose `G` lexicographically minimal in

1. `n = |V(G)|`, and then
2. `m = |E(G)|`.

Thus `delta(G) >= 3` and `G` has no dyadic cycle.  This exact two-stage choice is
important: vertex deletions use order-minimality, while deletion of an edge whose
endpoints both have degree at least four uses size-minimality.

Every proper subgraph `H` of `G` has `delta(H) <= 2`.  Indeed, otherwise `H` is
itself dyadic-free with minimum degree at least three.  If it has fewer vertices it
contradicts the first minimization; if it is spanning with fewer edges it contradicts
the second.  Also `G` is connected, since any component would itself be a smaller
counterexample.

No result of Carr is needed below.  Two local observations also present in Carr's
minimal-counterexample analysis are reproved here from the stated minimality.

## 2. Cubic-vertex abundance, with a strict strengthening

Let

```
D = {v : deg_G(v) = 3},       A = {v : deg_G(v) >= 4},
d = |D|,                       a = |A|.
```

### Lemma 2.1 (local structure) — PROVED HERE

`A` is independent, and every vertex of `G` has a neighbor in `D`.

**Proof.**  If an edge has both endpoints in `A`, deleting it leaves minimum degree
at least three and gives a same-order, smaller-size counterexample.  Hence `A` is
independent.  If a vertex `v` has no neighbor in `D`, all its neighbors have degree
at least four.  Deleting `v` lowers those degrees only to at least three, so `G-v`
is a smaller-order counterexample.  This proves both statements.  QED

In particular, every `x in D` has a neighbor in `D`, so it has at most two neighbors
in `A`.  Since every neighbor of a vertex in `A` lies in `D`,

```
4a <= e(A,D) <= 2d.                                      (2.1)
```

This already proves `d >= 2a`, equivalently `d >= ceil(2n/3)`.

### Theorem 2.2 (strict cubic abundance) — PROVED HERE

In fact

```
d >= 2a + 2,
```

and hence

```
d >= ceil((2n+2)/3),       a <= floor((n-2)/3).           (2.2)
```

**Proof.**  We exclude the only two integer possibilities below `2a+2` allowed by
(2.1).  Notice first that `G` is `C4`-free because 4 is dyadic.

Suppose `d=2a`.  Equality holds throughout (2.1).  Consequently every vertex of
`A` has degree exactly four, and every vertex of `D` has exactly two neighbors in
`A` (and one in `D`).  Construct a graph `J` on vertex set `A`: for every `x in D`,
join its two distinct `A`-neighbors by one edge.  Two different vertices of `D`
cannot yield the same unordered pair, because those two length-two paths would form
a `C4` in `G`.  Thus `J` is simple.  It is 4-regular.

Every simple cycle of length `ell` in `J` lifts, by replacing each edge with its
corresponding two-edge path through a distinct vertex of `D`, to a simple cycle of
length `2ell` in `G`.  Therefore `J` has no dyadic cycle: a `2^k`-cycle in `J` would
lift to a `2^(k+1)`-cycle in `G`.  But `delta(J)=4` and `|V(J)|=a<n`, contradicting
the order-minimality of `G`.

Now suppose `d=2a+1`.  Define the two nonnegative integer slacks

```
x = sum_{u in A}(deg_G(u)-4) = e(A,D)-4a,
y = sum_{v in D}(2-deg_A(v)) = 2d-e(A,D).
```

Then `x+y=2`.  Also

```
sum_{v in D} deg_{G[D]}(v)
  = sum_{v in D}(3-deg_A(v))
  = d+y
```

is even.  Since `d` is odd, `y` is odd.  Hence `x=y=1`.  Exactly one vertex
`u* in A` has degree five and all other vertices of `A` have degree four; exactly
one vertex `v* in D` has only one neighbor in `A`, while every other vertex of `D`
has two.

Construct `J` on `A` from the `2a` vertices of `D-{v*}` exactly as above.  Again
`J` is simple by `C4`-freeness.  If the unique `A`-neighbor of `v*` is `u*`, then
`J` is 4-regular.  Otherwise its degree in `J` is three, the degree of `u*` in `J`
is five, and all other degrees are four.  Thus in either case `delta(J)>=3`.
The same cycle-lifting argument says that `J` is dyadic-free, contradicting
`|V(J)|=a<n`.  The cases `a=0` cannot create an exception: `d=0` or `d=1` is
incompatible with a nonempty simple graph of minimum degree three.  QED

### Audit notes for Theorem 2.2

- Suppression does **not** claim that `J` is a subgraph or minor preserving all
  cycles.  Only the one-way lifting of each simple cycle of `J` is used.
- Simplicity of `J` uses exactly the forbidden `C4`; without it parallel suppressed
  edges would be possible.
- A lifted cycle is simple because a simple cycle of `J` has distinct vertices and
  distinct edges, and distinct edges were assigned distinct subdivision vertices.
- `J` need not be connected.  A finite dyadic-free graph with minimum degree at
  least three is already a smaller counterexample; alternatively any component is.
- The `+2` strengthening uses both the dyadic prohibition and order-minimality.  The
  raw incidence count alone gives only `d>=2a`.

## 3. Edge count

### Theorem 3.1 — PROVED HERE

`m <= 2n-2`.

**Proof.**  Theorem 2.2 in particular gives a vertex `v` of degree three.  Every
subgraph of `G-v` is a proper subgraph of `G`, so `G-v` is 2-degenerate.  A simple
2-degenerate graph on `N>=2` vertices has at most `2N-3` edges (delete a vertex of
degree at most two and induct, with the two-vertex base case).  Therefore

```
m-3 = |E(G-v)| <= 2(n-1)-3 = 2n-5,
```

which gives the claim.  QED

The proof uses neither connectedness of `G-v` nor an imported theorem.

### Corollary 3.2 — PROVED, ONE LITERATURE DEPENDENCY

Actually `m <= 2n-3`.

If equality `m=2n-2` held, Section 1 says that `G` has no proper (not necessarily
induced) subgraph of minimum degree three.  Theorem 1.4 of Narins, Pokrovskiy and
Szabó, *Graphs without proper subgraphs of minimum degree 3 and short cycles*,
Combinatorica 37 (2017), 495–519, states that every `n`-vertex, `(2n-2)`-edge graph
with that property is pancyclic.  In particular it has a `C4`, contradiction.

Primary source: <https://arxiv.org/abs/1408.5289>, Theorem 1.4.  This published
theorem is the sole external dependency in Corollary 3.2.  It is **not** needed for
the requested `m<=2n-2` result.

## 4. Exact three-pole gluing theorem

### Definitions

A **connected cubic three-pole** is a tuple

```
P = (P; p1,p2,p3)
```

where `P` is a finite connected simple graph, the three named terminals are distinct
and have degree two in `P`, and every other vertex has degree three.  It is *safe* if
it has no dyadic cycle.  For `1 <= i < j <= 3`, let

```
L_P(i,j) = {length(R) : R is a simple pi-pj path in P}.
```

Let `Q=(Q;q1,q2,q3)` be a vertex-disjoint connected cubic three-pole and let
`sigma` be a permutation of `{1,2,3}`.  Define `P glue_sigma Q` by adding the three
edges `pi q_{sigma(i)}`.

### Theorem 4.1 (three-pole gluing iff) — PROVED HERE

`P glue_sigma Q` is a connected simple cubic dyadic-free graph if and only if

1. `P` and `Q` are safe; and
2. for every `i<j`, every `r in L_P(i,j)`, and every
   `s in L_Q(sigma(i),sigma(j))`, the integer `r+s+2` is not dyadic.

**Proof.**  The glued graph is simple because the poles are vertex-disjoint and the
new edges have distinct endpoints.  Each terminal gains one edge, so it is cubic;
connectedness follows from connectedness of both poles.

Let `F` be the cut consisting of the three new edges.  Every cycle meets an edge cut
in an even number of edges, so a simple cycle meets `F` in zero or two edges.  If it
meets `F` in zero edges, it is wholly a cycle of `P` or wholly a cycle of `Q`.  If it
uses the two new edges incident with `pi,pj`, deleting those two edges from the cycle
leaves a simple `pi-pj` path in `P` and a simple
`q_{sigma(i)}-q_{sigma(j)}` path in `Q`.  Its length is therefore `r+s+2`.

Conversely, any such pair of terminal paths, together with its two joining edges,
is a simple cycle: the paths are individually simple and their vertex sets lie in
disjoint poles.  Thus the displayed list is an exhaustive and exact classification
of cycle lengths, proving both directions.  QED

### Caveats and useful corollaries

- The theorem as stated requires each pole connected.  A disconnected multipole
  needs an extra connectivity condition; no such generalization is silently used.
- If `K` is a simple cubic graph, `v` a non-cut vertex, and `P=K-v`, then `P` is a
  connected cubic three-pole.  It is safe exactly when `v` belongs to every dyadic
  cycle of `K`.
- The triangle is a safe three-pole with each terminal-pair spectrum `{1,2}`.
  Consequently replacing a non-cut vertex `v` of a cubic graph `K` by a triangle is
  dyadic-free exactly when `K-v` is safe and no cycle through `v` in `K` has length
  `2^k-1` or `2^k-2` (`k>=2`).  This follows because a cycle through `v` of length
  `ell` becomes cycles of lengths `ell+1` and `ell+2`.
- Conversely, in a cubic dyadic-free graph containing a triangle, its three external
  neighbors are distinct (a repeated neighbor creates a `C4` through the third
  triangle vertex) and pairwise nonadjacent (an external edge creates a `C4`).  Thus
  triangle contraction is simple and the preceding criterion is exact in reverse.

No literature result is used in Theorem 4.1.

## 5. Frozen computation attached to the theorem

Status: **COMPUTATIONALLY CHECKED, CONDITIONAL SCOPE**.

### Why the hard-core input suffices for safe deleted-vertex poles

In a cubic graph, two edge-disjoint simple cycles cannot share a vertex: sharing a
vertex would require four distinct incident cycle edges there.  Hence two
edge-disjoint dyadic cycles are vertex-disjoint and have empty vertex intersection.
Therefore a cubic graph with a vertex lying on every dyadic cycle must occur among
the upstream `no_pair_examples` records (graphs with no edge-disjoint pair of
dyadic cycles).  This reduction is proved here.  Completeness/canonicity of the
upstream connected-cubic census and of those records is not reproved by this scan.

### Results

1. All 645 order-22 hard-core records have empty dyadic vertex core.  Hence none
   yields a safe deleted-vertex three-pole.
2. Across orders 4,6,...,22, the 1,389 hard-core records have four graphs with
   nonempty dyadic vertex core and nine safe marked vertices: four poles of order 3,
   four of order 7, and one of order 15.  They give four labelled/canonical terminal
   path signatures.  All 10 unordered signature pairs and all six terminal
   bijections (60 tests) are incompatible; no glued counterexample results.
3. For every one of the `645 * C(33,2) = 340,560` distinct-edge-pair insertions into
   the order-22 hard core, the resulting order-24 cubic graph has empty dyadic vertex
   core.  This is the complete operation family, not the complete order-24 cubic
   census.

The cycle enumerator checks all simple cycles at dyadic lengths not exceeding the
graph order.  It may stop once a running vertex intersection becomes empty; the
reported “cycles seen until decision” is therefore not a total cycle count.

### Frozen artifact hashes

```
ABE5AD941D852710A879F4D7F62621A799A58C63A158563FA1D25CE5721E1DF2  three_pole_scan.py
EB66AF5F78D1A8942FB7E1299CA4E3E8F61C173FC3803E4123BCCE25C085335E  three_pole_scan.json
B6A2364F23A169DAD720EFB7D0526AF4B378DD5D37CA106DABC7C10A78EBC4CB  three_pole_scan_through22.json
751EA1CF18FCC71C6AB6EABEC79A6AEECCE63F2216A0691FD5807854A1C1C1FB  pair_insertion_vertex_poles.py
C55CEDD9D0096EB81FFFC69940AA9EADA1C763742F91A8F552F5731644363F5A  pair_insertion_vertex_poles.json
```

Each JSON output also embeds the SHA-256 hash of every upstream input file.  Run
`verify_frozen_scans.ps1` for hash, schema, count, completeness, and null-candidate
checks.  Run `rerun_scans.ps1` to regenerate all three outputs; on the current
machine the slow exhaustive operation replay took about 205 seconds.
