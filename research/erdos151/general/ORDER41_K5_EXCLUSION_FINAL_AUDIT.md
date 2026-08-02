# Final clean-room audit: order 41 and clique number five

**Date:** 2 August 2026  
**Auditor:** independent Codex subagent (`erdos151_k5_final_audit`)  
**Verdict:** **PASS, conditional on exactly one external catalogue premise**

## 1. Claim audited and immutable binding

This audit binds the following frozen theorem package:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_EXCLUSION.md` | `5cf0cfafb919ca3f6b8e81cc1ec66b94d1b72471fba657ec3e489cf95474462d` |
| `ORDER41_K5_EXCLUSION_RESULT.json` | `494ff5b1ced797fd6b44ab3cdf0847b9b405f0ef47c5621f0fca32ce8da5e453` |

The audited statement is:

> Assume that the complete list, up to isomorphism, of triangle-free graphs
> on 17 vertices with independence number at most five is the seven-record
> catalogue pinned in `experiments/erdos128/r36_17.g6`.  Then every graph
> `G` on 41 vertices with `omega(G)=5` has `beta(G)>=10`.

Here `beta(G)` is the maximum order of a vertex set containing no
inclusion-maximal clique of `G` of order at least two.

I did not trust the prior overlap program, row checkers, audit prose, or graph
parser.  I reconstructed the proof from the definitions, wrote a separate
graph6 decoder and finite guard, and explicitly audited every switch between
ambient and induced maximality.  The older overlap enumeration is not needed
for this theorem and was treated only as corroboration.

## 2. Verdict and exact dependency boundary

The proof passes.  After accepting the pinned-catalogue exhaustiveness
statement above, no conjectural combinatorial step or unaudited computation
remains.

The sole unverified premise is **external completeness and identification of
the seven Ramsey `(3,6;17)` classes**.  The repository and my independent
decoder verify the pinned bytes, record count, triangle-freeness,
independence bound, edge histogram, and minimum degrees.  Those local checks
do not prove that no eighth isomorphism class exists.

Other inputs are proved local or classical inputs, not additional open
premises:

- the verified theorem `beta(H)>=H(|H|)` through order 39;
- the exact Ramsey values through `R(3,6)=18`, including `H(9)=4` and
  `H(16)=H(17)=5`;
- `Delta(H)<=beta(H)`, Turan's theorem and its equality case; and
- the elementary classification of a connected bicyclic 2-core as a theta,
  figure-eight, or dumbbell.

The theorem does **not** depend logically on the repaired `4368 / 786 / 1963`
overlap enumeration, the `T: 10 -> 0` result, or the 17 row-D cores.

## 3. Clean-room residual reconstruction

Assume for contradiction that `|G|=41`, `omega(G)=5`, and `beta(G)<=9`.
Every open neighbourhood is admissible, because all its cliques extend by
the centre, so `Delta(G)<=9`.

Fix a maximum `K5`, denoted `M`.  Put `X=V(G)-M`, so `|X|=36`.  Let `n_i`
count the vertices of `X` with exactly `i` neighbours in `M`, for
`0<=i<=4`.  (Five neighbours would extend `M`.)  The five clique vertices
have 25 cross-edge slots in total, so

```text
W=sum_i i*n_i<=25,              t=25-W>=0.
```

For `c in M`, let `U` be the `n_0` class, let `A_c` be the vertices whose
exact `M`-neighbourhood is `{c}`, and set `Z_c=U union A_c`.

### 3.1 Residual beta: maximality direction checked

Let `F_c=G[Z_c]` and let `S` be admissible in `F_c`.  Put `P_c=M-{c}`.
There are no edges between `P_c` and `Z_c`.  The set `P_c union S` is
ambient-admissible in `G`:

- every clique contained in `P_c` extends by `c` and is not ambient-maximal;
- no nontrivial clique is mixed between `P_c` and `S`; and
- if a clique contained in `S` were maximal in `G`, it would also be maximal
  in the induced graph `F_c`, which admissibility of `S` forbids.

This uses only the sound implication

```text
ambient-maximal in G and contained in F_c  =>  maximal in F_c.
```

It never uses the false converse.  Hence

```text
4+beta(F_c)<=beta(G)<=9,
```

so `beta(F_c)<=5` pointwise.

If `|Z_c|>=18`, the verified through-order-39 theorem and monotonicity of
`H` give `beta(F_c)>=H(|Z_c|)>=H(18)=6`, a contradiction.  Thus
`|Z_c|<=17` for all five `c`.

### 3.2 Exact profile exhaustion

The two ledger equations give

```text
sum_c |Z_c| = 5n_0+n_1
            = 80+4t+3n_2+7n_3+11n_4.
