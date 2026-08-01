# Erdős 128: a human bridge for the order-16 residual case

## Status and boundary

This is **not a solution of Erdős Problem 128**.  It replaces the three
order-16 solver calls by a short combinatorial proof, conditional on the same
upstream reduction already documented in `experiments/erdos128/RESULTS.md`:

1. Razborov's theorem gives `alpha(G) <= 6` for an order-16 counterexample;
2. completeness of McKay's `(3,6,16)` catalogue, plus the retained checker,
   excludes `alpha(G) <= 5`;
3. after maximal triangle-free extension, the same catalogue exclusion
   ensures that the extended counterexample still has `alpha(G)=6`.

Only the last residual implication is proved here:

> A maximal triangle-free graph on 16 vertices with independence number six
> has an eight-vertex set spanning at most five edges.

Since `5 <= 16^2/50 < 6`, this is exactly the required order-16 sparse half.

## Lemma 1: pair-density bridge

Let `G` be triangle-free, let `I` be an independent set of size `a`, put
`O=V(G)\I`, and fix `x in O`.  Write

`d=|N(x) intersect I|`.

Suppose every `I union {x,y}`, for `y in O\{x}`, spans at least `q` edges.
If

`2(q-d)-1 > a`,

then `O\{x}` is independent.

Indeed, density gives

`|N(y) intersect I| + 1_xy >= q-d`

for every such `y`.  If `yz` were an edge, triangle-freeness would give both

- `(N(y) intersect I) intersect (N(z) intersect I) = empty`, and
- `1_xy + 1_xz <= 1`.

Consequently

`a >= |N(y) intersect I| + |N(z) intersect I| >= 2(q-d)-1`,

a contradiction.

For order 16, take `a=6` and `q=6`.  If the minimum `I`-degree `d` of an
outside vertex is one or two, the displayed left side is respectively nine
or seven.  Hence the other nine outside vertices would be independent,
contradicting `alpha(G)=6`.  Notice that this argument does not use
maximality or a solver.

## Lemma 2: complementary-half classification

Let `G` be maximal triangle-free, let `I` be independent of size `2d`, and
assume every vertex outside `I` has at least `d` neighbours in `I`, where
`d>=1`.  For `v outside I`, put `S_v=N(v) intersect I`.

Then `G-I` is a disjoint union of complete bipartite blocks between
complementary `d`-subsets of `I`, together with isolated vertices adjacent to
all of `I`.

Proof:

- If `uv` is an outside edge, triangle-freeness makes `S_u` and `S_v`
  disjoint.  Their sizes are at least `d` in a universe of size `2d`, so both
  have size `d` and are complementary.
- If `S_u` and `S_v` are complementary `d`-sets but `uv` is absent,
  maximality supplies a common neighbour.  It cannot lie in `I`, and an
  outside common neighbour would have an `I`-neighbourhood disjoint from all
  of `I`, contradicting the lower bound `d`.  Thus every complementary pair
  of types is complete bipartite.
- If `|S_v|>d` but `S_v` is not all of `I`, choose `i in I\S_v`.
  Maximality of the nonedge `iv` supplies an outside common neighbour `w`.
  Then `S_w` is disjoint from `S_v`, impossible because
  `|S_w|+|S_v|>2d`.
- If `|S_v|=d`, applying the same argument to any `i in I\S_v` produces an
  outside vertex of complementary type.  Thus every occurring half-type has
  a nonempty complementary side.

This classification is parameterized; it is not specific to 16 vertices.

## The remaining `d=3` case

Let `I` have size six and `O` size ten.  If every outside vertex had at least
four neighbours in `I`, then any two such neighbourhoods would intersect,
so `O` would be independent, contradicting `alpha(G)=6`.  Thus the minimum
`I`-degree is at most three.  Lemma 1 handles one and two.  In the last case,
Lemma 2 says

`G[O] = t K_1 disjoint union K_{p_1,q_1} disjoint union ...`,

where `1 <= p_j <= q_j`; each nontrivial block corresponds to a pair of
complementary triples, and each of the `t` isolated vertices is adjacent to
all six vertices of `I`.  Moreover

`t + sum q_j = alpha(G[O]) <= 6`,

and

`t + sum(p_j+q_j)=10`.

If some eight vertices of `O` span at most five edges, the proof is finished.
Assume otherwise.  Deleting any two vertices from the displayed union must
leave at least six block edges.  Put `P=sum p_j`.  The two preceding equations
give `4 <= P <= 5`.

- If `P=5`, equality forces `t=0` and `p_j=q_j` for all `j`.  The partitions
  of five survive the two-vertex deletion test only as `5`, `4+1`, and
  `3+2`.
- If `P=4`, then `sum q_j=6-t`, with `t=0,1,2`.  Distributing the surplus
  `sum(q_j-p_j)=2-t` over the partitions of four and applying the same
  deletion test leaves the seven additional rows below.

Thus the only possible size profiles are:

| isolated `t` | complete-bipartite blocks | an eight-set with at most 3 edges |
|---:|---|---|
| 0 | `K(1,1)+K(3,5)` | five vertices in the side of size five |
| 0 | `K(1,1)+K(4,4)` | four in one large side, one low-intersection singleton |
| 0 | `K(1,2)+K(3,4)` | four in the large side, one low-intersection vertex |
| 0 | `K(1,3)+K(3,3)` | three in the `K(1,3)` large side, two from a suitable side of `K(3,3)` |
| 0 | `K(2,2)+K(3,3)` | three in a `K(3,3)` side, two from a suitable `K(2,2)` side |
| 0 | `K(2,3)+K(2,3)` | three in one large side, two from a suitable side of the other block |
| 0 | `K(4,6)` | five vertices in the side of size six |
| 0 | `K(5,5)` | five vertices in one side |
| 1 | `K(4,5)` | five vertices in the side of size five |
| 2 | `K(4,4)` | four vertices in one side and one isolated vertex |

Here each advertised set contains five outside vertices.  Complete it to
eight vertices as follows.  For the first chosen block side, whose common
`I`-neighbourhood is the triple `A`, take the triple `J=I\A`.  Its vertices
have no neighbours in that side.  For any other complementary type pair
`B,I\B`,

`|J intersect B| + |J intersect (I\B)| = 3`,

so one orientation has intersection at most one.  The table always provides
enough vertices in that orientation; the only exceptional fill is the last
row, where a full-type isolated vertex contributes exactly three cross
edges.  The five outside vertices lie in at most one side of each block, so
they induce no edge.  Therefore every row supplies an eight-set `J union F`
with at most three edges, contradicting the assumed lower bound six.

This closes `d=3`, and hence the entire maximal `alpha=6` residual case.

## Adversarial checks

`verify_128_bridge_lemmas.py` exhaustively checks Lemmas 1 and 2 over all
33,868 labelled graphs through order six.  It checks 558,687 instances of
Lemma 1 and 654 applicable instances of Lemma 2.  The profile generator
independently enumerates the integer block equations and deletion condition,
returning exactly the ten rows above.

```powershell
python research/full_solution_bridges/verify_128_bridge_lemmas.py
python research/full_solution_bridges/enumerate_128_d3_profiles.py
```
