# Lean verification of the independent-set recurrence

This directory contains a sorry-free Lean 4/mathlib verification of the
structural recurrence used in the finite-order argument for Erdős problem
#151:

```text
beta(G) >= |I| + beta(G - N[I])
```

for every independent set `I` in a finite simple graph `G`.  It formalizes
nontrivial inclusion-maximal cliques, avoiding sets, the residual induced
graph outside the closed neighborhood, the required one-way maximality lemma,
and the cardinality recurrence.

## Scope boundary

This is **not** a Lean proof of the through-order-22 theorem or of Erdős
problem #151.  It does not formalize the clique-transversal duality, Ramsey
number inputs, the order-18 local counting argument, or the arithmetic that
propagates the result through order 22.

## Rebuild

The source was checked against the repository's pinned Formal Conjectures
dependency checkout (Lean 4.27.0 and mathlib 4.27.0).  From
`third_party/formal-conjectures`, run in PowerShell:

```powershell
& 'C:\Users\Edison Yi\.elan\toolchains\leanprover--lean4---v4.27.0\bin\lake.exe' env lean `
  -R '..\..\research\erdos151\lean' `
  -o '..\..\research\erdos151\lean\Erdos151Recurrence.olean' `
  '..\..\research\erdos151\lean\Erdos151Recurrence.lean'
```

The source ends with `#print axioms` commands.  The induced-maximality lemma
reports no axioms.  The other principal theorems report only `propext`,
`Classical.choice`, and `Quot.sound`, the standard logical dependencies
expected from the mathlib development used here.

The generated `.olean` file is a build artifact and is not committed.