```

The five residual caps make the left side at most 85.  Direct nonnegative
integer enumeration leaves exactly:

| row | `t` | `(n_0,n_1,n_2,n_3,n_4)` | fan sizes | residual sizes |
|---|---:|---:|---:|---:|
| R | 0 | `(11,25,0,0,0)` | `5,5,5,5,5` | `16,16,16,16,16` |
| D | 0 | `(12,23,1,0,0)` | `4,4,5,5,5` | `16,16,17,17,17` |
| T | 1 | `(12,24,0,0,0)` | `4,5,5,5,5` | `16,17,17,17,17` |

The fan sizes also follow independently from the five cross-degree
capacities.  In R all 25 slots are filled by unique-neighbour vertices.  In
D the one double-neighbour vertex consumes one slot at each of two clique
vertices, leaving capacities `4,4,5,5,5`, whose sum is the 23 singleton
vertices.  In T all vertices are singleton-neighbour vertices and exactly
one of the 25 slots is empty.

Every residual has order 16 or 17.  The through-order theorem and
`H(16)=H(17)=5`, combined with the upper bound above, give

```text
beta(F_c)=5
```

in every row.  The independent audit script reproduced exactly the three
profiles and no others.

## 4. Catalogue-conditional residual triangle-freeness

This is the only place where the external premise enters, so I reconstructed
the full reduction rather than taking it from the existing note.

### 4.1 Every order-16/17 beta-five residual is K4-free

Let `F` have order 16 or 17 and `beta(F)<=5`.  Again
`Delta(F)<=beta(F)<=5`.  If `C` were a `K4`, choose `c in C` and put
`P=C-{c}`.  Each of the three vertices of `P` has at most two neighbours
outside `C`, so at least

```text
|F|-4-3*2 >= 6
```

outside vertices are anticomplete to `P`.  Six of them induce a graph with
an admissible three-set because `H(6)=3`.  Joining that set to `P` produces
an admissible six-set in `F`: `P` extends by `c`, there are no mixed cliques,
and an `F`-maximal clique in the chosen residual set would be maximal in its
induced graph.  Contradiction.  Thus `F` is K4-free.

### 4.2 Transforming a hypothetical triangle into a catalogue graph

Now let `|F|=17` and suppose `abc` is a triangle.  For edge `ab`, each
endpoint has at most three neighbours outside the triangle.  If the union of
those outside neighbourhoods had at most five vertices, at least nine
vertices would be anticomplete to `{a,b}`.  An admissible four-set among
those nine (`H(9)=4`) joined to `{a,b}` would be an admissible six-set;
`ab` itself extends by `c`.  Therefore the union has size six.  Both
endpoints have degree five and their three outside-neighbour sets are
disjoint.

Applying this to every triangle edge shows that each such edge lies in
exactly one triangle; in particular, the triangles are edge-disjoint.  Let
`q>=1` be their number.  Let `L` contain every edge lying in no triangle and
form `J` by taking all of `L` plus one selected edge from each triangle.

The graph `J` is triangle-free.  Indeed, any triangle of `J` would be a
triangle of `F`, but its three edges belong uniquely to that same triangle,
from which only one edge was selected.  Moreover `J` contains every maximal
edge of `F` and one edge of every maximal triangle of `F`; K4-freeness says
there are no larger maximal cliques.  Hence every independent set of `J` is
admissible in `F`, so `alpha(J)<=5`.

The catalogue premise now identifies `J` with one of the seven pinned
Ramsey graphs.  My independent parser found, across those seven records,

```text
edge histogram {40:2, 41:3, 42:2},       minimum degree 4 in every record.
```

On the other hand, `Delta(F)<=5` gives `e(F)<=42`, and edge-disjointness of
the triangles gives

```text
e(J)=e(F)-2q.
```

Since `e(J)>=40` and `q>=1`, the only arithmetic possibility is
`q=1`, `e(F)=42`, `e(J)=40`.  The degree sequence of `F` is therefore one
4 and sixteen 5s.  All three vertices of the unique triangle have degree
five.  Keeping one triangle edge and deleting the other two leaves their
common endpoint with degree three in `J`, contradicting the catalogue's
minimum degree four.

Thus every order-17 residual is triangle-free, conditional solely on the
catalogue completeness premise.  It then also has `alpha<=5`, because every
independent set is residual-admissible.

## 5. Singleton-fibre mechanism

The same mechanism is used in all three profile exclusions, so I checked it
once at full ambient precision.

Let `c in M` have degree nine, write

```text
N(c)=(M-{c}) union B_c,        |B_c|=5,
```

and suppose `B_c` dominates `U`.  (Domination follows because adding any
`u in U` to the maximum admissible nine-set `N(c)` must expose an
ambient-maximal clique involving `u`, and `u` is anticomplete to `M`.)

For `a in B_c`, define

```text
P_c(a)={u in U:N(u) intersect B_c={a}}.
```

For `u in P_c(a)`, the only possible ambient-maximal clique in
`N(c) union {u}` is the edge `ua`; hence `ua` is ambient-maximal.  If
distinct `u,v` had the same anchor `a`, then `uv` must be absent, since
otherwise the triangle `uav` extends `ua`.  But then
`(N(c)-{a}) union {u,v}` is an admissible ten-set: `u,v` are isolated there
and every clique in the remaining neighbourhood extends by `c`.  This is
impossible.  Therefore `|P_c(a)|<=1`.

Consequently, if `|U|=m`, at most five vertices have spoke-degree one and

```text
e(U,B_c)>=5+2(m-5)=2m-5.
```

This is 17 for row R and 19 for rows D/T.  The proof remains valid when
`B_p=A_p union {w}` and the anchor is the shared vertex `w`: vertices of `U`
are still anticomplete to every vertex of `M`, and the duplicated `U-w`
edges matter only later in the summed degree identity.

## 6. Row R audit

Here `|U|=11`; all five degree-nine fans dominate it.  The singleton-fibre
bound yields five cuts of at least 17 edges.

Since `U` lies inside a beta-five residual, `alpha(U)<=5`.  Thus the
complement is K6-free, and Turan gives

```text
e(U)>=55-ex(11,K6)=55-48=7.
```

Because `U` is anticomplete to `M`, its exact global degree sum is

```text
2e(U)+sum_c e(U,A_c)<=11*9=99.
```

The lower bounds also sum to `2*7+5*17=99`, so equality holds everywhere.
Equality in Turan makes the complement `T_5(11)` with parts
`3,2,2,2,2`; hence

```text
G[U]=K3 disjoint-union 4K2.
```

Fix `a in A_c` and work now solely in `F_c=G[U union A_c]`.  The vertices
`u in U` for which `au` is an inclusion-maximal **residual** edge form an
independent set and therefore meet each of the five clique components of
`U` at most once.  Choose one vertex outside this endpoint set from each
component.  These five vertices are independent.  Together with `a`, their
only possible nontrivial cliques are non-maximal residual edges `au`; hence
the six-set is `F_c`-admissible.  This contradicts `beta(F_c)=5`.

I independently enumerated all independent endpoint sets: the forced graph
has 324 independent sets and 48 maximum independent five-sets, and no
independent endpoint set meets all 48.  Row R passes without the catalogue.

## 7. Sparse triangle-free lemma audit

Both rows D and T use:

> If `H` is triangle-free, `|H|=12`, and `alpha(H)<=5`, then `e(H)>=11`.
> Equality holds only for `C5 disjoint-union C5 disjoint-union K2`.

Here is the independent derivation.

If `H` had at least four components, their positive independence numbers
sum to at most five.  For four components the largest possible allocation
is `(2,1,1,1)`.  Triangle-freeness and `R(3,3)=6` cap their orders by
`(5,2,2,2)`, totaling only 11.  Five components total at most ten, and six
already force independence at least six.  Hence `H` has at most three
components.

Let `k` be the component count and `mu=e(H)-12+k` the total cycle rank.  A
tree of order `s` has independence at least `ceil(s/2)`; a connected
unicyclic graph has independence at least `floor(s/2)` after deletion of a
cycle vertex.

If `e(H)<=10`, connectedness is impossible; with two components `H` is a
forest; with three it is a forest or one unicyclic component plus two trees.
The displayed floor/ceiling bounds and parity at total order 12 give an
independent six-set in every case.  Therefore `e(H)>=11`.

At equality, the one- and two-component cases still give six.  With three
components the cycle-rank distribution is either `(2,0,0)` or `(1,1,0)`.
For `(2,0,0)`, the bicyclic 2-core is a theta, figure-eight, or dumbbell.
Except for a dumbbell with two vertex-disjoint odd cycles, one vertex meets
every odd cycle; deleting it yields a bipartite graph and the same parity
bound gives six.  In the exceptional case, triangle-freeness makes both odd
cycles length at least five.  The two other nonempty components leave room
only for two 5-cycles joined by one edge and two isolated vertices, which
again has an independent six-set.

For `(1,1,0)`, the lower bound can be five only if both unicyclic orders are
odd and their components non-bipartite, while the tree order is even.  The
two odd cycles have length at least five and the tree has order at least two,
forcing orders `(5,5,2)` and exactly `C5+C5+K2`.

My separate component-profile guard checked 231 low-edge profiles, found
minimum lower bound six, and found only equality order profile `(2,5,5)`.
The pre-existing independent spanning-tree-extension checker also replayed
successfully, but it is corroboration rather than the basis of this audit.

## 8. Row D audit

Let `w` be the unique vertex with `N_M(w)={p,q}` and define five spokes

```text
B_p=A_p union {w},       B_q=A_q union {w},
B_c=A_c                  for the other three c.
```

Every clique vertex has degree nine; every spoke dominates the common
12-set `U`.  The singleton-fibre bound gives

```text
e_c=e(U,B_c)>=19
```

for each `c`, including the two occurrences of `w`.

Put `e_U=e(G[U])` and `r=|N(w) intersect U|`.  Since `w` already sees `p,q`
and `Delta(G)<=9`, `r<=7`.  Summing the five spoke cuts counts every `U-w`
edge twice, while the actual degree sum counts it once.  Therefore the exact
identity is

```text
sum_{u in U}d_G(u)=2e_U+sum_c e_c-r.
```

There are no omitted neighbours: `U` is anticomplete to `M`, and the five
fans together with `w` exhaust `X-U`.  The twelve degree budgets give

```text
108 >= 2e_U+5*19-7 = 2e_U+88,
```

so `e_U<=10`.

Any of the three full order-17 residuals is triangle-free under the sole
catalogue premise, and `U` is its induced subgraph.  Also `alpha(U)<=5`.
The sparse lemma gives `e_U>=11`, contradiction.  No D17 overlap count or
ambient/residual maximality switch occurs in this finish.

## 9. Row T audit

There are four full degree-nine fans and one deficient four-fan `A_0` at a
degree-eight clique vertex.  Under the catalogue premise, a full order-17
residual is triangle-free, so the common 12-set `U` is triangle-free.

The four full fans each have cut at least 19.  At the deficient fan put

```text
D_0={u in U:N(u) intersect A_0=empty}.
```

If two members of `D_0` were nonadjacent, adjoining them to the eight-set
`N(c_0)` would produce an ambient-admissible ten-set: they are isolated in
it, and every clique in the neighbourhood extends by `c_0`.  Thus `D_0` is
a clique.  Triangle-freeness of `U` makes `|D_0|<=2`, so
`e(U,A_0)>=10`.  No singleton-fibre claim is made at the deficient fan.

The sparse lemma and `alpha(U)<=5` give `e(U)>=11`.  The exact degree sum is

```text
108 >= 2e(U)+e(U,A_0)+sum_{i=1}^4 e(U,A_i)
    >= 2*11+10+4*19 = 108.
