# Independent adversarial audit of the K4-free order-40 reduction

**Audit date:** 2 August 2026  
**Verdict:** **PASS.**  I found no mathematical defect in the conditional
order-40 proof.  This verdict is restricted to the `K4`-free lane and relies
on the already-audited order-41 core lemmas and their cited Bikov input.

Precisely, the audited claim is:

> If `R(3,10)=40`, then every `K4`-free graph `G` on 40 vertices satisfies
> `beta(G)>=10`.

If instead `R(3,10)=41`, the required order-40 lower bound is only nine and
follows from the verified order-39 theorem by induced-subgraph monotonicity.
Thus the two alternatives together clear the order-40 `K4`-free lane for
Erdős #151.  They do not clear the clique-number-four or clique-number-five
lanes and do not solve the full problem.

## 1. Entry hypotheses and the ambient/core separation

Under `R(3,10)=40`, a putative order-40 graph with `beta(G)<=9` is a
least-order counterexample because the conjecture has been verified through
order 39.  Consequently the degree floor used later is legitimate:

`4 <= delta(G) <= Delta(G) <= 9`.

The Folkman reduction supplies an arrowing subgraph, and an
inclusion-minimal arrowing core `Q` is a minimal `(3,3)`-Ramsey graph in the
sense needed by Bikov.  Since `G` is `K4`-free, `omega(Q)=3`.  The audited
order-41 argument therefore gives `d_Q in {8,9}`, at least ten core triangles
through every core vertex, and, for a core vertex of ambient degree nine,

`t_G(v)=10` and `sum_{a in N_G(v)}(9-d_G(a))<=1`.

Nothing in the new argument silently treats `Q` as induced.  In particular,
if `H=G[V(Q)]`, the set `F=E(H)-E(Q)` is retained explicitly in the
small-remainder argument.

## 2. Boundary fibres and ambient maximality

For `x` outside `Q`, put `B_x=N_G(x) intersect V(Q)`.  If `v in B_x`, then
`d_Q(v)=8` and the edge `vx` exhausts the one ambient incidence available
beyond `Q`.  Thus `d_G(v)=9`.  Comparing the Bikov lower bound
`t_Q(v)>=10` with the order-40 equality `t_G(v)=10` proves all of the needed
rigidity:

- `t_Q(v)=10`;
- `x` is anticomplete to `N_Q(v)`;
- `vx` is an ambient-maximal edge;
- `B_x` is independent not just in `Q` but in the ambient graph; and
- the deficiency inequality gives `d_G(x)>=8`.

The fibres are pairwise disjoint.  A boundary vertex has no capacity for an
ambient edge outside its eight core edges and its one boundary edge.  This
last observation is what makes the later ambient-admissibility arguments
valid even though `Q` need not be induced.

For distinct outside vertices `x,y`, the union `B_x union B_y` is
triangle-free.  Every edge it contains is a core edge and hence extends to a
core triangle, so none is ambient-maximal.  The union is therefore
ambient-admissible.  It is anticomplete to the induced remainder on the
other `r-2` outside vertices.  An admissible set in that induced remainder
is also ambient-admissible: any ambient-maximal clique contained in it would
remain maximal in the induced graph.  This verifies the full quantifier
chain behind

`w_x+w_y <= 9-h_{r-2}`.

## 3. Incidence, Turán, and the integer funnel

I re-derived the incidence inequality without assuming that distinct
boundary vertices contribute distinct pairs.  Counting distinct pairs
`(v,x)` with `N_Q(v) intersect B_x` nonempty gives

`q(r-2)+2b <= 8c`.

The right side is an upper bound because a boundary vertex lies in eight
open core neighbourhoods; equality is not assumed at this stage.  The same
remainder argument gives at least `r-2` nonempty fibres, and all `r` are
nonempty if a core-degree-nine vertex exists.

For a nonempty fibre, boundary rigidity gives
`d_R(x)>=8-w_x`; for an empty fibre the least-counterexample degree floor
gives `d_R(x)>=4`.  Summing degrees and applying the exact Turán bound
`ex(r,K4)=floor(r^2/3)` yields

`c >= 4r+4s-2 floor(r^2/3)`.

Together with `c<=q-b` and the fibre-pair bound, these inequalities leave
only

- `r=8`, with eight fibres of size three and `b=0`; and
- `r=10`, with ten fibres of size three and `b=0`.

