# Erdős–Lean campaign dossier

**Snapshot:** 2 August 2026, after the fixed-15 `t=62` transition and while
`t=67` was running.  Live computation can move after this snapshot; the
machine-readable runner state described below is authoritative.

> **Current claim:** no open Erdős problem has been solved by this campaign.
> The repository contains bounded theorems, exact counterexamples to auxiliary
> claims, formally checked reductions, reproducible negative investigations,
> and one active certificate campaign.  Every result below is stated at its
> actual scope.

## 1. Objective and definition of success

The objective is to identify and, if realistically feasible, solve a genuinely
open problem associated with Paul Erdős, using a faithful public Lean
formalization and a reproducible proof.  Problem selection is part of the
research rather than a preliminary clerical step.

A full success must satisfy all of these gates:

1. the informal problem is still open at announcement time;
2. the public Lean statement is traced to an authoritative source and audited
   for quantifiers, conventions, definitions, and hidden placeholders;
3. the mathematical result resolves the original problem, rather than a
   finite case, symmetry class, auxiliary lemma, or altered statement;
4. the Lean proof builds from pinned sources without `sorry`, `sorryAx`, custom
   conclusion axioms, unresolved metavariables, or an unreviewed weakening;
5. complete axiom output and unfinished-proof scans are recorded;
6. the central argument also has a readable mathematical account;
7. computation is accompanied by a small independently checkable witness or a
   replayable proof certificate, with the graph/number-theory encoding audited;
8. literature, priority, AI involvement, and remaining trust boundaries are
   disclosed.

A verified finite case is progress, but it is not a redefinition of success.
Conversely, a concrete counterexample to a universal conjecture is a complete
mathematical resolution once the object is independently checked and the
faithful public theorem is proved false from it.

## 2. Executive state

The strongest results, ordered by their relevance to the full objective, are:

1. **Erdős #742 (Murty–Simon):** two complete order-five automorphism classes
   at order 25 have been excluded with LRAT certificates.  For cycle type
   `1^5 5^4`, Lean proves all six exact generated CNFs unsatisfiable.  Cycle
   type `1^10 5^3` has an independently replayed native LRAT.  The fixed-15
   class is split into 21 cases; 17 have native-checked certificates, one
   (`t=62`) has only an inconclusive long timeout, one (`t=67`) was active at
   this snapshot, and `t=72,77` were queued.  This is the only active campaign
   during usage conservation.
2. **Erdős #128 (sparse halves):** conditional on the completeness of McKay's
   Ramsey catalogues, no counterexample exists through order 16.  The order-16
   residual was first independently excluded by two native-cardinality
   encodings; regenerated CNFs then received checked LRATs, and a short
   combinatorial argument ultimately replaced the solver step.
   All-order work narrows any smallest counterexample to a strict independence
   window and proves further degree and low-cross-degree constraints.  This is
   the most important general-proof progress, but the universal problem is
   still open and there is no full Lean theorem.
3. **Erdős #167 (Tuza):** a structural reduction plus two independent witness
   screens proves, conditional on nauty completeness and Puleo's theorem, that
   every graph on at most 11 vertices satisfies `tau <= 2 nu`.
4. **Barrier and audit results:** the campaign found an exact sparse
   counterexample to an advertised auxiliary conjecture for #488, isolated the
   unresolved escape condition in a published #276 construction, refuted a
   public false proof of #137, found ten composite numbers incorrectly used as
   primes in a partial #203 computation, and caught the stale status that made
   the already-proved fixed `r=5` case of #617 look open.

The campaign has produced no full proof and no full counterexample.  Its best
current chance of a full resolution remains a small, exactly checkable SAT
witness for a finitely falsifiable problem, principally #742.  That chance is
low; the repository does not assign a numerical probability to an unfinished
open-problem search.

## 3. How the strategy evolved

### Phase A — broad selection and fidelity audit

The campaign inspected the Erdős statements in Google DeepMind's Formal
Conjectures snapshot `735aee074327b8e78b0d92bb1ee8ea00937c3f51`, compared
them with the live problem database and primary sources, and removed 116
problem numbers already associated with public AI claims from the initial
pool.  The resulting survey is in
[`candidate-survey.md`](candidate-survey.md).

Candidate selection favored:

- an exact, public, credible Lean statement;
- finite falsifiability and a cheap independent witness checker;
- explicit constructions or elementary reductions;
- mature Mathlib support;
- a plausible gap between public computational frontiers and known theory;
- a result whose scope would actually end the problem.

