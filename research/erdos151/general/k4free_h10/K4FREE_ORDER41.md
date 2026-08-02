# The global K4-free lane at the h=10 jump

**Status (2 August 2026; independently audited).**  This note proves the
unconditional order-41 statement

`G is K4-free and |V(G)|=41  ==>  beta(G)>=10`.

Thus it analytically excludes the `omega(G)<=3` lane at order 41 without
assuming that order 40 has already been settled.  It does not exclude the
conditional order-40 lane.  The proof keeps the ambient graph `G` separate
from an edge-minimal arrowing core `Q`.

## Standing hypotheses and conventions

Suppose for a contradiction that `G` is a `K4`-free graph on 41 vertices
with `beta(G)<=9`.  Since `R(3,10)<=41`, the Folkman reduction implies
`G -> (3,3)`.  Also

`Delta(G)<=9` and `alpha(G)<=9`.

Only inclusion-maximal cliques of size at least two count in the definition
of admissibility.  Choose a subgraph `Q` of `G`, without isolated vertices,
which is inclusion-minimal subject to `Q -> (3,3)`.  Here `Q` is not assumed
induced.  Minimality gives:

- every `Q`-edge lies in at least two `Q`-triangles;
- `chi(Q)>=6`;
- `Q` is connected.

The first item follows by coloring `Q-e` and extending across `e`; the third
follows because an arrowing component would otherwise be a proper arrowing
subgraph.

We use the following published local theorem.

> **Bikov, Theorem 8.2.**  If a minimal `(3,3)`-Ramsey graph has clique
> number three, then its minimum degree is at least eight.  If a vertex has
> degree eight, its neighborhood is one of the seven displayed graphs
> `N_{8.1},...,N_{8.7}`.

Source: Aleksandar Bikov, *Small minimal (3,3)-Ramsey graphs*, Theorem 8.2
and Figure 13, article page 18 (PDF page 19 in one-based numbering),
<https://arxiv.org/abs/1604.03716>.

The seven links have respectively `10,11,12,10,10,11,12` edges.  The
standard-library checker
`experiments/erdos151_siege/k4free_h10/check_k4free_order41.py` verifies
these counts directly from graph6 representatives and also verifies that
each representative is triangle-free and admits an obstructing edge
signing.  Completeness of the seven-link list is the cited part of Bikov's
theorem, not a claim made by the checker.

Consequently, since `Delta(Q)<=Delta(G)<=9`, every `v in V(Q)` has

`d_Q(v) in {8,9}` and `t_G(v)>=t_Q(v)>=10`.                 (1)

For degree eight this uses Bikov's seven links.  For degree nine it also
follows from the elementary spoke-coloring inequality
`t_Q(v)>=d_Q(v)+1`: every core edge lying in two core triangles makes the
link have minimum degree at least two; if its edge count equaled its vertex
count, the link would be a disjoint union of cycles.  Color `Q-v` without a
monochromatic triangle, orient each link cycle, and color the spoke entering
each link vertex opposite to the color of the entering link edge.  Every
triangle through `v` is then nonmonochromatic, extending the coloring to
`Q`, a contradiction.

## Two quantifier audits used below

### Open core neighborhoods are ambient-admissible

For every ambient vertex `v`, the open neighborhood `N_G(v)` is
ambient-admissible: every clique contained in `N_G(v)` extends by `v`, so it
cannot be an ambient-maximal clique.  Admissibility is downward hereditary.
Therefore, for `v in V(Q)`,

`S_v=N_Q(v) subseteq N_G(v)` is ambient-admissible.          (2)

This does not assume that `Q` is induced.  In the `K4`-free setting one may
also see (2) directly: `G[S_v]` has no triangle, and every edge in it extends
with `v`.  Ambient maximality, not maximality in `G[S_v]`, is being used.

### The outside anticomplete remainder has beta at most one

Put `R=V(G)\V(Q)`.  If `d_Q(v)=8`, let

`Y_v={x in R : x is anticomplete to N_Q(v)}`.

Then

`beta(G[Y_v])<=1`.                                        (3)

Indeed, an admissible pair in the induced graph `G[Y_v]` is also ambient-
admissible: an ambient-maximal clique contained in the pair would remain
maximal in every induced graph containing it.  Its anticomplete union with
the ambient-admissible eight-set `N_Q(v)` would be an ambient-admissible
10-set, contradicting `beta(G)<=9`.

