# Erdős 128: a conditioned-half inequality and an all-order alpha window

## Status

This note does **not** solve Erdős Problem 128.  It proves a general lemma
that applies at every order and narrows the independence-number range of any
counterexample.  No novelty claim is made.

## Conditioned-half lemma

Let `G` be a triangle-free graph on `n` vertices, let `I` be a maximum
independent set of size `a`, and put

```text
k = floor(n/2),   b = n-a,   r = k-a,
M = e(I,V\I),     L = e(G[V\I]).
```

Assume `a < n/2`, so `r >= 0`.  There is a `k`-vertex set containing `I`
that spans at most

```text
(r/b) M + r(r-1)/(b(b-1)) L.                 (1)
```

Indeed, take `R` uniformly among the `r`-subsets of `V\I` and average the
number of edges in `I union R`.  Each cross edge is selected with probability
`r/b`, and each edge inside `V\I` is selected with probability
`r(r-1)/(b(b-1))`.

Triangle-freeness and maximality of `I` give the two bounds

```text
M <= a^2,                 2L <= ab-M.         (2)
```

For the first, the neighbourhood of every vertex of `I` is independent and
therefore has size at most `a`.  For the second, the neighbourhood of every
vertex of `V\I` is likewise independent, so its total degree is at most `a`;
summing `deg_{V\I}(v) <= a-deg_I(v)` over `v in V\I` proves the claim.

Write

```text
c = r/b,   h = r(r-1)/(b(b-1)).
```

Since `c-h/2 >= 0`, (1) and (2) imply that some such half spans at most

```text
c a^2 + (h/2)(ab-a^2).                       (3)
```

Consequently, any counterexample necessarily satisfies the sharper numerical
condition

```text
(c-h/2)M + (h/2)ab > n^2/50,                 (4)
```

and hence, whenever the numerator is positive,

```text
M > (n^2/50 - (h/2)ab)/(c-h/2).              (5)
```

Thus (4)--(5) are not merely an independence-number test: they force many
edges between every maximum independent set and its complement.

## General consequence

**Theorem.**  If a triangle-free `n`-vertex graph has
`alpha(G) <= n/6`, then it has a set of `floor(n/2)` vertices spanning at
most `n^2/50` edges.

**Proof.**  The case `n=0` is immediate.  Assume `n>0` and apply (3).  Put `x=a/n` and
`r_0=n/2-a`.  We have `r <= r_0`,

```text
r/b <= r_0/b,
r(r-1)/(b(b-1)) <= (r/b)^2 <= (r_0/b)^2.
```

The right side of (3) is therefore at most

```text
(r_0/b)a^2 + (r_0/b)^2 (ab-a^2)/2
  = n^2 * x(1-2x)/(8(1-x)^2).                (6)
```

For `0 <= x <= 1/6`,

```text
1/50 - x(1-2x)/(8(1-x)^2)
  = (6x-1)(9x-4)/(200(x-1)^2) >= 0.
```

The average in (1) is therefore at most `n^2/50`, so at least one of the
sampled sets has the required edge count.  This argument covers odd `n`
without relaxation error because only `r <= r_0` was used.  QED.

Combining this with Razborov's theorem for `alpha(G) >= 2n/5`, every possible
counterexample must lie in the strict window

```text
n/6 < alpha(G) < 2n/5.                       (7)
```

In integral form, `floor(n/6)+1 <= alpha(G) <= ceil(2n/5)-1`.

## A literature-based improvement of the lower endpoint

