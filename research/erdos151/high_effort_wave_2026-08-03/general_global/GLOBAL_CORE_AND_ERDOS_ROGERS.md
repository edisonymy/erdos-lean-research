# Global core saturation and the Erdős--Rogers gateway

**Status: 3 August 2026.**  This is an isolated high-effort research note.
It does **not** resolve Erdős #151, order 40, or order 41.  The statements
labelled **PROVED** below have self-contained proofs except at the explicitly
listed published dependencies.  Finite arithmetic and the one fixed-witness
test are replayed by [`check_global_lemmas.py`](check_global_lemmas.py).
No claim of literature priority is made for the campaign-derived lemmas.

## 1. Definitions and dependency boundary

All graphs are finite and simple.  A nontrivial maximal clique means an
inclusion-maximal clique of order at least two.  A set is **admissible** in
`G` if it contains no nontrivial maximal clique of `G`, and `beta(G)` is the
largest size of an admissible set.  Write `G -> (3,3)` when every red--blue
edge-colouring of `G` contains a monochromatic triangle.  A minimal
`(3,3)`-Ramsey graph has no proper arrowing subgraph; subgraphs here need not
be induced.

For a vertex `v`, write

```text
d_G(v) = |N_G(v)|,
t_G(v) = number of G-triangles containing v,
c_G(v,x) = |N_G(v) intersect N_G(x)|.
```

The following elementary facts will be used repeatedly.

1. `N_G(v)` is ambient-admissible: every clique in it extends by `v`.
   Hence `Delta(G) <= beta(G)`.
2. Admissibility is downward hereditary.  If `F` is induced in `G`, an
   `F`-admissible set is `G`-admissible.
3. `beta` is additive over components.  Indeed, the nontrivial maximal
   cliques of a disjoint union are exactly the nontrivial maximal cliques of
   its components, so a set is admissible exactly when its intersection
   with every component is admissible.  This includes isolated vertices.

### 1.1 Minimal-core facts, with the degree-nine spoke lemma audited

Let `Q` be minimal subject to `Q -> (3,3)`, with no isolated vertices.
Then `Q` is connected, `Q-v` has a good edge-colouring for every vertex
`v`, and every `Q`-edge lies in at least two `Q`-triangles.  For the last
assertion, a good colouring of `Q-e` extends over `e` whenever `e` lies in
zero or one triangle.

Fix `v`, put `d=d_Q(v)`, and let `L=Q[N_Q(v)]`.  Every spoke `vx` belongs to
at least two core triangles, so `delta(L)>=2`.  Thus
`t_Q(v)=e(L)>=d`.  If equality held, every component of `L` would be a
cycle.  Colour `Q-v` well and orient every link cycle.  For an oriented
link edge `a -> b`, colour the spoke `vb` opposite to the colour of `ab`.
Every link vertex has exactly one entering edge, so this assigns one colour
to every spoke; every triangle through `v` contains its link edge and the
oppositely coloured spoke at the head.  This extends the good colouring to
`Q`, a contradiction.  Therefore

```text
t_Q(v) >= d_Q(v)+1.                                      (1.1)
```

This proof works for `d=9`; it does not assume that `Q` is induced.  Also
`chi(Q)>=6`, by pulling back a good red--blue colouring of `K5` along a
proper five-colouring.

### 1.2 Exact Bikov dependency

The primary source was checked directly on 3 August 2026:

* A. Bikov, *Small minimal (3,3)-Ramsey graphs*,
  [arXiv:1604.03716v1](https://arxiv.org/abs/1604.03716), Definition 1.1,
  Theorems 8.1--8.2 and Figures 12--13.

Definition 1.1 uses exactly the proper-subgraph minimality above.  Theorem
8.1 states that `omega(Q)<=4` implies `delta(Q)>=5` (and classifies links at
degree five).  Theorem 8.2 states that `omega(Q)=3` implies
`delta(Q)>=8`, and that a degree-eight link is one of the seven displayed
graphs `N_{8.1},...,N_{8.7}`.  The seven displayed links have respectively

```text
10, 11, 12, 10, 10, 11, 12 edges.                         (1.2)
```

Completeness of the list is a published dependency.  The edge counts in
(1.2) are a Figure 13 transcription boundary, independently replayed in the
existing audited checker
`research/erdos151/general/k4free_h10/INDEPENDENT_AUDIT.md`; the proof below
uses only the lower bound ten.

## 2. PROVED: a uniform degree-saturation inequality

**Theorem 2.1 (degree-`r` neighbourhood cap).**  Let `G` have `n` vertices
and `beta(G)<=r`, and let `v` have degree `r`.  Put

```text
m = n-r-1,
kappa(v) = sum_{a in N_G(v)} (r-d_G(a)).
```

Then

```text
2 t_G(v) + kappa(v) <= r^2-2m.                           (2.1)
```

**Proof.**  Since `N_G(v)` is an admissible `r`-set, every set
`N_G(v) union {x}` with `x` a non-neighbour of `v` is bad.  Its witnessing
maximal clique contains `x`, and hence `c_G(v,x)>=1`.

Suppose `c_G(v,x)=1`, with unique common neighbour `a`.  The witnessing
clique is then exactly the ambient-maximal edge `xa`.  Two distinct such
vertices `x,y` cannot route through the same `a`: maximality of `xa` forces
`xy` to be absent, both vertices are anticomplete to `N_G(v)-{a}`, and

```text
(N_G(v)-{a}) union {x,y}
```

would be an admissible `(r+1)`-set.  Thus, if `u` is the number of
non-neighbours with exactly one common neighbour with `v`, then `u<=r`.

The exact two-walk identity is

```text
sum_{x outside N_G[v]} c_G(v,x)
  = sum_{a in N_G(v)}(d_G(a)-1)-2t_G(v)
  = r(r-1)-kappa(v)-2t_G(v).
```

The `m` summands are at least one, and all but the `u` exceptional summands
are at least two.  Hence the left side is at least
`u+2(m-u)=2m-u>=2m-r`.  Rearranging gives (2.1).  QED

At order 41 with `r=9`, `m=31`, this says

```text
2t_G(v)+kappa(v) <= 19,                                  (2.2)
```

so every ambient degree-nine vertex lies in at most nine triangles.  At
order 40 the corresponding right side is 21.

The same injection gives a useful companion statement.

**Proposition 2.2 (maximum-set sparsity).**  If `beta(G)=r` and `S` is an
admissible `r`-set, define
`kappa(S)=sum_{a in S}(r-d_G(a))`.  Then

```text
2e(G[S])+kappa(S) <= r^2+3r-2n.                          (2.3)
```

Indeed, every vertex outside `S` has a neighbour in `S`; at most one
outside vertex can have any fixed `a in S` as its unique neighbour.  Thus
`e(S,V-S)>=2(n-r)-r`, while
`e(S,V-S)=r^2-kappa(S)-2e(G[S])`.  In the order-41 case, every maximum
admissible nine-set satisfies `2e(G[S])+kappa(S)<=26`.

## 3. PROVED: no K4-free arrowing subgraph in an order-41 candidate

**Theorem 3.1.**  If `|V(G)|=41` and `beta(G)<=9`, then `G` contains no
`K4`-free subgraph `F` with `F -> (3,3)`.

**Proof.**  Suppose such an `F` exists and choose a proper-subgraph-minimal
arrowing `Q subseteq F`.  It contains a triangle and is `K4`-free, so
`omega(Q)=3`.  Bikov's Theorem 8.2 gives `d_Q(v)>=8` for every core vertex.
Since `Delta(G)<=9`, only degrees eight and nine are possible.

If `d_Q(v)=8`, (1.2) gives `t_Q(v)>=10`.  If `d_Q(v)=9`, the elementary
spoke inequality (1.1) gives the same conclusion.  Thus every core vertex
satisfies `t_G(v)>=10`.  Such a vertex cannot have ambient degree nine by
(2.2).  Therefore

```text
d_Q(v)=d_G(v)=8 for every v in V(Q).                      (3.1)
```

All ambient incidences of every core vertex are already core edges.  Hence
`Q` has no edge to `V(G)-V(Q)`, and there is no extra ambient edge inside
`V(Q)`: `Q` is an induced 8-regular component of `G`.

Every `Q`-edge lies in a core triangle, so `Q` has no maximal 2-clique.
Every triangle is maximal because `Q` is `K4`-free.  Brooks' theorem gives a
proper colouring of the connected 8-regular graph `Q` with eight colours:
it is neither complete nor an odd cycle.  The union of any two colour
classes is bipartite, hence triangle-free and admissible in `Q`.  Summing
the 28 pair inequalities, each vertex occurring seven times, gives

```text
7|V(Q)| <= 28 beta(Q), or |V(Q)| <= 4 beta(Q).            (3.2)
```

Write `R=G-V(Q)`.  If `|R|>=3`, then `G[R]` has an admissible pair: use a
nonedge if there is one, and use any pair of a triangle if the chosen three
vertices form `K3`.  For any core vertex `v`, the eight-set `N_Q(v)` is
admissible.  Since `Q` is a component, its union with that pair would be an
admissible ten-set, contrary to `beta(G)<=9`.  Hence `|R|<=2`.

Component additivity now finishes.  If `|R|=0`, then `beta(Q)<=9`, so (3.2)
gives `41<=36`.  If `|R|` is one or two, then `beta(G[R])>=1`, so
`beta(Q)<=8`; (3.2) gives `|Q|<=32`, whereas `|Q|` is 40 or 39.  QED

This is strictly stronger than the already audited statement that an
order-41 **ambient** `K4`-free graph has `beta>=10`: even a `K4`-bearing
candidate cannot hide a `K4`-free arrowing core.

## 4. PROVED: the surviving core range and a supported-K4 oracle

An order-41 counterexample arrows `(3,3)` by the campaign's audited Folkman
reduction and `R(3,10)<=41`.  Theorem 3.1 therefore implies:

```text
every minimal arrowing core in a candidate contains a K4.                 (4.1)
```

In the surviving `omega(G)=4` lane, Bikov's Theorem 8.1, (1.1), and (2.2)
also give, for every core vertex,

```text
5 <= d_Q(v) <= 8.                                         (4.2)
```

Indeed, core degree nine would force ambient degree nine and at least ten
ambient triangles.  If `d_Q(v)=8` and `d_G(v)=9`, all inequalities are
equalities: `t_Q(v)=t_G(v)=9`, and the one non-core ambient incidence at
`v` belongs to no triangle through `v`.

The following exact local predicate is consequently necessary for at least
one ambient `K4`.

**Lemma 4.1 (core-supported K4).**  Let `M subseteq Q` be a `K4`, and fix
`c in M`.  Put

```text
B_c = N_G(c)-M,
S_c = N_Q(c)-M,
s_c = |S_c|,
j_Q(x) = |N_Q(x) intersect M|.
```

Then `2<=s_c<=5`, and

```text
d_{Q[S_c]}(x)+(j_Q(x)-1) >= 2       for every x in S_c,   (4.3)
e_Q(S_c)+sum_{x in S_c}(j_Q(x)-1) >= s_c+1.              (4.4)
```

**Proof.**  Equation (4.2) gives the range for `s_c`.  The spoke `cx` must
lie in two core triangles, giving (4.3).  The exact link count is

```text
t_Q(c)=3+e_Q(S_c)+sum_{x in S_c}(j_Q(x)-1),
```

where the first term counts the three edges of `M-{c}`.  Apply (1.1) to
`d_Q(c)=3+s_c` to obtain (4.4).  QED

If `c` is saturated, meaning `d_G(c)=9`, (2.2) gives the ambient budget

```text
e_G(B_c)+sum_{x in B_c}(|N_G(x) intersect M|-1) <= 6.     (4.5)
```

Thus `s_c=5` forces equality throughout (4.4)--(4.5),
`d_Q(c)=8`, and `t_Q(c)=t_G(c)=9`.

There is also an aggregate form.  Put

```text
W = sum_c s_c,
A = sum_{x outside M} binom(j_Q(x),2),
B = sum_c e_Q(S_c).
```

Summing (4.4), and separately summing (4.3) over all core spokes, gives

```text
2A+B >= W+4,       A+B >= W.                            (4.6)
```

For a fixed maximum `K4`, the audited order-41 ledger

```text
sum_c(22-|Z_c|)+3t+2n_2+5n_3=12
```

implies `A<=n_2+3n_3<=7`.  These inequalities are useful exact solver
cuts, but they do not yield a contradiction.

### 4.1 Falsifier to an immediate K5 conclusion

The rigid count profile `t=n_2=n_3=0`, with six singleton fan vertices at
each clique vertex, is compatible with (4.3)--(4.5) without a `K5`.
For every `c`, choose four singleton fan vertices inducing `K4-e` and use
them as `S_c`.  Then every selected vertex has at least two neighbours in
`S_c`, and

```text
s_c=4,  e(S_c)=5=s_c+1,  t(c)=3+5=8<=9.
```

Joining the fan only to `c` creates no `K5`: a triangle of `K4-e` together
with `c` is only a `K4`.  This is a proof-level falsifier to deriving a K5
from the ledger plus the four **clique-vertex** support inequalities.  It is
not a full order-41 graph and does not realize the rest of a minimal core;
global arrowing remains essential.

### 4.2 New exact diagnosis of the fixed four-residual abstraction

The fixed graph in `checks/k4_fibre_attack/check_k4_fibre_attack.py` has a
unique `K4`, namely its designated `M`: each residual is triangle-free,
there are no cross-fan edges, and every outside vertex has at most one
neighbour in `M`.  Direct enumeration of each six-vertex fan finds no subset
of order two through five satisfying both (4.3) and (4.4).  Therefore its
unique `K4` cannot lie in a minimal arrowing core.

That fixed graph deliberately has `alpha=15`, so Theorem 3.1 does **not**
apply to it and cannot be used to exclude a `K4`-free core.  Its
non-arrowing status instead has a short explicit certificate: colour every
within-fan edge blue, colour the three `M`-edges
`37-39, 37-40, 38-39` blue, and colour every other edge red.  Direct
triangle enumeration verifies that neither colour contains a triangle.

This is an exact additional elimination of that already non-global witness.
It does not eliminate the broader cross-fan template, because new cross-fan
edges can create other `K4`s.

## 5. PROVED: an Erdős--Rogers counterexample gateway

For `s>=2`, let

```text
alpha_s(G) = max{|X| : G[X] is K_s-free},
f_{s,s+1}(n) = min alpha_s(G),
```

where the minimum is over `n`-vertex `K_{s+1}`-free graphs.

**Theorem 5.1.**  If `f_{s,s+1}(n)<H(n)` for any `s,n`, then Erdős #151 is
false.  Equivalently, Erdős #151 implies

```text
f_{s,s+1}(n) >= H(n) for every s>=2 and every n.           (5.1)
```

**Proof.**  Choose a `K_{s+1}`-free extremizer `G`.  Every copy of `K_s` in
`G` is ambient-maximal, since one extending vertex would create `K_{s+1}`.
Consequently every admissible set is `K_s`-free, so
`beta(G)<=alpha_s(G)=f_{s,s+1}(n)<H(n)`.  QED

The converse is not asserted: smaller maximal cliques can make `beta`
strictly smaller than `alpha_s`.

### 5.1 Dated primary-source check

The following preprint is newer than the older `f_{3,4}` discussion in the
repository and was checked at its primary source on 3 August 2026:

* R. Morris, J. Sahasrabudhe and J. Verstraëte,
  *On the Erdős--Rogers function*,
  [arXiv:2607.16118v1](https://arxiv.org/abs/2607.16118), submitted
  **17 July 2026**.

Its Theorem 1.1 proves
`f_{s,s+1}(n)=Theta(sqrt(n log n))` for every fixed `s>=2`.  The proof's
explicit simplifying choice is
`k=2^40 s^3 sqrt(n log n)` (equation (15)); Section 6.1 discusses an
improvement of the `s`-dependence to
`O(s^(3/2) sqrt(log s))`.  The same paper records the current asymptotic
window

```text
(1/sqrt(2)+o(1)) sqrt(n log n) <= H(n)
                                  <= (1+o(1)) sqrt(n log n).
```

Thus Theorem 5.1 is a genuine constant-comparison counterexample programme,
but the July construction's stated constants do not beat the known `H`
constant.  No counterexample or resolution follows from that preprint.

## 6. PROVED: top-clique counting and the order-40/41 arithmetic

Let `z_k(q)` denote the number of `K_k`s in the balanced complete
`k`-partite graph on `q` vertices.

**Theorem 6.1 (pure top-clique layer).**  Suppose an `n`-vertex
`K_{s+1}`-free graph has a `K_s` in every `h`-set.  Then

```text
binom(n,s)/binom(h,s) <= N_s(G) <= n z_{s-1}(h-1)/s.       (6.1)
```

**Proof.**  A vertex of degree at least `h` would have an `h`-subset in its
neighbourhood; a `K_s` there, together with the vertex, gives `K_{s+1}`.
Thus `Delta<=h-1`.  Double-counting pairs `(K_s,H)` with
`K_s subseteq H`, `|H|=h`, gives the lower bound.  A link is `K_s`-free and
has at most `h-1` vertices.  Zykov's clique theorem bounds its number of
`K_{s-1}`s by `z_{s-1}(h-1)`.  Sum over all vertices and divide by `s`.
QED

At `h=10`, `z_3(9)=27` and `z_4(9)=24`.  Exact integer bounds are:

| order | pure `K4` lower | pure `K4` upper | pure `K5` lower | pure `K5` upper |
|---:|---:|---:|---:|---:|
| 40 | 436 | 270 | 2612 | 192 |
| 41 | 483 | 276 | 2974 | 196 |

Hence neither an order-40 nor order-41 counterexample can have every bad
ten-set witnessed solely by a top `K4` layer in a `K5`-free graph, or solely
by a top `K5` layer in a `K6`-free graph.  Smaller maximal cliques must do
substantial work.

In the order-41 `omega=4` lane, Theorem 2.1 sharpens the total `K4` count.
For ambient degree at most eight, a link is `K4`-free on at most eight
vertices and has at most `z_3(8)=18` triangles.  For ambient degree nine,
the link has at most nine edges by (2.2), and the Kruskal--Katona triangle
bound gives at most seven triangles.  Therefore every vertex belongs to at
most 18 `K4`s and

```text
N_4(G) <= floor(41*18/4)=184.                            (6.2)
```

If `N_2,N_3` count ambient-maximal edges and triangles, coverage of all
ten-sets, followed by (6.2), forces

```text
61,523,748 N_2 + 12,620,256 N_3 >= 693,339,152.           (6.3)
```

Thus `N_2=0` forces `N_3>=55`, and `N_3=0` forces `N_2>=12`.  This is a
necessary global cut, not a contradiction.

## 7. Computational checks, limitations, and decision

**COMPUTATIONALLY CHECKED:**

* all binomial arithmetic in Sections 5--6;
* the 184-`K4` coverage residual in (6.3);
* the `K4-e` local support falsifier;
* the unique-`K4`, failed-support, and explicit good-colouring claims for the
  fixed fibre abstraction.

**NOT PROVED:** the `omega=4` order-41 case, existence or nonexistence of a
globally compatible supported core, any improvement of the July 2026
Erdős--Rogers constants sufficient for (5.1), or Erdős #151.

The global work is not exhausted: Theorems 2.1, 3.1 and 5.1 are reusable
structural advances.  But they also identify the honest remaining gate.
Every order-41 `omega=4` candidate must contain a genuinely `K4`-bearing
minimal core of degrees 5--8, and at least one of its `K4`s must pass the
four supported-link predicates while the smaller maximal-clique layers meet
(6.3).  The scalar residual ledger permits this.  A further attack must
couple the **full arrowing semantics** of that supported core to the four
ambient residual exchange webs; another one-K4 marginal count is not enough.

## 8. Priority statement

Internal repository search on 3 August 2026 found no earlier statement of
Theorem 2.1 or Theorem 3.1 in this generality.  That is not an external
literature-priority claim.  The published inputs are attributed above;
independent expert audit is required before any public theorem or novelty
claim.
