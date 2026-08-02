# Erdos #742: certified fixed-15 split case `t = 57`

## Exact result and boundary

This package certifies one central partition of the order-five, fixed-15
search for an order-25 counterexample to the Murty--Simon conjecture.

> The exact hash-locked DIMACS formula for 15 fixed vertices, two five-cycles,
> 57 fixed--fixed edges, 20 moving edge orbits, and 157 total edges is
> unsatisfiable.

The statement above is a computational CNF result. Conditional on the cited
published order-25 reductions and the separately audited graph-to-CNF and
symmetry correspondence, it excludes this one edge-orbit partition from the
remaining `1^15 5^2` automorphism class.

It does **not** exclude the other 20 fixed-15 partitions, exclude asymmetric
graphs, or solve Erdos Problem #742. At the time of this checkpoint, 11 of the
21 fixed-15 partitions had checked certificates:

```text
t = 2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 57.
```

## Certificate

Pinned CaDiCaL 1.9.5, invoked with `--lrat --no-binary`, returned UNSAT and
emitted a 6,520,830,008-byte direct ASCII LRAT. Its SHA-256 is
`aab63b00d30be593e657abe4be75e8c4246f147e8fb4f1cee7115ec5a3823c56`.

The separately compiled and hash-pinned `drat-trim/lrat-check` replayed the
entire proof and returned `c VERIFIED`. It checked 13,775,162 added clauses in
851.56 seconds. `MANIFEST.json` pins the CNF, compressed and uncompressed
certificate, source files, tool binaries, result metadata, and logs.

No Lean theorem is claimed for this oversized certificate in this checkpoint.
The repository's Lean/LRAT-Catcher pipeline has separately replayed smaller
fixed-five and fixed-15 CNFs, but the current reflection command materializes
multi-gigabyte proof text in memory. The native LRAT replay and its exact trust
boundary are therefore stated separately and without ambiguity.

## Replay

Download all assets from the linked GitHub release into one directory, then
run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File `
  experiments\erdos742\order5_fixed15_t57\verify.ps1 `
  -AssetDirectory path\to\downloaded-assets
```

Add `-Regenerate` to rebuild the exact split CNF and rerun the independent
split-implementation audit before replay. Regeneration requires the Python SAT
dependencies used elsewhere in `experiments/erdos742`.

## Trust boundary

The checked LRAT establishes only that the hash-locked CNF is UNSAT. The graph
interpretation additionally depends on:

1. Fan's published order-25 numerical bound;
2. the published maximum-degree and dominating-edge reductions;
3. the audited correspondence between diameter-2-critical graphs and the base
   encoder; and
4. the audited split partition and centralizer lex-leader safety.

The native checker is hash-pinned but is not itself a Lean kernel theorem in
this checkpoint. The recency search is evidence against an obvious collision,
not proof of novelty or priority.

The work is AI-assisted research directed by Edison Yi. Programs, reductions,
and exposition were generated and adversarially checked by Codex agents; all
claims remain subject to independent mathematical review.
