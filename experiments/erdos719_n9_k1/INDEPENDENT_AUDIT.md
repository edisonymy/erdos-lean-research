# Independent audit of the bounded Erdős #719 theorem

**Date:** 2 August 2026.  **Verdict:** **PASS**, including the post-audit
checker remediation.  The stated theorem for `r=3`, `n=9`, and `nu(G)<=1` is sound.
The reduction `phi(G)=e(G)-3nu(G)`, the value
`ex_3(9,K_4^3)=54`, the 3-intersecting-family dichotomy, and the
fixed-five missing-edge argument all survive independent derivation and
adversarial finite checks.  No counterexample was found.

This remains bounded progress only.  It does not solve Erdős #719, does not
certify any larger packing-number or order, and does not turn the stored
proofless SAT responses into formal UNSAT certificates.

The original audit found that `check_result.py` recomputed graph quantities
correctly but did not enforce its declared input scope.  Before publication it
was changed to require the exact schema, require a packing-number upper bound
of at most one, reject a graph whose recomputed packing exceeds that bound,
and emit the narrower status `VERIFIED_GRAPH_QUANTITIES`.  A second independent
pass confirmed those rejections.  The checker still is **not** a checker for
the universal nine-vertex theorem: the theorem is established by the short
mathematical proof, with `check_structure.py` and the exact extremal computation
as finite backstops.

## Verdict ledger

| claim | verdict | audit finding |
|---|---|---|
| Fidelity to Erdős #719 | **PASS** | The live statement asks for an edge-disjoint cover by singleton `r`-edges and `K_(r+1)^r` copies using at most the corresponding Turán number.  For `r=3`, the package specializes this correctly. |
| `phi(G)=e(G)-3nu(G)` | **PASS** | A packing of `t` tetrahedra uses `4t` triples and leaves `e-4t` singleton pieces, for `e-3t` pieces; maximizing `t` gives the exact minimum. |
| Empty/no-`K_4^3` case | **PASS** | If `nu=0`, then `G` is `K_4^3`-free and `phi=e<=54`.  No erroneous subtraction of three occurs. |
| Exact `ex_3(9,K_4^3)=54` | **PASS** | Exact `t_7=12`, two valid deletion inequalities, and checked 8- and 9-vertex cyclic constructions give `t_8=20`, `t_9=30`, and hence `84-30=54`. |
| Classification of 3-intersecting 4-set families | **PASS** | Families of size zero or one lie in the common-triple branch.  For at least two members, the stated common-triple/fixed-five dichotomy is exhaustive. |
| Common-triple branch | **PASS** | The common triple is an edge of every present tetrahedron.  Removing it makes the graph `K_4^3`-free, so `e<=55` and in fact `phi<=52`. |
| Fixed-five missing-edge argument | **PASS** | Missing triples hit all 121 external 4-sets.  Three specified triples hit the five internal 4-sets, so `t_9=30` forces at least 27 actual missing triples. |
| Bounded theorem `phi<=54` for `nu<=1` | **PASS** | The integer cases `nu=0` and `nu=1` are both covered, including one-copy and non-common-triple fixed-five families. |
| `check_structure.py` | **PASS within its declared finite scope** | It checks the decisive local implication for 18,900 `(A,B,C,D)` configurations and checks the three-triple internal cover.  It does not itself check `t_9=30`. |
| `check_result.py` | **PASS within its declared graph-checking scope** | It checks the supplied edge list, exact packing, schema, and packing-one bound and emits `VERIFIED_GRAPH_QUANTITIES`.  It deliberately does not prove the universal theorem. |
| Manifest hashes | **PASS with self-hash excluded** | All 20 listed hashes reproduce, including this audit, the result summary, and the adversarial checker test.  Only `MANIFEST.json` excludes its own hash. |
| Stored SAT UNSAT results | **ADVISORY ONLY** | Their files are hash-stable, but there are no proof logs.  The bounded theorem does not depend on them. |

## 1. Exact problem statement and specialization