Short Lean syntax was never treated as evidence of mathematical tractability.
Files using `answer(sorry)` or containing multiple theorems were audited to
ensure that the principal question, not an easier auxiliary theorem, was being
targeted.

### Phase B — Rethlas as an idea generator

The online Rethlas harness was installed at pinned commit
`622bc663d4212333ade4c4802af1db3da92262c0` and used non-blind for stage-one
idea generation.  It was useful for reductions, convention checks, and
creating material for adversarial review.  It was not reliable as a proof
authority: the #196 run used 252,802 tokens, produced no completed submission,
and ended with a failed automatic verifier call.  The campaign therefore
treats a Rethlas verdict as triage only; every usable lemma must be rederived,
checked mathematically, and then formalized.

See [`rethlas-stage1.md`](rethlas-stage1.md) and
[`../experiments/erdos196/RESULTS.md`](../experiments/erdos196/RESULTS.md).

### Phase C — collision correction and exact research wave

An important failure changed the workflow.  Erdős #617 still appeared open in
the database even though a 24 July 2026 Zenodo preprint already recorded
Robert Sneiderman's fixed-`r=5` proof and Ramazan Kara's independent Lean
verification.  The lane was stopped, the wasted work was retained as a
superseded audit, and an announcement-level recency gate became mandatory.

The gate now checks the live problem page and discussion, VibeMathed,
GitHub repositories/code/issues, Formal Conjectures issues and pull requests,
Zenodo, arXiv, SciNet/Constellate, and primary literature.  Fixed subcases are
searched by their exact parameter.  The process is documented in
[`recency-audit.md`](recency-audit.md).

This phase produced the audited finite and family-specific results for #128,
#167, #274, #366, #742, and #982, as well as negative audits for several other
problems.

### Phase D — optimize for a full solution

After the bounded wave, the allocation was changed to favor outputs that can
immediately end a problem:

- candidate generation before exhaustive UNSAT proof;
- multiple feasible orders rather than only the next unknown order;
- stochastic, evolutionary, local-search, and model-finding SAT funnels;
- cheap definition-level validation of every candidate;
- independent verification and minimization before publication;
- general bridge lemmas mined from finite computations;
- hard stopping rules for lanes producing only larger numerical bounds.

The preferred operating heuristic is the probability of full resolution per
unit of agent and compute cost.  Large proof certificates are generated when
they close an important finite layer or expose a reusable formal pipeline, not
merely because an UNSAT run is available.

### Phase E — conservation and immediate publication

When weekly model usage fell to about seven percent, the campaign collapsed to
one mature lane: the already-running #742 fixed-15 sequence.  Broad
counterexample searches, Lean proof-trimming work, and new scouts were paused.
Background computation may continue under hard caps without opening new agent
branches.

Significant reproducible results are published immediately with exact scope,
hashes, replay instructions, and permanent archival where possible.  Partial
solver output, timeouts, and heuristic near-misses are not promoted.

### Milestone timeline

| Time (Europe/London) | Milestone |
|---|---|
| 1 Aug, 11:56 | Repository initialized with the fidelity-first objective and pinned public inputs. |
| 1 Aug, 12:24–14:49 | Exact #488 obstruction, #273/#617/#699 audits, #128 finite census, and #366 restricted searches recorded. |
| 1 Aug, 14:07 | #617 fixed-`r=5` target withdrawn after the recent public proof/Lean collision was verified. |
| 1 Aug, 21:57 | Certificate-backed finite wave added, including the #167 order-11 and #128 order-16 results. |
| 1 Aug, 22:41 | #128 order-16 SAT residual replaced by a human combinatorial bridge. |
| 2 Aug, 00:37 | All-order #128 independence, degree, and low-cross-degree reductions added. |
| 2 Aug, 01:44 | #276 finite construction and unresolved escape condition audited. |
| 2 Aug, 03:10 | First #742 order-five symmetry class published with certificates. |
| 2 Aug, 04:17 | Second #742 order-five symmetry class published. |
| 2 Aug, 05:47 | Six fixed-five #742 CNFs certified in Lean. |
| 2 Aug, 09:01 | The difficult fixed-15 `t=57` certificate package published and permanently archived. |

## 4. Evidence and trust ladder

