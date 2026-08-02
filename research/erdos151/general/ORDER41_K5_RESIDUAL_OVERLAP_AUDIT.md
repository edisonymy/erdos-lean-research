# Independent audit of the order-41 `omega=5` residual-overlap package

**Date:** 2 August 2026.  **Verdict:** **FAIL as an exact package.**

The elementary graph-theoretic reduction is sound, the catalogue-conditional
exclusion of row T remains sound after correction, and the order-16
triangle-containing graph really has `beta=5`.  However, the advertised exact
overlap enumeration is incomplete: the checker omits automorphic transports of
the first fan pattern used to seed an isomorphism class.  Closing those missing
orbits changes

```text
stored aligned patterns:       1920 -> 1963
T preliminary core classes:       6 -> 10
T classes after the D0 test:       0 -> 0
D necessary-condition cores:      12 -> 17
```

Thus the note, result JSON, and checker's `status: VERIFIED` are false where
they claim the exact counts `6` and `12`.  The safe corrected frontier is:
row R remains open; row T is still excluded conditional on completeness of the
pinned `(3,6;17)` catalogue; and row D is reduced by the stated necessary
conditions to **17**, not 12, common-core isomorphism classes.  This audit does
not edit the implementation, run CEGAR, or make an order-41 theorem claim.

## Audited inputs and immutable values

The source artifacts were read without modification.  Their SHA-256 values at
audit time were:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP.md` | `5522f26889d086193e9d74694d51e7b56c48d66d877ecf3b071488f9a857fcfa` |
| `ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json` | `ab425f156f0f7d4c3f4a64ef8801d5c45442399fe13b4513b388cfd53217c1f7` |
| `checks/check_order41_k5_overlap.py` | `5711a2e1f7e3bc75aa1bf725d9d65a8a8d7d130676a159abdef207c5ac9cf754` |
| `checks/order16_beta5_triangle_witness.json` | `b3778f99571afed723c088143df118e00ab36515083167445b37f024a6e5ad36` |
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |
| `experiments/erdos128/r36_16.g6.gz` | `5fd4e68d880e1d4ed05337b97cba0ce15387e1f545744aed80b91bb4b2186f25` |
| decoded `r36_16.g6` bytes | `25e35e1bb46b3131ff00b430b56e4679fcde7988211aefd9036c1e4c0cd7d2bf` |
| `experiments/erdos128/MANIFEST.json` | `ef41bb5eb474a58503549a21b411f13a77217f70edbcc63479f00247c11c92fc` |
| `experiments/erdos151_siege/beta_lib.py` | `228c8d82de6a0c292f0f1c89b4a5fc9411feef051d9ddf9cb0950faa1fe6ffac` |
| `experiments/erdos151_siege/beta_bb.py` | `4f8d7fe9361d56119a4ed651ca46acb81366fba612916891178f7d28d06531d6` |

The three catalogue artifacts are tracked, unmodified blobs introduced by git
commit `b8064fdef93ef6fa760ddf0f35e34155273cb961`.  The manifest verifier passes
all of its entries.  The seven local order-17 records match the seven raw lines
served by Brendan McKay's site.

## Elementary proof audit

### 1. Residual direction and the three profiles — PASS

Fix a maximum five-clique `M`, put `X=V(G)-M`, and let `n_i` count vertices
with `i` neighbours in `M`.  No outside vertex has five such neighbours,
because that would extend `M` to a `K6`.  Since each member of `M` already has
four internal neighbours and `Delta(G)<=9`,

```text
W = sum_i i n_i <= 25,       t=25-W >= 0.
```

For `P_c=M-{c}` and `Z_c={x in X:N_M(x) subseteq {c}}`, every set `S`
admissible in `G[Z_c]` gives an ambient-admissible set `P_c union S`:

- every clique contained in `P_c` extends by `c`;
- `P_c` is anticomplete to `Z_c`, so there is no mixed clique; and
- if an ambient maximal clique were contained in `S`, it would also be
  maximal in the induced residual.

This is the required induced-to-ambient direction; no converse is used.
Hence `beta(G[Z_c])<=5`.  The verified theorem through order 39 then gives
`beta(G[Z_c])>=H(|Z_c|)`, so `|Z_c|<=17` because `H(18)=6`.

Writing `a_c=|A_c|`, direct elimination gives

```text
sum_c |Z_c| = 5n_0+n_1
            = 80+4t+3n_2+7n_3+11n_4 <= 85.
