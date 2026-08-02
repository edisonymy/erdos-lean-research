# Erdős #742: the `1^10 5^3` order-25 symmetry class

## Result and exact boundary

This directory certifies the following restricted result.

> **Conditional computational theorem.** Let `G` be a diameter-2-critical
> graph on 25 vertices. If `G` has an automorphism of order five with exactly
> ten fixed vertices, then `|E(G)| <= 156`.

Equivalently, no order-25 counterexample to the Murty--Simon conjecture has an
automorphism with cycle type `1^10 5^3`.

Together with the sibling `order5_fixed5` package, this excludes exactly five
or exactly ten fixed vertices. It does **not** exclude the fixed-15,
fixed-20, or asymmetric cases, solve Erdős Problem #742, or provide a Lean
proof.

## Why one quotient instance suffices

Fan's published order-25 numerical bound forces any counterexample to have
exactly 157 edges. The published maximum-degree and dominating-edge results
let the search require maximum degree at most 17 and no dominating edge.

After relabelling, the automorphism fixes vertices `0,...,9` and rotates three
five-cycles. Its action on unordered vertex pairs has 45 singleton orbits and
51 size-five orbits. The weighted edge-count constraint includes all nine
solutions to `t + 5q = 157`:

```text
(t,q) = (2,31), (7,30), (12,29), (17,28), (22,27),
        (27,26), (32,25), (37,24), (42,23).
```

The quotient CNF has 56,164 variables and 240,029 normalized clauses. It uses
the definition-level diameter/criticality encoder from the independently
published fixed-five package. Safe lex leaders cover generators of the full
centralizer `S_10 x (C5 wr S_3)`; they preserve at least one lexicographically
least member of every centralizer orbit.

## Independent implementation audit

`audit_search.py` checks the cycle-type arithmetic, every feasible weighted
edge-count pair, and every centralizer generator. It confirms that each
generator commutes with the canonical order-five action and bijects the edge
orbits. It also compares the quotient semantics with direct graph definitions
on 18,944 exhaustive small multi-cycle graphs, 5,000 deterministic random
fixed-ten graphs, and 4,095 invariant complete-bipartite graphs. There were
zero mismatches. See `AUDIT.md` for the full audit and remaining trust boundary.

## Proof certificate

Pinned CaDiCaL 1.9.5 returned UNSAT and emitted a 419,261,312-byte binary DRAT
trace. `drat-trim` independently reported `s VERIFIED` and converted the proof
to a 2,193,318,873-byte LRAT. The separately compiled `lrat-check` executable
then reported `c VERIFIED`. The LRAT compresses to 407,165,840 bytes.

GitHub's per-file repository limit prevents retaining the compressed LRAT in
Git history. The exact CNF, compressed LRAT, build metadata, and full solver
and checker logs are immutable assets on release
`erdos742-order5-fixed10-2026-08-02`. `MANIFEST.json` locks every asset by
byte size and SHA-256 hash. `verify.ps1` checks the assets, reruns the
implementation audit, decompresses the LRAT, and replays the native checker;
its optional `-Regenerate` switch also rebuilds and resolves the CNF.

## Replay

Download `case.cnf` and `case.lrat.zst` from the release into one directory,
then run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File `
  experiments\erdos742\order5_other_fixed\verify.ps1 `
  -AssetDirectory path\to\downloaded-assets
```

Add `-Regenerate` to reconstruct the CNF with the audited Python source and
rerun the PySAT/CaDiCaL search before certificate replay. Regeneration takes
several minutes and requires the search dependencies in
`experiments/erdos742/requirements-search.txt`.

## Trust boundary

The LRAT certifies only that the hash-locked CNF is UNSAT. The mathematical
theorem additionally depends on:

1. Fan's order-25 numerical bound;
2. the published maximum-degree and dominating-edge reductions;
3. the audited correspondence between graphs and the quotient CNF, including
   the critical-edge characterization and lex-leader safety; and
4. correctness of the native `lrat-check` executable, which is hash-pinned but
   is not formally verified here.

There is no kernel-checked Lean formalization or exhaustive audit over all
25-vertex graphs. The exact collision search is in `RECENCY_AUDIT.md`.

## References

- G. Fan, *On diameter 2-critical graphs*,
  [Discrete Mathematics 67 (1987)](https://doi.org/10.1016/0012-365X(87)90174-9).
- T. W. Haynes, M. A. Henning, L. C. van der Merwe, A. Yeo,
  [*A maximum degree theorem for diameter-2-critical graphs*](https://doi.org/10.2478/s11533-014-0449-3).
- A. Dailly, F. Foucaud, A. Hansberg,
  [*Strengthening the Murty--Simon conjecture on diameter 2 critical graphs*](https://arxiv.org/abs/1812.08420).

The work is AI-assisted research directed by Edison Yi. Programs, reductions,
and exposition were generated and adversarially checked by Codex agents; all
claims remain subject to independent mathematical review.
