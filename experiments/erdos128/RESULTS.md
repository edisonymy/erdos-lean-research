# Erdős Problem 128: audit and finite search

Status as of 2026-08-01: **no solution or counterexample is claimed here**.
The general problem remains open.  The catalogue checks give a reproducible
exclusion through 15 vertices.  At order 16, two independently constructed
native-cardinality encodings and different exact solvers now both return
UNSAT in all three exhaustive structural cases.  Regenerated CNFs for those
cases now also have retained LRAT certificates accepted by a separate checker.
The order-16 exclusion remains conditional on McKay catalogue completeness,
the documented reduction, and checker correctness.  It is a finite partial
result, not a proof of the open problem and not a claimed novel theorem.

## Exact statement and fidelity

The pinned input is Formal Conjectures commit
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`, file
`FormalConjectures/ErdosProblems/128.lean`.  Its right-hand side says that for
every finite simple graph `G` on `n` vertices,

```text
(for every V', 2 |V'| + 1 >= n implies 50 e(G[V']) > n^2)
  implies G contains a 3-clique.
```

This is faithful to the current source statement:

- For integral `k`, `2k + 1 >= n` is equivalent to
  `k >= floor(n/2)`, for both parities of `n`.
- `G.induce V'` is the induced graph and `edgeSet.ncard` counts its unordered
  edges once.
- `50 e > n^2` is exactly the integer form of `e > n^2/50`.
- `¬ G.CliqueFree 3` is existence of a 3-clique, hence a triangle.
- It suffices computationally to check sets of exactly `floor(n/2)` vertices:
  extending a vertex set cannot remove induced edges.

The history matters.  Earlier versions had three separate fidelity bugs or
ambiguities: use of a non-induced subgraph, the wrong inequality, and (most
seriously) an outer `V'` quantifier that required only one dense subgraph.  The
last was fixed by merged PR
[#4501](https://github.com/google-deepmind/formal-conjectures/pull/4501) on
2026-07-26.  The pinned version includes that fix and universally quantifies
`V'` inside the premise.

The source page [Erdős Problem 128](https://www.erdosproblems.com/128) marks
the problem open and describes the known partial results.  Razborov's
[More about sparse halves in triangle-free graphs](https://arxiv.org/abs/2104.09406)
still describes the conjecture as open, proves the general `27/1024` bound,
and proves the conjectured `1/50` bound for several classes.

### Recent-repository comparison

The announcement-level search found
[`cormundus/erdos-128-census`](https://github.com/cormundus/erdos-128-census),
commit `52e43ab4a6e9bc9a56951e113c823b340d706fe6`, updated 26 July 2026.
That project exactly checks named triangle-free strongly regular graphs and reports
heuristic direct searches through order 26. It found no counterexample. It does not
enumerate the complete Ramsey `(3,6,n)` catalogues or state the catalogue-based
`n <= 15` exclusion below. This comparison narrows the visible collision risk but is
not a claim of novelty.

## Reduction used for the finite search

Razborov's Corollary 3.7 proves the half-graph conjecture when the normalized
independence number is at least `2/5`.  His definition uses a weighted half of
total weight `n/2`.  For odd `n`, an extremal weighted half consists of
`floor(n/2)` full-weight vertices and one half-weight vertex.  Dropping the
half-weight vertex can only decrease its weighted edge count.  Therefore the
corollary implies the exact floor-sized subset required by the Formal
Conjectures statement.

Consequently, a finite counterexample on `n` vertices must satisfy

```text
alpha(G) < 2n/5.
```

This reduces the remaining small cases to complete Ramsey catalogues.  A
Ramsey `(3,t,n)` graph is triangle-free and has no independent set of size
`t`, so it has `alpha(G) <= t-1`.

For `n <= 7`, elementary independence bounds already contradict
`alpha(G) < 2n/5`.  For `n=9,10`, `R(3,4)=9` does the same.  The nontrivial
catalogue checks are:

| n | Necessary class | Complete records | Required half-edge count | First violating witness counts |
|---:|---|---:|---:|---|
| 8 | Ramsey `(3,4,8)` | 3 | at least 2 | 1: 3 graphs |
| 11 | Ramsey `(3,5,11)` | 105 | at least 3 | 1: 24; 2: 81 |
| 12 | Ramsey `(3,5,12)` | 12 | at least 3 | exact minimum 2 in all 12 |
| 13 | Ramsey `(3,6,13)` | 275,086 | at least 4 | 1: 41,259; 2: 106,389; 3: 127,438 |
| 14 | Ramsey `(3,6,14)` | 263,520 | at least 4 | 2: 30,865; 3: 232,655 |
| 15 | Ramsey `(3,6,15)` | 64,732 | at least 5 | 2: 3,308; 3: 17,589; 4: 43,835 |

In screen mode, the last column records the first subset found below the
strict counterexample threshold; it is not asserted to be the true minimum.
For `n=12`, an exhaustive pass over every half-set found true minimum 2 for
each of the 12 graphs.

Thus, accepting the published completeness of the Ramsey catalogues, no
counterexample exists for `n <= 15`.

For context only, the same checker also excludes all catalogue graphs with
`alpha <= 5` at `n=16` (2,576 records) and `n=17` (7 records).  These are
**not complete exclusions at those orders**, because the Razborov reduction
still permits `alpha=6`.

## Independent checker and reproduction

The graph data are the complete Ramsey catalogues maintained by Brendan
McKay, mirrored by
[RamseyGraph](https://huggingface.co/datasets/linxy/RamseyGraph).  McKay's
[catalogue page](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html) states
the record counts and describes graph6 format.  File and decoded hashes are
locked in `MANIFEST.json`.  McKay publishes his data under CC BY 4.0; the
mirror declares MIT licensing.

`check_g6_family.py` does not use NetworkX or trust parsed graph objects.  It:

1. decodes graph6 directly;
2. checks every record for triangles;
3. checks the advertised independence-number upper bound;
4. exhaustively searches floor-sized vertex sets until it finds a set below
   the strict counterexample threshold (or searches all sets without
   `--screen`);
5. prints catalogue hashes, record count, and an edge-count histogram.

From the repository root:

```powershell
python experiments/erdos128/verify_manifest.py
python experiments/erdos128/check_g6_family.py experiments/erdos128/r34_8.g6 --alpha-upper 3 --screen
python experiments/erdos128/check_g6_family.py experiments/erdos128/r35_11.g6 --alpha-upper 4 --screen
python experiments/erdos128/check_g6_family.py experiments/erdos128/r35_12.g6 --alpha-upper 4
python experiments/erdos128/check_g6_family.py experiments/erdos128/r36_13.g6.gz --alpha-upper 5 --screen
python experiments/erdos128/check_g6_family.py experiments/erdos128/r36_14.g6.gz --alpha-upper 5 --screen
python experiments/erdos128/check_g6_family.py experiments/erdos128/r36_15.g6.gz --alpha-upper 5 --screen
```

The separate `checker.py` validates any concrete edge-list counterexample
emitted by the exploratory SAT scripts.  No such edge list was found.

## Order-16 exact searches and proof contingency

At `n=16`, Razborov gives `alpha(G) <= 6` for a counterexample, while the
complete `(3,6,16)` catalogue exclusion above rules out `alpha(G) <= 5`.
Conditional on that catalogue's completeness, any remaining counterexample has
`alpha(G)=6`; relabelling one independent six-set to vertices `0..5` is
therefore lossless. `cnf_search.py` now supports this symmetry with
`--fix-independent-size 6` and supports deterministic DIMACS generation with
`--build-only`.

A direct MapleSAT search of this remaining case was launched on 2026-08-01.
It had consumed about 11,588 CPU seconds without terminating when it was
stopped in favor of the proof-producing reduced cases.  It had 1,698,960
variables and 3,203,775 clauses; no result is claimed from that stopped run.

`Z3_CROSS_SEARCH.md` gives a stronger lossless reduction.  A counterexample
may be extended to a maximal triangle-free one; choose a remaining independent
six-set `I`, then choose an outside vertex of minimum `I`-degree `d`.  One has
`1 <= d <= 3`, and relabelling makes its neighbourhood a prefix of `I`.
Z3's native pseudo-Boolean QF_FD backend returned UNSAT for `d=1,2,3` in
64.781, 76.110, and 91.813 seconds.  A separately constructed MiniCard
native-cardinality encoding, deliberately omitting Z3's ordering of the other
nine outside vertices, independently returned UNSAT in all three cases.  Its
`d=3` run took 823.094 wall seconds.

The exact logs and a small-model/model-lifting audit are retained in
`cross_results/`.  The audit exhaustively checked all 33,868 labelled graphs
through order 6, all maximum independent sets in the three Ramsey `(3,4,8)`
graphs, native-cardinality semantics, maximality-witness clauses, and a
concrete order-16 alpha-six symmetry lift.  This substantially reduces the
risk of an encoding or symmetry error, but it is not an UNSAT certificate.

`PROOF_PIPELINE.md` documents the pinned CaDiCaL-to-DRAT-to-LRAT tool chain.
The small known-UNSAT `n=8` smoke case produced byte-identical artifacts on
repeat runs and was accepted independently by `drat-trim` and `lrat-check`.
After disk capacity became available, the capped order-16 pipeline completed
all three cases.  CaDiCaL returned UNSAT, `drat-trim` verified each DRAT and
emitted LRAT, and `lrat-check` accepted every LRAT.  The `d=3` case produced
the largest intermediate DRAT at 896,522,879 bytes; its checked LRAT is
132,721,364 bytes.  `CROSS_PROOF_PIPELINE.md` records all dimensions and
hashes.  The compressed LRATs, manifest, and clean replay script are retained
in `cross_certificates/`.

## What is and is not certified

Certified by the local checker:

- every supplied record decodes as a graph of the advertised order;
- every supplied record is triangle-free and has the advertised independence
  bound;
- every supplied record has an explicit floor-sized sparse subset;
- all file hashes and record counts match `MANIFEST.json`.

Independently reproduced computational evidence:

- Z3 QF_FD and MiniCard agree that all three exhaustive order-16 cross-degree
  cases are UNSAT;
- the separate reduction audit passes the exact checks listed in
  `Z3_CROSS_SEARCH.md`;
- regenerated CNFs for all three cases match their recorded hashes, and the
  retained LRATs are accepted by the pinned `lrat-check` executable.

External dependency:

- completeness up to isomorphism of each Ramsey catalogue is taken from the
  published McKay catalogue; this work does not regenerate its enumeration or
  a proof certificate for completeness.

Not certified or claimed:

- a proof or disproof for arbitrary `n`;
- a Lean proof of the finite exclusion;
- novelty of either the `n <= 15` synthesis or the conditional order-16
  computation;
- any result from the stopped direct MapleSAT CNF search;
- any theorem-level conclusion from the proof pipeline's `n=8` smoke test.
  Its two native proof checkers share one upstream repository and are not
  formally verified.  The retained order-16 LRATs should additionally be
  replayed with a formally verified checker such as CakeML `cake_lpr` before
  treating the computational trust boundary as closed at theorem level.

The computation is therefore a rigorous, reproducible attack artifact with a
clear trust boundary, but it does not solve Erdős Problem 128.