```

Thus `4t+3n_2+7n_3+11n_4<=5`.  Its only feasible tuples are
`(t,n_2,n_3,n_4)=(0,0,0,0),(0,1,0,0),(1,0,0,0)`.  Substitution gives the
reported R, D, and T values of `(n_0,n_1)`.  Applying the five unit
cross-degree capacities pointwise forces fan sizes

```text
R: (5,5,5,5,5)
D: (4,4,5,5,5), with w incident to the two four-fan clique vertices
T: (4,5,5,5,5), with the four-fan clique vertex of degree eight.
```

The resulting residual sizes are exactly those in the note.  Since
`H(16)=H(17)=5`, every one has residual beta exactly five.  These claims hold
for each fixed maximum clique `M`; the audit found no quantifier swap between
“for every fixed `M`” and “there exists an `M`”.

### 2. Every residual is `K4`-free — PASS

For an order-16 or order-17 residual `F` with `beta(F)<=5`, every open
neighbourhood is `F`-admissible, so `Delta(F)<=5`.  If `C` were a `K4`, choose
`c in C` and put `P=C-{c}`.  Each member of `P` has at most two neighbours
outside `C`.  At least

```text
|F|-4-3*2 >= 6
```

outside vertices are therefore anticomplete to all of `P`.  Six of them
contain an admissible three-set by the established order-six case
(`H(6)=3`).  Its anticomplete union with `P` is an admissible six-set in `F`:
`P` extends by `c`, mixed cliques do not exist, and induced maximality is used
in the sound direction.  This contradicts `beta(F)<=5`.

### 3. Degree-nine domination, `Delta(U)<=4`, and `D_0` — PASS

If `d_G(c)=9`, then `N_G(c)` is an admissible nine-set.  For `u in U`, the
ten-set `N_G(c) union {u}` is not admissible.  A witnessing ambient maximal
clique cannot be contained in `N_G(c)`, because it would extend by `c`; it
must contain `u`.  Since `u` is anticomplete to `M`, it follows that `u` has a
neighbour in the outside spoke of `c`.  This proves exactly the domination
statements in R, D, and the four full fans of T.

Using any full fan, `d_{G[Z_c]}(u)<=5` and domination give
`d_{G[U]}(u)<=4`.  In row D this inference uses one of the three full fans,
not either four-fan spoke containing `w`; the note's conclusion is valid.

At the degree-eight clique vertex in T, `N(c_0)` consists of the other four
clique vertices and `A_0`.  If two members of
`D_0={u in U:N(u) intersect A_0=empty}` were nonadjacent, they would be
isolated inside `N(c_0)` together with those two vertices, while every clique
inside `N(c_0)` extends by `c_0`.  That would be an admissible ten-set.
Therefore `D_0` is a clique.

### 4. The order-17 triangle argument and construction of `J` — PASS

Let `F` have order 17 and `beta(F)<=5`, and suppose `abc` is a triangle.
For edge `ab`, each endpoint has at most three neighbours outside the
triangle.  If the union of those two outside neighbourhoods had size at most
five, at least nine outside vertices would be anticomplete to `{a,b}`.  The
established order-nine bound (`H(9)=4`) would supply an admissible four-set
there, whose anticomplete union with `{a,b}` is an admissible six-set.  Hence
the union has size exactly six: both endpoint degrees are five and their
three-element outside neighbourhoods are disjoint.

Applying this to each triangle edge proves that every edge lying in a
triangle lies in exactly one triangle.  Distinct triangles are consequently
edge-disjoint.  If there are `q>=1` triangles, let `L` be the edges in no
triangle and retain one edge from each triangle.  The spanning graph

```text
J = L union {one selected edge from each triangle}
```

is triangle-free.  It meets every nontrivial maximal clique: maximal edges
are precisely in `L`, and `K4`-freeness makes every larger maximal clique a
triangle.  Every independent set of `J` is therefore admissible in `F`, so
`alpha(J)<=5`, and `|E(J)|=|E(F)|-2q`.

The pinned order-17 catalogue has minimum edge count 40 and minimum degree
four, while `Delta(F)<=5` gives `|E(F)|<=42`.  Therefore `q=1`,
`|E(F)|=42`, and `|E(J)|=40`.  The degree sequence of `F` is one 4 and
sixteen 5s, and all three vertices of its unique triangle have degree five.
Deleting two triangle edges incident with their common endpoint leaves that
endpoint of degree three in `J`, contradicting the catalogue minimum degree.
The inference is valid conditional on catalogue completeness.

### 5. The order-16 reduction and explicit falsifier — PASS

The published theorem `F_e(3,3;4)>19` implies that a `K4`-free graph on 16
vertices has a red/blue edge-colouring with no monochromatic triangle.  If
`L` is the set of its maximal 2-cliques, then `L` together with either colour
class is triangle-free and meets every nontrivial maximal clique.  Its
independent sets are admissible in the original graph.  Thus every order-16
residual has a spanning triangle-free `J` with `alpha(J)<=5`; conditional on
the complete order-16 catalogue, it is a supergraph of a catalogue record.
This direction does not claim that the residual itself is triangle-free.

The advertised counterexample was checked a third way, sharing neither beta
engine.  A separate short-form graph6 parser reconstructed the candidate by
adding `(1,3)` to the stated catalogue record.  Exhaustive enumeration of all
`2^16` vertex subsets found 37 nontrivial maximal cliques and gave

```text
n=16, e=39, degrees=(4,4,5^14), triangles=1,
alpha=5, omega=3, beta=5.
```

Every subset was tested directly against the exhaustive maximal-clique list.
The independent maximum admissible witness `{0,1,2,4,5}` has size five, and
the artifact's witness `{0,6,9,13,14}` is also admissible.  The base record is
present among 2,576 distinct decoded lines.  Both compressed and decoded
catalogue hashes match the manifest and witness JSON.

## Exact overlap-enumeration audit — FAIL

### Intended enumeration space

For each of the seven order-17 catalogue graphs, choosing the five-vertex fan
`A` determines its twelve-vertex complement `U` and the vector
`(d_A(u):u in U)`.  The fan must dominate `U`.  A separate bitset graph6
parser enumerated the per-record counts

```text
620, 602, 471, 625, 470, 772, 808,
```

which sum to the reported 4,368 dominating partitions.  A separate exact
backtracking isomorphism classifier, using stable colour refinement only for
candidate pruning and checking every adjacency, found the reported 786
unlabelled `U` classes.  Those two counts pass.

For a fixed representative `U`, however, every isomorphism from a partition's
`U` onto that representative must transport its cross-degree vector.  In
particular, even a class containing only one partition must contain the full
orbit of that vector under `Aut(U)`.

### Defect in the shipped checker

For a record matched to an existing class, checker lines 196–206 enumerate all
VF2 isomorphisms and add every transported vector.  But when lines 215–223
create a new class, they add only

```python
"patterns": {tuple(cross_degrees[vertex] for vertex in ordered)}
```

and never apply the new representative's automorphisms to that seed vector.
There is no later guarantee that another partition supplies its missing
orbit.  In the actual data, 39 of 786 classes are not automorphism-closed.
Closing the orbits adds 43 vectors, changing the total from 1,920 to 1,963.

One concrete certificate is the class represented by this graph6 string:

```text
K`_PYYCE@BGQ
```

