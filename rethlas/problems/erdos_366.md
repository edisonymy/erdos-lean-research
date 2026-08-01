# Erdos Problem 366

## Target Statement

Prove or disprove the following exact existential statement: there is a positive integer n that is 2-full and for which n+1 is 3-full.

An integer is k-full when every prime dividing it occurs to exponent at least k. Thus n must be powerful (squarefull), while n+1 must have every prime exponent at least three.

## Research Contract

An affirmative solution requires one explicit integer n with complete prime factorizations of n and n+1. A negative solution requires a proof for all positive integers, not a finite search bound. Parametric elliptic or superelliptic reductions must cover every exponent pattern they claim to cover. Existing large computational exclusions are useful context but are not a solution.

The public Lean target is FormalConjectures/ErdosProblems/366.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. Source: https://www.erdosproblems.com/366.

## Requested Output

Search for a witness and, in parallel, derive mathematically exhaustive reductions. Verify every candidate with exact factorization. If incomplete, return the sharpest proven reduction and the finite or Diophantine subproblems that remain.

