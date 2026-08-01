# Erdős Problem 742: candidate-first order-25 search

## Bottom line

No counterexample has been found, and there is no new proof of the
Murty--Simon conjecture.  This directory contains an independently audited
candidate-search pipeline for the first order not covered by Fan's theorem,
`n = 25`.  Any eventual UNSAT response is exploratory unless it is accompanied
by a separately checked proof certificate.

The target is a finite simple graph `G` of diameter exactly two such that
deleting every edge makes the diameter different from two, with

```text
|V(G)| = 25 and |E(G)| >= floor(25^2/4) + 1 = 157.
```

A SAT model would be a genuine counterexample after the edge list passes
`verify_graph.py`; it would settle the full conjecture negatively.

## Why order 25

Fan proved the Murty--Simon inequality for every order at most 24 and for order
26.  Füredi proved it for every sufficiently large order, but the resulting
threshold is not a practical completed finite check.  Thus order 25 is the
first explicit order not covered by Fan; this does not imply that it is the
only remaining practical order.

Fan's general numerical bound

```text
m < n^2/4 + (n^2 - 16.2n + 56)/320
```

gives `m < 157.1125` at order 25.  Hence an order-25 counterexample would have
exactly 157 edges.  The unrestricted run uses only the weaker lower bound;
the strongest restricted run also passes `--max-edges 157` to search the
exact slice.

## Public input and trust boundary

