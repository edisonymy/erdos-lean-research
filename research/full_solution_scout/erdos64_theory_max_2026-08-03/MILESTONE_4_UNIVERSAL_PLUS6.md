# Milestone 4: universal six-unit slack

Date: 2026-08-03

Status: **PROVED HERE**.  This strengthens Milestone 3.

Use the same notation `A,D,a,d,D_i,d_i,J,R=G[D]`, and the same slacks `x,y`.
Milestone 3 proves `d>=2a+5`; Milestone 2 proves `d>=2a+6` whenever `a>=6`.
It remains to exclude

```
d=2a+5                                                   (1.1)
```

for `a<=5`.

## 1. Equality arithmetic

Under (1.1),

```
x+y=10,
d_2=2a-5+d_0+x,             d_1=10-x-2d_0.              (1.2)
```

Moreover `d` is odd and `d+y=sum_D deg_R` is even, so `y` is odd and therefore
`x` is odd.  We repeatedly use Lemma 2.1 of Milestone 3:

> If two `D_1` vertices are joined by a two-edge path in `R`, then their colors
> are neither equal nor two vertices with a common neighbor in `J`.

## 2. Cases `a=0,1,2`

### `a=0`

Equation (1.1) would make `G` cubic of odd order five, contradicting the handshake
lemma.

### `a=1`

Here `d_2=0`, so (1.2) leaves two possibilities.

- `(d_0,d_1,x)=(0,7,3)`: `R` is 2-regular and all its vertices have the same
  color; any two-edge segment closes through the `A`-vertex to a `C4`.
- `(d_0,d_1,x)=(2,5,1)`: the five `D_1` vertices have pairwise disjoint
  two-element `R`-neighborhoods, or else there is a `C4` through their common
  color.  Ten distinct neighborhood elements cannot fit inside the seven vertices
  of `D`.

### `a=2`, no kernel edge

The first possibility is `(d_0,d_1,d_2,x)=(0,9,0,1)`.  The graph `R` is a union
of cycles, colored with the two `A`-colors.  On a cycle of length `ell`, joining
vertices at distance two gives one odd cycle when `ell` is odd and two cycles of
length `ell/2` when `ell` is even.  It is bipartite only when `ell` is divisible
by four.  Thus avoiding a same-colored distance-two pair would force every
component length to be divisible by four; at order at most nine that means a
`C4` or `C8` component, already forbidden.  Contradiction.

### `a=2`, one kernel edge

The other possibility is `(d_0,d_1,d_2,x)=(1,7,1,1)`.  As in Milestone 3, `R`
has one degree-three vertex `z`, one degree-one vertex `e`, seven degree-two
colored vertices, and consists of a unicyclic component containing `z,e` plus
possible colored cycle components.  Every separate colored cycle has length at
most seven.  The distance-two graph argument above gives a same-colored pair
unless its length is four, which is itself forbidden.  Hence there is no separate
cycle.

Let `t` be the number of colored vertices strictly between `e` and `z` on the
pendant path.  The vertex `e` meets both `A` vertices.  If `t>=2`, its two-edge
`R`-path to the second colored vertex gives a `C4`; if `t=0`, the same is true for
either cycle-neighbor of `z`.  Thus `t=1`.  The unique cycle is a 7-cycle

```
z,c1,c2,c3,c4,c5,c6,z.
```

If the six colored vertices contain unequal color-class sizes, their distance-two
graph (the path `c2,c4,c6,c1,c3,c5`) cannot be properly two-colored and there is a
`C4`.  Otherwise its two classes have size three, and avoiding a `C4` forces the
colors to alternate along that displayed path.  In particular `c2` and `c3` have
the same color.  They are adjacent on the 7-cycle, so the complementary six-edge
`c2-c3` path around that cycle, together with the two edges through their common
`A`-neighbor, is a `C8`.  Contradiction.

## 3. Cases `a=3`

Since `J` is simple, (1.2) forces `x=1` and gives two kernels.

### `J=P3`, `(d_0,d_1,d_2)=(0,9,2)`

Call the colors `L,M,R` along `J`.  Relative to the slack-four case there is one
extra `D_1` vertex at the unique degree-five `A`-vertex, so the number of
`M`-colored vertices is either two or three.

The two degree-one `D_2` vertices supply at most two cross-incidences, giving

```
sum_{v in D_1} deg_{R[D_1]}(v) >= 18-2=16.
```

If `h` of the nine `D_1` vertices have induced degree two, the left side is at most
`9+h`, so `h>=7`.  The two neighbors of every such vertex must have colors `M`
and one of `L,R`; otherwise the two-step lemma gives a `C4` or `C8`.  Hence each
is incident with an `M`-colored vertex.  At most three such vertices exist and
their total `R`-degree is at most six, contradicting `h>=7`.

### `J=K3`, `(d_0,d_1,d_2)=(1,7,3)`

Any two distinct colors have a common `J`-neighbor, so no vertex of `R` can have
two `D_1` neighbors.  Each of the seven degree-two `D_1` vertices needs a neighbor
outside `D_1`.  The three degree-one `D_2` vertices supply three incidences, and
the sole degree-three `D_0` vertex supplies at most one without becoming the middle
of a forbidden path.  Capacity four is less than seven.

## 4. Cases `a=4,5`

The `C4`-free 2-degenerate edge bound and (1.2) force `x=1,d_0=0`.  Thus exactly
one vertex of `A` has degree five, all others degree four, and there is one extra
`D_1` vertex of its color compared with the slack-four kernels.

### `a=4`: paw

Here `d_1=9,d_2=4`.  The four `D_2` vertices supply at most four cross-incidences,
so

```
sum_{v in D_1} deg_{R[D_1]}(v) >= 18-4=14.
```

If `h` of the nine `D_1` vertices have induced degree two, then `14<=9+h`, so
`h>=5`.  In the paw, the only two distinct colors without a common `J`-neighbor
are the center of degree three and the leaf.  Every one of the `h` vertices must
therefore be incident with a center-colored `D_1` vertex.  There are at most two
such vertices (one normally, plus the possible extra one), of total `R`-degree at
most four.  Hence `h<=4`, contradiction.

### `a=5`: two triangles sharing a vertex

Here `d_1=9,d_2=6`.  Any two distinct colors that can occur on `D_1` have a common
`J`-neighbor: this is clear for two outer colors (the shared center), and if the
extra color is the center, it and an outer vertex share the other outer vertex of
that triangle.  Thus no vertex of `R` can have two `D_1` neighbors.  Each of the
nine degree-two `D_1` vertices needs an incidence to `D_2`, but the six degree-one
`D_2` vertices supply only six.

## 5. Consequence

All slack-five cases are impossible.  Therefore every lexicographically minimum
counterexample satisfies

```
d >= 2a+6,                                               (5.1)
d >= ceil((2n+6)/3) = ceil(2n/3)+2,
a <= floor((n-6)/3).                                    (5.2)
```

No external result or computation is used in this proof.
