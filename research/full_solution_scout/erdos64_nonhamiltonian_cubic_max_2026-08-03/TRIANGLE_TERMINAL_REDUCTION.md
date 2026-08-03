# Adjacent-terminal triangle reduction

## Setting

Let `B` be a connected finite simple graph with one distinguished vertex `t`
of degree two and every other vertex of degree three.  Write
`N(t)={u,v}` and suppose, unlike the predecessor's simple suppression case,
that `uv` is an edge.

Let `a` be the third neighbour of `u`, so

```text
N(u) = {t,v,a},
```

and let `b` be the third neighbour of `v`.

## Forced-square alternatives

If `a=b`, then

```text
t-u-a-v-t
```

is a simple four-cycle.  If `a` and `b` are distinct but adjacent, then

```text
a-u-v-b-a
```

is a simple four-cycle.  Therefore any dyadic-cycle-free block in this
adjacent-terminal case must have `a != b` and `ab` absent.

## Triangle-reduction lemma

Under those necessary conditions, delete `t,u,v` and their incident edges and
add the edge `e=ab`.  The resulting graph `K` is finite, simple, connected,
and cubic.  Conversely, replacing a marked edge `ab` of a simple cubic graph
by the five-edge gadget

```text
a-u, u-v, v-b, u-t, t-v
```

produces an exact `(2,3,...,3)` block whose terminal neighbours are adjacent.

The simple cycles correspond as follows.

- The gadget has its internal triangle `t-u-v-t`, of length three.
- Every cycle of `K` avoiding `e` remains unchanged in `B`.
- Every length-`L` cycle of `K` containing `e` gives exactly two cycles in
  `B`: replace `ab` by `a-u-v-b`, giving length `L+2`, or by
  `a-u-t-v-b`, giving length `L+3`.
- Every non-triangle cycle of `B` arises in exactly one of these ways: a
  simple cycle that enters the gadget at `a-u` and leaves at `v-b` must use
  exactly one of the two internally disjoint `u-v` paths.

Consequently `B` has no dyadic cycle if and only if its marked cubic graph
`(K,e)` satisfies both conditions:

1. every dyadic cycle of `K` contains `e`; and
2. `e` lies in no cycle of length `2^k-2` or `2^k-3`.

Equivalently, the eligible marked edges are

```text
(intersection of all dyadic-cycle edge sets)
minus
(union of the edge sets of all cycles of lengths 2^k-2 or 2^k-3).
```

The first condition alone makes an empty dyadic edge core a complete
rejection certificate.

## Exact finite consequence

The canonical census and its full order-22 successor prove that every
connected simple cubic graph through order 22 has empty dyadic edge core.
Since the triangle reduction lowers block order by three, no connected exact
one-defect block with adjacent terminal neighbours exists through block order
25.

Together with the predecessor's suppression lemma and the full simple-cubic
census through order 20, this gives:

- no non-triangular-terminal exact one-defect block through order 23; and
- no triangular-terminal exact one-defect block through order 25.

The earlier separate non-Hamiltonian catalogue check is now subsumed by the
complete order-22 census, which includes all Hamiltonian and non-Hamiltonian
connected cubic graphs.

Disconnected blocks require no extra case: discard every component not
containing `t`.  The retained terminal component has the same degree pattern
and cycle avoidance, so a minimal block may be assumed connected.
