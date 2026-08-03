# Independent exact-61 obstruction audit

**Date:** 3 August 2026. **Verdict: PASS.** No 61-edge 3-graph on nine
vertices has packing number at most two.  Combined with the audited all-edge
window theorem and the independent exact-64 obstruction, this proves the
`r=3,n=9` instance of Erdős #719.  It does not prove the conjecture for every
`r,n`.

For a 61-edge nine-vertex 3-graph with `nu<=2`, the packing-one bound rules
out `nu<=1`, so `nu=2`.  A maximum two-packing has two four-sets meeting in
0, 1, or 2 vertices; these are the three complete isomorphism types.  Its
maximality forces every tetrahedron edge-disjoint from both members to be
dirty.  The explicit 18-block packing gives `q<=7nu=14`.

`independent_certificate61.py` encodes exactly 23 missing triples, both core
members present, maximality, clean indicators in both directions, and at most
14 clean tetrahedra.  It uses the handwritten signed Sinz counter and imports
neither the design-agent code nor its totalizer formulas.

All three Glucose DRAT proofs passed native `drat-trim`, were converted to
LRAT, and then passed the separate native `lrat-check`.  A structural replay
enumerated all 6,615 labeled two-packings, split exactly as 315/2,520/3,780 by
intersection size 0/1/2, regenerated every checked DIMACS byte-for-byte, and
checked the 18-block packing.

The verified manifest is `certificates/manifest.verified.json`, SHA-256
`4b8ea16d4c574c644083b9013a1768281614a83e9ba510947c37c3e46c196656`.
Certified artifact sizes are:

```text
CNF       843,747 bytes
DRAT  420,414,466 bytes
LRAT 1,021,524,148 bytes
```

One-command replay of this branch:

```powershell
.venv\Scripts\python.exe -B research\full_solution_scout\erdos719_exact64_independent_max_2026-08-03\exact61\replay_all61.py
```

The command ends with `ALL_EXACT61_INDEPENDENT_AUDITS_PASS` only after all six
native checker calls and the structural audit pass.

Claim boundary: this closes the last surviving `n=9` window.  The integrated
conclusion is the `r=3,n=9` instance only, not the all-order Erdős–Sauer
conjecture and not a full solution of Erdős #719.