The campaign uses the following levels.  A higher level does not automatically
broaden a result's mathematical scope.

| Level | Evidence | What it justifies |
|---|---|---|
| E0 | heuristic score, numerical optimizer, unfinished solver | search direction only |
| E1 | explicit object checked against the definition | a positive finite witness; potentially a full disproof |
| E2 | second independent checker or small exhaustive semantic audit | stronger confidence in E1 or an encoding |
| E3 | hash-locked CNF plus independently accepted DRAT/LRAT | UNSAT of that exact CNF, subject to checker trust |
| E4 | Lean theorem that the exact CNF is unsatisfiable | kernel/compiler-backed CNF result; encoding still external unless formalized |
| E5 | Lean theorem connecting the mathematical definitions to E4 | formal bounded mathematical theorem |
| E6 | faithful public theorem resolved with audited novelty | full campaign success |

Current high-water marks:

- #742 `1^5 5^4`: E4 for the six exact CNFs, but not E5 for the graph theorem;
- #742 fixed-10 and certified fixed-15 slices: E3;
- #128 order 16: E3 plus a human combinatorial replacement, conditional on
  catalogue completeness; no end-to-end Lean theorem;
- #167 order 11: independently replayed witness computation, conditional on
  nauty and the published reduction;
- #699: sorry-free Lean reductions and a concrete finite certificate, not the
  universal theorem;
- no result has reached E6.

## 5. Active problem: Erdős #742

### Mathematical target

The Murty–Simon conjecture says that every diameter-2-critical graph on `n`
vertices has at most `floor(n^2/4)` edges.  A counterexample is a finite edge
list and can be checked directly by recomputing all-pairs distances before and
after deleting every edge.

Fan's theorem covers orders at most 24 and order 26.  At order 25, Fan's
numerical estimate forces a counterexample to have exactly 157 edges.  The
active encoding also uses published reductions giving maximum degree at most
17 and excluding dominating edges.  These literature dependencies are part of
the mathematical trust boundary.

### Completed order-five classes

| Cycle type | Scope | Result | Verification |
|---|---|---|---|
| `5^5` | no fixed vertices | impossible for a 157-edge invariant graph | sorry-free Lean orbit arithmetic |
| `1^5 5^4` | six fixed-edge graph types | all excluded | native DRAT/LRAT and six Lean `CNF.Unsat` theorems |
| `1^10 5^3` | all nine feasible weighted edge-count pairs | excluded | audited quotient CNF and native `lrat-check` |
| `1^15 5^2` | 21 fixed-edge-count partitions | 17 certified, 4 unresolved at snapshot | native direct LRAT per completed partition |
| `1^20 5^1` | 23 split partitions | not closed | audited split machinery only |
| no order-five symmetry | unrestricted/asymmetric remainder | not closed | candidate search only |

The 17 certified fixed-15 partitions are

```text
t = 2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57,
    82, 87, 92, 97, 102.
```

The unresolved set is exactly `t=62,67,72,77`.  The long `t=62` run reached
its 5,400-second cap with a 10,535,209,325-byte partial LRAT; this is
**inconclusive**, and no checker or UNSAT claim followed.  At this snapshot
`t=67` was active, with `t=72,77` queued in the same bounded runner.

The live sources of truth are:

- `.research-cache/erdos742-fixed15-long.json`;
- `.research-cache/erdos742-fixed15-long.stdout.log`;
- each split case's `result.json` and proof-checker log.

Ignored `.research-cache` artifacts are working data, not publication by
themselves.

### Paused #742 lanes

- unrestricted order-25 and fixed-20 candidate searches;
- independently encoded model searches at orders 27, 28, and 29;
- an unpromoted local search across orders 27–30;
- dependency-cone trimming of the multi-gigabyte RUP-only LRATs for unchanged
  Lean replay.

The large-proof Lean investigation found that the current LRAT-Catcher eagerly
materializes the proof text.  A custom streaming runtime would widen the trust
boundary, so that route was rejected.  A backward dependency-cone trimmer is a
promising same-trust alternative, but it is paused until a completed layer
justifies the cost.

### Exact trust boundary

The LRATs prove that the generated CNFs are UNSAT.  The graph-theoretic claims
also depend on the cited published reductions, the quotient graph-to-CNF
correspondence, exact orbit partition, and safe centralizer lex leaders.  These
have independent exhaustive small-instance audits, but they are not yet an
end-to-end Lean formalization of the graph theorem.

