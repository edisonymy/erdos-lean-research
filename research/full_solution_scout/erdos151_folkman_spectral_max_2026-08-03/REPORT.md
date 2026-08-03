# Erdős #151: bounded Folkman–spectral construction scout

**Date:** 3 August 2026  
**Lane:** low-degree endpoint Cayley constructions, maximal-edge spectra, and exact construction operations  
**Decision:** **KILL / DEMOTE this lane**

## Outcome

This scout found neither a counterexample nor a proof of Erdős problem #151.
It exhausts three precisely stated connected Cayley families and proves that
none contains a counterexample at the relevant Ramsey threshold. The true
minimum values of `beta` in the scanned families are two, two, and three above
the sufficient counterexample targets:

| family | connected multiplier/automorphism orbits | sufficient target | exact family minimum `beta` | gap | number attaining minimum |
|---|---:|---:|---:|---:|---:|
| `Cay(Z_50,D)`, degree at most 10 | 6,693 | `beta <= 10` | 12 | 2 | 30 |
| `Cay(Z_2 x Z_5 x Z_5,D)`, degree at most 10 | 401 | `beta <= 10` | 12 | 2 | 3 |
| `Cay(Z_59,D)`, degree at most 10 | 5,055 | `beta <= 11` | 14 | 3 | 14 |

There is therefore **no one-away graph** in any stated family. The
deterministically selected minimizer checked in detail in each family is
triangle-free, so its maximal-clique-free number is just its independence
number; these checked examples do not expose a promising nontrivial
maximal-clique mechanism.

The exact values 16, 20, and 25 appearing in
`audit_family_minima.result.json` have a narrower meaning: they are the minima
only among the 610, 128, and 39 representatives that pass the necessary
`alpha <= 10`, `alpha <= 10`, and `alpha <= 11` filters. They are **not** the
whole-family minima. The result schema and field names say this explicitly.

## Definitions and Ramsey calibration

All graphs here are finite, simple, and undirected. A *nontrivial maximal
clique* is an inclusion-maximal clique of size at least two. A set of vertices
is *admissible* if it contains no nontrivial maximal clique, and

```text
beta(G) = max{|S| : S is admissible}.
```

Let

```text
H(n) = min{alpha(T) : T is a triangle-free graph on n vertices}.
```

Problem #151 asks whether `beta(G) >= H(n)` for every `n`-vertex graph `G`.
This is equivalent to the original clique-transversal formulation. The basic
reduction and the campaign's established finite-order context are recorded in
[`GENERAL.md`](../../erdos151/general/GENERAL.md).

Using the current bounds `R(3,11) <= 50` and `R(3,12) >= 53`, one has
`H(50) = 11`: the first inequality gives the lower bound, while the second
gives a triangle-free 52-vertex graph with independence number at most 11,
whose induced 50-vertex subgraphs give the upper bound. The bound
`R(3,12) <= 59` gives `H(59) >= 12`. Thus `beta <= 10` at order 50 or
`beta <= 11` at order 59 would suffice for a counterexample. Ramsey inputs are
from Radziszowski's April 2026 revision of
[*Small Ramsey Numbers*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1).

The degree cut is sound for these targets. For every vertex `v`, its open
neighborhood `N(v)` is admissible: a maximal clique contained in `N(v)` could
be extended by `v`. Hence `beta(G) >= Delta(G)`. A target-50 candidate must
therefore have degree at most 10. A target-59 candidate has degree at most 11,
and an undirected Cayley graph on the odd group `Z_59` has even degree, hence
degree at most 10.

The Folkman gateway used by this lane is the established implication

```text
G does not edge-arrow (3,3)  =>  beta(G) >= H(|V(G)|).
```

Consequently, any graph found with `beta(G) < H(n)` would automatically be an
edge-Folkman graph. Since the scans found no such graph, no edge-arrowing claim
or edge-coloring certificate is made here.

## Proved analytic statements

The following statements are ordinary mathematical deductions, independent
of the finite scans.