```

All inequalities are equalities, and the sparse equality case forces

```text
G[U]=C5 disjoint-union C5 disjoint-union K2.
```

Fix `a` in a full fan and now work only in its residual
`F=G[U union A_i]`.  Let `E_a` contain the vertices `u` for which `au` is a
maximal 2-clique **of F**.  This set is independent: adjacent members with
`a` would extend both incident edges to a triangle.  In each C5, an
independent `E_a` removes at most two vertices and leaves an independent
pair; in the K2 it removes at most one endpoint.  Therefore a maximum
independent five-set `I` of `U` can be chosen disjoint from `E_a`.

The six-set `I union {a}` is `F`-admissible: `I` is independent, and every
possible edge `au` in the set is non-maximal in `F`.  This contradicts
`beta(F)=5`.

This row uses ambient maximality only for the full-fan cut and residual
maximality only for the final `F`-admissible set.  It never transfers
maximality in either direction.  My independent enumeration found 363
independent endpoint sets, 50 maximum independent five-sets, and no endpoint
set meeting all 50.

## 10. Independent finite replay

The new checker is intentionally independent of the campaign graph parser,
beta engines, overlap checker, and row checkers:

```text
research/erdos151/general/checks/final_audit/check_order41_k5_final_audit.py
SHA-256 8685e8e6eeddd339de725649ba2d195d208dd4c77bb2dd578b9c9eafedcefe6c
```

Run from the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\final_audit\check_order41_k5_final_audit.py
```

