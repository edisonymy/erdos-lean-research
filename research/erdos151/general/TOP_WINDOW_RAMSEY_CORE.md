# Top-window Ramsey-core saturation inequality

**Status (2 August 2026).** Campaign-derived theorem. The proof was
independently reconstructed by the primary campaign agent and a second
adversarial agent; both audits found no defect. This result does not claim a
full solution of Erdos #151, and no claim of literature priority is made.

## Theorem

Let `G` be a least-order counterexample to Erdos #151. Put `h=H(n)`,
`r=h-1`, and suppose `G` is at the top of its first-counterexample window:

`n = R(3,h-1) + r`.

Write `R=R(3,h-1)`. Then `G` is `r`-regular. Let `Q` be an edge-minimal
subgraph of `G` satisfying `Q -> (3,3)`, chosen without isolated vertices.
For every `v in V(Q)`, with `d=d_Q(v)`,

`d(r+1) <= 2r(r-1) - 2R`.                         (1)

In particular, a least counterexample with `h=8` cannot have order 30.

## Proof

First recall the needed reductions. An open neighbourhood is admissible, so
`Delta(G)<=beta(G)<=r`. The independent-set recurrence at a vertex and
least-order minimality give

`r >= beta(G) >= 1+H(n-1-deg(v))`.

Thus `n-1-deg(v)<R(3,h-1)`, or `deg(v)>=n-R(3,h-1)=r` at the top of the
window. Hence `G` is exactly `r`-regular.

Also `G -> (3,3)`. Otherwise choose a red/blue edge-colouring with no
monochromatic triangle. Let `M` be the red edges and `L` the edges contained
in no triangle. The spanning graph `J=L union M` is triangle-free. Every
maximal 2-clique of `G` contributes its edge to `L`, and every larger maximal
clique contains a triangle and hence an `M`-edge. Therefore any independent
`H(n)`-set of `J` is admissible in `G`, a contradiction. This supplies the
edge-minimal arrowing subgraph `Q`.

Finally, regularity gives the two-sided swap used below. For nonadjacent
`v,x`, the `h`-set `N_G(v) union {x}` must contain a nontrivial maximal
clique. Such a clique must contain `x`, since a clique inside `N_G(v)` extends
by `v`, so `v,x` have a common neighbour. If it is uniquely `a`, then `xa`
is a maximal edge. Applying the same argument to `N_G(x) union {v}` proves
that `va` is maximal as well. Thus both edges lie in no ambient triangle.

### 1. Saturation of the minimal Ramsey core

Every edge `e` of `Q` lies in at least two `Q`-triangles. Indeed, colour
`Q-e` with no monochromatic triangle. If `e` lies in no triangle, colour it
arbitrarily. If it lies in one triangle, colour it opposite to the common
colour of the other two edges when those agree, and arbitrarily when they do
not. Either case extends the colouring to `Q`, contradicting arrowing.

Fix `v in V(Q)`, write `d=d_Q(v)`, and let `t_Q(v)` be the number of
`Q`-triangles containing `v`. The link `Q[N_Q(v)]` has minimum degree at
least two, so `t_Q(v)>=d`. Equality would make the link a disjoint union of
cycles. Colour `Q-v` with no monochromatic triangle. Orient each link cycle.
For every oriented link edge `a -> b`, colour the spoke `vb` opposite to the
colour of `ab`. Every link vertex has one incoming edge, so this assigns one
consistent colour to every spoke; and every triangle through `v` contains an
edge and a spoke of opposite colours. This would extend the good colouring to
`Q`. Hence

`t_Q(v) >= d+1`.                                   (2)

Also `chi(Q)>=6`: a proper 5-colouring would pull back the standard
red-`C5`/blue-complement-`C5` colouring of `K5`, producing a good edge
colouring of `Q`. Consequently `Delta(Q)>=5`.

### 2. Ambient two-walk pressure

Let `t=t_G(v)`. The vertex `v` has `n-1-r=R-1` ambient nonneighbours.
Counting nonbacktracking two-walks from `v` gives

`sum_{x notin N_G[v]} c_G(v,x) = r(r-1)-2t`.        (3)

Let `u` be the number of these nonneighbours having exactly one common
neighbour with `v`. Every other summand in (3) is at least two, so

`u >= 2(R-1)-r(r-1)+2t`.

Since `Q` is a subgraph of `G`, (2) gives

`u >= 2(R-1)-r(r-1)+2(d+1)`.                       (4)

For a pair counted by `u`, let `a` be its unique common neighbour. The
two-sided regular swap says `va` lies in no ambient triangle. Thus `a` cannot
belong to `N_Q(v)`, because every `Q`-edge is in at least two `Q`-triangles.
All such pairs are therefore routed through

`B=N_G(v)\N_Q(v)`, with `|B|=r-d`.

For a fixed `a in B`, at most `r-1` vertices can be routed through `a`,
because they are neighbours of `a` other than `v`. Hence

`u <= (r-d)(r-1)`.                                 (5)

Combining (4) and (5) and simplifying yields (1):

`2(R-1)-r(r-1)+2(d+1) <= (r-d)(r-1)`,

so

`d(r+1) <= 2r(r-1)-2R`.

## Consequences

For `h=8`, `r=7` and `R=R(3,7)=23`. Inequality (1) becomes `8d<=38`,
so every vertex of `Q` would have degree at most four. This contradicts
`Delta(Q)>=5`. Therefore order 30 cannot be the order of a least
counterexample.

Together with the proved through-order-27 result and the window
`n in {28,29,30}`, it is enough to search orders 28 and 29: if neither has a
counterexample, order 30 is automatically excluded. This does **not** assert
unconditionally that no 30-vertex counterexample exists before orders 28 and
29 are cleared.

| `h` | `r` | `R(3,h-1)` | ceiling on `Delta(Q)` |
|---:|---:|---:|---:|
| 7 | 6 | 18 | 3 |
| 8 | 7 | 23 | 4 |
| 9 | 8 | 28 | 6 |

The `h=7` row supplies a short alternate top-order-24 proof. At `h=9`, the
remaining ceiling six points toward a 6-critical/Gallai analysis rather than
an immediate chromatic contradiction.
