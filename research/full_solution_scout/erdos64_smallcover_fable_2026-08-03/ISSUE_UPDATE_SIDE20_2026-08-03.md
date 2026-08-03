## 3 August 2026 — certified bipartite part-size bound (not a solution)

We have obtained the following restricted computational theorem:

> Every finite simple bipartite graph of minimum degree at least three with
> no `C4`, `C8`, or `C16` has at least 20 vertices in each bipartition class.

Thus every bipartite counterexample to Erdős problem #64 has both sides at
least 20. This does **not** resolve #64.

The side-size ladder through 18 and the final side-19 formula have all been
checked by DRAT replay. The side-19 CNF has 85,498 variables and 381,858
clauses. A fresh single-writer CaDiCaL run produced a 230,688,966-byte binary
DRAT proof; Linux `drat-trim` read every byte and returned `s VERIFIED` after
160,990,667 resolution steps. Separate semantic audits reconstructed the
base CNF, checked all 512 `C16` blockers, checked the `C8` encoding on 42,878
small linear hypergraphs, and checked the symmetry breaker on all small
orbits.

The full certificate archives and SHA-256 manifest are attached to the
[`erdos64-bipartite-side20-v1`](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos64-bipartite-side20-v1)
release. The mathematical reduction and exact scope are in
[`BIPARTITE_SIDE20_THEOREM_2026-08-03.md`](https://github.com/edisonymy/erdos-lean-research/blob/main/research/full_solution_scout/erdos64_smallcover_fable_2026-08-03/BIPARTITE_SIDE20_THEOREM_2026-08-03.md).

Priority correction: the balanced 38-vertex graph found during discovery is
Gordon Royle's 2009 graph `F038A`, and the weaker total-order threshold is
already implicit in McKay--Afzaly's exact extremal table. Those are not new.
The potentially new point is the stronger *part-size* exclusion, which also
rules out highly unbalanced graphs. A targeted search found no prior statement
of that form, so the current wording is **certificate-backed and plausibly
new, pending confirmation from configuration/extremal-graph specialists**.

Core hashes:

```text
CNF    2B78BD846EEF041355834C1A1EEF1D526E9F88F844DA624C9C40E5DF27E3AD02
DRAT   9995B9DC0EE484E525826F18D8D2C17448C466372C9B5C57D34F54E6F0A0F98E
replay CEF389F9182F86EB26C47B7DA0893ADD2D436D2D47A137E54BE379CD9FADCBE6
```