I reran `check_order40_reduction.py`; it exhausts all sorted nonnegative
integer fibre vectors in the pair-bound box and returned exactly these two
rows.  Allowing odd values of `b` in the checker only relaxes the true
handshaking constraint, so it cannot create a false exclusion.

## 4. Equality row `r=10`

Here all 30 core vertices are boundary vertices.  Each has ten core
triangles, so `Q` has exactly 100 triangles.  A core triangle meets three
distinct fibres, while there are 120 triples of fibres.  Even allowing many
triangles to use the same fibre triple, at most 100 triples can be supported;
hence some triple supports none.  The union of its three fibres is a
triangle-free ambient-admissible nine-set.  Any outside vertex belonging to
one of the other seven fibres is anticomplete to it, and adding that vertex
gives an admissible ten-set.  No non-core edge has been overlooked because
every selected boundary vertex is already saturated.

## 5. Equality row `r=8`

Equality in both sides of the incidence count is strong enough for the
claimed local structure.  Every core vertex sees exactly six distinct
fibres, and equality in the multiplicity upper bound forces exactly one
neighbour in each of them.  Its remaining two core neighbours lie in the
eight-vertex set `A` outside all fibres.

For `a in A`, its degree-eight Bikov link has at most 12 edges.  Therefore at
most 12 of the 28 fibre pairs support a triangle through `a`; choose an
unsupported pair `x,y`.  The set

`B_x union B_y union {a}`

is a triangle-free ambient-admissible seven-set.  The potentially dangerous
non-core-edge case is sound: a boundary vertex has no spare incidence, and
any non-core edge at `a` must end in `A`, of which the set contains no other
vertex.  An admissible three-set in the six-vertex induced graph
`G[R-{x,y}]` is anticomplete to this seven-set, producing the required
admissible ten-set.

## 6. Small remainders and the Borodin--Kostochka boundary

The coloring input used here is a proved 1977 consequence, not the open
Borodin--Kostochka conjecture that would force a `K9`.  Borodin and
Kostochka's Corollary 2 implies the needed statement at maximum degree
nine; the modern paper of Galindo and McDonald also records explicitly that
every graph with `chi=Delta=9` contains a `K5`.  Componentwise Brooks plus
that result gives:

`K4`-free and `Delta<=9` implies `chi<=8`.

The `Delta<=8` boundary is covered by Brooks (a 9-chromatic exception would
be a `K9` component), while at `Delta=9` a 9-chromatic component would
contain a `K5`.  Thus the application to the possibly disconnected graph
`H=G[V(Q)]` is valid.

The non-core edges `F=E(H)-E(Q)` form a matching: core-degree-nine vertices
have no spare incidence and core-degree-eight vertices have at most one.
In an eight-coloring of `H`, delete one endpoint of every `F`-edge contained
in a chosen pair of color classes.  What remains is triangle-free and has no
ambient-maximal edge; all surviving edges are core edges and extend to core
triangles.  Summing the guaranteed sizes over all 28 color pairs gives

`7q-|F|`.

For `r=0` this is at least `260`, and for `r=1` at least `254`, both strictly
larger than `28*9=252`.  Hence some pair contains an ambient-admissible set
of size at least ten.  This validates both small-remainder contradictions.

Primary coloring references checked:

- O. V. Borodin and A. V. Kostochka, *On an Upper Bound of a Graph's
  Chromatic Number, Depending on the Graph's Degree and Density*, JCTB 23
  (1977), 247--250, Corollary 2,
  <https://doi.org/10.1016/0095-8956(77)90037-5>.
- R. Galindo and J. McDonald, *On graphs with chromatic number and maximum
  degree both equal to nine*, arXiv:2408.12693, introduction,
  <https://arxiv.org/abs/2408.12693>.

## 7. Reproduction and residual scope

From the repository root:

```text
python experiments/erdos151_siege/k4free_h10/order40/check_order40_reduction.py
```

returned `status: VERIFIED_ARITHMETIC`, with only the `r=8` and `r=10`
rows above.  The executable check covers the integer funnel and displayed
counts only; the graph-semantic proof was audited separately in this note.

An explicit UTF-8 scan of this package found no remaining replacement
characters or mojibake sequences in mathematical names.

**No public-result or novelty claim is made by this audit.**
