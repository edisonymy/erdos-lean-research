# Pure-triangular chromatic gate at order 50

## Audited statement

Let `G` be a `K4`-free graph on `n` vertices in which every edge lies in a
triangle.  If `beta(G) <= h-1`, then

```text
chi(G) <= q := 3 ceil(h/4),
beta(G) >= ceil(2n/q),
n <= (h-1)q/2.
```

Here `beta` is the packet's ambient parameter: the largest vertex set that
contains no nontrivial ambient maximal clique.

At `(n,h)=(50,11)`, `q=9` and

```text
beta(G) >= ceil(100/9) = 12,
```

contradicting `beta(G)<=10`.  Consequently every order-50 `K4`-free graph
with `beta<=10` has at least one ambient-maximal edge, equivalently an edge
lying in no triangle.

The strongest audited corollary in this note is that its
ambient-maximal-edge graph has a matching of size at least three.

## Independent proof audit

Because `G` is `K4`-free, every open neighborhood `N(v)` is triangle-free.
Because every edge is triangular, `G` has no ambient-maximal two-clique.
Thus `N(v)` contains no nontrivial ambient maximal clique and is admissible.
It follows that

```text
Delta(G) <= beta(G) <= h-1.
```

Lovasz's maximum-degree decomposition theorem says that if nonnegative
integers `d_1,...,d_t` satisfy

```text
sum_i (d_i+1) >= Delta(G)+1,
```

then the vertices can be partitioned into induced parts of maximum degrees
at most `d_i`.  Take

```text
t = ceil((Delta(G)+1)/4),    d_i=3 for every i.
```

Every part remains `K4`-free.  Each connected component of a part is
3-colorable by Brooks' theorem: the only maximum-degree-three complete
exception is `K4`, which is excluded, and an odd-cycle exception still uses
only three colors.  Therefore

```text
chi(G) <= 3 ceil((Delta(G)+1)/4) <= 3 ceil(h/4) = q.
```

In a proper coloring with at most `q` colors, the two largest color classes
have union of size at least `ceil(2n/q)`.  Their union is bipartite and hence
triangle-free.  In a `K4`-free graph with no maximal edge, the only
nontrivial ambient maximal cliques are triangles, so this union is
admissible.  This proves the beta lower bound and the displayed inequality.

## Matching-size-two strengthening

Let `M` be the graph of ambient-maximal edges of an arbitrary order-50
`K4`-free graph `G` with `beta(G)<=10`, and put `F=G-M`.  Every edge of `F`
lies in a triangle of `G`; all three edges of that triangle are nonmaximal,
so the triangle remains in `F`.  Thus every `F`-edge is triangular.

For every vertex `v`, `N_F(v)` is ambient-admissible in `G`: it contains no
triangle by `K4`-freeness, and any edge inside it lies in a triangle with
`v`, so it is not ambient-maximal.  Hence `Delta(F)<=beta(G)<=10`.  Applying
the preceding Lovasz/Brooks argument to `F` gives `chi(F)<=9`.  The two
largest `F`-color classes have a union `S` of order at least 12.  Every
triangle of `G` uses only nonmaximal edges and therefore lies in `F`, so `S`
is triangle-free in `G` as well.

If `C` is a vertex cover of `M[S]`, then `S-C` contains neither a triangle
of `G` nor an ambient-maximal edge.  Since `G` is `K4`-free, it is
ambient-admissible.  Therefore

```text
|S| - tau(M[S]) <= beta(G) <= 10,
tau(M[S]) >= |S|-10 >= 2.
```

The graph `M[S]` is triangle-free: three maximal edges forming a triangle
would make each of them triangular.  A simple graph with no two
vertex-disjoint edges is pairwise intersecting; such an edge family is a
star or a triangle.  The triangle alternative is excluded for `M[S]`, so
matching number at most one would imply a one-vertex cover, contradicting
`tau(M[S])>=2`.  Thus `M[S]`, and hence `M`, contains two vertex-disjoint
ambient-maximal edges.

## Matching-size-three strengthening

The argument has the following finite, non-asymptotic form.  Let `G` be
`K4`-free on `n` vertices with `beta(G)<=b`, let `M` be its maximal-edge
graph, and define

```text
q = 3 ceil((b+1)/4),
P_q(b) = b + (q-2) floor(b/2).
```

Then

```text
nu(M) >= ceil((n-P_q(b))/2).
```

