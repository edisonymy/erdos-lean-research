# Root audit: incidence-kernel cubic-abundance theorem

Date: 2026-08-03

## Verdict

**PASS**, after two independent line-by-line audits.  The following claims are
proved without computational or literature dependencies:

- every lexicographically minimal counterexample to Erdős problem #64 has
  `d >= 2a+4`, where `d` is the number of degree-three vertices and `a` the
  number of degree-at-least-four vertices;
- if `a >= 6`, then `d >= 2a+6`;
- equivalently, universally `d >= ceil((2n+4)/3)` and
  `a <= floor((n-4)/3)`.

These are necessary conditions on a hypothetical counterexample, **not a
resolution of Erdős #64**.

## Quantifier and lifting audit

The minimality convention is minimum order and then minimum size.  Therefore
every proper subgraph has minimum degree at most two.  This justifies both
edge deletion inside the high-degree set and vertex deletion when a vertex
has no cubic neighbour.

For `D_i = {v in D : deg_A(v)=i}`, the graph `J` on `A` with one edge for
each vertex of `D_2` is simple: repeated endpoint pairs would give a `C4` in
the original graph.  A simple cycle of length `l` in `J` lifts through
distinct `D_2` vertices to a simple cycle of length `2l`.  Thus every
subgraph of `J` with minimum degree at least three would itself be a smaller
dyadic-cycle-free counterexample.  The conclusion that `J` is 2-degenerate
is therefore valid for every subgraph, not only for `J` globally.

## Edge-bound audit

A simple 2-degenerate graph on `r` vertices has at most `2r-3` edges.  If a
`C4`-free example with `r >= 4` attained equality, every deletion in a
degeneracy ordering would have degree two until a triangle remained; the
next reverse addition makes a four-cycle.  Hence `e <= 2r-4`.

If `r >= 6` and `e = 2r-4`, the same equality recursion reaches the unique
four-vertex paw and then the unique five-vertex friendship graph `F_2`.
Every pair of vertices of `F_2` has a common neighbour, so the next
degree-two reverse addition creates a `C4`.  Hence `e <= 2r-5` for `r >= 6`.

The independent script `verify_incidence_kernel_bounds.py` enumerated every
labelled simple graph through order seven.  Its observed maxima among
`C4`-free 2-degenerate graphs were:

```text
n=4  max_edges=4
n=5  max_edges=6
n=6  max_edges=7
n=7  max_edges=9
VERIFIED
```

This enumeration is an audit aid and is not used as a proof premise.

## Incidence algebra and parity audit

Write `e=e(A,D)`,

```text
x = e-4a,
y = 2d-e = d_1+2d_0.
```

Then `x,y >= 0` and the exact identity is

```text
2(d-2a) = x+y.
```

For `a >= 4`, the kernel bound `d_2 <= 2a-4` gives
`d_1 >= 8+x`, hence `y >= 8+x` and `d >= 2a+4`.  The cases
`a=0,1,2,3` were checked separately; the only numerical boundary cases are
eliminated respectively by simplicity, an explicit `C4`, or an odd degree
sum in `G[D]`.

For `a >= 6`, `d_2 <= 2a-5` first gives `d >= 2a+5`.  Equality would force
`x=0,y=10`, while

```text
sum_{v in D} deg_{G[D]}(v) = 3d-e = d+y
```

would be odd.  This proves the sharpened `d >= 2a+6`.

## Deliberately unpromoted finite experiment

The existing exact CEGAR encoding, with its residual lexicographic symmetry
break, returned solver-level `UNSAT_FAMILY` for the degree patterns
`(n,a)=(16,4)` after 820 `C8` cuts and `(19,5)` after 8,071 `C8` cuts.  A
symmetry-free `(16,4)` run had not completed after 52,353 cuts.  No checked
proof certificate was produced, so these results are **not** used to claim a
universal `+5` or `+6` theorem.

## Priority boundary

The primary source checked was Avery Carr, *Every Minimal Counterexample to
the Erdős--Gyárfás Conjecture is Predominantly Cubic*, arXiv:2605.22844,
submitted 13 May 2026.  It states the `4/7` bound.  Exact-constant,
exact-title, arXiv, and broad web searches on 3 August 2026 found no prior
`2a+4`, `2a+6`, `ceil((2n+4)/3)`, or incidence-kernel result in this setting.
That is a search-relative noncollision check, not a guarantee about
unpublished or unindexed work.
