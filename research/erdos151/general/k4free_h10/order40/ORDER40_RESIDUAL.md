# The K4-free order-40 residual

**Status (2 August 2026): independently audited conditional theorem, released
for public expert review.**  Assuming `R(3,10)=40`, every
`K4`-free graph `G` on 40 vertices has `beta(G)>=10`.  If instead
`R(3,10)=41`, the order-40 instance of Erdős #151 asks only for
`beta(G)>=9`, which already follows from the verified through-order-39
theorem by induced-subgraph monotonicity.  Thus this note closes the
`K4`-free lane at order 40 for the purpose of #151, but does not settle the
clique-number-four or clique-number-five lanes.

The proof starts from the independently audited order-41 core note and
keeps an edge-minimal arrowing core `Q` separate from the ambient graph.
Its new ingredients are a fibre-pair admissibility bound and two rigid
equality arguments.

## 1. Standing conditional hypotheses

Suppose `R(3,10)=40` and, for a contradiction, that `G` is a `K4`-free
graph of order 40 with `beta(G)<=9`.  The verified order-39 theorem gives
`beta(G)=9`.  The Folkman reduction gives `G -> (3,3)`, and the usual jump
constraints give

`Delta(G)<=9`, `delta(G)>=4`, and `alpha(G)<=9`.                 (1)

Choose an inclusion-minimal arrowing subgraph `Q` without isolated
vertices.  Put

`q=|V(Q)|`, `R=V(G)-V(Q)`, and `r=|R|=40-q`.

The audited Bikov input and the two-walk argument give

- `d_Q(v) in {8,9}` for every `v in Q`;
- every core edge lies in at least two core triangles;
- if `d_G(v)=9`, then `t_G(v)=10` and
  `sum_{a in N_G(v)}(9-d_G(a))<=1`;
- `0<=r<=10`.

Let `b` be the number of core-degree-nine vertices.  For `x in R`, define

`B_x=N_G(x) intersect V(Q)`, and put `w_x=|B_x|`, `c=sum_x w_x`.

Every vertex of `B_x` has core degree eight and uses its only available
ambient incidence on `x`.  Hence the fibres `B_x` are pairwise disjoint and

`c<=q-b`.                                                       (2)

## 2. Fibre facts

### 2.1 Boundary rigidity

If `v in B_x`, then `d_Q(v)=8` and `d_G(v)=9`.  Bikov's link list gives
`t_Q(v)>=10`, whereas the order-40 degree-nine equality gives `t_G(v)=10`.
Consequently

- `t_Q(v)=10`;
- `x` is anticomplete to `N_Q(v)`;
- the cross-edge `vx` is ambient-maximal;
- `B_x` is independent in `Q`;
- `d_G(x)>=8`.

The last point follows from the deficiency sum at `v`: if `d_G(x)<=7`,
the single neighbor `x` already contributes at least two.

### 2.2 Core/outside incidence

For a core-degree-eight vertex `v`, at most two vertices of `R` are
anticomplete to `N_Q(v)`.  Otherwise an admissible pair in that remainder,
together with the ambient-admissible eight-set `N_Q(v)`, would give an
admissible ten-set.  For a core-degree-nine vertex, every vertex of `R`
sees `N_Q(v)`.

Count pairs `(v,x)` such that `N_Q(v) intersect B_x` is nonempty.  The
preceding paragraph gives the lower bound

`q(r-2)+2b`,

while each boundary vertex belongs to eight core neighborhoods.  Thus

`q(r-2)+2b <= 8c`.                                           (3)

If `s` is the number of nonempty fibres, then

`s>=r-2`.                                                     (4)

Indeed, this follows from any core-degree-eight vertex when `b=0`; if
`b>0`, a core-degree-nine vertex shows the stronger `s=r`.

### 2.3 The fibre-pair bound

For distinct `x,y in R`, the set `B_x union B_y` is triangle-free: both
fibres are independent and a triangle cannot be supported on only two
independent parts.  It is ambient-admissible.  Every edge of `Q` lies in a
core triangle, while a boundary vertex has no ambient incidence left for a
non-core edge.

Moreover, `B_x union B_y` is anticomplete to `R-{x,y}`.  An admissible set
in the induced graph on those `r-2` vertices remains ambient-admissible and
can therefore be united with the two fibres.  Let `h_m` denote the verified
lower bound for beta at order `m`; for `m<=8` the values used here are

`h_0=0`, `h_1=h_2=1`, `h_3=h_4=h_5=2`, and
`h_6=h_7=h_8=3`.

Since `beta(G)=9`, we obtain

`w_x+w_y <= P_r := 9-h_{r-2}`.                               (5)

### 2.4 The outside degree budget

If `w_x>0`, boundary rigidity gives `d_R(x)>=8-w_x`; if `w_x=0`, the
degree floor in (1) gives `d_R(x)>=4`.  Since `G[R]` is `K4`-free, Turán's
theorem yields

`4r+4s-c <= 2e(G[R]) <= 2 floor(r^2/3)`,

or

`c >= 4r+4s-2 floor(r^2/3)`.                                (6)

## 3. The exact arithmetic funnel

If `s` nonnegative integers are pairwise constrained by sum at most `P`,
their total is at most

- `0` for `s=0`;
- `P` for `s=1`;
- `s(P/2)` for even `P` and `s>=2`;
- `s floor(P/2)+1` for odd `P` and `s>=2`.

Combine this upper bound with (3), (4), and (6), for
`q=40-r` and `2<=r<=10`.  In the following table each entry is
`upper(c) / lower(c)` for `s=r-2,r-1,r`, respectively; the lower number is
the maximum of the `b=0` version of (3) and (6).  An entry is feasible only
when its left side is at least its right side.

