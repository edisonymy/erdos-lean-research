# Cycle 3 — local extension structure at a degree-three vertex

Status: PROVED structural lemma; not a full proof.

Mechanism fingerprint:

* representation: partial 20-colour strong edge-colourings and list systems;
* central lemma: a degree-three vertex is either extendable or completely
  palette-locked;
* search object: the three available-colour lists at its incident edges;
* checker: Hall's theorem plus a definition-level count of coloured strong
  neighbours;
* predicted obstruction: all three lists collapse to the same two colours.

## Lemma

Let `G` be a smallest-order finite simple subquartic graph with no strong
20-edge-colouring.

1. `delta(G) >= 3`.
2. If `v` has degree three, then for every strong 20-edge-colouring `phi` of
   `G-v`, the three uncoloured edges at `v` have identical available-colour
   lists, each of size exactly two.
3. Every vertex at distance one or two from such a `v` has degree four.
   Moreover, the counting neighbourhoods attaining the bound below are
   edge-disjoint; in particular no triangle or 4-cycle contains `v`, and no
   triangle contains one of its neighbours together with two of that
   neighbour's other neighbours.
4. Consequently, distinct degree-three vertices of `G` are at distance at
   least three.

## Proof

By minimality, `G-v` has a strong 20-edge-colouring. Let `e=vu`, where
`d(v)=d`. Among already coloured edges, `e` sees at most

* three edges incident with `u`;
* three further edges at each of the at most three neighbours of `u` other
  than `v`, for at most nine; and
* three further edges at each of the `d-1` other neighbours of `v`.

Thus `e` sees at most `3+9+3(d-1)=9+3d` coloured edges.

If `d<=2`, every incident edge initially has at least five available colours.
Colouring the at most two edges successively loses at most one further colour,
so the colouring extends. This proves `delta(G)>=3`.

Now let `d=3`. Each of the three incident edges has an available list of size
at least two. Three sets of size at least two fail Hall's condition for a
system of distinct representatives only when their total union has size at
most two; hence all three sets must be the same two-element set. If any
colouring of `G-v` avoided this condition, its distinct representatives would
extend the colouring to `G`, so the palette lock holds for every colouring.

For each incident edge, exactly the other 18 colours occur among at most 18
coloured edges that it sees. Therefore all 18 counted edges exist, are
distinct, and receive distinct colours. Equality forces degree four at `u`,
at the other two neighbours of `v`, and at every other neighbour of `u`.
Applying this to all three incident edges gives degree four throughout the
distance-two ball. Any triangle or 4-cycle described above would make one
edge appear in two of the three counting groups, contradicting equality.
The distance assertion for degree-three vertices follows immediately.

## Packing corollary

If such a smallest counterexample has `n` vertices and exactly `t`
degree-three vertices, then

`3t <= n-t`, hence `n >= 4t`.

Indeed, every neighbour of a degree-three vertex has degree four, and the
three-element neighbourhoods of distinct degree-three vertices are disjoint
because those vertices have distance at least three.  All these
neighbourhoods therefore lie disjointly inside the `n-t` degree-four
vertices.

For `n=13`, the degree sum gives `t=52-2|E(G)|`, which is even.  The packing
corollary gives `t<=3`, hence `t` is either zero or two.  Thus an order-13
smallest counterexample must have 26 or 25 edges; edge counts 22, 23 and 24
are excluded structurally.

## Audit and next implication

`audit_local_extension.py` exhausts the abstract three-list Hall condition.
The lemma does not eliminate degree-three vertices in general: the
common-two-colour palette lock is a real remaining obstruction, not something
silently assumed away.  At order 13, however, its neighbourhood-packing
consequence reduces the nonregular residual to the degree sequence
`4^11 3^2`.
