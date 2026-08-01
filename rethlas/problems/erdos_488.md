# Erdos Problem 488

## Target Statement

Prove or disprove the following exact statement. Let A be any nonempty finite set of positive integers with 0,1 not in A, and let B be the set of positive integers divisible by at least one a in A. For all integers m > n >= max(A),

|B intersect [1,m]| / m < 2 |B intersect [1,n]| / n.

All quotients are rational numbers and the inequality is strict.

## Research Contract

Solve the universal statement, or give an explicit finite counterexample A,n,m with exact integer counts and a cross-multiplied verification. It is harmless to reduce A to its divisibility-minimal elements, but that reduction must be justified. Numerical searches, density heuristics, or proofs covering only dense/sparse subregimes count as partial progress, not a full solution.

The corrected public Lean target is FormalConjectures/ErdosProblems/488.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. The source problem and active discussion are https://www.erdosproblems.com/488 and https://www.erdosproblems.com/forum/thread/488. Treat recent partial arguments as untrusted until reconstructed.

## Requested Output

Write a referee-ready proof or exact counterexample. Compute before trusting each proposed extremal inequality. If the full problem remains open, isolate the uncovered parameter regime and the exact lemma that would close it.

