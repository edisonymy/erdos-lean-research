# Milestone 3: eliminating all slack-four kernels

Date: 2026-08-03

Status: **PROVED HERE**.  No census, solver, or external theorem is used.

Retain the notation of `MILESTONE_2_INCIDENCE_KERNEL.md`:

```
A = {vertices of degree at least 4},       a=|A|,
D = {vertices of degree 3},                d=|D|,
D_i = {v in D : deg_A(v)=i},               d_i=|D_i|,
J = the simple graph on A encoded by D_2.
```

The earlier milestone proves `d>=2a+4`, and proves the stronger `d>=2a+6` when
`a>=6`.  This note rules out equality `d=2a+4` in the remaining cases `a<=5`.

## 1. Equality arithmetic

Assume for contradiction that

```
d=2a+4.                                                   (1.1)
```

As before, put

```
x = sum_{u in A}(deg_G(u)-4),
y = sum_{v in D}(2-deg_A(v)) = d_1+2d_0.
```

Then `x+y=8`.  Since

```
sum_{v in D} deg_{G[D]}(v)=d+y
```

is even and `d` is even, both `y` and `x` are even.  Counting incidences and using
`d_1=d-d_0-d_2` gives the useful exact formulas

```
d_2 = 2a-4+d_0+x,             d_1=8-x-2d_0.              (1.2)
```

For `a>=4`, Milestone 2 gives `d_1>=8`, so equality in (1.2) forces

```
x=d_0=0,       d_1=8,       d_2=2a-4.                    (1.3)
```

The `C4`-free 2-degenerate equality classification from that milestone says:

- when `a=4`, `J` is the paw (a triangle with one pendant edge);
- when `a=5`, `J` is the friendship graph consisting of two triangles sharing one
  vertex; and
- `a>=6` is impossible already (indeed it has the stronger `+6` bound).

For completeness: a four-vertex, four-edge `C4`-free graph must be a triangle with
a pendant edge.  A five-vertex, six-edge `C4`-free 2-degenerate graph deletes a
degree-two vertex to that paw; the only neighbor pair to which it can be restored
without making a `C4` is the pendant edge, producing the stated friendship graph.

## 2. The two-step obstruction

Write `R=G[D]`.  A vertex of `D_i` has degree `3-i` in `R`.  Color each vertex of
`D_1` by its unique neighbor in `A`.

### Lemma 2.1

Suppose two `D_1` vertices `u,w` are the endpoints of a two-edge path `u-z-w` in
`R`.

1. Their colors cannot be equal.
2. Their colors cannot be two distinct vertices having a common neighbor in `J`.

**Proof.**  Equal color `alpha` gives the four-cycle

```
alpha-u-z-w-alpha.
```

For distinct colors `alpha,beta` with common `J`-neighbor `gamma`, let `p,q in D_2`
encode the edges `alpha gamma` and `beta gamma`.  Then

```
alpha-u-z-w-beta-q-gamma-p-alpha
```

is an eight-cycle.  Its vertices are distinct: in particular, the middle vertex
`z` cannot be `p` or `q`, since a `D_2` vertex has degree one in `R` and cannot be
the middle of an `R`-path.  QED

We now eliminate every possible value of `a`.

## 3. Cases `a=0,1,2`

### `a=0`

Equation (1.1) gives a cubic graph on four vertices, necessarily `K4`, which has a
`C4`.

### `a=1`

Here `d_2=0`.  Equations (1.2) and parity leave two possibilities.

- If `(d_0,d_1,x)=(0,6,2)`, all six vertices of `R` have degree two and all meet
  the sole vertex of `A`.  Any two-edge segment in a cycle component of `R`, closed
  through that `A`-vertex, is a `C4`.
- If `(d_0,d_1,x)=(2,4,0)`, the four `D_1` vertices have two-element neighborhoods
  in the six-vertex graph `R`.  These four neighborhoods must be pairwise disjoint,
  since a common neighbor makes a `C4` through the sole `A`-vertex.  Four disjoint
  two-element subsets cannot fit inside six vertices.

### `a=2`

Simplicity of `J` gives `d_2<=1`; (1.2) and parity leave two possibilities.

First, `(d_0,d_1,d_2)=(0,8,0)`.  Then `R` is 2-regular on eight vertices.  A `C4`
or `C8` component is already forbidden.  The only remaining partition into simple
cycle lengths is `3+5`.  The triangle has two vertices of the same one of the two
colors, and those vertices share its third vertex as an `R`-neighbor, making a
`C4` through their color.

