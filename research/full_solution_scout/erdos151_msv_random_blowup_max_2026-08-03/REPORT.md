# CONTINUE_PACKET: Erdős #151 finite MSV counterexample probe

## Status

`LANE_EXHAUSTED` for the **theorem-faithful `s=3` MSV construction with
tripartite owners**. This is a rigorous lane-local impossibility theorem, not
an `UNRESOLVED` verdict and not a reallocation away from Erdős #151.

The key outcome is stronger than the negative grids: every possible output of
this construction has an explicit red--blue edge-colouring with no
monochromatic triangle. By the campaign's independently audited Folkman
reduction, every such output satisfies the #151 inequality. No choice of
parameters, random seeds, regularized copy family, or faithful second-deletion
optimizer can turn it into a counterexample.

The proof and its five-point adversarial audit are in
[`FOLKMAN_OBSTRUCTION.md`](FOLKMAN_OBSTRUCTION.md).

## Immutable target match

Target lock: [`TARGET_LOCK.md`](TARGET_LOCK.md), SHA-256
`8E467292CE0FAC815956A4C3A1E6D50AE2B3AEF3B7BA32C6A579CA11F6973037`.

The exact #151 statement is `beta(G)>=H(n)` for every `n`-vertex graph. Its
exact negation is the existence of `G` with `beta(G)<H(n)`. The finite route
searched for the stronger sufficient witness

```text
G is K4-free and tf_3(G)<H(n).
```

This is target-faithful as a disproof route, not an equivalent restatement: in
a `K4`-free graph every triangle is ambient-maximal, so
`beta(G)<=tf_3(G)`. No witness was found, and the obstruction theorem now
proves that no theorem-faithful tripartite-owner MSV output can be one.

## Route fingerprint

- **Representation:** two independently partitioned families of indexed
  blow-ups of `T_3(q)` on a common `n`-vertex set.
- **Central theorem:** Morris--Sahasrabudhe--Verstraëte Definition 2.1,
  Observation 2.2, and Lemma 2.3, combined with the campaign's Erdős--Rogers
  gateway and Folkman reduction.
- **Search object:** finite random pregraphs followed by globally coordinated
  choices of one deleted edge per extrinsic triangle.
- **Evaluator:** current certified `H(n)` lower thresholds; literal D1/D2
  replay; independent `K4` audit; mandatory `Delta<h`; independent-set and
  induced-triangle-free lower witnesses; triangle-coverage count; and an
  explicit nonarrowing edge-colouring.
- **Predicted finite obstruction:** coverage/degree imbalance.
- **Observed decisive obstruction:** unique tripartite ownership gives a good
  edge-colouring for every output, independently of finite metrics.

This fingerprint cannot be reopened by changing `n,r,q,m`, partitions, seeds,
copy correlations, or the faithful D2 objective. It reopens only if the proof
is falsified or at least one of tripartite owners, unique edge ownership, or
destruction of every extrinsic triangle is changed.

## Exact construction audit

The implementation in [`msv_s3_probe.py`](msv_s3_probe.py) preserves all
load-bearing details of the 17 July 2026 preprint:

- copies are indexed, sampled with replacement, and share one random
  equipartition within each colour;
- the two colour partitions are independent;
- D1 uses endpoint co-membership in owner supports, not edge provenance;
- every post-D1 edge has a unique owner and colour;
- D2 is built from the complete post-D1 triangle ledger and replayed
  simultaneously;
- mixed triangles force the minority-colour edge;
- degree-constrained MaxSAT uses explicit exactly-one `(triangle,edge)` choice
  variables, so it does not smuggle in arbitrary extra deletions.

The April 2026 Radziszowski survey was checked from the preserved primary PDF,
[`small_ramsey_ds1_2026.pdf`](small_ramsey_ds1_2026.pdf). In particular the
probe corrected the initial finite table to `H(171)>=22`, using
`R(3,22)<=171`; later thresholds use explicit recurrence/Shearer certificates.

[`SMOKE.json`](SMOKE.json) records 24 small final graphs on which literal D1,
D2, brute/bitset `K4` checks, and the explicit nonarrowing colouring pass.

## Finite cycles and progress-vector delta

The finite work remains useful as a faithful implementation/audit trail even
though the structural theorem supersedes it.

| Cycle | Unique pregraphs | Final graphs | Material mechanism change | Best observed `alpha/h` | Best observed `tf_3/h` |
|---|---:|---:|---|---:|---:|
| Registered core | 60 | 120 | random versus global greedy D2 | `59/22 = 2.682` | `116/22 = 5.273` |
| Ramsey-jump boundary | 136 | 408 | lower jumps plus exact weighted RC2 D2 | `19/11 = 1.727` | `38/11 = 3.455` |
| Degree-capped D2 | 56 | 56 | literal exactly-one D2 assignment with hard `Delta<h` | `16/11 = 1.455` | `34/11 = 3.091` |
| Exact triangle survival | same 56 | 56 | exact destroyed-triangle objective on identical pregraphs | `16/11 = 1.455` | `34/11 = 3.091` |

Totals: 252 unique pregraphs, 308 pregraph-policy evaluations, and 640 final
graph records. Verdicts were 434 sound independent-set rejections, 103
mandatory degree rejections, 69 uncovered-vertex rejections, and 34 infeasible
degree-capped D2 assignments. There were no heuristic survivors requiring an
exact `tf_3` solve and no candidate counterexample.

