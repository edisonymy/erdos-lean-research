# Erdős Problem 64

## Exact target

Construct a finite simple graph `G` with minimum degree at least `3` and with
no simple cycle whose length is a power of two `2^k` for any `k >= 2`, or prove
that no such graph exists.  A construction would disprove Erdős Problem 64.

The public Lean target is
`FormalConjectures/ErdosProblems/64.lean` at pinned Formal Conjectures commit
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`.  It quantifies over finite simple
graphs and asks for a simple cycle of length `2^k`, `k >= 2`.

## Current frontier and collision constraints (2026-08-01)

- The live Erdős Problems page still marks #64 falsifiable/open; no current
  full solution or counterexample announcement was found.
- A public July 2026 SAT repository claims UNSAT for all minimum-degree-at-least-3
  graphs through 31 vertices.  Therefore do not spend effort on orders below 32.
- Public work excludes cubic-bipartite counterexamples below 60 vertices.
- Named cubic graphs, generalized Petersen graphs, several cyclic cover
  families, and an exact CEGAR sweep of all 8-sheeted permutation covers of
  `K4` have produced no counterexample in this campaign.
- Several groups are actively working on the problem.  Any candidate must be
  checked before any priority or novelty statement.

## Research contract

A negative solution must be an explicit finite certificate: give `n` and the
complete undirected edge list.  Independently verify simplicity, minimum
degree, and exhaustive absence of cycles of lengths `4,8,16,...` up to `n`.
Finite samples, random-search failures, or an UNSAT solver response without a
proof certificate are partial evidence only.

Prioritize genuinely different construction mechanisms at `n >= 32`, such as
nonabelian lifts/voltage graphs, Cayley or coset graphs, replacement products,
or gadgets that force all cycle lengths to have an odd factor while preserving
minimum degree.  Explicitly test every structural lemma against small graphs.

If no candidate is found, identify the sharpest rigorously justified obstruction
and record exact failed families without claiming a solution.
