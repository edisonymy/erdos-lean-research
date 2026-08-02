# Proof and structural consequences for Erdős problem 151

## Definitions

Let `M(G)` be the family of inclusion-maximal cliques of `G` with at least two
vertices, and define

```text
beta(G) = max {|S| : S subset V(G), and C is not a subset of S for every C in M(G)}.
```

Let `tau(G)` be the minimum size of a vertex set meeting every member of
`M(G)`.  Taking complements of vertex sets gives the exact identity

```text
tau(G) = |V(G)| - beta(G).
```

Thus problem 151 asks whether `beta(G) >= H(n)` for every graph on `n`
vertices.  Here `H(n)` is the minimum independence number of a triangle-free
graph on `n` vertices, equivalently

```text
H(n) = max {k : R(3,k) <= n}.
```

All occurrences of *maximal* below mean inclusion-maximal, not
maximum-cardinality.

## Lemma 1: neighborhoods are avoiding

For every vertex `v`,

```text
beta(G) >= d(v).
```

Indeed, `N(v)` contains no member of `M(G)`: every clique contained in `N(v)`
can be extended by `v`.

In particular, `beta(G) >= Delta(G)`.  Also `beta(G) >= alpha(G)`, since an
independent set contains no nontrivial clique.

## Lemma 2: the independent-set recurrence

For every independent set `I`,

```text
beta(G) >= |I| + beta(G - N[I]).                 (1)
```

Let `F=G-N[I]`, and take an avoiding set `S` of size `beta(F)` in `F`.  The set
`I` is independent and anticomplete to `S`.  Hence a nontrivial clique
contained in `I union S` must lie entirely in `S`.  If such a clique were
maximal in `G`, it would also be maximal in the induced graph `F`, because any
vertex of `F` extending it would extend it in `G`.  This contradicts the
choice of `S`, so `I union S` is avoiding and proves (1).

Notice that the proof uses only

```text
maximal in G and contained in F  =>  maximal in F.
```

It does not use the false converse.

This recurrence, including the required one-way maximality implication, has
also been checked in Lean 4/mathlib.  The formalization is deliberately scoped
to Lemma 2 and is available in
[`lean/Erdos151Recurrence.lean`](lean/Erdos151Recurrence.lean); it does not
formalize the remaining argument in this note.

## Theorem: the conjecture holds through order 17

The exact thresholds

```text
R(3,2)=3,  R(3,3)=6,  R(3,4)=9,  R(3,5)=14,  R(3,6)=18
```

give `H=1` on orders 1--2, `H=2` on 3--5, `H=3` on 6--8, `H=4` on 9--13,
and `H=5` on 14--17.

For `n<=2`, a singleton is avoiding.  For `3<=n<=5`, either
`Delta(G)>=2`, in which case Lemma 1 applies, or `Delta(G)<=1`, in which case
an independent pair exists.

For `6<=n<=8`, Lemma 1 settles `Delta(G)>=3`.  If `Delta(G)<=2`, the graph is
a disjoint union of paths and cycles.  It has an independent set of size at
least three except for the only possible `alpha=2` case, `n=6` and
`G=2 K_3`.  In that exceptional graph, taking two vertices from each triangle
is an avoiding set of size four.  Thus `beta(G)>=H(n)` through order eight.

At `n=9`, Lemma 1 settles `Delta(G)>=4`.  Otherwise every degree is at most
three.  A cubic graph cannot have odd order, so some vertex `v` has degree at
most two.  The residual `G-N[v]` has between six and eight vertices, and (1)
gives

```text
beta(G) >= 1 + 3 = 4 = H(9).
```

For `10<=n<=13`, use strong induction.  Lemma 1 settles `Delta(G)>=4`.
Otherwise, for any vertex `v`, the residual has at least `n-4>=6` vertices
and smaller order, so its beta is at least three.  Equation (1) gives
`beta(G)>=4=H(n)`.

For `14<=n<=17`, Lemma 1 settles `Delta(G)>=5`.  Otherwise the residual has
at least `n-5>=9` vertices and smaller order, so its beta is at least four.
Equation (1) gives `beta(G)>=5=H(n)`.  This completes the proof.

## General minimal-counterexample restriction

Suppose `G` is a smallest counterexample, put `n=|V(G)|` and `h=H(n)`, and let
`I` be an independent `r`-set with `1<=r<h`.  Since `beta(G)<=h-1`, (1) gives

```text
beta(G-N[I]) <= h-r-1.
```

Minimality gives `H(n-|N[I]|) <= h-r-1`.  By the Ramsey characterization of
`H`,

```text
|N[I]| >= n - R(3,h-r) + 1.                     (2)
```

Taking `r=1` and combining (2) with Lemma 1 yields

