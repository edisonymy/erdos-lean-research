# Erdős #151: whole-switch Folkman counterexample lane

This lane explores a materially different construction family from the fixed
clique CEGAR runs and from the fixed-core Ramsey perturbation.  It preserves
the labelled degree sequence `9^40,8^1` of a published-Ramsey order-41 near
miss, but allows unrestricted degree-preserving 2-switches across the whole
graph.  No compact Folkman core is fixed.

The exact outer checkpoints separately ask for:

- an independent 10-set (retained as a high-weight Ramsey constraint);
- an ambient-admissible 10-set;
- a proper five-colouring; and
- a red/blue edge-colouring with no monochromatic triangle.

The five-colouring separator uses the elementary homomorphism obstruction:
every five-colourable graph maps to `K5`, whose good edge colouring pulls
back, so every graph arrowing `(3,3)` has chromatic number at least six.  It
is used only as a constructive bridge; the exact edge-colouring separator is
still authoritative.

Every possible hit is exported from its raw edge list and sent to the two
independent definition-level validators in
`experiments/erdos151_siege/n41_candidate_heuristic/`.

Example from the workspace root:

```powershell
.\.venv\Scripts\python.exe `
  research\erdos151\high_effort_wave_2026-08-03\folkman_counterexample\switch_search.py `
  --run-dir research\erdos151\high_effort_wave_2026-08-03\folkman_counterexample\runs\seed15141301 `
  --random-seed 15141301 --rounds 30 --moves-per-round 2000 `
  --time-limit-seconds 300
```

This is stochastic negative/positive discovery machinery, not an exhaustive
encoding.  A bounded failure has no global theorem scope.

## Exact pinned-base obstruction obtained in this lane

`audit_ramsey39_extensions.py` proves that the unmodified pinned order-39
Ramsey base cannot be extended by two vertices while retaining both
`Delta <= 9` and `alpha <= 9`.

`audit_one_switch_extensions.py` strengthens this to every one of the 16,694
valid old-old 2-switches of that labelled base.  It uses two independent
switch enumerators, two independent catalogues of the base's 4,511
independent 9-sets, definition-level branch witnesses, and CaDiCaL checks for
all 389 relevant UNSAT claims.  The resulting certificate summary is
`one_switch_extension_audit.json`.

From this directory, reproduce the stronger audit with:

```powershell
& 'C:\Users\Edison Yi\Documents\Math Frontier\.venv\Scripts\python.exe' `
  .\audit_one_switch_extensions.py
```

The stronger statement is still a bounded family theorem: it covers this
fixed labelled base, exactly one old-old 2-switch, and then two added vertices.
It is not a resolution of Erdos #151.
