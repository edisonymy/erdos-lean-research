# Bounded diversification probe: Erdős #719 at `r=3,n=9,nu<=1`

**Declared before computation:** 2 August 2026.

## Why this target and slice

Among the campaign's non-#151 candidates, #719 remains the strongest
finite-witness geometry: one explicit finite hypergraph with

`e(G)-3 nu(G) > ex_3(n,K_4^3)`

would disprove the full displayed Erdős--Sauer conjecture. The earlier private
probe exhausted its declared scope through `n=8`. Its strongest signal was the
exact packing-one optimum `e=38`, giving `e-3nu=35`, only one below
`ex_3(8,K_4^3)=36`.

This probe does not repeat that work. It moves to `n=9` but only attacks the
structurally complete packing-one slice. The exact Turán value is cheaply and
independently certifiable: `ex_3(9,K_4^3)=54` follows from the exact
seven-vertex missing-edge hitter, two vertex-deletion inequalities, and the
checked balanced cyclic Turán construction.

## Exact reduction

The minimum number of allowed decomposition pieces is

`phi(G)=e(G)-3 nu(G)`.

Thus a packing-one counterexample needs at least 58 edges. If the family of
present `K_4^3` copies is 3-intersecting, it is either:

1. a common-triple family, which has at most `ex_3(9)+1=55` edges after
   deleting the common triple; or
2. contained in a fixed five-vertex set, optimized exactly by
   `optimize_fixed5.py`.

The two cases are exhaustive; the elementary classification is recorded in
`RESULTS.md` after the run.

## Predeclared caps and kill rule

- One exact RC2 MaxSAT optimization of the fixed-five case.
- Hard wall cap: 60 minutes; memory cap target: 4 GiB; disk cap: 100 MiB.
- No `n=10`, packing-two, or other enlargement in this task.
- Promote only if the independent standard-library checker reports positive
  margin. Otherwise record the exact solver optimum, independently checked
  witness quantities, and kill this slice.
- Solver optimality without a proof log is recorded as an exact solver result,
  not a formally certified universal theorem.