Primary documentation:

- [`../experiments/erdos742/RESULTS.md`](../experiments/erdos742/RESULTS.md)
- [`../experiments/erdos742/order5_fixed5/README.md`](../experiments/erdos742/order5_fixed5/README.md)
- [`../experiments/erdos742/order5_other_fixed/README.md`](../experiments/erdos742/order5_other_fixed/README.md)
- [`../experiments/erdos742/order5_fixed15_t57/README.md`](../experiments/erdos742/order5_fixed15_t57/README.md)

## 6. Other promoted problems and results

| Problem | Status | Strongest justified progress | Decision |
|---|---|---|---|
| #64 | paused | Exact structured searches found no counterexample. Three Carr-structured order-32 degree families were excluded by trusted SMS runs; a promising 264-vertex voltage lift was independently rejected by an explicit 32-cycle. | Do not spend on more structured covers without a qualitatively new witness mechanism. |
| #128 | proof lane paused | Conditional exclusion through order 16; human order-16 bridge; every smallest counterexample is even, has minimum degree `> 1+2(n-1)/25`, and has independence ratio in `((33-sqrt(161))/116,2/5)`, with an added low-cross-degree constraint below `3/10`. | Highest-value general-proof reserve after #742; seek amplification/classification, not another small census. |
| #137 | audit only | An explicit negative-Pell solution at recurrence index 29 refutes a named lemma in a public “complete” proof attempt; other fatal gaps were recorded. | Problem remains open; do not treat the competing repository as a solution. |
| #167 | bounded result | Conditional proof of Tuza's inequality through 11 vertices over 2,174,357 residual isomorphism classes, with constructive packing/cover witnesses and an independent verifier. | Mine the residual for a general reducible configuration; do not brute-force order 12 without a new reduction. |
| #196 | stopped | Three Rethlas attempts yielded useful corrected lemmas but no global-linkage argument, proof, counterexample, verifier acceptance, or Lean theorem. | Intrinsically infinite; finite avoiding prefixes are not progress toward the quantifier. |
| #203 | audit/paused | Corrected ten claimed “new primes” in a public partial computation: all are explicit semiprimes. Exact phase searches remained far from a full cover. | Preserve the correction; resume only with a structured recursive cover. |
| #273 | superseded/paused | Exact density and parity obstructions were developed, but stronger July work already certifies the relevant finite periods and ranges. | Do not duplicate the prior SAT siege. |
| #274 | bounded result | Exact normalized search excludes 25 named solvable non-supersolvable groups of order 1440, with zero search caps and clean replay for the hardest group. | No all-order or all-order-1440 claim; further batches have low full-solution value. |
| #276 | barrier audit | Verified the finite 30-prime covering construction and proved why neither the 616,000 distinct-modulus theorem nor mirrored algebraic factorization closes the escape quantifier. | Resume only if a theorem controls repeated induced moduli. |
| #366 | bounded result | Exact exclusion of `n+1=x^3` and `n+1=x^4` for `2<=x<=2^32-1`; the public unrestricted search below `10^22` remains prior art. | A witness is valuable, but more one-dimensional subfamily ranges have poor return. |
| #488 | barrier result | Exact sparse counterexample `A={4,6,9,10,14,15,21,22,25,26}`, `n=91` disproves the proposed auxiliary incidence inequality, not Erdős #488. | Any proof must preserve floor-position information more finely. |
| #617, `r=5` | withdrawn | Local Ramsey/SAT work is superseded by Sneiderman's proof and Kara's independent Lean verification deposited 24 July 2026. | Permanently exclude this fixed case from target claims; all-`r` remains open. |
| #699 | formal reductions, paused | Sorry-free Lean proves the weak/strict boundary split, a large-prime sufficient condition, and a concrete `(28,5,14)` certificate. Independent searches reproduce known data but do not improve the public `n<=100000` computation. | The unresolved core is simultaneous Kummer digit avoidance, not finite enumeration. |
| #742 | active | See Section 5. | Sole live lane during conservation. |
| #982 | family theorems, paused | Exact integer-octagon exclusion through span 7; a rational equality family; all-order exclusion of alternating two-radius dihedral polygons; exact proof for a four-parameter `D2` octagon family. | Stop bounded symmetric enumeration; a future lane must attack arbitrary configurations. |