### 1. Maximal-edge spectral gateway

Let `L(G)` be the spanning graph whose edges are exactly the edges of `G` that
lie in no triangle of `G`. Equivalently, these edges are the maximal cliques of
`G` of size two.

**Lemma.** `L(G)` is triangle-free and

```text
beta(G) <= alpha(L(G)).
```

**Proof.** A triangle in `L(G)` would be a triangle in `G`, contradicting the
definition of each of its edges. An admissible set cannot contain an edge of
`L(G)`, since that edge is itself a nontrivial maximal clique of `G`. Every
admissible set is therefore independent in `L(G)`. ∎

If `L(G)` is `d`-regular with least adjacency eigenvalue `theta < 0`, Hoffman's
ratio bound gives

```text
beta(G) <= alpha(L(G))
        <= floor(|V(G)| (-theta) / (d - theta)).
```

Thus a graph satisfying

```text
floor(n (-theta) / (d - theta)) <= H(n) - 1
```

would be a counterexample and, by the Folkman reduction, would edge-arrow
`(3,3)`. This is a valid sufficient construction criterion, not an existence
theorem. Notice especially that Hoffman supplies an **upper** bound here.

### 2. Fractional identity under vertex transitivity

Let `A(G)` be the family of admissible sets, and define its fractional covering
number by

```text
chi_A^*(G) = min sum_S w_S,
```

where `w_S >= 0` and `sum_{S contains v} w_S >= 1` for every vertex `v`.

**Lemma.** If `G` is vertex-transitive on `n` vertices, then

```text
chi_A^*(G) = n / beta(G).
```

**Proof.** Summing all vertex-cover constraints gives
`n <= sum_S w_S |S| <= beta(G) sum_S w_S`, proving the lower bound. For the
upper bound, average the orbit of a maximum admissible set under the
automorphism group. Every vertex occurs equally often, and uniform orbit
weights give total weight `n/beta(G)`. ∎

This identity explains why fractional averaging is exact in the Cayley
setting, but it does not by itself compute or upper-bound `beta`.

### 3. Exact blow-up and join identities

For isolated-vertex edge cases, define

```text
gamma(G) = max{|S| : S contains no inclusion-maximal clique of any size}.
```

Singleton maximal cliques are exactly isolated vertices, so `gamma(G)=beta(G)`
when `G` has no isolated vertices. For `t >= 2` and nonempty graphs `G,H`,

```text
beta(G[empty K_t]) = t beta(G),
beta(G[K_t])       = (t-1)|V(G)| + gamma(G),
beta(G join H)     = max(gamma(G)+|V(H)|, |V(G)|+gamma(H)).
```

Here `G[empty K_t]` is the independent lexicographic blow-up and `G[K_t]` is
the clique blow-up.

For the independent blow-up, a lifted nontrivial maximal clique chooses one
vertex from every bag above a nontrivial maximal clique of `G`; the support of
any admissible set must therefore be admissible in `G`, and filling every
supported bag proves equality. For the clique blow-up, maximal cliques are
unions of full bags above maximal cliques of `G`. Put `t-1` vertices in every
bag and fill exactly the bags indexed by a `gamma`-admissible support. For the
join, every maximal clique is the union of one maximal clique from each
factor. Avoiding all such unions means that the selected vertices in at least
one factor are `gamma`-admissible, which gives the displayed maximum.

These formulas do not rule out every finite construction using these
operations, but they show that the standard amplifications do not shrink the
relevant normalized obstruction. `check_operation_lemmas.py` independently
regression-checks the formulas on 150 independent blow-ups, 150 clique
blow-ups, and 121 joins of small labelled graphs; the proofs above are the
general justification.

## Computationally established results

All claims in this section are limited to the stated finite families.

### Family scope and orbit completeness

The connection sets are inverse-closed, omit the identity, and have degree at
most 10. Only connected graphs are retained. The quotient actions are sound
Cayley automorphism actions; they need not be complete graph-isomorphism
quotients, so duplicate isomorphic graphs may remain, but no connection set is
lost.

