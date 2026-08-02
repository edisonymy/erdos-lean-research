# Erdős #742: the `1^5 5^4` order-25 symmetry class

## Result and exact boundary

This directory certifies the following restricted result.

> **Conditional computational theorem.** Let `G` be a diameter-2-critical
> graph on 25 vertices. If `G` has an automorphism of order five with exactly
> five fixed vertices, then `|E(G)| <= 156`.

Equivalently, no order-25 counterexample to the Murty–Simon conjecture has an
automorphism with cycle type `1^5 5^4`.

This is **not a solution of Erdős Problem 742**, does not close order 25, and
is not a Lean proof. The theorem depends on the published reductions and the
explicit computational trust boundary below. No novelty claim is made without
external literature review.

## Why six finite cases suffice

Suppose that `G` were a counterexample. Fan's published numerical bound gives

```text
|E(G)| < n^2/4 + (n^2 - 16.2n + 56)/320 = 157.1125
```

at `n=25`. Since a counterexample has more than `floor(25^2/4)=156`
edges, it has exactly 157 edges. The maximum-degree theorem of
Haynes–Henning–van der Merwe–Yeo reduces to `Delta(G) <= 17`, and the
dominating-edge result of Dailly–Foucaud–Hansberg lets us require that no edge
is dominating.

After relabelling, the automorphism fixes vertices `0,...,4` and rotates four
5-cycles. Its action on the 300 unordered vertex pairs has:

- 10 singleton orbits, the pairs of fixed vertices; and
- 58 orbits of size five.

If `t` is the number of fixed–fixed edges, then `157 = t (mod 5)` and
`0 <= t <= 10`, so `t` is 2 or 7. Up to isomorphism there are two graphs with
two edges on five vertices: `P3 + 2K1` and `2K2 + K1`. A seven-edge graph is
the complement of a three-edge graph, and the four three-edge graphs on five
vertices are `K3 + 2K1`, `K1,3 + K1`, `P4 + K1`, and `P3 + K2`. These are the
six cases in `MANIFEST.json`. `audit_reduction.py` independently enumerates
all 45 labelled two-edge graphs and all 120 labelled seven-edge graphs and
recovers exactly these six isomorphism classes.

## Definition-level CNF

`generate_cases.py` constructs each CNF from the graph definition. It uses
one primary variable per edge orbit and checks one representative of every
pair orbit. This quotient is lossless because the imposed automorphism carries
all pairs in an orbit to one another.

Diameter at most two is encoded by selecting either the pair's edge or a
common-neighbour two-path. Edge criticality uses the following exact local
characterization. In a diameter-two graph, deletion of an edge `uv` destroys
diameter two exactly when at least one of these holds:

1. `u` and `v` have no common neighbour;
2. some `x in N(u) - (N(v) union {v})` satisfies
   `N(x) intersect N(v) = {u}`; or
3. the symmetric condition holds with `u` and `v` exchanged.

The three cases enumerate the only paths of length at most two that can use
`uv`. The public `../audit_witness_counts.py` separately found no disagreement
between this characterization and direct edge deletion over every relevant
edge of every labelled diameter-two graph through order six.

`audit_small_quotient.py` adds a quotient-specific check: it compares the CNF
with direct all-pairs distances and all edge deletions for every graph invariant
under one order-five cycle with zero through five fixed vertices. It checks
135,468 invariant graphs, including all 131,072 graphs of cycle type `1^5 5^1`,
and finds zero mismatches. This is a strong falsification test, not a proof of
the order-25 encoder.

The remaining clauses encode the exact orbit edge count, maximum degree 17,
absence of a dominating edge, and safe lex leaders for relabellings that
normalize the fixed order-five action. A globally lexicographically least
member of every relabelling orbit survives those leaders. Repeated literals
are removed and tautological clauses are dropped before DIMACS output.

## Certificates

Pinned CaDiCaL returned UNSAT in all six cases and emitted DRAT traces.
`drat-trim` independently reported `s VERIFIED`, converted each trace to LRAT,
and the separate `lrat-check` executable reported `c VERIFIED` for every LRAT.
The compressed LRATs are retained in `certificates/`; exact CNF, DRAT, LRAT,
and compressed-certificate sizes and SHA-256 hashes are in `MANIFEST.json`.
The original solver and both checker logs are retained in `logs/`.

From the repository root, a clean replay regenerates every CNF, checks its
hash, decompresses each LRAT, checks its hash, runs both finite audits, and
replays all six certificates:

```powershell
python -m pip install -r experiments\erdos742\requirements-search.txt
powershell -ExecutionPolicy Bypass -File `
  experiments\erdos742\order5_fixed5\verify.ps1
```

The replay requires `zstd`, WSL, and the pinned proof tools already documented
under `third_party/`.

## Statement fidelity and trust boundary

At Formal Conjectures commit
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`, `ErdosProblems/742.lean` defines
diameter-2-critical as `G.diam = 2` and deletion of every edge giving diameter
different from two. Its conjectured bound is exactly
`edgeFinset.card <= n^2 / 4`, with natural-number division. The computation
uses the same finite simple-graph statement; disconnected edge deletions count
as diameter different from two.

The retained LRATs certify only that the generated CNFs are UNSAT. The
mathematical theorem additionally depends on:

1. Fan's published numerical bound at order 25;
2. the published maximum-degree and dominating-edge reductions;
3. the hand-audited equivalence between the graph property and the generated
   quotient CNFs, including the safety of the orbit and lex reductions; and
4. correctness of the native `lrat-check` executable, which is independently
   compiled and hash-pinned but not formally verified here.

There is no exhaustive order-25 definition audit and no kernel-checked Lean
formalization of this restricted theorem. The exact recency search is recorded
in `RECENCY_AUDIT.md`.

## Research recommendation

**GO** for external review and publication as a sharply bounded,
certificate-backed symmetry-class exclusion. **NO-GO** as the campaign's
primary route to a full solution: the unrestricted order-25 instance remains
open, and graphs with trivial or other automorphism groups dominate the
remaining search space.

## References

- G. Fan, *On diameter 2-critical graphs*,
  [Discrete Mathematics 67 (1987)](https://doi.org/10.1016/0012-365X(87)90174-9).
- T. W. Haynes, M. A. Henning, L. C. van der Merwe, A. Yeo,
  [*A maximum degree theorem for diameter-2-critical graphs*](https://doi.org/10.2478/s11533-014-0449-3).
- A. Dailly, F. Foucaud, A. Hansberg,
  [*Strengthening the Murty–Simon conjecture on diameter 2 critical graphs*](https://arxiv.org/abs/1812.08420).

The work is AI-assisted research directed by Edison Yi. Programs, reductions,
and exposition were generated and adversarially checked by Codex agents; all
claims remain subject to independent mathematical review.
