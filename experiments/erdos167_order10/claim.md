# Claim and proof boundary

## Bounded claim

Assume Puleo's theorem that every graph of maximum average degree strictly
less than seven satisfies Tuza's inequality. Then every simple graph `G` with
at most ten vertices satisfies `tau(G) <= 2 nu(G)`.

## Deduction

Adding isolated vertices changes neither the triangle set nor `tau` or `nu`.
Thus any counterexample of order at most ten pads to one of order exactly ten.
If such a graph were a counterexample, Puleo's theorem
would give a (not necessarily induced) subgraph `H` with average degree at
least seven.  If `h=|V(H)|`, then `|E(H)| >= ceil(7h/2)`.  A simple graph with
`h <= 7` has average degree at most six, so `h` is 8, 9, or 10.

- `h=8`: `|E(H)| >= 28`, hence `H=K8`.
- `h=9`: `|E(H)| >= 32`.
- `h=10`: `|E(G)| >= 35`.

Thus every possible order-ten counterexample lies in the residual screened in
this package.  The official catalogue contains one representative of every
order-ten simple-graph isomorphism class.  Complementation is an involution on
isomorphism classes.  The two independent screeners agree on all 4,769
residual representatives.  The primary optimizer and independent verifier
agree that every one has `tau <= 2 nu`.

## What is not claimed

- no statement for graphs on eleven or more vertices;
- no proof of the full Erdős 167 / Tuza conjecture;
- no machine-checked Lean proof;
- no unconditional novelty or priority claim beyond the documented public
  searches performed on 2026-08-01.

The finite computation depends on the integrity and completeness of McKay's
published catalogue.  The mathematical reduction depends on Puleo's published
theorem.  Those are explicit trust boundaries rather than hidden assumptions.
