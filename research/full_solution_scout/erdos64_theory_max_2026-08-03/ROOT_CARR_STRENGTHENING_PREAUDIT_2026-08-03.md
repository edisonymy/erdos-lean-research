# Root pre-audit: a strict predominantly-cubic bound

**Date:** 3 August 2026.  **Status:** new elementary deduction under hostile
audit; not yet a publication claim and not a resolution of Erdős #64.

## Input from Carr

Let `G` be a counterexample chosen first with minimum order and then with
minimum size.  Write

```text
A = {v : deg_G(v) >= 4},       D = {v : deg_G(v) = 3}.
```

The argument uses the two conclusions stated in Avery Carr,
*Every Minimal Counterexample to the Erdős--Gyárfás Conjecture is
Predominantly Cubic*, arXiv:2605.22844 (13 May 2026):

1. `A` is independent; and
2. every vertex has a neighbour in `D`.

The exact primary-source wording and minimality convention remain to be
frozen in the independent audit.

## Theorem under audit

Every such `G` satisfies

```text
|D| >= 2|A| + 2,
```

and therefore

```text
|D| >= ceil((2|V(G)| + 2)/3).
```

This improves Carr's published `4|V(G)|/7` lower bound if the two quoted
inputs have exactly the scope above.

## Proof

Put `a=|A|`, `d=|D|`, and `e=e_G(A,D)`.  Since `A` is independent and every
vertex of `A` has degree at least four,

```text
e >= 4a.                                                    (1)
```

Every vertex of `D` has a neighbour in `D`, so it has at most two neighbours
in `A`.  Hence

```text
e <= 2d.                                                    (2)
```

Thus `d>=2a`.  It remains to exclude the two boundary values.

If `a=0`, then `G` is cubic and a finite simple graph of minimum degree
three has at least four vertices, so `d>=4>=2a+2`.  We may therefore assume
`a>0` in the boundary analysis.

### Case `d=2a`

Equality holds throughout (1)--(2).  Every vertex of `A` has degree exactly
four, and every vertex of `D` has exactly two neighbours in `A` and one in
`D`.

Construct a graph `J` on vertex set `A`: for every `x in D`, join its two
`A`-neighbours by an edge.  These neighbours are distinct.  No two vertices
of `D` give the same pair, because otherwise those two vertices and the
shared pair in `A` form a simple `C4` in `G`.  Since `G` has no power-of-two
cycle, in particular it has no `C4`; consequently `J` is simple.  Each
vertex of `A` has degree four in `J`, so `delta(J)=4`.

Every simple cycle of length `l` in `J` lifts, by replacing each edge with
its distinct length-two path through the corresponding vertex of `D`, to a
simple cycle of length `2l` in `G`.  Hence a power-of-two cycle in `J` would
give one in `G`.  Thus `J` is a smaller finite simple graph of minimum degree
at least three with no power-of-two cycle, contradicting the minimum order
of `G`.

### Case `d=2a+1`

Let

```text
x = e - 4a,              y = 2d - e.
```

Then `x,y>=0` and `x+y=2`.  The sum of the degrees in `G[D]` is

```text
3d-e = d+y,
```

which is even.  Since `d` is odd, `y` is odd.  Therefore `x=y=1`.
It follows that exactly one vertex of `A` has degree five and all other
vertices of `A` have degree four; exactly one vertex `z` of `D` has only one
neighbour in `A`, while every other vertex of `D` has two.

Construct `J` on `A` from the `2a` vertices of `D-{z}` exactly as above and
discard `z`.  Again `J` is simple, since a repeated pair would lift to a
`C4` in `G`.  If the sole `A`-neighbour of `z` is the degree-five vertex,
then `J` is four-regular.  Otherwise that neighbour has degree three in `J`,
the degree-five vertex retains degree five, and all remaining vertices have
degree four.  In either case `delta(J)>=3`.  Every cycle of `J` again lifts
to a cycle twice as long in `G`, so `J` is a smaller counterexample.  This is
again impossible.

The only remaining integer possibility is `d>=2a+2`, as claimed.

## Hostile-audit checklist

- Confirm Carr's two statements apply simultaneously to the same
  order-then-size minimal counterexample.
- Check that "adjacent to a cubic vertex" means an ordinary distinct
  neighbour, including when the vertex itself is cubic.
- Check the parity identity and both equality classifications.
- Check simplicity of `J` (the repeated-pair obstruction is exactly a
  four-cycle, with four distinct vertices).
- Check that the lifted cycle is simple and has length exactly twice the
  source cycle.
- Search the pre-3-August-2026 literature and public web for this `2/3` or
  strict additive strengthening before asserting novelty.
