# Milestone 2: the suppressed incidence kernel

Date: 2026-08-03

Status: **PROVED HERE**.  This strengthens Theorem 2.2 of
`MILESTONE_1_AUDIT.md`.

Let `G` be the lexicographically minimum counterexample fixed there.  Put

```
A = {v : deg_G(v) >= 4},        D = {v : deg_G(v) = 3},
a = |A|,                         d = |D|,
D_i = {v in D : deg_A(v)=i},     d_i = |D_i|  (i=0,1,2).
```

The earlier local proof gives that `A` is independent and every vertex has a
neighbor in `D`; hence every `D`-vertex has at most two `A`-neighbors.

## 1. Incidence-kernel theorem

Define a graph `J` on vertex set `A` by putting one edge between the two
`A`-neighbors of every vertex in `D_2`.

### Theorem 1.1

`J` is simple, dyadic-free, and 2-degenerate.  In particular, every subgraph of
`J` has a vertex of degree at most two.

**Proof.**  The two `A`-neighbors of a `D_2` vertex are distinct because `G` is
simple.  Two different `D_2` vertices cannot have the same neighbor pair: the two
corresponding length-two paths would form a `C4` in `G`.  Thus `J` is simple.

Every simple `ell`-cycle of `J` lifts to a simple `2ell`-cycle of `G` by replacing
each kernel edge with its assigned two-edge path through `D_2`.  Therefore `J`
has no dyadic cycle.  The same lifting applies to every subgraph `J'` of `J`.  If
some `J'` had minimum degree at least three, it would be a dyadic-free graph of
minimum degree at least three on at most `a<n` vertices, contradicting the
order-minimality of `G`.  Hence `J` is 2-degenerate.  QED

This gives more than a global edge count: for every `X subseteq A`, the number of
vertices of `D_2` whose two `A`-neighbors both lie in `X` is at most `2|X|-3`
when `|X|>=2`.

## 2. A sharp elementary edge lemma

### Lemma 2.1

If a simple 2-degenerate `r`-vertex graph is `C4`-free and `r>=4`, then it has at
most `2r-4` edges.

**Proof.**  Every simple 2-degenerate graph on `r>=2` vertices has at most
`2r-3` edges.  Suppose equality holds.  Repeatedly delete a vertex of degree at
most two.  A deleted vertex cannot have degree at most one, since the remaining
graph would then exceed its `2(r-1)-3` edge bound.  Thus every deletion has degree
exactly two and preserves equality, down to a three-vertex graph with three edges,
namely `K3`.  The next vertex in the reverse construction has two neighbors in
that `K3`; together with the third triangle vertex these four vertices form a
`C4` (possibly with a chord).  Contradiction.  QED

For later use, the same deletion proof gives a slightly sharper finite statement:
a `C4`-free 2-degenerate graph with `r>=6` has at most `2r-5` edges.  Indeed,
an equality example with `2r-4` edges recursively reduces to the unique
four-vertex `C4`-free four-edge graph (a paw), then to the five-vertex friendship
graph consisting of two triangles sharing one vertex.  In that friendship graph
every pair of vertices has a common neighbor, so adding another degree-two vertex
creates a `C4`.  This refinement is not needed for the universal theorem below.

## 3. Four units of strict slack

### Theorem 3.1

```
d >= 2a+4,
```

and consequently

```
d >= ceil((2n+4)/3),       a <= floor((n-4)/3).
```

**Proof for `a>=4`.**  The edges of `J` are in bijection with `D_2`, so Lemma 2.1
gives

```
d_2 <= 2a-4.
```

Counting `A-D` incidences gives

```
4a <= e(A,D) = d_1+2d_2,
```

and hence `d_1>=8`.  Define

```
x = sum_{u in A}(deg_G(u)-4) >= 0,
y = sum_{v in D}(2-deg_A(v)) = d_1+2d_0 >= 8.
```

The exact slack identity is

```
2(d-2a) = x+y.
```

Thus `d-2a>=4`.

**Small cases.**

- `a=0`: `G` is a nonempty simple cubic graph, so `d=n>=4`.
- `a=1`: here `d_2=0` and the sole `A`-vertex has at least four distinct
  `D_1` neighbors.  If `d=4`, then `G[D]` is a four-cycle.  If `d=5`, parity of
  `sum_{D} deg_{G[D]}` forces all five `D` vertices to meet `A`, so `G[D]` is a
  five-cycle; the `A`-vertex plus any two-edge segment of that cycle gives a `C4`.
  Hence `d>=6=2a+4`.
- `a=2`: `C4`-freeness gives `d_2<=1`, so
  `8<=d_1+2d_2<=d+1`.  The only possible value below eight is `d=7`, which forces
  `(d_0,d_1,d_2)=(0,6,1)`.  Then the degree sum of `G[D]` is `2d_1+d_2=13`,
  impossible.  Hence `d>=8`.
- `a=3`: simplicity gives `d_2<=3`, so
  `12<=d_1+2d_2<=d+3`.  The only possible value below ten is `d=9`, forcing
  `(d_0,d_1,d_2)=(0,6,3)` and the odd degree sum
  `2d_1+d_2=15` in `G[D]`.  Hence `d>=10`.

This proves all cases.  QED

## 4. Extra structural output

For `a>=4`, a minimum counterexample has at least eight cubic vertices with exactly
one high-degree neighbor.  Such vertices have degree exactly two inside `G[D]`.

For `a>=6`, the finite sharpening in Lemma 2.1 gives `d_2<=2a-5` and hence
`d_1>=10`.  In fact

```
d >= 2a+6                                            (4.1)
```

in this range.  To see the extra unit, suppose `d=2a+5`.  The exact slack identity
would give `x+y=10`, while `y=d_1+2d_0>=10`.  On the other hand

```
sum_{v in D} deg_{G[D]}(v) = d+y
```

is even.  Since `d=2a+5` is odd, `y` must be odd, so actually `y>=11`, contradicting
`x+y=10` with `x>=0`.  This parity step is essential: the kernel edge count alone
only yields `d>=2a+5`.

The only equality patterns left by this milestone for a universal `+5` bound have
`a<=5`; they are treated separately in the next milestone.

No Carr theorem, census result, or other external source is used in this milestone.
