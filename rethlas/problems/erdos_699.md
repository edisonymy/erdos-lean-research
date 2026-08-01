# Erdos Problem 699

## Target Statement

Prove or disprove the following exact statement. For every n,i,j in N with 1 <= i < j <= floor(n/2), there exists a prime p >= i such that p divides gcd(binomial(n,i), binomial(n,j)).

## Research Contract

A positive solution must handle all triples satisfying the inequalities. A negative solution needs one explicit triple together with exact binomial/gcd factorization showing that no prime p >= i divides the gcd. Sylvester--Schur only gives a large prime divisor of each binomial coefficient separately; do not assume those primes coincide. A computation through a finite n bound is evidence, not a proof.

The public Lean target is FormalConjectures/ErdosProblems/699.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. The repository also contains a Lean formalization of the relevant Sylvester--Schur theorem. Source: https://www.erdosproblems.com/699.

## Requested Output

Develop either a complete p-adic/binomial proof or an exact counterexample. Use Kummer/Legendre digit criteria carefully and test every universal auxiliary lemma before relying on it. If incomplete, isolate a sharply stated common-prime lemma and record the strongest verified ranges.

