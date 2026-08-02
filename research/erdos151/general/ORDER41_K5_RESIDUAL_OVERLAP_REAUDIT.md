# Post-remediation independent re-audit of the order-41 `omega=5` overlap package

**Date:** 2 August 2026.  **Verdict:** **PASS after remediation.**

The defect identified by the immutable FAIL audit has been repaired.  A fresh
replay of the current checker and a separate standard-library implementation
both return

```text
dominating fan partitions                 4368
exact common-U isomorphism classes         786
automorphism-closed aligned patterns      1963
row T before / after the D_0 test        10 / 0
row D necessary-condition cores             17
order-16 triangle witness beta                5
```

All 786 current pattern sets are closed under the full automorphism group of
their representative.  The five formerly omitted row-D cores are present in
the checker output and result JSON.  The note continues to state the correct
claim boundary: row T is excluded only conditional on completeness of the
pinned order-17 catalogue; row D is reduced, not excluded; row R remains open;
and no order-41 theorem, SAT/UNSAT result, or solution of Erdos problem 151 is
claimed.

This re-audit read and preserved the original FAIL audit and its JSON binding.
It made no source edit, ran no candidate-generation search or CEGAR, used no
web or Git operation, and performed no publication action.

## Immutable baseline and remediated artifacts

The original audit remains byte-for-byte unchanged:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` | `bde66a3d221f5e1762e218cc7b40de70ca690e019c3c99c93a1b0cd1d2120567` |
| `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.json` | `6f3411401846cc7304264c0025da252f4421467c15190a19572b94b270a19165` |

The remediated package and its binding have these exact hashes:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| `ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json` | `02452b459e79c672b79089c550fd48b1f0eba7cf6257b90c0e891f01efc9d987` |
| `checks/check_order41_k5_overlap.py` | `d4eee390c83862f5b166b9bbd6c71415929d0bf428e7f62aeec2817ba3cc3d95` |
| `checks/order16_beta5_triangle_witness.json` | `b3778f99571afed723c088143df118e00ab36515083167445b37f024a6e5ad36` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.md` | `d5e7b337867bf449f946472e690ce3119f1f6f8c4e351d583567bb5f2d02896f` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json` | `c015740e97888f230bb0e769ea887eb27d8ac86154a115a297f3fb1c50dee4db` |

The note, result, checker, witness, remediation Markdown, original audit, and
all pinned dependency hashes agree with the remediation JSON.  The remediation
JSON is noncircular: it binds the remediation Markdown and repaired inputs but
does not claim a hash for itself.  This re-audit separately binds that JSON.

## Repair review

The original blocker was precise: a record matching an existing common-core
class was transported through every representative-to-record isomorphism, but
the first record creating a class contributed only one seed vector.  Its orbit
under `Aut(U)` could therefore be incomplete.

The current `exact_common_core_classes` now does the following when creating a
class:

1. relabels the seed `U` to representative vertices `0,...,11`;
2. forms the seed cross-degree vector in that same order;
3. enumerates every automorphism of the representative with exact VF2; and
4. stores every vector `seed_pattern[mapping[i]]` in the seed orbit.

The mapping direction matches the later-record branch: in both cases the
tuple at representative coordinate `i` reads the degree at its mapped source
vertex.  Therefore the new seed orbit is the exact set that the prior branch
omitted.  Later records still enumerate every representative-to-record
isomorphism, so their transported vectors remain complete.

As a direct invariant test, the current classifier was reconstructed and,
for every one of its 786 classes, every stored vector was transported through
every automorphism of that representative.  The recomputed closure equalled
the stored pattern set in all cases:

```text
non-automorphism-closed classes = 0.
```

The checker now also asserts the aggregate orbit-sensitive total `1963`, in
addition to the corrected T and D counts.  This would catch the exact prior
regression even if the coarser counts happened not to change.

## Independent exact replay

### Current checker

A fresh process with bytecode writing disabled ran

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\check_order41_k5_overlap.py
```

It exited zero with `status: VERIFIED`, returned `4368`, `786`, `1963`,
`10 -> 0`, and `17`, and reported `beta_A=beta_B=5` for the order-16
candidate.

### Separate implementation

The independent implementation used in the FAIL audit was replayed unchanged.
It does not import the package checker or either beta engine.  It uses:

- its own short-form graph6 parser and bitset adjacency representation;
- stable colour refinement only to prune candidates;
- exact adjacency-preserving backtracking for every isomorphism and
  automorphism;
- complete seed-orbit construction and set-valued bounded-sum dynamic
  programming; and
- exhaustive enumeration of all `2^16` subsets for the witness beta value.

It independently returned:

```text
per-catalogue fan counts = 620,602,471,625,470,772,808
fan partitions           = 4368
common-U classes         = 786
aligned patterns         = 1963
T                        = 10 -> 0
D cores                  = 17
order-16 beta            = 5
```