In representative order its degrees and the seed pattern are

```text
degrees = (3,3,3,3,4,4,4,4,3,3,3,3)
p       = (1,1,1,1,1,1,1,1,2,2,2,2).
```

An automorphism transports `p` to the omitted valid pattern

```text
q       = (2,2,2,2,1,1,1,1,1,1,1,1).
```

For T, two copies each of `p` and `q` have sum

```text
(6,6,6,6,4,4,4,4,6,6,6,6),
```

which respects the degree-nine budget and saturates eight vertices.  Hence
this is a genuine seventh-or-later preliminary T class missed by the checker.
For D, one `q` and two `p` patterns leave remaining capacities
`(2,2,2,2,2,2,2,2,1,1,1,1)`: exactly four vertices are forced to meet `w`,
within its cap of seven.  Thus the same omitted orbit supplies a genuine
missing D core as well.

### Corrected T calculation

With every automorphic alignment present, ten classes—not six—carry four
full residuals within the `U` degree budget.  In every corrected feasible
state at least four vertices of `U` are already saturated at degree nine
(the observed minima range from four to eight).  Such vertices cannot meet
the remaining four-fan and lie in `D_0`.  Since `D_0` is a clique while `U`
is triangle-free, `|D_0|<=2`, a contradiction.  The corrected count is