The [live Erdős Problems statement](https://www.erdosproblems.com/719) defines
`ex_r(n;K_(r+1)^r)` as the largest number of `r`-edges in an `n`-vertex
`K_(r+1)^r`-free hypergraph.  It asks whether every `r`-graph can be covered
by at most that many copies of `K_r^r` and `K_(r+1)^r`, with no two pieces
sharing an `r`-edge.  The cited primary source is Erdős,
[Combinatorica 1 (1981), 25–42](https://doi.org/10.1007/BF02579174).

For `r=3`, a `K_3^3` is one triple and a `K_4^3` consists of the four triples
on four vertices.  Thus “no two share a `K_3^3`” means edge-disjoint pieces,
not vertex-disjoint pieces.  The package's use of the maximum number `nu(G)`
of edge-disjoint `K_4^3` copies is exactly the relevant packing parameter.

The proved statement is only

```text
for every 3-graph G on 9 vertices:
    if nu(G)<=1, then e(G)-3nu(G)<=54.
```

That is a faithful finite slice of the conjecture.  It is not an affirmative
proof for arbitrary `n`, `r`, or `nu`.

## 2. Exact decomposition reduction

Fix a decomposition containing `t` edge-disjoint copies of `K_4^3`.  They
cover `4t` edges.  Every other edge must be covered by its singleton
`K_3^3`, so the number of pieces is

```text
t + (e(G)-4t) = e(G)-3t.
```

Conversely, every packing of `t` tetrahedra extends to such a decomposition
by making every uncovered edge a singleton.  The expression decreases with
`t`, so its minimum is attained at `t=nu(G)`:

```text
phi(G)=e(G)-3nu(G).
```

This includes `e=0` and `nu=0` without qualification.  As an independent
finite attack, a separate direct set-partition recursion was run on all 1,024
3-graphs on five vertices.  In every case its minimum number of pieces agreed
with `e-3nu`, including the empty graph.  No counterexample was found.

The sentence in `PLAN.md` that a “packing-one counterexample needs at least
58 edges” is correct specifically when `nu=1`:

```text
e-3 > 54  iff  e>=58.
```

It should not be read as the threshold for `nu=0`; that case is impossible
already because `e<=ex_3(9,K_4^3)=54`.

## 3. Independent derivation of `ex_3(9,K_4^3)=54`

Let `t_n` be the minimum number of triples meeting every 4-subset of an
`n`-set.  The complement of such a hitting family is `K_4^3`-free, so

```text
ex_3(n,K_4^3)=C(n,3)-t_n.
```

### Exact base value

`check_result.py` computes `t_7=12` by an exact memoized hitting-set
recurrence.  At any state it selects one uncovered 4-set and branches on its
four triples.  Every completion must choose at least one of those four, so
the recurrence is exhaustive; memoization changes only runtime, not the
search space.

The checker was rerun from clean output and again returned 12.  A separately
written PySAT encoding, not importing the checker, found:

```text
t_7<=11: UNSAT
t_7<=12: SAT with a 12-triple hitter.
```

The SAT response has no proof log and is only a cross-check; the standard-
library recurrence is the exact exhaustive computation.

### Deletion inequalities

For a hitting family `T` on `n` vertices and a vertex `v`, let `T-v` be the
triples of `T` avoiding `v`.  It hits every 4-set avoiding `v`, so
`|T-v|>=t_(n-1)`.  Every triple avoids exactly `n-3` vertices.  Summing gives

```text
(n-3)|T| = sum_v |T-v| >= n t_(n-1),
```

and therefore `(n-3)t_n>=n t_(n-1)`.  Hence

```text
t_8 >= ceil(8*12/5) = 20,
t_9 >= ceil(9*20/6) = 30.
```

### Matching constructions

The independently regenerated cyclic construction uses three parts and the
profiles

```text
(1,1,1), (2,1,0), (0,2,1), (1,0,2).
```

Every 4-set was checked directly.  The `3,3,2` instance is `K_4^3`-free
with 36 edges, hence has 20 missing triples.  The `3,3,3` instance is
`K_4^3`-free with 54 edges, hence has 30 missing triples.  Thus

```text
t_8=20,
t_9=30,
ex_3(9,K_4^3)=C(9,3)-30=84-30=54.
```

The extremal certificate is complete; it does not assume the unresolved
asymptotic Turán problem.

## 4. Classification of the present tetrahedra

Let `F` be the family of 4-vertex sets supporting present `K_4^3` copies.
Two distinct tetrahedra share a hyperedge exactly when their vertex sets
intersect in three vertices.  Therefore `nu(G)<=1` and `F` nonempty imply
that every two members of `F` intersect in at least three vertices.

If `|F|=1`, any triple in its sole member is a common triple.  Now suppose
`|F|>=2`.  Choose distinct `A,B in F`.  Write

```text
S=A intersect B,       A=S union {a},
|S|=3,                 B=S union {b},
U=A union B=S union {a,b}.
```

If every member contains `S`, the family has a common triple.  Otherwise
choose `C` not containing `S`.  The inequalities
`|C intersect A|>=3` and `|C intersect B|>=3` force

```text
C=(S\{s}) union {a,b}
```

for one `s in S`, so `C` lies in `U`.

For any further member `D`, suppose that `D` contains a point outside `U`.
Its intersections with both `A` and `B` can have size at least three only if

```text
D=S union {y},  where y is outside U.
```

But then `|C intersect D|=2`, contradicting 3-intersection.  Hence every
member lies in the fixed five-set `U`.

This proves the stated dichotomy with all family-size quantifiers included.
The shipped checker verified 18,900 local `(A,B,C,D)` configurations.  A
separate exhaustive test fixed a canonical pair
`A=0123`, `B=0124`, enumerated every pairwise 3-intersecting family containing
that pair (which is exhaustive up to relabelling), and found 23 families:

```text
16 common-triple families;
 7 fixed-five families with no common triple;
 0 counterexamples.
```

## 5. The two nonempty branches

### Common triple

If every member of `F` contains the same triple `S`, then `S` is an edge of
`G`, because `F` is nonempty.  Deleting that one edge destroys every present
`K_4^3`; deletion cannot create a new copy.  Consequently

```text
e(G)-1 <= ex_3(9,K_4^3)=54,
e(G) <= 55,
phi(G)=e(G)-3 <= 52.
```

The regenerated 55-edge example has exactly the three tetrahedra `0123`,
`0124`, and `0125`, exact packing number one, and decomposition value 52.

### Fixed five-set

Suppose instead that every member of `F` lies in a fixed five-set `U`.  Let
`M` be the missing triples of `G`.  Every 4-set not contained in `U` fails to
support a tetrahedron, so at least one of its four triples lies in `M`.
Thus `M` hits all 121 external 4-sets.

For `U={0,1,2,3,4}`, the three triples

```text
012, 034, 123
```

hit all five 4-subsets of `U`.  Adjoin these triples to `M` as an abstract
hitting family.  They need not themselves be missing edges of `G`; that is
irrelevant because `t_9` minimizes over all hitting families.  The union hits
all 126 four-sets, so

```text
30=t_9 <= |M union {012,034,123}| <= |M|+3.
```

Therefore `|M|>=27`, and

```text
e(G) <= 84-27=57.
```

This branch is nonempty, so `nu(G)=1`, not merely `nu(G)<=1`.  Hence

```text
phi(G)=e(G)-3 <= 57-3=54.
```

A fresh counterexample search encoded the 84 triples as missing-edge
variables, required them to hit all 121 external 4-sets, and imposed
`|M|<=26`.  CaDiCaL returned UNSAT in 28.141 seconds.  This proofless solver
response is supporting evidence only; the hitting-completion argument above
already proves the bound.

The stored threshold-57 SAT response would strengthen the fixed-five bound to
`|M|>=28` if certified.  That strengthening is unnecessary, and this audit
does not promote it beyond the package's existing “solver result, no proof
log” status.

## 6. Empty and boundary cases

The proof's outer case split is exhaustive because `nu` is a nonnegative
integer and the hypothesis is `nu<=1`:

1. `nu=0`: `F` is empty, `G` is `K_4^3`-free, and `phi=e<=54`.
2. `nu=1`: `F` is nonempty and 3-intersecting, so one of the two classified
   branches applies.

Independent definition-level checks included these four boundary examples:

| example | edges | present tetrahedra | `nu` | `phi` | branch |
|---|---:|---:|---:|---:|---|
| empty graph | 0 | 0 | 0 | 0 | empty |
| cyclic extremal graph | 54 | 0 | 0 | 54 | empty/equality |
| one isolated tetrahedron | 4 | 1 | 1 | 1 | common triple |
| all ten triples on a fixed five-set | 10 | 5 | 1 | 7 | fixed five, no common triple |

The last example is useful: its five 4-sets have empty total vertex
intersection, so the fixed-five branch is genuinely needed and is not a
rephrasing of the common-triple branch.

## 7. What the standard-library checkers actually certify

### `check_result.py`

For the supplied nine-vertex edge list, the checker does all of the following
correctly:

- sorts and validates triples and rejects duplicate or invalid edges;
- enumerates all 126 possible `K_4^3` vertex sets;
- computes the exact edge-disjoint packing number by an independent-set
  recursion on the present copies;
- computes `e-3nu` using that exact packing number;
- computes exact `t_7=12`, checks the deletion bounds, and checks the two
  cyclic constructions;
- rejects incorrect optional reports for edge count, extremal value,
  decomposition value, and margin.

Its clean rerun reproduced `lower_55_checked.json` byte for byte, including
packing number one, decomposition value 52, and margin `-2`.

It does **not**:

- check the 3-intersecting classification or the fixed-five 27-missing-edge
  implication;
- verify `MANIFEST.json`, `result_summary.json`, or any SAT output;
- produce a universal enumeration over all 3-graphs on nine vertices.

The first audit's adversarial inputs exposed the old scope bug.  After
remediation, `test_check_result.py` and a separate second pass confirmed that
the checker rejects a wrong schema, a missing or false packing bound, a bound
greater than one, and a graph with recomputed packing number two claiming
bound one.  Valid packing-zero and packing-one inputs are accepted with status
`VERIFIED_GRAPH_QUANTITIES`.  That status means the input scope and graph
quantities were checked; it does not mean the universal theorem was
machine-proved.

### `check_structure.py`

This checker has no input artifact.  It reruns a fixed enumeration of the
local classification implication and checks the displayed three-triple
cover.  Its 18,900 count is a count of compatible `(A,B,C,D)` loop instances,
not a count of all 3-graphs or all set families.  The loop is nevertheless
sufficient for the local implication used in the human proof.  The elementary
case “if no `C` omits `S`, then `S` is common” is logical rather than
enumerated.

It records the string consequence “missing>=27,” but does not compute
`t_9=30`; that is done in `check_result.py` and joined to the structure result
by the human argument.

## 8. Reproduction and artifact integrity

The two checker runs and the construction generator were executed in a clean
temporary directory so the retained artifacts were not overwritten.  Their
outputs reproduced byte for byte:

```text
structure_checked.json
  ff5e093f3377f2a31f225361a4456af72a67b28168dd6aa9cddf5dfc496c0a63
lower_55.json
  150cd0f96e3d8729fdd8b25c1b04745f4146711d4cac91f2592143c9f0c2cc30
lower_55_checked.json
  2fb899f9f1cf2736f8dd4a260493397ed4d0eb05220bf36226dcdf5409915bad
```

All 20 file hashes listed in `MANIFEST.json` match the current files.  The
manifest authenticates `result_summary.json`, this audit, and the adversarial
checker test.  Only the manifest's own self-hash is excluded, avoiding a
circular self-reference.

The threshold JSON files reproduce their recorded manifest hashes, but a hash
only establishes file identity.  The files contain no solver proof, complete
command transcript, or independently checkable UNSAT certificate.  The
analytic bounded theorem is valuable precisely because it does not rely on
those responses.

## Final boundary

The package soundly proves:

```text
nu(G)<=1 and |V(G)|=9 and G 3-uniform
    => phi(G)=e(G)-3nu(G)<=54=ex_3(9,K_4^3).
```

The common-triple branch actually gives `phi<=52`; the fixed-five branch gives
the sharp bound needed here, `phi<=54`.  No counterexample to any intermediate
lemma was found in the independent exhaustive, SAT, or boundary-case attacks.

No conclusion is made for `nu>=2`, `n>=10`, `r!=3`, or the full Erdős–Sauer
conjecture.  At audit time no external mathematical claim beyond this bounded
scope had been made.
