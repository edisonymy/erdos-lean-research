# Root audit of the two-class gate

**Verdict:** the two-class theorem and maximal-edge burden lemma are valid.
Two advertised consequences in the discovery log were not valid and have
been withdrawn there: the claimed all-`n >= 200` tail, and the use of isolated
test points such as `(87,15)` or `(98,16)` as though the displayed second
coordinate were necessarily `H(n)`.

## Definitions

`beta(G)` is the largest cardinality of a vertex set containing no nontrivial
inclusion-maximal clique of `G`.  A *maximal edge* is an edge contained in no
triangle.  A graph is *pure-3* here when it is `K4`-free and every edge lies in
a triangle; its nontrivial maximal cliques are then exactly its triangles.

## Audited theorem

Let `G` be an `n`-vertex pure-3 graph and suppose `beta(G) <= h-1`.  Then

```text
n <= (h-1) q / 2,       q = 3 ceil(h/4).
```

Proof reconstruction:

1. Every open neighbourhood is admissible, because a clique contained in
   `N(v)` extends by `v`.  Hence `Delta(G) <= beta(G) <= h-1`.
2. Lovasz's vertex-decomposition theorem partitions `V(G)` into
   `ceil((Delta+1)/4)` induced subgraphs of maximum degree at most three.
3. Every component of each part is 3-colourable by Brooks: the only
   maximum-degree-three complete exception is `K4`, which is excluded, and
   the odd-cycle exception still uses only three colours.  Thus
   `chi(G) <= 3 ceil((Delta+1)/4) <= q`.
4. The union of the two largest proper colour classes has at least
   `ceil(2n/q)` vertices and is bipartite.  It contains no triangle and,
   because every edge of `G` lies in a triangle, no maximal edge.  It is
   therefore admissible.  So `ceil(2n/q) <= beta(G) <= h-1`, giving the
   displayed inequality.

The proof does not need the exploratory DSATUR samples.

## Correct Ramsey use

Write `B(h)=floor((h-1) 3 ceil(h/4)/2)`.  The theorem excludes a pure-3
least counterexample at the jump `R(3,h)` only when a rigorous lower bound
on `R(3,h)` exceeds `B(h)`.  Revision 18 (24 April 2026) of Radziszowski's
*Small Ramsey Numbers* gives

```text
47 <= R(3,11) <= 50,   B(11)=45;
53 <= R(3,12) <= 59,   B(12)=49;
61 <= R(3,13) <= 68,   B(13)=72;
67 <= R(3,14) <= 77,   B(14)=78;
74 <= R(3,15) <= 87,   B(15)=84;
82 <= R(3,16) <= 97,   B(16)=90.
```

Thus the gate unconditionally excludes pure-3 jump witnesses for `h=11,12`.
It does not presently exclude the jumps for `h=13,14`; for `h=15,16` it is
conditional on the unknown exact Ramsey number exceeding 84 or 90.  Since
`R(3,h)=Theta(h^2/log h)`, the threshold of order `3h^2/8` is asymptotically
too high, so this argument is not a large-order solution.

## Primary-source refinement

Borodin and Kostochka (1977), and independently Catlin and Lawrence, proved
the stronger finite-degree bound

```text
chi(G) <= floor(3(Delta(G)+2)/4)
```

for `K4`-free graphs.  The Borodin--Kostochka paper gives the specialization
directly; Catlin's 1978 paper states the general bound
`chi(G) <= r(Delta+2)/(r+1)` for graphs containing no `K_{r+1}`.  Applying
the integer form with `Delta<=h-1` improves the pure-3 threshold to

```text
B*(h)=floor((h-1) floor(3(h+1)/4) / 2).
```

For `h=13`, `chi<=10` and `B*(13)=60`; the rigorous lower bound
`R(3,13)>=61` therefore excludes the pure-3 jump face.  For `h=14`,
`chi<=11` and `B*(14)=71`; the known lower bound is only `R(3,14)>=67`, so
the argument leaves possible jump orders 67 through 71.  The discovery
note's claim that the stronger theorem closes `h=14` used the upper bound
`R(3,14)<=77` in the wrong direction and is withdrawn.  Primary-source
verification therefore closes the `h=13` pure-3 strip only, not both
`h=13,14`.

## Maximal-edge burden

For any `K4`-free `G` with `beta(G) <= h-1`, let `M` be the graph formed by
the maximal edges.  Removing `M` changes no triangle, so `G-M` is pure-3.
For every triangle-free induced set `S` of `G`, every vertex cover `C` of
`M[S]` leaves `S-C` with neither a triangle nor a maximal edge.  Hence

```text
tau(M[S]) >= |S|-(h-1).
```

At `(n,h)=(50,11)`, the two-class theorem applied to `G-M` gives a
triangle-free 12-set; every such 12-set has maximal-edge vertex-cover number
at least two.  In particular every `K4`-free 50-vertex graph with
`beta(G)<=10` has at least one maximal edge.  This is a sound constraint for
a future exact search.  It has not been injected into the already-running
CEGAR process and is not a full #151 result.

## Sources and priority boundary

- L. Lovasz, *On decomposition of graphs*, Studia Scientiarum Mathematicarum
  Hungarica 1 (1966), 237--238.
- R. L. Brooks, *On colouring the nodes of a network*, Proceedings of the
  Cambridge Philosophical Society 37 (1941), 194--197,
  <https://doi.org/10.1017/S030500410002168X>.
- O. V. Borodin and A. V. Kostochka, *On an upper bound of a graph's
  chromatic number, depending on the graph's degree and density*, Journal of
  Combinatorial Theory, Series B 23 (1977), 247--250,
  <https://doi.org/10.1016/0095-8956(77)90037-5>.
- P. A. Catlin, *Another bound on the chromatic number of a graph*, Discrete
  Mathematics 24 (1978), 1--6,
  <https://doi.org/10.1016/0012-365X(78)90167-X>.
- S. P. Radziszowski, *Small Ramsey Numbers*, revision 18 (24 April 2026),
  <https://doi.org/10.37236/21>.

The chromatic inequality is a direct standard corollary of Lovasz plus
Brooks and should not be presented as novel.  The application to `beta` and
maximal edges may be useful for #151, but no priority claim has been audited.
