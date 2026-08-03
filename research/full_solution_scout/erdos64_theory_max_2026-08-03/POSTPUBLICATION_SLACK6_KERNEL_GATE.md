# A finite kernel gate for the next incidence equality

Date: 2026-08-03

Status: **PROVED WITH ONE NAMED EXTERNAL THEOREM**.  The independent finite
enumeration is retained only as corroboration.  This is a post-publication
strengthening, not part of the already frozen incidence-kernel packet.

Use the notation of the published incidence-kernel packet.  Put

```text
q = 2a-|E(J)| = 2a-d_2.
```

This note investigates the next possible equality

```text
d=2a+6.                                                (0.1)
```

## 1. Exact collapse to two patterns

As before,

```text
x=e(A,D)-4a,
y=2d-e(A,D)=d_1+2d_0.
```

Under (0.1), `x+y=12`.  Since `d` is even, the degree sum in `G[D]` makes
`x,y` even.  Direct substitution gives

```text
d_2=2a-6+x+d_0,
q=6-x-d_0,
d_1=12-x-2d_0.                                        (1.1)
```

For `a>=6`, the proved `C4`-free 2-degenerate kernel bound gives `q>=5`.
Thus `x+d_0<=1`.  Because `x` is even, exactly two patterns remain:

```text
q=6: x=0, d_0=0, d_1=12;
q=5: x=0, d_0=1, d_1=10.                              (1.2)
```

In both patterns every high vertex has degree exactly four, so additionally
`Delta(J)<=4` and the number of `D_1` vertices of color `v` is exactly
`4-deg_J(v)`.

## 2. Why two finite kernel orders control all larger orders

The following propagation uses only proved edge bounds.

### Deficit five

Let `H` be a dyadic-cycle-free 2-degenerate graph with
`|E(H)|=2|V(H)|-5`.  If `|V(H)|>=5`, then `H` is connected: in a disconnected
graph the component deficits add, an isolated vertex has deficit two, a
nontrivial component has deficit at least three, and a deficit-three component
has order at most three.  Thus a disconnected deficit-five graph has order at
most four.

If `|V(H)|>=7`, it has no degree-one vertex.  Deleting one would leave a
dyadic-free 2-degenerate graph of order at least six and deficit four,
contrary to the proved bound `|E|<=2|V|-5` at order at least six.  Since `H`
is 2-degenerate, it therefore has a degree-two vertex.  Deleting it preserves
deficit five and all hereditary restrictions.

Consequently, a deficit-five example of any order at least nine would reduce
one vertex at a time to an example of order nine.

### Deficit six

A disconnected deficit-six graph has order at most six: its possible deficit
partitions are `2+2+2`, `2+4`, or `3+3`, and the order bounds for deficit
two, three, and four components are respectively one, three, and five.

Once deficit-five graphs of order at least nine have been excluded, a
deficit-six graph of order at least eleven cannot have degree one, because
deleting it would give a deficit-five graph of order at least ten.  It has
a degree-two vertex and reduces to the preceding order.  Therefore excluding
deficit six at order eleven excludes it at every larger order.

## 3. The finite bases follow from a sharp extremal theorem

Győri, Li, Salia, Tompkins, Varga and Zhu prove the following sharp result:

> Every `n`-vertex graph with more than
> `floor(19(n-1)/12)` edges contains a cycle whose length is divisible by
> four.

Source: E. Győri, B. Li, N. Salia, C. Tompkins, K. Varga and M. Zhu,
*On graphs without cycles of length 0 modulo 4*, Journal of Combinatorial
Theory, Series B 176 (2026), 7--29, Theorem 1;
<https://arxiv.org/abs/2312.09999>.

At order nine the bound is `floor(19*8/12)=12`.  A deficit-five graph has
`2*9-5=13` edges, so it has a cycle of length divisible by four.  At this
order that length can only be four or eight, hence is dyadic.

At order eleven the bound is `floor(19*10/12)=15`.  A deficit-six graph has
`2*11-6=16` edges, so the same theorem again gives a cycle of length four or
eight.

These two contradictions, together with the deletion propagation in Section
2, prove without finite enumeration that

```text
q=5 implies |V(J)|<=8,
q=6 implies |V(J)|<=10.                               (3.1)
```

The only external dependency in this note is the quoted extremal theorem.

## 4. Independent finite audit (corroboration only)

`audit_next_slack_kernel_gate.py` asks nauty `geng` for exactly the relevant
connected minimum-degree-two graphs, then uses an independent graph6 parser,
explicit `C4` enumeration, degeneracy peeling, and a Held--Karp subset DP for
`C8`.  Only lengths four and eight matter at orders nine and eleven.

The exact results are:

```text
n=9,  q=5, e=13:  2,287 geng records;
                   10 are C4-free and 2-degenerate;
                    0 are also C8-free.

n=11, q=6, e=16: 125,766 geng records;
                  735 are C4-free and 2-degenerate;
                    0 are also C8-free.
```

The `geng.exe` SHA-256 used in the audit is

```text
64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef.
```

The calculation exactly reproduces the two consequences of the external
theorem.  It is not a premise of (3.1).

## 5. Consequence and remaining finite family

Combining Sections 1--3, a hypothetical equality case (0.1) with `a>=6`
must have `6<=a<=10`.  In particular, the published universal bound sharpens
unconditionally (with the one named source) to

```text
a>=11  ==>  d>=2a+7.                                  (5.1)
```

Exact kernel enumeration plus `Delta(J)<=4` leaves:

```text
       a:       6   7   8   9  10       total
q=5 kernels:   2   4   2   0   0          8
q=6 kernels:   1   4   8  12   4         29
```

So the entire large-`a` equality layer collapses to 37 unlabelled marked
kernels.  `slack6_kernel_cegar.py` is probing the residual `G[D]` realization
problem.  At this checkpoint all three `a=6` kernels are UNSAT already using
only `C4/C8` obstructions; this is exploratory corroboration, not a checked
proof certificate.

The highest-value mathematical next step is now to prove directly that none
of the 37 residual colored kernels admits the required subcubic residual
graph.  Doing so, together with a separate treatment of `a<=5`, would upgrade
the universal abundance constant once more.