Second, `(d_0,d_1,d_2)=(1,6,1)`.  Let `z` be the degree-three vertex of `R` and
`e` its degree-one vertex.  They lie in the same component (otherwise a component
has odd `sum(deg_R-2)`).  That component is unicyclic: it consists of a cycle
through `z` and a path from `z` to the leaf `e`; all other components, if any, are
cycles of colored `D_1` vertices.

Any separate colored cycle has length at most six.  Length four is forbidden
directly; on lengths 3, 5, or 6 the distance-two graph contains an odd cycle, so a
two-coloring has two same-colored vertices with a common `R`-neighbor, giving a
`C4`.  Thus there is no separate cycle.

Let `t` be the number of `D_1` vertices strictly between `e` and `z` on the pendant
path.  If `t>=2`, the second such vertex has one of the two colors and is joined to
`e` by a two-edge `R`-path; since `e` meets both `A` vertices, this gives a `C4`.
If `t=0`, either cycle-neighbor of `z` similarly lies two `R`-steps from `e` and
gives a `C4`.  Hence `t=1`.  The unique cycle is then a six-cycle containing `z`
and the other five colored vertices.  Its three alternating colored vertices are
pairwise at `R`-distance two; two have the same color, again giving a `C4`.

## 4. The two `a=3` kernels

Formula (1.2), parity, and `d_2<=3` give `x=0` and precisely two cases.

### `J=P3`, `(d_0,d_1,d_2)=(0,8,2)`

Call the colors `L,M,R` along the path `J`, with multiplicities `3,2,3` among
`D_1`.  The only pair of distinct colors with a common `J`-neighbor is `L,R`.

Let `h` be the number of `D_1` vertices having two `D_1` neighbors in `R`.  The two
`D_2` vertices have total `R`-degree two, so

```
sum_{v in D_1} deg_{R[D_1]}(v) >= 16-2=14.
```

With eight vertices of induced degree at most two, this forces `h>=6`.  For each
such vertex, Lemma 2.1 says its two neighbor colors must consist of `M` and one of
`L,R`.  Thus it is incident with one of the two `M`-colored vertices.  Those two
vertices have total `R`-degree four, so they can supply at most four such incidences.
This contradicts `h>=6`.

### `J=K3`, `(d_0,d_1,d_2)=(1,6,3)`

Every pair of distinct colors has a common neighbor in `J`, so Lemma 2.1 says that
no vertex of `R` has two `D_1` neighbors.  Each of the six degree-two `D_1` vertices
therefore needs at least one neighbor outside `D_1`, requiring six cross-incidences.
The three degree-one `D_2` vertices can supply three.  The sole degree-three `D_0`
vertex can supply at most one (otherwise it is the middle of a forbidden two-edge
path).  Total capacity is at most four, contradiction.

## 5. The paw and friendship kernels

### `a=4`: paw

Label its triangle `0,1,2` and attach its leaf `3` to `0`.  The `D_1` color
multiplicities are `1,2,2,3`, since they are `4-deg_J(color)`.

The four degree-one `D_2` vertices supply at most four incidences from `D_1` to its
complement.  Hence

```
sum_{v in D_1} deg_{R[D_1]}(v) >= 16-4=12.
```

If `h` of the eight `D_1` vertices have induced degree two, the left side is at
most `8+h`, so `h>=4`.  In the paw the unique pair of distinct colors with no common
`J`-neighbor is `{0,3}`.  Lemma 2.1 therefore forces the two neighbors of each of
those `h` vertices to have colors `0` and `3`.  There is only one color-0 vertex,
of total `R`-degree two, so it can be incident with at most two of them.  Thus
`h<=2`, contradiction.

### `a=5`: two triangles sharing a vertex

The shared vertex has `J`-degree four and hence has no `D_1` vertex of its color;
each of the four outer colors occurs twice.  Any two distinct outer vertices have
the shared center as a common `J`-neighbor.  Together with the equal-color part of
Lemma 2.1, this says that no vertex of `R` has two `D_1` neighbors.

Each of the eight degree-two `D_1` vertices therefore needs a neighbor in `D_2`,
requiring at least eight cross-incidences.  But the six `D_2` vertices have degree
one in `R`, so they supply at most six.  Contradiction.

## 6. Consequence

Every slack-four case is impossible.  Therefore a lexicographically minimum
counterexample satisfies

```
d >= 2a+5,                                               (6.1)
d >= ceil((2n+5)/3),       a <= floor((n-5)/3).          (6.2)
```

When `a>=6`, Milestone 2 already gives the still stronger `d>=2a+6`.

The accompanying `slack4_finite_probe.py` independently returns UNSAT for the seven
nontrivial solver-encoded skeletons using lazy exact `C4/C8` blocking.  The immediate
`K4` and all-degree-two single-color cases are dispatched directly above rather than
encoded.  The computation is only an adversarial cross-check and is not a dependency
of this proof.