Detailed records live under each corresponding `experiments/erdos*`
directory.  The table deliberately calls several mathematically useful outputs
“barriers”: disproving a tempting route is valuable, but it is not progress of
the same logical kind as proving the target.

## 7. Rapid scouts and deliberately unpromoted work

The full-solution scout tested many targets briefly instead of granting each a
large exhaustive campaign.  Its machine-readable logs remain local and
unpromoted.  Notable outcomes were:

- #106 was immediately withdrawn after a public exact counterexample and a
  separate Lean verification were found;
- #850 had no radical-triple collision for `x<=100,000,000`; flat enumeration
  was parked because strong ABC points negative;
- #993 direct search was parked after collision with a much larger public
  certified computation;
- #1082 lattice searches had margins far from the target and were parked;
- #97 numerical geometry “zeros” failed exact convexity/distinctness checks;
  an exact parabola no-go lemma survived, but the lane was stopped;
- #64 small random searches collided with stronger public frontiers;
- #203 flat phase synthesis left large uncovered fractions and was parked.

There are additional untracked scratch directories for problems such as #7,
#375, #548, and #672.  They are not part of the claim ledger.  Until a result
has an audited statement, recency check, independent verification, and a
written scope boundary, its presence in the workspace is not evidence of
mathematical progress.

## 8. Lean formalization status

The public problem inputs are pinned to Formal Conjectures commit
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`.  The principal formal sources
used in promoted lanes include
[`128.lean`](https://github.com/google-deepmind/formal-conjectures/blob/735aee074327b8e78b0d92bb1ee8ea00937c3f51/FormalConjectures/ErdosProblems/128.lean),
[`167.lean`](https://github.com/google-deepmind/formal-conjectures/blob/735aee074327b8e78b0d92bb1ee8ea00937c3f51/FormalConjectures/ErdosProblems/167.lean),
[`699.lean`](https://github.com/google-deepmind/formal-conjectures/blob/735aee074327b8e78b0d92bb1ee8ea00937c3f51/FormalConjectures/ErdosProblems/699.lean),
and
[`742.lean`](https://github.com/google-deepmind/formal-conjectures/blob/735aee074327b8e78b0d92bb1ee8ea00937c3f51/FormalConjectures/ErdosProblems/742.lean).

| Artifact | Lean status | Mathematical scope not yet in Lean |
|---|---|---|
| #742 fixed-five `LeanCNF/Main.lean` | Six exact `CNF.Unsat` theorems via pinned LRAT-Catcher; no `sorry`; explicit theorem-specific `native_decide` dependency | published graph reductions, graph-to-CNF equivalence, quotient and lex-leader correctness |
| #742 `OrbitArithmetic.lean` | Sorry-free proof of mod-5 orbit arithmetic, fixed-point-free impossibility, fixed-10 count pairs, and fixed-15/fixed-20 split ranges | diameter-critical graph semantics and solver instances |
| #699 `Sanity.lean` | Sorry-free reductions and one concrete binomial-gcd certificate; standard foundational axioms only | universal Kummer covering argument |
| Formal Conjectures inputs | pinned public statements audited problem by problem | the upstream problem files themselves retain their intended open declarations |

No campaign artifact is currently a sorry-free Lean proof of an entire open
Erdős problem.  “Lean-certified #742” always means the exact generated CNF,
not yet the complete restricted graph theorem and certainly not the universal
Murty–Simon conjecture.

## 9. Failure ledger and methodological lessons

1. **Database labels lag.**  #617 and #106 showed that `OPEN` is a lead, not a
   novelty certificate.
2. **Theorem selection matters.**  A dashboard marked #699 done by selecting
   the formalized Sylvester–Schur auxiliary theorem instead of the open common-
   divisor conjecture.
3. **Floating-point verifiers can be scale-broken.**  The public #982
   benchmark accepted tiny scaled regular polygons with false metrics because
   it mixed absolute tolerances with a scale-free problem.
4. **A solver's `UNSAT` line is not a theorem.**  Native certificate replay,
   hash locking, and semantic audits are required; timeouts are `UNKNOWN`.
5. **Formal CNF checking does not formalize an encoding.**  #742's Lean LRAT
   replay removes the SAT checker from the trust base but leaves the graph-to-
   CNF bridge external.
6. **Finite prefixes do not solve infinite objects.**  This was the central
   failure mode in #196.
7. **Symmetric families can be mathematically beautiful and strategically
   weak.**  #64 and #982 produced valid family exclusions without much chance
   of a full counterexample.
8. **Unsound CEGAR cuts can fabricate negative evidence.**  An early #64 cut
   based only on net voltage was retracted; the retained version blocks only a
   preserved explicit witness.
9. **Independent positive checking is unusually valuable.**  Explicit cycles,
   edge lists, integer factorizations, and arithmetic witnesses often reveal
   errors immediately and should be preferred when the conjecture is
   falsifiable.
10. **Bounded certification can displace the real objective.**  The campaign
    now asks whether a computation can end the problem or produce a general
    bridge before investing in another finite exclusion.

## 10. Publication and permanent record

Public repository:
[`edisonymy/erdos-lean-research`](https://github.com/edisonymy/erdos-lean-research).

Published releases, in chronological scope:

| Release | Content |
|---|---|
| [`research-wave-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/research-wave-2026-08-02) | audited #128/#167/#276/#366/#982 wave |
| [`erdos742-order5-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos742-order5-2026-08-02) | native certificate package for `1^5 5^4` |
| [`erdos274-order1440-batch25-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos274-order1440-batch25-2026-08-02) | exact 25-group frontier |
| [`erdos742-order5-fixed10-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos742-order5-fixed10-2026-08-02) | native certificate package for `1^10 5^3` |
| [`erdos742-order5-fixed5-lean-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos742-order5-fixed5-lean-2026-08-02) | Lean imports for all six fixed-five CNFs |
| [`erdos742-order5-fixed15-t57-2026-08-02`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos742-order5-fixed15-t57-2026-08-02) | 6.52 GB direct-LRAT `t=57` checkpoint and clean replay assets |

