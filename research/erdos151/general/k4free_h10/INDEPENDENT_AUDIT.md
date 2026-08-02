# Independent adversarial audit of the K4-free order-41 theorem

**Audit date:** 2 August 2026  
**Verdict:** **PASS, after one scope-strengthening correction and a matching
checker update.**  No counterexample to any mathematical step was found.
Repository attributes pin this note and the checked source artifacts to LF
line endings so that the published SHA-256 values are platform-stable.

The corrected theorem is stronger than the submitted version:

> Every `K4`-free graph `G` on 41 vertices satisfies `beta(G)>=10`.

This is unconditional with respect to the unresolved value
`R(3,10) in {40,41}`.  It therefore excludes the whole `omega<=3` lane at
order 41 even if order 40 has not been settled.  It does **not** settle the
order-40 lane.

## Correction made by this audit

The submitted completion used the assertion that a least counterexample is
connected and hence that the Ramsey-minimal core `Q` equals `G`.  That
assertion is sound under the stated least-counterexample hypothesis, but it
made the order-41 conclusion conditional on there being no order-40
counterexample.  The hypothesis is unnecessary.

After the degree-nine obstruction, `Q` is an 8-regular ambient component and
the earlier remainder argument gives `q=|Q|>=31`.  In `Q`, admissibility is
exactly triangle-freeness.  An eight-color Brooks coloring, summed over all
pairs of color classes, gives

`q <= 4 beta(Q)`.                                           (A)

Write `r=41-q`.  Component additivity gives
`beta(G)=beta(Q)+beta(G[R])`.  The elementary lower bounds

- `beta(G[R])>=0` if `r=0`,
- `beta(G[R])>=1` if `r=1,2`, and
- `beta(G[R])>=2` if `r>=3`

turn (A) into respectively `q<=36`, `q<=32`, and `q<=28`.  These contradict
respectively `q=41`, `q in {39,40}`, and `q>=31`.  This proves the corrected
statement without connectedness or least-order validity.  The executable
checker was updated to test all eleven cases `0<=r<=10`, rather than only
the old `Q=G` arithmetic.

## Dependency and quantifier audit

### 1. Entry to a Ramsey-minimal core

Assuming `beta(G)<=9` at order 41, the published bound `R(3,10)<=41` and the
campaign's Folkman reduction imply `G -> (3,3)`.  Only `H(41)>=10` is needed;
the exact value of `R(3,10)` is not.  Also `Delta(G)<=beta(G)<=9`, because
every open neighborhood is ambient-admissible.

A finite inclusion-minimal arrowing subgraph `Q` is a minimal `(3,3)`-Ramsey
graph in Bikov's sense.  Since `G` is `K4`-free and an arrowing graph must
contain a triangle, `omega(Q)=3`.  Minimality gives all three properties used
in the note:

- `Q` is connected (otherwise one component would itself arrow);
- `Q-v` has a triangle-avoiding edge coloring for every vertex `v`;
- every core edge is in at least two core triangles.  If an edge were in
  zero or one triangle, a good coloring of `Q-e` could always be extended
  over `e`.

The stated `chi(Q)>=6` is standard and correct, but is not used in the proof.

### 2. Bikov theorem and the degree-eight links

The primary source was checked directly: A. Bikov, *Small minimal (3,3)-
Ramsey graphs*, arXiv:1604.03716v1, Definition 1.1 and Theorem 8.2 with
Figure 13 (article page 18, PDF page 19).  It defines minimality as absence
of a proper arrowing subgraph and states exactly:

- if `omega(Q)=3`, then `delta(Q)>=8`;
- if `d_Q(v)=8`, then the induced link `Q[N_Q(v)]` is one of
  `N_{8.1},...,N_{8.7}`.

Direct inspection of Figure 13 agrees with the checker counts
`10,11,12,10,10,11,12`.  The checker independently verifies for its seven
graph6 representatives that each has eight vertices, is triangle-free,
has the stated edge count and minimum degree at least two, and has an edge
signing for which all `2^8` spoke assignments fail.  It correctly does not
claim to reprove completeness of Bikov's list.  The source figure is the
remaining provenance boundary for the graph6 transcription; the proof only
needs the visibly checkable lower bound of ten link edges.

A separate one-off check decoded the same strings with NetworkX's graph6
parser, compared every decoded edge set with the standard-library decoder,
verified pairwise nonisomorphism, and re-tested markedness with direct nested
loops over edge signings and spoke assignments.  It returned
`NETWORKX_GRAPH6_AND_DIRECT_MARKED_CHECK_OK [10, 11, 12, 10, 10, 11, 12]`.

For `d_Q(v)=9`, the note's self-contained substitute is sound.  Core-edge
minimality makes the link minimum degree at least two, hence it has at least
nine edges.  Equality would make it a disjoint union of cycles.  Orienting
each cycle and coloring the spoke entering a vertex opposite to the entering
link edge extends a good coloring of `Q-v`, a contradiction.  Therefore
every core vertex lies in at least ten core, and hence ambient, triangles.

### 3. Ambient maximality versus core maximality

No illicit change of ambient graph occurs.

- `N_G(v)` is ambient-admissible because every clique inside it extends by
  `v`; hence the subset `N_Q(v)` is ambient-admissible even though `Q` need
  not be induced.
- If a set is admissible in an induced subgraph, it is ambient-admissible:
  an ambient-maximal clique contained in the set remains maximal in that
  induced subgraph.  The converse is not used.