```text
10 preliminary classes -> 0 after the D0 condition.
```

Therefore the conditional exclusion of row T survives, but every occurrence
of the exact preliminary count six must be corrected.

### Corrected D calculation and its scope

After three full fans, let `r(u)` be the remaining degree capacity of
`u in U`.  The note's necessary-condition logic is sound:

- `r(u)>=1`, because one edge to `w` can dominate both remaining spokes;
- if `uw` is absent, domination needs distinct edges into `A_p` and `A_q`,
  costing at least two units;
- hence `r(u)=1` forces `uw`; and
- at most seven vertices can be forced this way because `w` already meets
  `p,q in M` and has degree at most nine.

These are only necessary conditions.  They impose neither the two order-16
extensions nor the edges between other fans, and the note correctly avoids
calling them sufficient.  With complete automorphism orbits, **17** common
cores survive.  The five classes omitted from the result JSON are:

```text
K`_PYYCE@BGQ
K??P`XMUCKyG
K`_PYWWOkHCI
K@?JKhheagT?
K@hWOHacbAqK
```

Together with the 12 reported representatives they still satisfy
`e(U) in {20,21,22}`, `alpha(U) in {4,5}`, and `Delta(U)=4`.  Those invariant
ranges therefore survive, while the claimed twelve-core frontier does not.

## Catalogue completeness, provenance, and priority wording

The current [official Ramsey data page](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html)
labels its section “All Ramsey(3,6)-graphs” and lists 2,576 graphs at order 16
and seven at order 17.  Its raw order-17 file is byte-for-byte the pinned
seven-line file.  The [Hugging Face mirror for order 17](https://huggingface.co/datasets/linxy/RamseyGraph/blob/main/data/r36_17.g6)
publishes the same SHA-256 as the local file, and the
[order-16 mirror](https://huggingface.co/datasets/linxy/RamseyGraph/blob/main/data/r36_16.g6.gz)
publishes the same compressed SHA-256 as the local gzip.  Independent local
checks found all seven order-17 records pairwise nonisomorphic,
triangle-free, without an independent six-set, with edge histogram
`{40:2,41:3,42:2}` and minimum degree four.

This verifies byte provenance and the properties used after accepting the
catalogue.  It does not turn catalogue completeness into a theorem checked by
the repository, and the note is correct to state the T conclusion
conditionally.  The manifest is acquisition provenance, not a bibliographic
priority record.  Historical/public wording should also cite
[Radziszowski–Kreher, *On (3,k) Ramsey graphs: theoretical and computational results*, JCMCC 4 (1988), 37–52](https://repository.rit.edu/article/640/),
which describes the complete catalogue for `k<=6`.  Referring to the hosted
files as “Brendan McKay's Ramsey catalogue” identifies the present source but
should not be used as a claim of original priority.  Likewise, “new
reduction” is safe only as repository chronology unless a separate novelty
search is supplied.

## Reproduction record and final blockers

A fresh Python process was run with bytecode writing disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\check_order41_k5_overlap.py
```

It exited zero and printed `status: VERIFIED`, `4368`, `786`, `6 -> 0`, and
`12`.  That is a successful replay of the shipped program, not an independent
validation: the program both omits seed automorphisms and hard-codes the
resulting counts in assertions.

The independent reconstruction shared no checker parsing, classification, or
beta code.  It used a separate graph6 parser, a direct adjacency-preserving
backtracking isomorphism enumerator (including all automorphisms), set-valued
degree-budget dynamic programming, and exhaustive subset testing for the
order-16 beta value.  It returned `4368`, `786`, `1963`, `10 -> 0`, `17`, and
`beta=5`.

Exact blockers to a PASS are:

1. `exact_common_core_classes` must close the seed pattern under every
   automorphism of its new representative.
2. The hard-coded T preliminary count, D survivor count, and derived emitted
   data must be recomputed (`10`, `17`, and the five additional cores above).
3. The note and `ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json` must be updated to
   those corrected exact results and then rebound to a corrected checker.

Until those are done and independently replayed, the package is **FAIL** even
though its elementary lemmas, conditional T exclusion, catalogue hashes, and
order-16 falsifier pass.