| family | raw connection sets covered by audit | quotient action | audited orbit result |
|---|---:|---|---:|
| `Z_50` | 66,792 connected | multiplication by the 20 units modulo 50 | 6,693 |
| `Z_2 x Z_5 x Z_5` | 68,405 nonempty; 66,657 connected | full `GL(2,5)`, order 480 | 437 total = 401 connected + 36 disconnected |
| `Z_59` | 146,595 nonempty (all connected) | multiplication by the 58 nonzero residues | 5,055 |

`audit_orbits.py` independently forms every raw bounded-degree connection set,
forms the full named action orbit, and verifies that the disjoint orbit union
matches the raw set and the representatives consumed by the scans. All three
`complete` flags are true.

### Threshold scan and `beta` semantics

For a requested size `k`, the SAT encoding has one selection variable per
vertex, an exact-cardinality constraint, and the unit clause selecting vertex
0. Fixing vertex 0 is equisatisfiable because every graph is Cayley and any
nonempty selected set can be translated to contain the identity.

The fast first stage asks for an independent set of size 11 at order 50 or 12
at order 59. Every independent set is admissible. If none exists, a custom
bitset Bron–Kerbosch enumerator lists all inclusion-maximal cliques of size at
least two. For every such clique `C`, the second-stage clause is exactly

```text
OR_{v in C} not x_v,
```

so a satisfying assignment is definitionally an admissible set of the
requested size. Admissibility is hereditary, so testing exact size is enough.

| family | reps tested | rejected by independent witness | alpha-threshold survivors | rejected by general admissible witness | candidates |
|---|---:|---:|---:|---:|---:|
| cyclic 50 | 6,693 | 6,083 | 610 | 610 | 0 |
| noncyclic abelian 50 | 401 | 273 | 128 | 128 | 0 |
| cyclic 59 | 5,055 | 5,016 | 39 | 39 | 0 |

`audit_beta_semantics.py` reconstructs all 777 alpha-threshold survivors,
compares the custom maximal-clique set with `NetworkX.find_cliques`, and checks
every recorded size-11 or size-12 witness directly against the definition.
All maximal-clique sets and all witnesses agree.

### True near-miss values

The fast scan does not retain graphs rejected by its independent-set stage, so
the true family minima require a separate all-representative audit.
`audit_global_near_miss.py` regenerates every connected representative and
tests successively larger admissible-set sizes:

| family | all SAT at sizes | first mixed size | UNSAT count | exact minimum `beta` |
|---|---|---:|---:|---:|
| cyclic 50 | 12 | 13 | 30 | 12 |
| noncyclic abelian 50 | 12 | 13 | 3 | 12 |
| cyclic 59 | 13, 14 | 15 | 14 | 14 |

At the first mixed size, an UNSAT representative has `beta` exactly one less,
because every representative was SAT at the preceding size. For the
minimum-edge-hash minimizer in each family, Checker A uses bitset
Bron–Kerbosch plus CaDiCaL exact-cardinality SAT. Checker B independently
reconstructs the graph, uses `NetworkX.find_cliques`, and maximizes `beta` with
RC2 weighted MaxSAT. The maximal-clique sets and exact values agree. The
exhaustive Checker-A counts establish the number of minimizers; Checker B is a
cross-check on one minimizer per family.

The checked minimizers have the following parameters:

| family | parameters | clique-size distribution | exact `beta` |
|---|---|---|---:|
| cyclic 50 | steps `[1,3,8,14,20]` | 250 cliques of size 2 | 12 |
| noncyclic abelian 50 | generators `[(0,0,1),(0,1,0),(0,1,2),(1,0,1),(1,2,2)]`, no involution | 250 cliques of size 2 | 12 |
| cyclic 59 | steps `[1,3,5,18,25]` | 295 cliques of size 2 | 14 |

Thus each checked minimizer is triangle-free and `beta=alpha`. This makes the
gap rigorous but offers no maximal-clique construction leverage.