- The union of two anticomplete ambient-admissible sets is admissible,
  because a nontrivial clique cannot meet both sides.

Thus, for a degree-eight core vertex, an admissible pair inside the outside
anticomplete remainder would combine with `N_Q(v)` to make an admissible
10-set.  Hence that remainder has `beta<=1` and at most two vertices.  Each
of the eight core neighbors has at most one ambient edge leaving `Q`, so
`|V(G)-V(Q)|<=10` and `q>=31`.  The degree-nine version, using an admissible
nine-set plus one outside vertex, is also valid.

### 4. Unique-common-neighbor injection

For a core vertex `v` of ambient degree nine, `S=N_G(v)` is an admissible
nine-set.  Every nonneighbor `x` must therefore have a common neighbor with
`v`.  If the common neighbor `a` is unique, the witnessing ambient-maximal
clique in `S union {x}` is exactly the maximal edge `xa`.

Two distinct such vertices `x,y` cannot route through the same `a`:
maximality of `xa` forces `xy` to be a nonedge, and both are anticomplete to
`S-{a}`.  Their union with that admissible eight-set would be an admissible
10-set.  The resulting injection into `S` proves `u<=9`.  This uses ambient
maximal edges and does not assume that `xa` or any other ambient edge lies in
the core.

### 5. Two-walk arithmetic

For `t=t_G(v)`, the exact identity is

`sum_{x outside N_G[v]} c(v,x)`
` = sum_{a in N_G(v)} (d_G(a)-1) - 2t`.

The subtraction by `2t` is correct: every link edge contributes two
nonbacktracking two-walks ending back inside `N_G(v)`.  At order 41 the upper
bound is `72-2t`.  The 31 nonneighbors contribute at least
`u+2(31-u)=62-u`, so `u>=2t-10>=10`, contradicting `u<=9`.

Consequently no core vertex has ambient degree nine.  Bikov's lower bound
and the ambient degree ceiling then force `d_Q(v)=d_G(v)=8` for every core
vertex.  This also proves that `Q` is an induced ambient component: all eight
ambient incidences of each core vertex are already core edges.

### 6. Brooks and the component finish

In the 8-regular connected core, every edge lies in a triangle and every
triangle is maximal because the graph is `K4`-free.  Hence a subset is
admissible in `Q` exactly when it is triangle-free.  Brooks applies because
`Q` is neither complete nor an odd cycle.  The union of any two of eight
proper color classes is bipartite, hence admissible.  Each class occurs in
seven of the 28 pairs, giving (A).  The component case split above is then
exhaustive and proves the theorem.

## Exact scope of the order-40 residue

The order-40 interpretation is conditional on `R(3,10)=40`.  In that case a
counterexample has `beta(G)=9`: `beta<=9` is the counterexample inequality,
and the verified order-39 theorem plus induced-subgraph monotonicity gives
`beta>=9`.  If `R(3,10)=41`, then `H(40)=9` and order 40 is already inherited
from order 39, so there is no order-40 `h=10` lane.

Under the conditional order-40 premises, the residual claims were
re-derived:

- the same two-walk argument gives `u>=2t-12`; together with `u<=9` and
  `t>=10`, every ambient-degree-nine core vertex has `t=10`;
- with `k(v)=sum_{a in N(v)}(9-d(a))`, the exact refinement is
  `u>=8+k(v)`, hence `k(v)<=1`;
- if `b` is the number of core-degree-nine vertices and `r>=2`, double
  counting the pairs `(v,x)` for which `N_Q(v)` sees `x outside Q` gives
  `10b <= (10-r)q`; for `r=1` it gives `9b<=8q`;
- `b` is even by the handshaking lemma, and all displayed integer bounds in
  the note match these inequalities;
- at `r=10,q=30`, equality makes `Q` 8-regular, gives every core vertex one
  outside neighbor, and partitions `Q` into ten fibers.  Equality forces
  each core neighborhood to meet eight distinct fibers.  Two vertices in
  one fiber cannot be at distance one (a core edge has a common core
  neighbor) or two (they already share one), so their closed 9-vertex
  neighborhoods are disjoint.  Every fiber has size at most three; all ten
  therefore have size exactly three.

These are necessary local conditions only.  They do not prove arrowing or
`beta=9`, and they do not exclude order 40.

## Reproduction and hashes

Command run from the repository root:

```text
python experiments/erdos151_siege/k4free_h10/check_k4free_order41.py
```

It returned `status: VERIFIED`, checked all seven links, the order-41
component cases, the order-40 incidence table, and the order-40/41
unique-neighbor arithmetic.

SHA-256 after the audit corrections:

```text
A06DDC79C5DB44AF51B098B404B2355055835866DDAE0EDFBEE5606AA195E7A4  research/erdos151/general/k4free_h10/K4FREE_ORDER41.md
87A1A2ABE28354946AD54A4407306B71F235CEED7CDFCDBE73380241D0646FF3  experiments/erdos151_siege/k4free_h10/check_k4free_order41.py
71707D0CFF8A6D00D4D646E9A04C29D8CB9C84C26C0757AAD0191AA7C6D0653B  arXiv:1604.03716v1 PDF downloaded 2026-08-02
```

The PDF is an audit input in temporary storage, not a repository artifact.
No public-result or novelty claim is made by this audit.