Indeed, `F=G-M` has a proper `q`-coloring by the already audited argument.
If `r=nu(M)`, the `2r` endpoints `C` of a maximum matching cover `M`.
For the color-class remainders `x_i=|C_i-C|`, every two-class union is
ambient-admissible, so `x_i+x_j<=b`.  After sorting,

```text
x_2 <= floor(b/2),
sum_i x_i <= x_1+(q-1)x_2
             <= b+(q-2)floor(b/2) = P_q(b).
```

Since `sum_i x_i=n-2r`, the bound follows.  For `(n,b)=(50,10)`, this gives
`q=9`, `P_q=45`, and `nu(M)>=3`.  As a second exact arithmetic check,
`(n,b)=(59,11)` gives `q=9`, `P_q=46`, and `nu(M)>=7`.  These are finite
instances; no asymptotic tail is claimed.

Keep `M`, `F`, and a proper nine-coloring `C_1,...,C_9` of `F`.  Empty
classes may be appended if fewer than nine colors are used.  Suppose for a
contradiction that `nu(M)<=2`.  The endpoints `C` of any maximal matching
of `M` form a vertex cover of `M`, and the assumption gives `|C|<=4`.

Put

```text
a_i = |C_i|,    c_i = |C intersect C_i|,    b_i = a_i-c_i.
```

For every `i<j`, the set `(C_i union C_j)-C` contains no `M`-edge because
`C` covers `M`.  It contains no triangle of `G` because every `G`-triangle
lies in `F`, while two proper `F`-color classes induce a bipartite graph.
It is therefore ambient-admissible, and

```text
b_i+b_j <= beta(G) <= 10.
```

Relabel so that `b_1>=...>=b_9`.  Then `b_1+b_2<=10` and `b_2<=5`, whence

```text
sum_i b_i <= b_1+8b_2 <= 10+7b_2 <= 45.
```

On the other hand,

```text
sum_i b_i = 50-|C| >= 46,
```

a contradiction.  Thus `nu(M)>=3`.  This analytic argument supersedes the
matching-size-two conclusion for the next-run constraint; the preceding
12-set cover argument remains a valid intermediate check.

## Three-edge transversal/prism corollary

Take three vertex-disjoint maximal edges `e_1,e_2,e_3`.  Between the two
endpoints of `e_i` and the two endpoints of `e_j`, the cross-edge graph is a
matching: a vertex adjacent to both ends of a maximal edge would put that
edge in a triangle.

Choosing one endpoint from each `e_i` is a three-variable Boolean problem.
A perfect cross matching forbids two complementary endpoint pairs and hence
imposes one XOR relation.  A one-edge cross matching forbids only one pair.
If exactly two cross graphs are perfect, their relations leave two
complementary global choices, and the remaining one-edge constraint can
kill at most one.  With at most one perfect cross graph, the at most two or
three remaining one-pair prohibitions likewise cannot cover all choices.
Thus failure of an independent transversal forces all three cross graphs to
be perfect matchings.

The three XOR relations are inconsistent exactly when their parity around
the three pairs is odd.  Flipping endpoint labels normalizes this case to
two disjoint three-cycles joined by the original three maximal edges: the
six endpoints induce a triangular prism whose vertical matching is in `M`.
Both three-cycles are ambient-maximal triangles because `G` is `K4`-free.
Therefore every three-edge matching in `M` has an independent endpoint
transversal unless its endpoints induce this odd-parity prism.

This is a structural corollary, not an additional live-run constraint.

The decomposition statement was cross-checked against the classical Lovasz
theorem, originally: L. Lovasz, *On decomposition of graphs*, Studia
Scientiarum Mathematicarum Hungarica 1 (1966), 237-238.  No stronger
Borodin-Kostochka/Catlin/Lawrence bound is used.

## Constraint status

This is a sound **next-run** constraint only.  If a future exact order-50
CEGAR encoding has an exact Boolean `M_uv` for "`uv` is an edge in no
triangle", it may add the stronger constraint

```text
OR over all three-edge matchings {(u,v),(x,y),(z,w)}
    (M_uv AND M_xy AND M_zw).
```

No live inherited CEGAR process was mutated or restarted to add this gate.

The arithmetic replay is `audit_pure_triangular_gate.py`; a `PASS` result
checks `q=9`, `ceil(100/9)=12`, the intermediate cover lower bound 2, and
the final `46>45` matching contradiction.  It is a numeric audit, not a
substitute for the proof above.