Every graph on three vertices has an admissible pair under the nontrivial-
clique convention: use a nonedge if one exists; in `K3`, any two vertices
do not contain the induced graph's maximal triangle.  Hence (3) implies
`|Y_v|<=2`.  Since each of the eight core neighbors has at most one ambient
edge outside `Q`, at most eight vertices of `R` can see `N_Q(v)`.  Thus
`|R|<=10`.  If `d_Q(v)=9`, the same argument with the admissible nine-set
`N_Q(v)` shows directly that every vertex of `R` sees it, again giving
`|R|<=9`.  In particular `|V(Q)|>=31` at order 41.  This core-size bound is
valid but will be superseded by the argument below.

## The degree-nine obstruction

We prove a statement about ambient degree, not core degree.

**Lemma.** No vertex of `Q` has ambient degree nine.

**Proof.**  Suppose `v in V(Q)` and `d_G(v)=9`.  Put `S=N_G(v)`.  By (2),
`S` is an ambient-admissible nine-set.  For every nonneighbor `x` of `v`,
the 10-set `S union {x}` is not admissible.  A witnessing ambient-maximal
clique cannot lie in `S`, so it contains `x`.  It follows that

`c(v,x)=|N_G(v) intersect N_G(x)|>=1`.                     (4)

If `c(v,x)=1`, with unique common neighbor `a`, then the witnessing clique
is exactly the edge `xa`; hence `xa` is an ambient-maximal edge.

At most one nonneighbor can have unique common neighbor `a`, for each fixed
`a in S`.  Otherwise let `x,y` be two.  Maximality of `xa` forces `xy` to be
a nonedge (or `xay` would extend `xa`).  Both `x` and `y` are anticomplete
to `S\{a}`.  Therefore

`(S\{a}) union {x,y}`

is the anticomplete union of an admissible set and an independent pair, so
it is an admissible 10-set, a contradiction.  If `u` is the number of
nonneighbors having exactly one common neighbor with `v`, then

`u<=9`.                                                    (5)

There are `41-1-9=31` nonneighbors.  Counting nonbacktracking two-walks
from `v` which end at a nonneighbor gives, with `t=t_G(v)`,

`sum_{x notin N_G[v]} c(v,x)`
` = sum_{a in N_G(v)}(d_G(a)-1)-2t`
` <= 9*8-2t = 72-2t`.                                    (6)

By (4), the same sum is at least `u+2(31-u)=62-u`.  Combining
(1), (5), and (6) yields

`u>=2t-10>=10`,

contradicting `u<=9`.  This proves the lemma.  Notice that the routing
argument uses ambient maximal edges and never asserts that every ambient
edge belongs to `Q`.  QED

## Completion at order 41

By Bikov, `d_Q(v)>=8`, while the lemma rules out `d_G(v)=9`.  Hence

`d_Q(v)=d_G(v)=8` for every `v in V(Q)`.                   (7)

Thus no vertex of `Q` has an ambient edge outside `Q`; `Q` is an ambient
component of `G`, and `E(G[V(Q)])=E(Q)`.  Put `q=|V(Q)|` and
`r=41-q`.  The preceding outside-remainder argument gives `q>=31`.

Every edge of `Q` lies in at least two triangles, so there are no maximal
2-cliques in `Q`.  Since `Q` is `K4`-free, every triangle is maximal.
Therefore a vertex set of `Q` is admissible exactly when it induces no
triangle.

Brooks' theorem gives a proper coloring of the connected 8-regular graph
`Q` with at most eight colors: `Q` is neither a complete graph (`K4`-free)
nor an odd cycle.  Let the eight color classes be `C_1,...,C_8`, allowing
empty classes.  For every pair `i<j`, `C_i union C_j` induces a bipartite,
hence triangle-free, graph.  It is admissible in `Q`, so summing the 28
pair inequalities gives

`7q <= 28 beta(Q)`, or equivalently `q<=4 beta(Q)`.          (8)

Because `Q` is a component, `beta(G)=beta(Q)+beta(G[R])`.  If `r=0`, then
`q=41` and `beta(Q)<=9`, contradicting (8).  If `r` is 1 or 2, then the
nonempty graph `G[R]` has `beta(G[R])>=1`, so `beta(Q)<=8`, whereas
`q` is 40 or 39, again contradicting (8).  Finally, if `r>=3`, every graph
on at least three vertices has `beta>=2`: on any three vertices there is
an admissible pair, and induced-subgraph monotonicity lifts it to `G[R]`.
Thus `beta(Q)<=7`, while `q>=31`, contradicting (8) once more.