The frozen output was:

```text
status: PASS
catalogue: sha256 3286c5...; 7 records; edges {40:2,41:3,42:2}; all min degree 4
profiles: R=(11,25,0,0,0), D=(12,23,1,0,0), T=(12,24,0,0,0)
sparse: 231 low-edge profiles; minimum alpha bound 6; equality (2,5,5)
transversals: K3+4K2 -> 324/48; 2C5+K2 -> 363/50; no hitting set
arithmetic: cuts 17/19; R budget 99; D at e(U)=11 gives 110>108;
            T lower degree sum 108; order-17 J possibility only (1,42,40)
```

I also replayed the manifest, rigid guard, strengthened-D exact enumerator,
triangle-saturation guard, and both through-order-39 finite checkers.  All
returned their documented PASS/VERIFIED results.  These replays support but
do not replace the clean-room arguments above.

## 11. Hash verification

Every one of the 42 dependency paths recorded in
`ORDER41_K5_EXCLUSION_RESULT.json` existed and matched its claimed SHA-256 at
the time of this audit.  The JSON's theorem binding also matched the frozen
theorem hash.  Particularly relevant logical dependencies were:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| `ORDER41_K5_RIGID_ATTACK.md` | `9e3803fcb92234c8c75d9c687347bb82e92e7ae30262460d68dc38483c592ab3` |
| `ORDER41_K5_DOUBLE_SATURATION.md` | `8353be6fde22d8e6edeb455187169b5eae4f6093ae971debcae353e7debddebd` |
| `ORDER41_K5_DOUBLE_SATURATION_REAUDIT.md` | `af7a974a02891d02a7bb72596ecf5ae442975acb8c3c196aa137c09190e0dbcf` |
| `ORDER41_K5_TRIANGLE_SATURATION.md` | `8b4bf32e955e0d8853d157b87c3a29fe9bf16b1e69ac649a5dbc5601e2aa97ce` |
| `research/erdos151/result.json` | `bec51fe5d82881c2ed3a47f258ab0818a542de05bc9d79ac06e8bf55f3455c3a` |
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |

## 12. Adversarial failure search and nonclaims

I specifically searched for and did not find:

- an induced-to-ambient maximality reversal in the residual lift;
- use of the degree-eight T fan as if its neighbourhood were maximum;
- a failure of the singleton-fibre proof when the D spoke anchor is `w`;
- double counting of `U-w` edges without the `-r` correction;
- an omitted edge class in either row-D or row-T degree sum;
- circular use of the repaired overlap enumeration to prove a premise of
  that same enumeration; or
- an equality case other than `C5+C5+K2` in the sparse lemma.

This PASS does **not** prove the external catalogue is complete.  It does
not provide a whole-order-41 UNSAT certificate, exclude `omega=4`, settle
order 40, prove the theorem at other orders, or solve Erdős problem #151.
It supports only the frozen conditional theorem stated in Section 1.

