# A strict cubic-abundance bound for minimal Erdős--Gyárfás counterexamples

**Campaign note, 3 August 2026.**  Prepared for public expert review by
Edison Yi's Erdős-problem research campaign, with AI-assisted discovery and
adversarial checking.

## Scope

This note does **not** resolve the Erdős--Gyárfás conjecture (Erdős problem
#64).  It sharpens a necessary condition on any hypothetical minimal
counterexample.

Avery Carr proved in May 2026 that at least `4/7` of the vertices of a
counterexample chosen with minimum order and then minimum size are cubic, and
also observed that its degree-at-least-four vertices form an independent set
and that its cubic vertices dominate the graph:

> A. Carr, *Every Minimal Counterexample to the Erdős--Gyárfás Conjecture is
> Predominantly Cubic*, arXiv:2605.22844 (2026).

The two local observations are short consequences of minimality and are
reproved below.  They imply a substantially stronger asymptotic proportion;
the absence of a four-cycle and a suppression argument make the bound strict.

## Theorem

Let `G` be a finite simple graph of minimum degree at least three with no
cycle whose length is a power of two.  Suppose `G` has minimum order among all
such graphs and, subject to that, minimum size.  Let

```text
D = {v : deg_G(v)=3},       A = {v : deg_G(v)>=4}.
```

Then

```text
|D| >= 2|A|+2.
```

Equivalently, if `n=|V(G)|`, then

```text
|D| >= ceil((2n+2)/3)
and
|A| <= floor((n-2)/3).
```

## Proof

Every proper subgraph of `G` has minimum degree at most two.  Otherwise that
subgraph would be a smaller counterexample, either in order or in size.  It
follows that `A` is independent: deleting an edge with both endpoints in `A`
would preserve minimum degree three.  It also follows that every vertex has a
neighbour in `D`: if `v` had none, deleting `v` would leave all its neighbours
with degree at least three.

Write `a=|A|`, `d=|D|`, and `e=e_G(A,D)`.  All neighbours of a vertex in `A`
lie in `D`, while every vertex in `D` has a neighbour in `D` and hence at most
two neighbours in `A`.  Therefore

```text
4a <= e <= 2d,
```

so `d>=2a`.  We exclude equality and the next integer value.

If `d=2a`, every vertex in `A` has degree four and every vertex in `D` has
exactly two neighbours in `A`.  Make a graph `J` on `A` by replacing each
vertex of `D` with the edge joining its two `A`-neighbours.  Distinct vertices
of `D` give distinct edges: a repeated pair would make a four-cycle in `G`.
Thus `J` is a simple four-regular graph.  Every simple `l`-cycle of `J` lifts
through the distinct suppressed vertices to a simple `2l`-cycle of `G`.
Consequently `J` has no power-of-two cycle.  It is a smaller graph of minimum
degree at least three, contradicting the choice of `G`.

Suppose instead that `d=2a+1`, and put

```text
x = e-4a,
y = 2d-e.
```

Then `x,y` are nonnegative integers with `x+y=2`.  Moreover, the sum of the
degrees in `G[D]` is

```text
3d-e = d+y,
```

which is even.  Since `d` is odd, `y` is odd, so `x=y=1`.  Hence exactly one
vertex of `A` has degree five, exactly one vertex `z` of `D` has only one
neighbour in `A`, and all other vertices have the boundary degrees described
in the preceding case.

Now suppress the vertices of `D-{z}` to obtain a simple graph `J` on `A`.
If the sole `A`-neighbour of `z` is the degree-five vertex, `J` is
four-regular.  Otherwise `J` has one vertex of degree three, one of degree
five, and all others of degree four.  In both cases `delta(J)>=3`.  The same
cycle-lifting argument shows that `J` has no power-of-two cycle, again
contradicting order-minimality.  (When `A` is empty, simplicity and minimum
degree already give `d>=4`, so there is no boundary exception.)

Thus `d>=2a+2`, as required.  ∎

## Verification and novelty boundary

The full hostile-audit proof, equality-case caveats, a related edge bound,
and independently replayable low-cut computations are in
`MILESTONE_1_AUDIT.md`.  The mathematical proof above has two independent
derivations within the campaign.  Exact-title, exact-constant, arXiv, and web
searches conducted on 3 August 2026 found Carr's `4/7` theorem but no prior
`2/3` or `ceil((2n+2)/3)` bound.  That is a search-relative priority check,
not a guarantee that unpublished or unindexed prior work does not exist.