The latest source package before this dossier is commit
[`2e82b92b951bc34fe506fd9cd97974dae2e3e67a`](https://github.com/edisonymy/erdos-lean-research/commit/2e82b92b951bc34fe506fd9cd97974dae2e3e67a).
Software Heritage archived a
full repository snapshot as
[`swh:1:snp:25bf299a47c37608e03436da6d9e765f8ef26279`](https://archive.softwareheritage.org/swh:1:snp:25bf299a47c37608e03436da6d9e765f8ef26279).

[Public issue #1](https://github.com/edisonymy/erdos-lean-research/issues/1)
is the timestamped campaign ledger.  It records the fixed-10 release, orbit
arithmetic audit, fixed-five Lean replay, fixed-15 `t=57` checkpoint, 16/21
sweep, and the later 17/21 state after `t=52` certification.  Public records
always repeat the boundary “not a solution of #742.”

The publication rule is:

- publish a verified full counterexample immediately after two exact checks;
- publish a full proof only after statement, recency, Lean, axiom, and human-
  readable proof audits;
- timestamp a significant bounded certificate promptly, with exact scope;
- archive source and large assets by hashes and immutable release tags;
- never announce an unchecked solver line, timeout, heuristic optimum, or
  unreviewed blueprint as mathematics.

## 11. Reproduction map

- Environment and pinned toolchains: [`environment.md`](environment.md)
- Candidate-selection evidence: [`candidate-survey.md`](candidate-survey.md)
- Announcement-level novelty protocol: [`recency-audit.md`](recency-audit.md)
- Primary source index: [`sources.md`](sources.md)
- Audited release summary: [`releases/2026-08-02.md`](releases/2026-08-02.md)
- Per-problem scripts, manifests, checkers, and notes: [`../experiments/`](../experiments/)
- Rethlas prompts: [`../rethlas/problems/`](../rethlas/problems/)

Generated binaries, third-party checkouts, virtual environments, Lean caches,
and multi-gigabyte working proofs are intentionally excluded from Git.  Public
large certificates live as hash-locked release assets.  A result is
reproducible only to the extent stated in its own README and manifest.

## 12. Current next steps

During conservation:

1. let the existing bounded #742 runner finish `t=67,72,77`;
2. independently replay and publish any new certificate;
3. retain timeouts as inconclusive partial artifacts;
4. open no new agent or solver branch.

After usage refresh, rank choices by probability of a full resolution per
cost.  The leading options are:

1. resume multi-order #742 model discovery with independent edge-list
   verification, including orders with more combinatorial freedom;
2. attack the all-order amplification gap in #128 rather than extending the
   finite census;
3. mine #167's constructive witnesses for a genuine reducible-configuration
   or induction theorem;
4. return to #982 only with an arbitrary-configuration method rather than
   another symmetric family;
5. resume large-LRAT trimming and the graph-to-CNF Lean bridge only when they
   materially improve a completed mathematical layer.

The decision point after the fixed-15 sequence is explicit: completing that
symmetry class would be a publishable bounded theorem, but it would not by
itself justify allowing certificate production to consume the campaign at the
expense of full counterexample or general-proof searches.

## 13. Strategy revision, 2 August 2026

A same-day strategic review (Claude Fable 5, cross-examined by GPT 5.6)
concluded that the portfolio was over-weighted toward famous, believed-true
conjectures where counterexample-first search has a near-zero prior, and
that bounded certificate production had displaced the full-resolution
objective exactly as failure-ledger lesson 10 warns.  The allocation
ranking in section 12 is superseded by
[`target-acquisition.md`](target-acquisition.md): a tiered funnel
(scripted pool construction → statement triage → recency-lite plus
one-CPU-day probes → at most three evidence-gated sieges), with #742
certification demoted to justified background work.  On user direction later
that day, the controlling objective was simplified to being first to a
publicly creditable full resolution within roughly one week.  Existing Lean
formalization is therefore a bonus rather than a selection gate; verification,
novelty, reproducibility, expert review, and accurate scope remain mandatory.
The witness announcement fast path is
[`announcement-template.md`](announcement-template.md).

## 14. AI disclosure

This is an AI-assisted research campaign directed by Edison Yi.  Codex agents
performed literature triage, mathematical experimentation, solver orchestration,
formalization, implementation, adversarial checking, documentation, and
publication preparation.  Independent agent agreement is treated as a bug-
finding technique, not peer review.  Every claim remains subject to expert
mathematical review, and the public artifacts disclose the exact computational
and formal trust boundaries.

## 15. Full-solution funnel update: Erdős #151

On 2 August 2026, the first promoted unformalized target produced a structural
bridge rather than a solver witness.  Writing `beta(G)` for the largest vertex
set containing no nontrivial inclusion-maximal clique, the campaign derived

```text
beta(G) >= |I| + beta(G-N[I])
```

for every independent set `I`.  A second agent independently audited the
maximality direction, all base cases, the strong induction, and the exact
Ramsey thresholds.  The first result proves the conjectured #151 bound for
every graph of order at most 17 and confines a smallest counterexample with
`h=H(n)` to `R(3,h) <= n <= R(3,h-1)+h-1`.  A second, separately audited
local-link argument excludes the first surviving order 18.  Parity and
`R(3,7)=23` then propagate the result through order 22.  Two further
independently audited analytic arguments exclude orders 23 and 24.  The
order-23 proof combines a Ramsey-minimal subgraph, exact link counts,
Brooks' theorem, and Gallai's low-vertex theorem.  The order-24 proof uses a
triangle-edge-coloring lemma after forcing a putative candidate to be
6-regular.  Strong induction gives `beta(G)>=7` at every order at least 23;
with `R(3,8)=28`, the conjectured #151 inequality therefore holds through
order 27.  The next possible first-counterexample interval is 28--30, so the
universal problem remains open.

The order-14 SAT portfolio was stopped after 1,024.859 seconds because the
structural proof makes a counterexample there impossible.  It produced no
candidate and no solver conclusion, and is recorded as
`STOPPED_AFTER_STRUCTURAL_PROOF`, not `UNSAT`.  Three later order-18
candidate runs (`q=0,2,4`) were stopped under the same label after the analytic
contradiction passed a fresh Sol/max audit; they likewise produced no solver
conclusion.  The proof, audit boundary, order-18 contradiction, and
machine-readable record are published in
[`erdos151/`](erdos151/).  The universal Erdős problem remains open.

The recurrence itself now has a sorry-free Lean 4/mathlib verification with
a separate semantic audit.  Its public scope is deliberately narrow: the
Ramsey inputs and finite-order arguments are prose proofs, not formalized
theorems.

A dedicated priority sweep found prior art for the complementary parameter
and identity `tau+beta=n` (Bhat--Bhat--Bhat 2023, with the equivalent
maximal-clique-free parameter in McDiarmid--Mitsche--Prałat 2019), but no
public occurrence of the recurrence, Ramsey interval, or through-27 result.
Novelty confidence is about 90%, not a substitute for expert literature
review.