Progress vector, before to after:

- faithful finite construction: absent -> implemented and smoke-tested;
- current `H` certificate at `n=171`: stale `20` -> audited `22`;
- best finite independent-set ratio: `2.682` -> `1.455`;
- best finite triangle-free ratio: `5.273` -> `3.091`;
- degree allocation: uncontrolled -> exact faithful `Delta<h` assignment;
- structural route status: empirical uncertainty -> universal impossibility
  theorem for the complete tripartite-owner family;
- independent artifact verification: absent -> graph, `K4`, degree, triangle,
  alpha/tf witness, and nonarrowing-colouring replay all pass.

The exported representative in [`NEAR_MISS.json`](NEAR_MISS.json) has
`n=50`, `h=11`, `Delta=10`, an independent 16-set, an induced
triangle-free 34-set, and 43 surviving triangles against the elementary
coverage minimum 119. [`INDEPENDENT_AUDIT.json`](INDEPENDENT_AUDIT.json)
reparses its 180-edge graph without importing generator code and confirms the
`K4` check, both witnesses, exact triangle count, and explicit good edge
colouring.

## Exact obstruction

D1 gives every surviving edge a unique indexed `T_3` owner. D2 kills every
triangle not jointly contained in an owner. Label each owner's parts
`0,1,2`; colour part pairs `01,12` red and `02` blue. This pastes globally
because ownership is unique, and every final triangle has colour pattern
red--red--blue. Thus the graph does not arrow `(3,3)`, so audited Theorem A
gives `beta(G)>=H(n)` exactly.

The argument handles all five adversarial points requested by the controller:
fixed labels per indexed owner, support-based D1 ambiguity removal, complete
post-D1 triangle processing, pre-D1 two-colour overlap, and exact matching of
the `beta/H` definitions. See the dependency audit in the theorem file.

## Four gates

1. **Target fidelity:** PASS for the route and impossibility conclusion. The
   stronger counterexample target is explicitly distinguished from #151.
2. **Correctness:** PASS at research-package level. The proof was independently
   reconstructed from the MSV deletion definitions and the already audited
   Folkman theorem; explicit colourings pass a separate graph parser/checker.
3. **Full coverage/significance:** NOT A FULL #151 RESULT. It excludes one
   infinite construction family from the counterexample programme.
4. **Novelty/provenance:** UNKNOWN. A light primary-source/arXiv scan found no
   matching statement, but the proof is elementary and rediscovery is likely.
   [`PRIORITY_CHECK.md`](PRIORITY_CHECK.md) records queries and limitations.
   Do not publish as novel before a full semantic audit and expert contact.

## Next orthogonal mechanism

The generalized-owner theorem sharpens the next experiment. With unique
ownership and extrinsic-triangle deletion, the final graph arrows `(3,3)` if
and only if at least one surviving owner graph arrows `(3,3)`. Hence a new
owner must not merely start arrowing: D1 and D2 must preserve an arrowing
subgraph inside it.

The smallest decisive next gate is therefore:

1. source and hash-pin candidate `K4`-free edge-Folkman cores `F`;
2. independently certify `F -> (3,3)`, `K4`-freeness, and at the `n=50,
   h=11` jump the necessary `Delta(F)<=10`;
3. encode owner embeddings and both deletions with hard clauses protecting an
   arrowing subgraph of at least one owner;
4. reject before any beta work if no owner remains arrowing;
5. only after that gate, run exact/dual-checked `tf_3` or `beta` separation.

This changes the representation (protected Folkman cores rather than
tripartite pieces), the central lemma (arrowing retention), and the search
object (core-preserving packing SAT). It is not more sampling of the closed
lane.

A second escape is to abandon the MSV second deletion and hit only `K4`s,
allowing cross-owner triangles to couple owners. A bounded diagnostic found
the eight saved `n=50,q=3` pregraphs nonarrowing even before D2, so that variant
also needs a changed pregraph template rather than a deletion-policy tweak.
That diagnostic is exploratory and is not used by the proved closure result.

## Artifact index

- `TARGET_LOCK.md` — exact statement, negation, and route relationship.
- `FOLKMAN_OBSTRUCTION.md` — universal proof and adversarial audit.
- `msv_s3_probe.py` — faithful generator, four D2 optimization families,
  structural colouring, gates, and sweeps.
- `independent_verify.py` — separate graph/witness/colouring checker.
- `PARAMETER_GRID.json`, `JUMP_BOUNDARY_CYCLE_GRID.json`,
  `DEGREE_CAPPED_D2_CYCLE_GRID.json`,
  `DEGREE_CAPPED_EXACT_SURVIVAL_CYCLE_GRID.json` — immutable job records.
- `RESULTS.json`, `BOUNDARY_RESULTS.json`, `DEGREE_CAP_RESULTS.json`,
  `DEGREE_CAP_EXACT_RESULTS.json` — complete result records.
- `NEAR_MISS.json`, `INDEPENDENT_AUDIT.json`, `SMOKE.json` — independently
  replayable representative and smoke artifacts.
- `PRIORITY_CHECK.md` — limited novelty search with exact limitations.
- `small_ramsey_ds1_2026.pdf` — preserved authoritative Ramsey survey.
- `CLEANUP.json` — exact temporary-file cleanup ledger.
