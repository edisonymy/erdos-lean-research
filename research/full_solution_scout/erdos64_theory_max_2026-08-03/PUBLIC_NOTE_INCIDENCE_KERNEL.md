# An incidence-kernel bound for minimal Erdős--Gyárfás counterexamples

**Campaign note, 3 August 2026.** Prepared for public expert review by
Edison Yi's Erdős-problem research campaign, with AI-assisted discovery and
independent adversarial checking.

## Exact scope

This note does **not** resolve the Erdős--Gyárfás conjecture (Erdős problem
#64). It proves a stronger necessary condition on any hypothetical minimal
counterexample.

Let `G` be chosen first with minimum order and then, subject to that, minimum
size among finite simple graphs of minimum degree at least three with no
cycle whose length is a power of two. Put

```text
D = {v : deg_G(v)=3},       A = {v : deg_G(v)>=4},
d = |D|,                    a = |A|.
```

Then, uniformly,

```text
d >= 2a+6.
```

In particular, for `n=|V(G)|`, universally

```text
d >= ceil((2n+6)/3) = ceil(2n/3)+2,
a <= floor((n-6)/3).
```

## Incidence kernel

Every proper subgraph of `G` has minimum degree at most two. Consequently,
`A` is independent and every vertex has a neighbour in `D`. Each cubic
vertex therefore has at most two neighbours in `A`.

For `i=0,1,2`, let `D_i` be the cubic vertices with exactly `i` neighbours
in `A`, and put `d_i=|D_i|`. Define a graph `J` on `A` by placing one edge
between the two `A`-neighbours of every vertex of `D_2`.

The graph `J` is simple: two vertices of `D_2` with the same endpoint pair
would produce a four-cycle in `G`. Every `l`-cycle of `J` lifts through
distinct `D_2` vertices to a `2l`-cycle of `G`. Hence every subgraph of `J`
with minimum degree at least three would be a smaller counterexample. Thus
`J` is simple, `C4`-free, and 2-degenerate.

## Edge lemma and count

A simple `C4`-free 2-degenerate graph on `r>=4` vertices has at most `2r-4`
edges. Indeed, equality in the usual `2r-3` degeneracy bound recursively
reduces to a triangle; the next reverse degree-two addition creates a
four-cycle. For `r>=6`, the sharper bound `2r-5` holds: equality at `2r-4`
reduces to the five-vertex friendship graph consisting of two triangles
sharing a vertex, in which every vertex pair has a common neighbour, so the
next reverse addition again creates a four-cycle.

Since `d_2=|E(J)|`, for `a>=4` we have `d_2<=2a-4`. Write

```text
x = e_G(A,D)-4a,
y = 2d-e_G(A,D) = d_1+2d_0.
```

Then `x,y>=0`, `d_1>=8+x`, and

```text
2(d-2a)=x+y.
```

Therefore `d>=2a+4`. The cases `a=0,1,2,3` follow separately from
simplicity, four-cycle exclusion, and parity of the degree sum in `G[D]`.

When `a>=6`, the sharper kernel bound gives `d_1>=10+x`, hence
`d>=2a+5`. Equality would force `x=0,y=10`, but then

```text
sum_{v in D} deg_{G[D]}(v) = d+y
```

is odd. Thus `d>=2a+6` whenever `a>=6`.

For `a<=5`, the two remaining incidence slacks are finite but are eliminated
without computation. Color every `D_1` vertex by its unique `A`-neighbor.
If two `D_1` vertices are the endpoints of a two-edge path in `G[D]`, equal
colors give a `C4`; distinct colors with a common neighbor in `J` give a
lifted `C8`. The exact slack identities leave only the empty graph, `P3`,
`K3`, the paw, and the five-vertex friendship graph as kernels. Direct
degree-capacity counts exclude the last four, while the empty-kernel cases
reduce to short colored cycles and one explicit seven-cycle coloring. This
rules out both `d=2a+4` and `d=2a+5` for every `a<=5`, proving the uniform
six-unit bound.

## Verification and priority boundary

The full proof and its literature-dependent edge-count corollary are in the
focused preprint under `preprint/`. Separate root audits check the
minimality quantifiers, simplicity and cycle lifting, all small cases, the
incidence algebra, and the parity sharpening. An independent agent repeated
that audit without finding an error. The kernel edge bounds were also
exhaustively tested on every labelled graph through seven vertices; the
computation is corroboration, not a premise.

Avery Carr's May 2026 preprint proves that at least `4/7` of a minimal
counterexample's vertices are cubic:

> A. Carr, *Every Minimal Counterexample to the Erdős--Gyárfás Conjecture is
> Predominantly Cubic*, arXiv:2605.22844 (2026).

Exact-constant, title, arXiv, and broad web searches on 3 August 2026 found
Carr's theorem but no prior `2a+6` or incidence-kernel statement.
That is a search-relative priority check, not a guarantee about unpublished
or unindexed work.
