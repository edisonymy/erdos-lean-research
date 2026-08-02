# Proof and structural consequences for Erdős problem 151

## Definitions

Let `M(G)` be the family of inclusion-maximal cliques of `G` with at least two
vertices, and define

```text
beta(G) = max {|S| : S subset V(G), and C is not a subset of S for every C in M(G)}.
```

Taking complements of vertex sets gives the exact identity

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

## Theorem: the conjecture holds through order 17

The exact thresholds

```text
R(3,3)=6,  R(3,4)=9,  R(3,5)=14,  R(3,6)=18
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

## The first live core: order 18

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

These are necessary conditions, not a proof that an order-18 counterexample
exists.  They define the campaign's next exact construction target.