The preceding elementary endpoint `1/6` is not the best consequence of the
known general theory.  This is a consequence of Theorem 3.4 in Razborov's
[*More about sparse halves in triangle-free graphs*](https://arxiv.org/abs/2104.09406),
not a new result of this note.

Put

```text
rho_0 = (33-sqrt(161))/116 = 0.1750984694... .
```

Razborov proves the sparse-half conjecture whenever the normalized edge
density

```text
rho(G) = 2e(G)/n^2
```

is at most `rho_0`.  In a triangle-free graph every vertex neighbourhood is
independent.  Consequently

```text
rho(G) = average_degree(G)/n
       <= maximum_degree(G)/n
       <= alpha(G)/n.
```

It follows immediately that the conjecture holds whenever

```text
alpha(G)/n <= rho_0.                          (7a)
```

Razborov states his result for weighted halves.  This gives exactly the
floor-sized set needed here: for even `n` an extremal weighted half is a
zero-one half, while for odd `n` it has `floor(n/2)` vertices of weight one
and one vertex of weight one half; deleting the latter cannot increase its
edge weight.  Thus there is no parity or asymptotic qualification in (7a).

Combining (7a) with the upper independence-number reduction, every
counterexample in fact lies in

```text
(33-sqrt(161))/116 < alpha(G)/n < 2/5.        (7b)
```

In particular, the interval from `1/6` through `rho_0` is closed at every
order.  The conditioned-half lemma remains useful as an elementary proof of
the weaker endpoint and for its explicit cross-edge constraint, but it should
not be quoted as the current best lower endpoint.

## Optimizing how much of `I` to retain

The preceding proof takes all of `I`.  More generally, choose a uniform
`s`-subset `J` of `I` and, independently, a uniform `t`-subset `R` of
`V\I`, where `t=k-s`.  Then

```text
E e(J union R) = A M + B L,
A = st/(ab),   B = t(t-1)/(b(b-1)).           (8)
```

There is also a lower bound `M >= b`: every outside vertex has a neighbour
in the maximum independent set `I`, since otherwise it could be added to
`I`.  Put `C=A-B/2`.  Maximizing (8), subject only to

```text
b <= M <= a^2,   2L+M <= ab,
```

is therefore exact at an endpoint of the allowed `M` interval and gives the
finite envelope

```text
U(n,a,s) = C a^2 + B ab/2,   if C >= 0,
U(n,a,s) = C b   + B ab/2,   if C < 0.        (9)
```

Thus every integer `s in [0,a]` can be optimized without a graph search.
The sign change occurs exactly at

```text
s = a(k-1)/(2n-a-2).                         (10)
```

The continuous relaxation shows that this extra freedom does not enlarge
the asymptotic interval proved above.  Write `x=a/n`, `y=s/n`, and
`z=1/2-y`.  Ignoring the lower endpoint `M>=b`, which is lower order after
division by `n^2`, set

```text
A = yz/(x(1-x)),   B = z^2/(1-x)^2.
```

The sign boundary `A=B/2` is

```text
y_0 = x/(2(2-x)).
```

For `y <= y_0`, the worst envelope decreases to

```text
x(1-x)/(2(2-x)^2).
```

For `y >= y_0`, it is

```text
x(2y-1)(2x-2y-1)/(8(x-1)^2),                 (11)
```

a concave quadratic in `y`.  Hence its minimum on this interval is at
`y=y_0` or `y=x`.  The boundary value minus the value at `y=x` is

```text
-x^3(2x-3)/(8(x-2)^2(x-1)^2) > 0
```

for `0<x<2/5`.  The unique optimum in the relevant continuous range is
therefore `y=x`, i.e. retaining all of `I`, and (11) reduces to the function
in (6).  It meets `1/50` at `x=1/6` (and next at `x=4/9`, outside
Razborov's counterexample range).  Consequently the elementary bounds
`M<=a^2` and `2L+M<=ab`, even after full optimization over `s`, cannot
improve their own asymptotic window

```text
1/6 < alpha(G)/n < 2/5.                      (12)
```

Finite floors do give a small exact strengthening.  Taking `s=a` in (9),
if `n=6u+3` or `n=6u+5` and `a=u+1=ceil(n/6)`, the slack in (3) is,
respectively,

```text
n^2/50-U(n,a,a)
 = (40u^3+287u^2+157u+18)/(50(5u+1)(5u+2)),

n^2/50-U(n,a,a)
 = (310u^3+757u^2+595u+150)/(50(5u+3)(5u+4)).
```

Both are positive.  Hence at orders congruent to `3` or `5` modulo `6`, a
counterexample must in fact have `alpha(G) >= floor(n/6)+2`; at the other
residue classes the uniform all-order conclusion remains
`alpha(G) >= floor(n/6)+1` (apart from irrelevant sporadic small-order gains
obtainable directly from (9)).

## A general low-cross-degree consequence of the block classification

There is a second all-order reduction in the lower part of the remaining
window.  Extend a putative counterexample to a maximal triangle-free graph,
let `I` be a maximum independent set of size `a`, and write

```text
delta_I = min_{v outside I} |N(v) intersect I|.
```

**Lemma.**  If `a <= 3n/10`, then

```text
delta_I <= floor((a-1)/2).                    (13)
```

For odd `a`, if every outside vertex had at least `(a+1)/2` neighbours in
`I`, the `I`-neighbourhoods of the endpoints of any outside edge could not be
disjoint.  Thus `G-I` would be independent.  But `|V\I|=n-a>a`, contrary to
maximality of `I`.

Now let `a` be even and suppose, towards a contradiction, that every outside
vertex has at least `a/2` neighbours in `I`.  The complementary-half
classification from `erdos128_order16_human_bridge.md` writes `G-I` as

```text
t K_1 disjoint union K_{p_1,q_1} disjoint union ... disjoint union K_{p_j,q_j},
```

with `p_i<=q_i`.  The isolates have full `I`-type, while the two sides of
each block have complementary `a/2`-types.  Since an independent set obtained
by taking all isolates and the larger side of every block has size at most
`a`,

```text
t + sum q_i <= a.
```

Putting `P=sum p_i` and `b=n-a` gives

```text
P = b-(t+sum q_i) >= b-a = n-2a.             (14)
```

Let

```text
s = max(0, k-(n-2a)),   where k=floor(n/2).
```

Choose any `s`-set `J` in `I`.  In every complementary pair of block types,
one type meets `J` in at most `floor(s/2)` vertices.  Select that side of each
block.  It has at least `p_i` vertices, so (14) supplies at least `n-2a`
vertices in total, and their union is independent in `G-I`.  Because
`k-s <= n-2a`, choose `k-s` of them and call the resulting set `F`.  Then

```text
e(J union F) <= floor(s/2)(k-s).              (15)
```

If `s=0`, this is zero.  Otherwise `k-s=n-2a`, and

```text
s <= 2a-n/2.
```

Writing `x=a/n`, (15) is at most

```text
n^2 (2x-1/2)(1-2x)/2.
```

For `1/4 <= x <= 3/10`,

```text
1/50 - (2x-1/2)(1-2x)/2
  = (10x-3)(20x-9)/100 >= 0.
```

Thus `J union F` is a sparse half, contradicting the counterexample
hypothesis.  This proves (13).

Consequently, in the subwindow

```text
(33-sqrt(161))/116 < alpha(G)/n <= 3/10,
```

every maximal counterexample has a maximum independent set with an outside
vertex whose `I`-degree is strictly below `alpha(G)/2`.  Above `3/10`, the
same elementary disjoint-neighbourhood argument gives only
`delta_I <= floor(a/2)`.

## What minimality adds

There is a useful all-order constraint on a smallest counterexample.  Choose
a counterexample with the fewest vertices and then extend it, at the same
order, to a maximal triangle-free graph.  Its order `n` is even.  Indeed, if
`n=2k+1`, deleting any vertex and applying minimality gives a `k`-set with at
most `(n-1)^2/50<n^2/50` edges in the original graph.

Moreover every vertex `v` satisfies the slightly stronger bound

```text
deg(v) > 1 + 2(n-1)/25.                       (16)
```

First, the same argument with any other vertex shows that `v` cannot be
isolated.  Choose a neighbour `w` of `v` and apply minimality to
`G-{v,w}`, which has even order `n-2`.  It supplies an `(n/2-1)`-set `S`
spanning at most `(n-2)^2/50` edges.  Adding `v` gives a half of `G` with at
most

```text
(n-2)^2/50 + deg(v)-1
```

edges, since the deleted neighbour `w` is not in `S`.  This contradicts the
counterexample property if
`deg(v)-1 <= (n^2-(n-2)^2)/50 = 2(n-1)/25`, proving (16).

For the low-cross-degree vertex `x` above, write

```text
d = |N(x) intersect I|,
D = |N(x) outside I|.
```

Then (16) gives the additional necessary inequality

```text
d+D > 1 + 2(n-1)/25.                          (17)
```

This is stronger than the analogous one-vertex deletion bound
`(2n-1)/50`, but it does not close the low-cross-degree case: the information
`d<a/2` permits `d=a/2-O(1)`, in which regime (17) gives no positive
linear lower bound on `D` throughout the current `a<=3n/10` window.

## Exact audit of conditioning on the exceptional vertex

The most direct attempt to exploit `d<a/2` is to force `x` into the random
half containing `I`.  With the notation of the conditioned-half lemma, let
`D=deg_{V\I}(x)` and select a uniform `(r-1)`-subset of
`(V\I)\{x}`.  The exact expected number of edges is

```text
d + p(M-d+D) + g(L-D),                        (18)
p = (r-1)/(b-1),
g = (r-1)(r-2)/((b-1)(b-2)).
```

(The evident zero-denominator cases are handled directly.)  Formula (18)
accounts respectively for the fixed `x-I` edges, edges with exactly one
random outside endpoint, and edges with two random outside endpoints.

This conditioning cannot close a fixed interval of values of `a/n`.  In
comparison with the unconditioned coefficients

```text
c = r/b,    h = r(r-1)/(b(b-1)),
```

we have `p-c=O(1/n)` and `g-h=O(1/n)`.  Also `d,D=O(n)` while
`M,L=O(n^2)`.  Hence (18) differs from the unconditioned expectation by only
`O(n)`, and after division by `n^2` has exactly the same continuous envelope
(6).  The strict inequality `d<a/2` may have a deficit of only one, so it
does not supply a hidden constant-scale saving.

The two natural induction moves have the same obstruction.  Deleting `x`
retains `I`, so the normalized independence ratio increases rather than
giving a descending parameter; on returning from the odd-order graph one
must add a vertex and can only bound its cost by `deg(x)`, for which (16)
is a lower, not an upper, bound.  Deleting `N[x]` lowers the absolute
independence number, but returning to a half requires adding about
`deg(x)/2` vertices of the independent set `N(x)` and the available
maximum-degree bounds allow a quadratic cross-edge cost.

Thus the low-cross-degree reduction is genuinely isolated at present.  Any
constant-width improvement from it must amplify the one-vertex deficit using
additional structure--for example, prove that a positive proportion of the
outside vertices have `I`-degree bounded away from `a/2`, or classify the
near-boundary types `a/2-O(1)`.  Conditioning on only `I union {x}` and the
plain deletion/induction moves cannot provide such an amplification.

## Why the order-16 bridge does not yet close the window

The pair-density lemma in `erdos128_order16_human_bridge.md` uses the density
of `I union {x,y}`.  Its premise follows from the problem only when
`|I|+2 >= floor(n/2)`.  Under `alpha(G)<2n/5`, this already fails at orders
20 and 22, and uniformly from order 24 onward (orders 21 and 23 are small
parity exceptions).  Averaging completions of `I union {x,y}` introduces edges
incident with the extra vertices, and the present degree bounds do not recover
the pair-density premise.

The complementary-half classification remains fully general at its boundary:
when `a` is even and every outside vertex has at least `a/2` neighbours in
`I`, the complement is a union of complementary complete-bipartite type
blocks and full-type isolates.  The unresolved step is to force this boundary
case, or to control the substantially broader case in which the minimum
`I`-degree is strictly below `a/2`.  The dense-half hypothesis has not yet
provided such a lower bound.
