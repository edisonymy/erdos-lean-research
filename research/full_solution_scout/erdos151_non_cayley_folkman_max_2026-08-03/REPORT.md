# Erdős #151: bounded non-Cayley Folkman-seed attack

## Outcome

**KILL / DEMOTE.**  This lane found neither a counterexample nor a one-away
seed.  It did, however, close the most concrete new construction lead cleanly:
the 43-vertex edge-Folkman graph HoG 51171 has exact campaign value

```text
beta = 25,     H(43) = 10,
```

where a counterexample at order 43 would require `beta <= 9`.  Thus its exact
gap above the counterexample ceiling is **16**, substantially worse than the
gaps 2--3 in the already exhausted Cayley families.

The sparse 63-vertex graph HoG 51177 is not an edge-Folkman seed at all: the
paper claims only *vertex*-arrowing, and two independent SAT solvers found and
validated triangle-avoiding edge 2-colorings.  Its exact `beta` is 37.

No public solution of #151 was found in the fresh 2026-08-03 status search.
The live database result is negative evidence, not proof of priority.

## Definitions and target

An admissible set contains no nontrivial ambient-maximal clique.  `beta(G)` is
the maximum size of such a set, equivalently `|V(G)|` minus the minimum clique
transversal number.  Erdős #151 asks whether

```text
beta(G) >= H(|V(G)|)
```

for every graph.  The campaign's audited Folkman reduction says any
counterexample must edge-arrow `(3,3)`, so explicit non-Cayley edge-Folkman
graphs are a natural counterexample source.

For order 43, `H(43)=10`: the published bounds give
`R(3,10) <= 41 < 43 < 47 <= R(3,11)`.  Hence the counterexample ceiling is 9.

## Exact literature seeds

The primary source is Hassan--Radziszowski--Van Overberghe,
*On Small Folkman Graphs Arrowing K2 or K3*, arXiv:2605.16542v1.  Its House of
Graphs identifiers were downloaded through the public HoG export API and
hash-pinned in `PROVENANCE.json`.

| HoG ID | Paper claim | `(n,m)` | degree range | exact `beta` | `H(n)` | independently edge-arrows? | verdict |
|---|---|---:|---:|---:|---:|---|---|
| 51288 | edge-arrows `(3,3)`, `J6`-free | `(11,37)` | 6--10 | 10 | 4 | yes, CaDiCaL and Glucose UNSAT | eligible but gap 6 |
| 51171 | edge-arrows `(3,3)`, `J5`-free | `(43,440)` | 18--23 | 25 | 10 | paper claim; bounded independent replays timed out | eligible by provenance, exact gap 15 above `H` and 16 above the needed ceiling |
| 51177 | vertex-arrows `(3,3)`, `C4`-free | `(63,252)` | 8-regular | 37 | 12 or 13 under current Ramsey bounds | **no**; both solvers return checked colorings | ineligible and gap at least 24 |

The distinction in the last row matters.  The paper obtains an edge-arrowing
64-vertex graph by adding a universal vertex to HoG 51177.  The universal
cone has `beta=63`, so that construction is unusable for #151.

## Independent beta verification

Two pipelines agree on the exact values.

1. A custom graph6 parser plus bitset Bron--Kerbosch enumerates ambient-maximal
   cliques.  A binary SciPy/HiGHS integer program minimizes a clique
   transversal.
2. NetworkX independently parses/reconstructs the graph and enumerates
   maximal cliques.  RC2 weighted MaxSAT maximizes an admissible set for HoG
   51288 and 51177.  For the denser HoG 51171, CaDiCaL exact-cardinality SAT
   finds an admissible 25-set and proves there is no admissible 26-set.

The maximal-clique statistics are:

| HoG ID | maximal cliques |
|---|---|
| 51288 | one `K4`, five `K5` |
| 51171 | 293 triangles, 200 `K4`'s |
| 51177 | 84 triangles |

The especially useful diagnostic is HoG 51171: the paper reports
`alpha(G)=7`, but exact `beta(G)=25`.  Low independence alone is therefore a
very poor proxy for the campaign objective on this concrete edge-Folkman
family.

## Bounded local-modification pulse

The only plausible operation on HoG 51171 is aggressive edge deletion while
preserving arrowing.  Vertex deletion is closed: the paper says every
vertex-deleted subgraph is nonarrowing, and this lane independently checked
all 43 deletions with both CaDiCaL 1.9.5 and Glucose 4.  Each returned a
validated triangle-avoiding coloring.

Before an edge-deleted subgraph can even meet the necessary condition
`Delta <= beta <= 9`, its degrees must fall from

```text
18^7 19^15 22^14 23^7
```

to at most 9.  The total degree excess is

```text
7(18-9) + 15(19-9) + 14(22-9) + 7(23-9) = 493,
```

so at least `ceil(493/2)=247` edges must be deleted, even under perfect
endpoint efficiency.  Simultaneously `beta` must fall from 25 to at most 9.

`minimize_hog51171.py` implements the strongest bounded version attempted:
activate both NAE clauses of every triangle, ask CaDiCaL for an UNSAT triangle
core, take its edge union, then greedily edge-minimize while preserving exact
arrowing.  A 60-second CaDiCaL source replay and a 120-second Kissat replay
both timed out before a first core.  A timeout is not mathematical evidence;
it is only the preset resource gate.  No core or candidate was emitted.

## Why this is not one-away

The source has exact beta gap 16, not 1.  It also needs at least 247 edge
deletions merely to satisfy the degree gate.  All one-vertex deletions lose
arrowing.  There is consequently no mathematically justified short operation
from this seed to a counterexample, and continuing would be a large
subgraph-search programme with no positive signal.

This meets hard-gate outcome (c): exact concrete-family coverage and a precise
failure reason.  Do not resume this lane unless one of the following appears:

* a published low-degree edge-Folkman graph with `Delta <= H(n)-1`;
* a supplied edge-arrowing certificate/core for HoG 51171 with maximum degree
  near 9; or
* a proved transformation that preserves edge-arrowing while controlling
  `beta`, not merely `alpha`.

## Reproduction

From the repository root, with the campaign virtual environment:

```powershell
.venv\Scripts\python.exe research\full_solution_scout\erdos151_non_cayley_folkman_max_2026-08-03\audit_literature_seeds.py
```

Expected headline values are `beta=10`, `beta=37`, and `beta=25` for HoG
51288, 51177, and 51171 respectively; HoG 51177 is nonarrowing; HoG 51288 is
arrowing; and all 43 vertex deletions of HoG 51171 are nonarrowing.

## Claim boundary

This is **not** a solution of Erdős #151 and not an exhaustive search of all
edge-deleted subgraphs of HoG 51171.  The two source-arrowing timeouts give no
SAT/UNSAT conclusion.  The edge-arrowing status of HoG 51171 is retained only
as a hash-pinned primary-paper claim.  Exact computational claims are limited
to the values and finite deletion family explicitly recorded above.

