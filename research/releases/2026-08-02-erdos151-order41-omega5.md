# Conditional order-41 clique-number-five theorem for Erdős #151

Published: 2 August 2026

## Audited result

Assume the published catalogue of Ramsey `(3,6;17)` graphs is complete and
its seven isomorphism classes are the seven records pinned in this repository.
Then every graph `G` on 41 vertices with `omega(G)=5` satisfies

```text
beta(G)>=10,
```

equivalently, its nontrivial maximal cliques have a vertex transversal of
order at most 31.

This is a conditional finite-order theorem.  It does **not** settle the
remaining order-41 `omega=4` case, the possible unrestricted order-40 case
when `R(3,10)=40`, later Ramsey jumps, or Erdős Problem #151 itself.

## Proof architecture

A maximum `K5`, the degree bound `Delta(G)<=beta(G)`, and five clique
residuals force exactly three incidence profiles.  Each is impossible:

- In the rigid profile, five simultaneous maximum neighbourhoods force exact
  degree equality and `G[U]=K3 disjoint-union 4K2`; a residual transversal
  then yields an admissible six-set.
- In the double-neighbour profile, singleton-fibre saturation gives
  `e(U)<=10`.  Independently, every triangle-free 12-vertex graph with
  independence number at most five has at least 11 edges.
- In the deficient profile, four full cuts, one deficient cut, and the same
  sparse lemma exhaust the degree budget and force
  `U=C5 disjoint-union C5 disjoint-union K2`.  No independent endpoint set
  hits all maximum independent five-sets of this graph, again producing an
  admissible residual six-set.

The catalogue premise enters only through the lemma that an order-17
residual with `beta<=5` is triangle-free.  The repository verifies the pinned
bytes, record count, and graph properties; it does not itself prove external
catalogue completeness.

## Verification and correction record

The package retains the full error history.  An initial residual-overlap
audit found a missing automorphism orbit and returned `FAIL`; the corrected
enumeration then passed an independent re-audit.  That computation is now
corroboration rather than a logical premise, because the final D and T
contradictions are analytic.  Independent audits separately reconstructed
the rigid-row argument, the sparse 12-vertex lemma, the shared-spoke degree
identity, and the deficient-row terminal transversal.  Standard-library
checkers backstop the finite profiles and exact arithmetic.

The principal artifacts are:

- `research/erdos151/general/ORDER41_K5_EXCLUSION.md`;
- `research/erdos151/general/ORDER41_K5_EXCLUSION_RESULT.json`;
- the companion `ORDER41_K5_*AUDIT*`, saturation, priority, and checker
  files in the same directory; and
- the pinned catalogue and manifest under `experiments/erdos128/`.

Frozen primary hashes:

```text
ORDER41_K5_EXCLUSION.md
  5cf0cfafb919ca3f6b8e81cc1ec66b94d1b72471fba657ec3e489cf95474462d
ORDER41_K5_EXCLUSION_RESULT.json
  494ff5b1ced797fd6b44ab3cdf0847b9b405f0ef47c5621f0fca32ce8da5e453
ORDER41_K5_EXCLUSION_FINAL_AUDIT.md
  67d75a073499e38be26f20663380653d8290e04304c984040dda72b2a1b010e0
```

The final clean-room audit independently rederived the profile exhaustion,
residual lift, order-17 triangle-freeness reduction, and all three terminal
contradictions.  Its independent checker returned `PASS`; all 42 frozen
dependency hashes and the theorem-to-result binding matched.

## Priority boundary

Bhat, Bhat, and Bhat, *Clique Free Number of a Graph* (2023), Proposition
II.3, already proved `Delta(G)<=beta_vc(G)` and its equality consequence for
maximum-degree neighbourhoods.  That fact is credited and not claimed here.
A targeted literature and announcement search through 2 August 2026 found no
source stating the order-41 clique-number-five theorem or using the combined
five-neighbourhood singleton-fibre architecture.  Negative search evidence is
not proof of priority, so the result is offered publicly for expert review
without a categorical “first” claim.

## Remaining campaign decision

Together with the unconditional order-41 `K4`-free theorem, this result leaves
only clique number four at order 41 under the catalogue premise.  A first
attack has identified the exact missing global cross-fan coupling and an
explicit local abstraction that survives all scalar inequalities.  The
campaign authorizes one global counterexample-search cycle, followed by the
evidence-based reallocation checkpoint in
`research/erdos151/ALLOCATION_CHECKPOINT.md`.

## AI disclosure

This is AI-assisted research directed by Edison Yi.  Codex agents materially
assisted discovery, exact computation, adversarial auditing, documentation,
and publication.  Agent agreement is a bug-finding mechanism, not peer
review; the public package exposes the assumptions, failed audit, repaired
computation, independent checks, and exact nonclaims for human scrutiny.