```text
n - R(3,h-1) <= delta(G) <= Delta(G) <= h-1.    (3)
```

Since `R(3,h)<=n`, (3) implies that a smallest counterexample can occur only
in the interval

```text
R(3,h) <= n <= R(3,h-1) + h - 1.               (4)
```

The parameter `beta` is additive on disjoint unions.  The function `H` is
subadditive: disjointly unite triangle-free extremizers on `a` and `b`
vertices to see `H(a+b)<=H(a)+H(b)`.  Therefore a smallest counterexample is
connected.

## Reduction of the first live core: order 18

The theorem above and (4) show that 18 is the first order at which a
counterexample can exist.  Here `h=H(18)=6`.  Any such graph `G` must satisfy:

1. `G` is connected and `beta(G)<=5`.
2. Every degree is four or five, by (3).
3. `alpha(G)<=5` and the number of degree-four vertices is even.
4. For every independent pair `{u,v}`, (2) gives
   `|N[u] union N[v]|>=10`.  Thus nonadjacent degree pairs `(4,4)`, `(4,5)`,
   and `(5,5)` have at most zero, one, and two common neighbors respectively.
5. Every independent triple has closed-neighborhood union of size at least
   13, and every independent four-set has union of size at least 16.
6. Every degree-five vertex has eccentricity two.  If `x` is a nonneighbor of
   such a vertex `v`, the six-set `N(v) union {x}` must contain a nontrivial
   maximal clique.  Nothing lying wholly in `N(v)` is maximal because `v`
   extends it, so that clique contains `x`, giving a common neighbor of `v`
   and `x`.
7. `omega(G)<=4`.  A `K_6` would be a connected component because
   `Delta(G)<=5`.  If `M` were a `K_5`, choose four vertices `P` of `M`.
   Each vertex of `P` has at most one neighbor outside `M`, so at least nine
   of the 13 outside vertices are anticomplete to `P`; two of those nine are
   nonadjacent because `Delta(G)<=5`.  Adding that pair to `P` gives a six-set
   containing no maximal clique: cliques in `P` extend by the omitted vertex
   of `M`, and there are no nontrivial mixed cliques.
8. `G` is not 4-regular.  If it were, fix `v`.  Equality in the recurrence
   forces the 13-vertex residual `G-N[v]` to have beta four.  Applying the
   already-proved order bounds and Lemmas 1--2 inside the residual forces it
   to be 4-regular.  Hence there are no edges from the residual to `N(v)`,
   while the four vertices of `N(v)` must form a `K_4` to attain degree four.
   Then `N[v]` is a `K_5` component, contradicting connectedness.

These conditions in fact suffice to obtain a contradiction.

## Theorem: no order-18 counterexample exists

Assume that `G` is an order-18 counterexample.  The preceding reduction gives
`beta(G)<=5`.  The 4-regular case is excluded by item 8 above, so
`Delta(G)=5`; Lemma 1 then gives `beta(G)=5`.

### Mixed degree sequences

Let `p` be the number of degree-five vertices.  The handshake lemma makes `p`
even.  Suppose a degree-four vertex `u` exists, and put

```text
s = |N(u) intersect V_5|,
t = e(G[N(u)]),
z = number of isolated vertices of G[N(u)].
```

The number of nonbacktracking length-two walks starting at `u` is

```text
sum_{a in N(u)} (d(a)-1) = 12+s.
```

Walks ending back in `N(u)` contribute `2t`.  A nonadjacent degree-four
vertex has no common neighbor with `u`, by the `(4,4)` cap.  Every
nonadjacent degree-five vertex has exactly one: the `(4,5)` cap gives at most
one, while the degree-five eccentricity property gives at least one.  There
are `p-s` such vertices.  Therefore

```text
12+s = 2t+(p-s),        t = 6+s-p/2.             (5)
```

For each of those `p-s` degree-five vertices `v`, let `a` be its unique common
neighbor with `u`.  Apply the six-set argument to `N(v) union {u}`.  The edge
`ua` must be a maximal two-clique, hence it lies in no triangle.  Equivalently,
`a` is isolated in `G[N(u)]`.  Each such `a` can account for at most four
vertices `v`, because it has at most four neighbors besides `u`.  Thus

```text
p-s <= 4z,              t <= binom(4-z,2).       (6)
```

The `4-s` degree-four neighbors of `u` form a clique: two nonadjacent ones
would share the common neighbor `u`, contradicting the `(4,4)` cap.  Hence

```text
t >= binom(4-s,2).                                  (7)
```

Also `s>=1`, since `s=0` would make `N[u]` a `K_5`, contrary to
`omega(G)<=4`.  Substituting the even possibilities `p=2,4,...,16` and
`1<=s<=min(4,p)` into (5)--(7), with
`z>=ceil((p-s)/4)`, leaves no feasible case:

| `p` | `s=1` | `s=2` | `s=3` | `s=4` |
|---:|:---:|:---:|:---:|:---:|
| 2  | `6/[3,3]` | `7/[1,6]` | -- | -- |
| 4  | `5/[3,3]` | `6/[1,3]` | `7/[0,3]` | `8/[0,6]` |
| 6  | `4/[3,1]` | `5/[1,3]` | `6/[0,3]` | `7/[0,3]` |
| 8  | `3/[3,1]` | `4/[1,1]` | `5/[0,1]` | `6/[0,3]` |
| 10 | `2/[3,0]` | `3/[1,1]` | `4/[0,1]` | `5/[0,1]` |
| 12 | `1/[3,0]` | `2/[1,0]` | `3/[0,0]` | `4/[0,1]` |
| 14 | `0/[3,0]` | `1/[1,0]` | `2/[0,0]` | `3/[0,0]` |
| 16 | `-1/[3,0]` | `0/[1,0]` | `1/[0,0]` | `2/[0,0]` |

Each entry is `t/[lower bound from (7), upper bound from (6)]`; every entry
fails.  Consequently no degree-four vertex exists and `G` is 5-regular.

### The 5-regular case

For a vertex `v`, put `t_v=e(G[N(v)])`.  The 12 nonneighbors of `v` each have
one or two common neighbors with `v`.  If `q_v` of them have two, counting the
20 nonbacktracking length-two walks from `v` gives

```text
20 = 2t_v + (12-q_v) + 2q_v,
q_v = 8-2t_v,
number with a unique common neighbor = 4+2t_v.     (8)
```

Let `L` be the spanning graph whose edges are the edges of `G` contained in no
triangle, and let `ell_v=d_L(v)`.  A neighbor of `v` is isolated in the link
`G[N(v)]` exactly when its edge to `v` lies in `L`, so `ell_v` is the number
of isolated link vertices.

If a nonneighbor `x` has unique common neighbor `a` with `v`, applying the
six-set argument in both orientations shows that both `va` and `ax` lie in
`L`.  Assign `x` to its unique `a`.  This gives distinct `L`-neighbor slots
of `a` other than `v`, and hence

```text
4+2t_v <= sum_{a in N_L(v)} (ell_a-1) <= 4 ell_v. (9)
```

All `t_v` link edges lie among the `5-ell_v` nonisolated link vertices, so

```text
t_v <= binom(5-ell_v,2).                           (10)
```

Equation (8) gives `t_v<=4`.  For `t_v=3` or `4`, (9) forces
`ell_v>=3`, whereas (10) permits at most one link edge, a contradiction.
For `t_v=0,1,2`, (9)--(10) give exactly

```text
t_v=0:  G[N(v)] = 5K_1,
t_v=1:  G[N(v)] = K_2 + 3K_1,
t_v=2:  G[N(v)] = P_3 + 2K_1.
```

In the last line, the only other two-edge link, `2K_2+K_1`, has only one
isolated vertex and violates (9).

Thus every vertex belongs to at most two triangles; if it belongs to two,
those triangles share an edge.  It follows that the components of the
triangle hypergraph are vertex-disjoint isolated triangles and diamonds
(`K_4` minus an edge).  Indeed, after two triangles share an edge, any third
triangle meeting that diamond would force some vertex into three triangles.

Choose one edge from each isolated triangle and the shared edge from each
diamond.  Since the triangle components are vertex-disjoint, the chosen edges
form a matching `M` meeting every triangle of `G`.  Define the auxiliary graph

```text
J = (V(G), E(L) union M).
```

The graph `J` is triangle-free.  Any triangle in `J` would be a triangle in
`G`; it cannot contain an edge of `L`, and if all three edges lay in `M` it
would contradict that `M` is a matching.

Since `R(3,6)=18`, `J` has an independent six-set `S`.  The maximal
two-cliques of `G` are exactly the edges of `L`, so `S` contains none.  Every
clique of size at least three contains a triangle, and every triangle contains
an edge of `M`, so `S` contains no such clique either.  Therefore `S` contains
no member of `M(G)`, giving `beta(G)>=6`, the final contradiction.

## Corollary: the conjecture holds through order 22

The exact value `R(3,7)=23` gives `H(n)=6` for `18<=n<=22`.  If a first
counterexample occurred in this range after order 18, the interval (4) would
force

```text
n <= R(3,5)+5 = 19.
```

At `n=19`, (3) forces every degree to equal five, impossible by the handshake
lemma on an odd number of vertices.  Hence no counterexample exists through
order 22.  The next orders admitted by (4) are 23 and 24.