### Spectral audit

For those triangle-free minimizers, `L(G)=G`. The maximal-edge spectral
gateway is quantitatively loose:

| family | degree | least eigenvalue of `L(G)` | Hoffman upper bound on `beta` | sufficient target | true `beta` |
|---|---:|---:|---:|---:|---:|
| cyclic 50 | 10 | -6.547424 | 19 | 10 | 12 |
| noncyclic abelian 50 | 10 | -5.854102 | 18 | 10 | 12 |
| cyclic 59 | 10 | -5.757017 | 21 | 11 | 14 |

The alpha-threshold survivor minimizers have exact `beta` values 16, 20, and
25; their corresponding `L(G)` Hoffman bounds are 21, 22, and 28. The spectral
criterion therefore misses the target in both the whole-family near misses and
the structurally necessary survivor pool.

## What is not proved

- No graph outside the three stated connected Cayley families is excluded.
- The quotient counts are not counts of abstract graph-isomorphism classes.
- No counterexample, all-graphs theorem, new Ramsey bound, or edge-Folkman
  number is established.
- The spectral gateway is only sufficient; failure of its Hoffman bound does
  not imply that `beta` is large in an arbitrary graph.
- The operation identities do not exclude ad hoc finite modifications.
- No publication-priority claim is made. The live
  [Erdős Problems #151 page](https://www.erdosproblems.com/151) remains the
  status reference, and this negative bounded scout is not a solution claim.

## Hard recommendation

**Kill and demote this endpoint Cayley/spectral construction lane. Do not
expand it to more cyclic orders, larger degree, or additional symmetric group
families.**

The stopping evidence is cumulative:

1. Every representative at the two selected Ramsey endpoints fails.
2. The true gaps are 2, 2, and 3, so there is no one-away object.
3. The independently checked minimizer in each family is triangle-free; these
   concrete nearest witnesses merely reproduce the ordinary independence
   obstruction.
4. Representatives satisfying the necessary independence thresholds are far
   worse, with minima 16, 20, and 25.
5. Hoffman's bound on the maximal-edge graph is substantially looser than the
   exact `beta` values and nowhere near the targets.
6. Independent/clique blow-ups and joins obey exact identities that supply no
   gap-reducing amplification.

Redeploy to this lane only if an external argument supplies one of the
following bounded triggers:

- an explicit low-degree non-Cayley edge-Folkman seed whose maximal-edge graph
  already has a certified independence upper bound at most `H(n)-1`;
- a rigorously checked graph with `beta=H(n)` together with a local operation
  proved to lower `beta` without lowering the Ramsey threshold; or
- a new upper-bound mechanism for `alpha(L(G))` that is demonstrably much
  sharper than Hoffman on a concrete candidate.

Absent such a trigger, further symmetric enumeration is low-value expansion.

## Replay

From the repository root in PowerShell, using the recorded environment:

```powershell
$py = '.\.venv\Scripts\python.exe'
$d = 'research\full_solution_scout\erdos151_folkman_spectral_max_2026-08-03'

& $py "$d\make_manifest.py"  # verify the frozen delivery before regenerating outputs
& $py "$d\scan_circulants_n50.py"
& $py "$d\scan_abelian_n50.py"
& $py "$d\scan_circulants_n59.py"
& $py "$d\audit_orbits.py"
& $py "$d\audit_family_minima.py"
& $py "$d\audit_beta_semantics.py"
& $py "$d\audit_global_near_miss.py"
& $py "$d\check_operation_lemmas.py"
```

The observed full replay is approximately five minutes on the recorded
Windows/Python environment; `audit_global_near_miss.py` is the dominant step.
The scan JSON files include wall-clock runtimes, so a replay is semantically
reproducible but not byte-identical in those fields and will no longer match
the frozen manifest after regeneration. `MANIFEST.json` records
SHA-256 hashes of the frozen delivered artifacts. Run `make_manifest.py`
without `--write` to verify them; use `--write` only when intentionally
refreezing an updated artifact set.