Brian Li's public
[`diameter2critical`](https://github.com/BrianLi009/diameter2critical)
repository, commit
[`57fd4b41913670227f7bc86708297d695af7823e`](https://github.com/BrianLi009/diameter2critical/commit/57fd4b41913670227f7bc86708297d695af7823e),
contains raw diameter-2-critical CNFs through order 30.  The immutable GitHub
blob for the order-25 file has canonical-LF SHA-256

```text
f43f7d69fc204d7be37da4e869c1771fe516dac7995175f16c49b7f4990c0c25
```

The active Windows checkout was automatically converted to CRLF and has
SHA-256 `29132925be690801780c9c69c7244115cc19f214876b410ab6545f24125ea2cc`;
line endings do not change the parsed clauses.  Both copies begin with
`p cnf 21300 359400`.  The first `C(25,2)=300` variables are the graph edges
in lexicographic pair order.  The upstream repository states no order-25
counterexample or UNSAT result.  Long-running searches hash the input before
parsing and reject the result if the file's ending hash differs.

From a clean clone, install the exact SAT binding and fetch byte-pinned LF
copies of the order-5, order-6, and order-25 inputs with:

```powershell
python -m pip install -r experiments\erdos742\requirements-search.txt
python experiments\erdos742\fetch_upstream_cnfs.py
```

The fetcher pins upstream commit `57fd4b4...` and verifies each blob before
writing it under `.research-cache/diameter2critical-lf/`.

The upstream encoding is not accepted on authority.  `audit_source_cnf.py`
fixes every edge assignment and asks whether the auxiliary variables can be
completed, comparing the answer with the separate definition-level graph
checker.  It found zero mismatches over all 1,024 labelled graphs at order 5
and all 32,768 labelled graphs at order 6.  The source CNFs accepted exactly
27 and 571 diameter-2-critical graphs, respectively.

The same exhaustive test was repeated after the strongest local symmetry
constraints (a fixed triangle and degree sorting within the triangle and its
complement).  It again found zero mismatches.  The retained audit outputs are
`audit_n5.json`, `audit_n6.json`, `audit_triangle_degree_n5.json`, and
`audit_triangle_degree_n6.json`; `audit_exact7_n6.json` separately checks the
combined lower/upper edge-cardinality encoding.

These small-order tests are strong bug detectors but do not prove the upstream
order-25 CNF correct.  Their role is candidate-oracle validation: every SAT
edge list is checked without its auxiliary variables.  No uncertified UNSAT
result is promoted to a theorem.

## Sound search restrictions

`candidate_search.py` supports several independently checkable restrictions:

- `--degree-order` sorts vertex degrees.  Without other fixed vertices this
  loses no isomorphism class.
- `--fix-triangle` fixes a triangle on vertices 0, 1, 2.  A counterexample has
  more than `floor(n^2/4)` edges and therefore contains a triangle by Mantel's
  theorem.  With degree ordering enabled, the triangle and the remaining
  vertices are sorted as separate blocks.  The executable rejects this flag
  when the requested edge bound does not exceed the Mantel bound, where the
  symmetry restriction would no longer be exhaustive.
- `--max-degree 17` uses Haynes--Henning--van der Merwe--Yeo, Theorem 2.1(a):
  a diameter-2-critical graph with `Delta >= 0.7 n` satisfies the conjecture.
  At order 25 a counterexample therefore has `Delta <= 17`.  This literature
  dependency is explicit and is not needed by the unrestricted run.
- `--no-dominating-edge` uses the published dominating-edge case: every
  diameter-2-critical graph with a dominating edge satisfies the bound.  The
  encoding existentially chooses a vertex missed by the closed neighborhoods
  of each present edge.

The degree sorting network was tested exhaustively at orders 5 and 6.  It uses
exact Boolean comparators whose outputs are equivalent to OR and AND, so the
`k`-th unary output means that the degree is at least `k+1`.
The no-dominating-edge encoding was also checked on every graph at orders 5
and 6, retaining 12 and 180 labelled diameter-2-critical graphs and producing
zero disagreements with direct neighborhood unions.  The lower/upper
cardinality combination was separately checked on all order-6 graphs at the
exact seven-edge slice, again with zero disagreements.

Representative commands are:

```powershell
python experiments\erdos742\candidate_search.py `
  .research-cache\diameter2critical-lf\25.cnf 25 `
  --solver maplesat --result .tmp\erdos742_n25.json

python experiments\erdos742\candidate_search.py `
  .research-cache\diameter2critical-lf\25.cnf 25 `
  --solver glucose42 --fix-triangle --degree-order --max-degree 17 `
  --no-dominating-edge --max-edges 157 `
  --result .tmp\erdos742_n25_triangle_max17.json `
  --candidate .tmp\erdos742_n25_triangle_max17_candidate.json
```

## Definition-level certificate checker

`verify_graph.py` recomputes all-pairs graph distances from the edge list.  It
requires original diameter exactly two and, for every edge, recomputes the
diameter after deletion and rejects the graph if it remains two.  Disconnected
deletions are accepted as having diameter different from two, matching the
mathematical convention.

The checker then verifies that the edge count exceeds `floor(n^2/4)`.  It does
not import the SAT formula or inspect any SAT auxiliary variable.
`candidate_search.py` additionally checks every requested fixed-triangle,
degree-order, maximum-degree, and no-dominating-edge restriction directly on
the decoded edge set before writing a candidate.

## Local witness reduction

A bounded Rethlas pass suggested, and direct inspection proves, the following
useful characterization.  For an edge `uv` in a diameter-two graph, deletion
of `uv` destroys diameter two exactly when at least one condition holds:

1. `u` and `v` have no common neighbour;
2. some `x in N(u) \ (N(v) union {v})` satisfies `N(x) intersect N(v) = {u}`;
3. the symmetric condition holds with `u` and `v` exchanged.

Indeed, a path of length at most two that uses `uv` either joins the endpoints
or has one endpoint at `u` or `v`; the three cases enumerate precisely when
that path is unique.  `audit_witness_counts.py` found no disagreement with the
deletion definition across every edge of every labelled diameter-two graph
through order 6: 102,405 edge instances at order 6 alone.

This gives a simple counting inequality.  Let `D` be the number of edges whose
endpoints have no common neighbour and `S` the number of nonedges whose
endpoints have exactly one common neighbour.  Every remaining critical edge
chooses a unique-common-neighbour nonedge, and each such nonedge can witness at
most the two incident edges through its unique common neighbour.  Hence

```text
|E(G)| <= D + 2*S.
```

The exhaustive audit found no violation through order 6, but also found
equality already at orders 4, 5, and 6.  The inequality is therefore a sound
reduction rather than a solution; a new stability bound on `D+2S` would still
be needed.

The same Rethlas pass falsified a tempting stronger route: a maximum cut need
not admit an injection from its internal edges to cross nonedges witnessed by
unique two-paths.  `maximum_cut_matching_obstruction.json` retains its
definition-checked order-10 example, and `verify_cut_obstruction.py` confirms
that its maximum cut is unique up to complementation and contains an internal
edge with no eligible cross-nonedge witness.  The harness was stopped after it
entered a repeated full-patch transcript loop; it produced no counterexample
to #742 and no verified proof blueprint.

## Live collision audit, 2026-08-01

- The live [Erdős Problems entry](https://www.erdosproblems.com/742) still
  labels the problem decidable/resolved only up to a finite check, not fully
  solved.
- The VibeMathed dataset generated `2026-08-01T17:07:01.367Z` contained 247
  entries and no problem 742 or Murty--Simon entry.
- Formal Conjectures issue 2132 and pull requests 2137, 2197, and 2200 concern
  statement formalization, not a proof.
- Exact-title searches found no Zenodo record, recent arXiv resolution,
  SciNet/Constellate finding, or competing public GitHub solution claim.
- The newest directly relevant primary paper located was Lin--Wang (2025), a
  restricted `C5`-free/high-density classification that still calls the full
  statement the longstanding Murty--Simon conjecture.
- A directly relevant public
  [order-25 structural investigation](https://github.com/txmy/ultra-mathematician/tree/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-24-001/tasks/audit-murty-n25-structural)
  reports no SAT/UNSAT verdict.  It audits a heuristic injection route rather
  than duplicating this exact candidate-search pipeline.

Search non-discovery cannot establish priority or novelty.  This is a dated
collision screen, not a claim that private or poorly indexed work does not
exist.

## References

- T. W. Haynes, M. A. Henning, L. C. van der Merwe, and A. Yeo,
  *A maximum degree theorem for diameter-2-critical graphs*,
  [DOI 10.2478/s11533-014-0449-3](https://doi.org/10.2478/s11533-014-0449-3).
- A. Dailly, F. Foucaud, and A. Hansberg,
  *Strengthening the Murty--Simon conjecture on diameter 2 critical graphs*,
  [arXiv:1812.08420](https://arxiv.org/abs/1812.08420).
- X. Lin and T. Wang, restricted high-density classification,
  [DOI 10.1016/j.dam.2025.06.025](https://doi.org/10.1016/j.dam.2025.06.025).
- G. Fan, *On diameter 2-critical graphs*,
  [DOI 10.1016/0012-365X(87)90174-9](https://doi.org/10.1016/0012-365X(87)90174-9).