| `r` | `P_r` | the three `upper/lower` entries |
|---:|---:|---|
| 2 | 9 | `0/6, 9/10, 9/14` |
| 3 | 8 | `8/10, 8/14, 12/18` |
| 4 | 8 | `8/14, 12/18, 16/22` |
| 5 | 7 | `10/16, 13/20, 16/24` |
| 6 | 7 | `13/17, 16/20, 19/24` |
| 7 | 7 | `16/21, 19/21, 22/24` |
| 8 | 6 | `18/24, 21/24, 24/24` |
| 9 | 6 | `21/28, 24/28, 27/28` |
| 10 | 6 | `24/30, 27/30, 30/30` |

Thus the finite table leaves exactly two rows:

| `r` | `q` | surviving `s` | surviving fibre sizes | `b` |
|---:|---:|---:|---|---:|
| 8 | 32 | 8 | `(3,3,3,3,3,3,3,3)` | 0 |
| 10 | 30 | 10 | `(3,3,3,3,3,3,3,3,3,3)` | 0 |

All rows `2<=r<=7` and `r=9` violate one of the displayed lower and upper
bounds.  The standard-library checker in
`experiments/erdos151_siege/k4free_h10/order40/check_order40_reduction.py`
enumerates every allowed `s` and every integer fibre vector and reproduces
this table.  This is an arithmetic check, not a graph-existence claim.

## 4. The equality row `r=10`

Here `q=c=30`, `b=0`, and all ten fibres have size three.  Thus every core
vertex has one boundary edge and no other non-core incidence.  Boundary
rigidity gives `t_Q(v)=10` for every core vertex, so `Q` has exactly

`(30*10)/3=100`

triangles.  A core triangle uses three distinct fibres because every fibre
is independent.  There are `binom(10,3)=120` triples of fibres, so some
three fibres support no core triangle.  Their union is an ambient-admissible
nine-set.  Add any outside vertex belonging to one of the other seven
fibres.  It is anticomplete to the chosen core set, producing an admissible
ten-set, a contradiction.

## 5. The equality row `r=8`

Here `q=32`, `c=24`, `b=0`, and the eight fibres all have size three.  Let

`A=V(Q)-union_x B_x`, so `|A|=8`.

Equality holds throughout (3).  Hence every core vertex sees exactly six
distinct fibres in its core neighborhood, and within a fixed fibre the
three open core neighborhoods are pairwise disjoint.  It follows that
every core vertex has exactly six boundary neighbors, one in each of six
fibres, and exactly two neighbors in `A`.  In particular `Q[A]` is
2-regular, though only the six-plus-two split is needed below.

Fix `a in A`.  Bikov's degree-eight link list gives `t_Q(a)<=12`.  The six
boundary neighbors of `a` lie in six distinct fibres.  Among the 28 pairs
of fibres, at most 12 support a triangle consisting of `a` and one vertex
from each fibre.  Choose a pair `x,y` which supports no such triangle.
Then

`B_x union B_y union {a}`

is a triangle-free seven-set.  It is ambient-admissible: its core edges
are nonmaximal, its boundary vertices have no unused ambient incidence,
and any non-core edge incident with `a` would have its other endpoint in
`A`, of which only `a` was selected.

The induced graph `G[R-{x,y}]` has order six, and the verified small-order
bound supplies an admissible three-set `T`.  The seven-set above is
anticomplete to `T`: the two fibres see only `x,y` outside the core, and
`a` has no outside neighbor.  Their union is an admissible ten-set, again a
contradiction.

## 6. The small-remainder rows `r=0,1`

We use the classical Borodin--Kostochka consequence that a graph with
`chi=Delta=9` contains a `K5`.  Together with Brooks' theorem, this implies
that every `K4`-free graph of maximum degree at most nine is
eight-colorable.  See
O. V. Borodin and A. V. Kostochka, *On an Upper Bound of a Graph's
Chromatic Number, Depending on the Graph's Degree and Density*, JCTB 23
(1977), 247--250, Corollary 2; the explicit `chi=Delta=9 => K5` formulation
is also recorded in R. Galindo and J. McDonald, *On graphs with chromatic
number and maximum degree both equal to nine*, arXiv:2408.12693, p. 2.

Let `H=G[V(Q)]`.  The edges of `H` which are not core edges form a matching
`F`: a core-degree-nine vertex has no spare incidence and a core-degree-
eight vertex has at most one.  Properly color `H` with eight colors.  For
each pair of color classes, remove one endpoint from every `F`-edge inside
the pair.  The resulting set is triangle-free and contains no ambient-
maximal edge, hence is admissible.  Summing its guaranteed size over the 28
color pairs gives

`7q-|F|`.

For `r=0`, `q=40` and `|F|<=20`, so this sum is at least `260>28*9`.
For `r=1`, `q=39` and again `|F|<=19`, so it is at least
`254>28*9`.  In either case some pair yields an admissible ten-set.

This finishes every value `0<=r<=10` and proves the conditional strong
statement.

## 7. Scope and dependencies

**Proved in this note:** the fibre facts, the exact arithmetic funnel, and
the contradictions in both equality rows.

**External proved inputs:** the verified through-order-39 theorem, Bikov's
degree-eight link classification, Turán's theorem, and the 1977
Borodin--Kostochka coloring consequence.

**Computationally checked:** only the integer table and its displayed
arithmetic.  No solver output is used to assert graph nonexistence.

**Not claimed:** a full solution of Erdős #151.  The order-40 clique-number
four and five lanes remain separate.
