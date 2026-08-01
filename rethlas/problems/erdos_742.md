# Erdős Problem 742 — Murty–Simon conjecture

## Exact target

Let `G` be a finite simple graph on `n` vertices.  It is diameter-2-critical
when its graph diameter is exactly 2 and deleting any one edge makes the
diameter different from 2 (larger or disconnected).  Either prove

`|E(G)| <= floor(n^2/4)`

for every such graph, or give an explicit counterexample.  A counterexample
must include `n` and the complete edge list so it can be checked directly.

## Current frontier and collision constraints (checked 2026-08-01)

- Fan proved the inequality for `n <= 24` and `n = 26`; thus `n = 25` is the
  first order not covered by that theorem.
- Füredi proved the conjecture for all sufficiently large `n`, but the bound is
  not a practical completed finite check.
- Public SAT-modulo-symmetries work verifies orders through 19.  Brian Li's
  public repository contains raw diameter-2-critical CNFs through order 30 but
  does not state a solution for the counterexample cardinality constraint.
- The live VibeMathed dataset generated 2026-08-01 has no #742 entry.  Exact
  Zenodo, recent-arXiv, SciNet, Constellate, GitHub, and Formal Conjectures
  searches found no full proof/counterexample claim; the 2025 Lin–Wang paper is
  a restricted `C5`-free/high-density classification.
- A local candidate-only run is testing the public order-25 CNF with at least
  157 edges.  Do not treat an uncertified UNSAT response as a theorem.

## Research contract

Counterexample-first is preferred.  Any proposed graph must be independently
checked from the definition, without trusting the SAT encoding.  If pursuing a
proof, exploit the very narrow order-25 extremal window and known structural
results rather than asserting that a finite search was completed.  Test every
lemma on small graphs and distinguish graph diameter exactly 2 from merely at
most 2.  Do not claim novelty or resolution without a checkable certificate.

Useful directions include the complement/total-domination correspondence,
degree-sequence restrictions, critical-pair witnesses for every edge, and
double-counting strong enough to exclude 157 edges at order 25.  A rigorous
new reduction or falsifiable structural lemma is useful even if it does not
close the conjecture.
