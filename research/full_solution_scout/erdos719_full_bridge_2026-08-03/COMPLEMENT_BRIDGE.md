# Exact complement-cover bridge for Erdős #719

This is a proved all-parameter reformulation, not a solution.

## The bridge

Fix `n>=r+1` and put `s=n-r`.  Complementation identifies each `r`-edge of
`G` with an `s`-set.  Let `F` be the resulting `s`-graph and let `H` be its
missing `s`-sets; write `h=|H|`.

An `r`-simplex `K_{r+1}^r` on vertex set `W` corresponds to the
`(s-1)`-set

```text
A=V\W.
```

Its `r+1` edges correspond exactly to all `s`-sets containing `A`.  Hence the
simplex is present precisely when `A` is uncovered by `H`.  Let `U(H)` be the
family of uncovered `(s-1)`-sets.

Two such simplices are edge-disjoint precisely when their `(s-1)`-sets
`A,B` are not contained in a common `s`-set, equivalently

```text
|A intersect B| <= s-3.
```

Thus `nu(G)` is exactly the maximum size `rho(U)` of a subfamily of `U(H)`
with pairwise intersections at most `s-3`.

Finally, `G` is simplex-free exactly when `H` covers every `(s-1)`-set.
Writing `C(n,s,s-1)` for the minimum size of such a covering,

```text
ex_r(n,K_{r+1}^r)=C(n,s)-C(n,s,s-1).
```

Since `|G|=C(n,s)-h`, the conjectured inequality is exactly

```text
h+(n-s)rho(U(H)) >= C(n,s,s-1).                 (CB)
```

This reformulation is definition-level and valid for every parameter.

## Completion lemma that would finish the conjecture

Let `tau_s(U)` be the fewest `s`-sets whose lower shadows cover `U`.  Since
`H` together with such a completion covers all `(s-1)`-sets,

```text
h+tau_s(U(H)) >= C(n,s,s-1).
```

Consequently the following purely design-theoretic statement would prove
#719 in full:

```text
tau_s(U) <= (n-s)rho(U)
```

for every realizable uncovered family `U=U(H)`.  The adjective realizable is
essential: a generic set family need not be the zero-codegree family of a
partial covering.

No proof of this completion lemma was obtained.  It is the precise global gap,
not a numerical or formalization gap.

## Two proved boundary facts

### Packing number at most one never refutes #719

If the present simplices have matching number one, their `(r+1)`-vertex sets
pairwise share an `r`-edge.  A family of sets pairwise intersecting in all but
one point either has a common `r`-set or is contained in one fixed `(r+2)`-set.

In the first case one `r`-edge hits every simplex.  In the second case at most
`ceil((r+2)/2)<=r` `r`-edges hit all the simplices: represent an `r`-edge by
the pair omitted from the fixed `(r+2)`-set and take an edge cover of those
`r+2` vertices.  Deleting at most `r` edges therefore makes `G` simplex-free,
so

```text
|G|-r nu(G) <= ex_r(n,K_{r+1}^r).
```

This proves the conjecture whenever `nu<=1` and justifies starting any
counterexample hunt at packing number two.

### Greedy core deletion leaves only a one-unit-per-core gap

Delete the `r+1` edges of all but one member of a maximum `k`-packing.  The
remaining graph has packing number one, so the previous fact gives

```text
|G| <= ex_r(n,K_{r+1}^r)+(r+1)k-1.
```

A counterexample would also require

```text
|G| >= ex_r(n,K_{r+1}^r)+rk+1.
```

The universal problem is therefore exactly the missing saving of one edge per
packing member.  A generic transversal inequality such as `tau<=r nu` would
be stronger than necessary and runs into Tuza-type barriers already for
graphs.

## Design averaging

When a Steiner system `S(r,r+1,n)` exists, its blocks partition all `r`-edges.
Randomly relabeling one fixed system shows that if `q(G)` is the number of
present simplices, then

```text
q(G) <= (n-r)nu(G).
```

This is the all-parameter source of the `q<=7nu` squeeze at `r=3,n=10`.
It is a strong finite filter, but by itself does not imply (CB).