This contradiction proves `beta(G)>=10` for every `K4`-free order-41
graph.  In particular, the conclusion is independent of the unresolved
order-40 case.  Induced-subgraph monotonicity also gives `beta(G)>=10` for
every `K4`-free graph of order at least 41.

## What the same argument leaves at order 40

The order-40 discussion is conditional on `R(3,10)=40`.  Under that
condition, a counterexample has `beta(G)=9`: the upper bound is the
counterexample assumption and the lower bound follows from the verified
order-39 theorem by induced-subgraph monotonicity.  If instead
`R(3,10)=41`, order 40 still lies on the `H=9` plateau and is already
settled by that same monotonicity argument.

The last numerical step would also exclude an 8-regular order-40 graph:
two color classes have total size at least ten.  The degree-nine lemma,
however, loses exactly two units.  If `v in V(Q)` has ambient degree nine,
the same proof gives

`u>=2t_G(v)-12`, while still `u<=9`.                        (9)

Since (1) gives `t_G(v)>=10`, order 40 does not contradict (9).  It does
give the following exact residual conditions:

- at least one core vertex has ambient degree nine (otherwise `Q` is an
  8-regular ambient component; the additive-`beta` case split used in the
  order-41 completion excludes it here as well);
- every ambient-degree-nine core vertex satisfies `t_G(v)=10`;
- writing `k(v)=sum_{a in N_G(v)}(9-d_G(a))`, the sharpened count gives
  `u>=8+k(v)`, hence `k(v)<=1`: at least eight of its nine neighbors have
  ambient degree nine, and the remaining neighbor, if any, has degree eight;
- with `r=|V(G)\V(Q)|`, the audit above gives `0<=r<=10`, hence
  `30<=|V(Q)|<=40`;
- if `b` is the number of degree-nine vertices of `Q`, then for `r>=2`

  `10b <= (10-r)|V(Q)|`,                                   (10)

  and `b` is even.  Inequality (10) follows by counting, over `v in Q`,
  the distinct outside vertices seen by `N_Q(v)`: a degree-eight `v` sees
  at least `r-2`, a degree-nine `v` sees all `r`, and a degree-eight core
  vertex can carry at most one ambient edge outside `Q` and contributes to
  at most its eight core neighbors.

For order 40, `q=40-r`, (10) and parity give the following maxima:

| `r` | `q` | maximum even `b` from (10) |
|---:|---:|---:|
| 10 | 30 | 0 |
| 9 | 31 | 2 |
| 8 | 32 | 6 |
| 7 | 33 | 8 |
| 6 | 34 | 12 |
| 5 | 35 | 16 |
| 4 | 36 | 20 |
| 3 | 37 | 24 |
| 2 | 38 | 30 |

For `r=1`, the direct nonnegative version of the same incidence count gives
`9b<=8q`, hence the parity-adjusted bound `b<=34`; for `r=0` it gives no
improvement over `b<=40`.  Thus the two remaining integer rows are:

| `r` | `q` | maximum even `b` |
|---:|---:|---:|
| 1 | 39 | 34 |
| 0 | 40 | 40 |

The extremal `r=10,q=30` case is especially rigid.  Equality holds in the
incidence count: `Q` is 8-regular; every core vertex uses its one ambient
extra edge on `R`; and these boundary edges partition `V(Q)` into ten
fibers.  Each core neighborhood meets eight distinct fibers.  Within each
fiber, core vertices are pairwise at distance at least three (otherwise
open-neighborhood overlap, and for a core edge the two forced core triangles,
would make the incidence inequality strict).  Each fiber therefore has at
most `floor(30/9)=3` vertices, so all ten fibers have exactly three.  This is
a finite residual core case, not a contradiction.

A proof-grade order-40 search can consequently be limited to a connected
`K4`-free core `Q` on 30--40 vertices with degrees 8 or 9, every edge in at
least two core triangles, the marked-link condition, (9)--(10), followed by
at most ten ambient vertices and at most one non-core ambient edge incident
with each degree-eight core vertex.  The semantic checks `Q -> (3,3)` and
`beta(G)=9` remain necessary; the local conditions alone do not imply either.