The per-record fan counts sum to 4,368 and agree with the shipped enumerator.
The independent 17-core representative set equals the result JSON set exactly.
In particular, all five orbit-sensitive cores that the old checker omitted
are restored:

```text
K`_PYYCE@BGQ
K??P`XMUCKyG
K`_PYWWOkHCI
K@?JKhheagT?
K@hWOHacbAqK
```

The remaining 12 representatives are unchanged.  The corrected 17 all retain
the stated ranges `e(U) in {20,21,22}`, `alpha(U) in {4,5}`, and
`Delta(U)=4`.

## T and D logical scope

The repair changes the enumerated input space, not the elementary logic.

For T, all four full order-17 fans are now combined over the full set of
aligned patterns.  Exactly ten common-core classes respect the degree-nine
budget.  None survives the `D_0` condition.  A vertex saturated before the
four-fan is attached cannot meet that fan and therefore lies in `D_0`; the
catalogue-conditional triangle-freeness of `U` gives clique size at most two,
whereas every feasible state has too many saturated vertices.  Thus the
corrected conditional exclusion is `10 -> 0`.

For D, the checker still applies only the stated necessary conditions after
three full fans: at least one unit of remaining degree at every `u`, adjacency
to `w` forced when exactly one unit remains, and no more than seven such
forced neighbours because `w` already meets two vertices of `M`.  Exactly 17
classes pass.  The note explicitly leaves the two order-16 extensions, shared
`w`, other fan edges, global degree budget, and order-41 admissibility for a
future exhaustion.  It does not promote the 17-core reduction to an exclusion
or sufficiency claim.

## Catalogue, witness, and binding checks

The pinned artifacts remain unchanged:

| artifact | SHA-256 |
|---|---|
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |
| `experiments/erdos128/r36_16.g6.gz` | `5fd4e68d880e1d4ed05337b97cba0ce15387e1f545744aed80b91bb4b2186f25` |
| decoded order-16 catalogue | `25e35e1bb46b3131ff00b430b56e4679fcde7988211aefd9036c1e4c0cd7d2bf` |
| `experiments/erdos128/MANIFEST.json` | `ef41bb5eb474a58503549a21b411f13a77217f70edbcc63479f00247c11c92fc` |
| `experiments/erdos151_siege/beta_lib.py` | `228c8d82de6a0c292f0f1c89b4a5fc9411feef051d9ddf9cb0950faa1fe6ffac` |
| `experiments/erdos151_siege/beta_bb.py` | `4f8d7fe9361d56119a4ed651ca46acb81366fba612916891178f7d28d06531d6` |

The full manifest verifier passed every catalogue entry and decoded hash.  The
seven order-17 records again passed order, triangle, independent-six-set,
edge-histogram, and minimum-degree checks.  Catalogue completeness remains an
external premise in the note, result, checker warning, and remediation claim
boundary.

The independent order-16 replay reconstructed the candidate by adding
`(1,3)` to the pinned base record.  Direct exhaustive subset testing found
37 nontrivial maximal cliques and confirmed

```text
n=16, e=39, degrees=(4,4,5^14), triangles=1,
alpha=5, omega=3, beta=5.
```

It again produced the independent admissible witness `{0,1,2,4,5}`; the
artifact's witness `{0,6,9,13,14}` remains valid as well.

## Closure of the original blockers

| original blocker | post-remediation result |
|---|---|
| Close every new-class seed under `Aut(U)` | **CLOSED.** The implementation constructs the complete seed orbit, and all 786 final classes pass an independent closure test. |
| Recompute and emit `1963`, T `10 -> 0`, D `17`, and the five omitted cores | **CLOSED.** Checker and separate implementation agree; note and result contain the corrected values and representatives. |
| Update and rebind the note, result, and checker | **CLOSED.** Current hashes match the remediation Markdown and JSON, whose binding validates. |

No new blocker or overclaim was found.  The adjective “new” in the main note
is pre-existing and remains subject to the priority qualification recorded in
the immutable audit; the remediation does not add a novelty claim.  All
mathematical conclusions preserve their previous catalogue qualification and
necessary-versus-sufficient scope.

## Final claim boundary

The repaired package receives **PASS** for the finite residual-overlap
reduction only:

1. the unconditional elementary three-profile, residual-beta, `K4`-free, and
   domination lemmas remain as previously audited;
2. conditional on completeness of the pinned `(3,6;17)` catalogue, row T is
   excluded by the corrected exact enumeration;
3. row D is reduced to 17 necessary-condition cores and remains open;
4. row R remains open; and
5. no survivor exhaustion, order-41 closure, SAT/UNSAT result, or solution of
   Erdos problem 151 is established.
