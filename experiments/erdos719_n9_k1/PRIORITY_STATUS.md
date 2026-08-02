# Priority and status gate for Erdős #719

**Search cutoff:** 2 August 2026, 20:10 BST (19:10 UTC).

## Verdict

No public proof or counterexample to the Erdős--Sauer conjecture in #719 was
located. The problem is genuinely open to the best of this targeted current
search. No public result was claimed or announced from this probe.

The result in `RESULTS.md` is only the finite `r=3,n=9,nu<=1` slice. It does
not settle #719.

## Current checks

- The live [Erdős Problems #719 page](https://www.erdosproblems.com/719) still
  says `OPEN`, records no claimed partial or complete solutions, and identifies
  it as a conjecture of Erdős and Sauer.
- Its [revision history](https://www.erdosproblems.com/history/719) contains
  only the 20 October 2025 statement revision.
- The [discussion thread](https://www.erdosproblems.com/forum/thread/719) has
  one comment, dated 8 February 2026. It reports only the exhaustive
  `r=3,n=6` check and an immediate `r=7,n=8` observation.
- The live [VibeMathed dataset](https://vibemathed.com/api/dataset), generated
  `2026-08-02T16:33:16.140Z` with 252 entries, contains no problem-number 719,
  #719 title, or matching hypergraph-decomposition claim.
- Exact web, arXiv, and GitHub-index searches through the cutoff for the
  statement, `m-3nu(G)`, Erdős--Sauer plus `K_(r+1)^r`, and the decomposition
  terminology found only statement mirrors, incomplete formalizations, the
  existing February comment, and unrelated hypergraph decomposition work.
- The local llm-hunter attack reaches the same packing reduction and only the
  already-known small ranges; it records no solution.

The primary source is P. Erdős, *On the combinatorial problems which I would
most like to see solved*, Combinatorica 1 (1981), 25--42,
[DOI](https://doi.org/10.1007/BF02579174). On p. 8 of the article, Erdős writes
that he and Sauer conjectured the decomposition bound and hoped it could be
proved without knowing the relevant Turán number. The source uses the
threshold convention `f(n;K)-1`, which is the extremal number used by the live
page.

The database tooltip saying the problem “cannot be resolved with a finite
computation” is correct for an affirmative proof, but not for disproof: one
finite hypergraph with `e-r nu > ex_r(n,K_(r+1)^r)` would refute the universal
statement completely.

## Why #719 dominated the alternatives

The campaign's full 2 August triage had exactly two non-formalized candidates
meeting every one-week promotion gate: #151 and #719. With #151 excluded from
this diversification task, #719 was the unique probe-grade candidate.

It also had a live quantitative signal rather than mere formal
counterexample-falsifiability: the completed `n=8,nu=1` optimization had exact
margin `-1`. Moving to `n=9` preserved all decisive advantages:

- one explicit witness would settle the full conjecture negatively;
- `ex_3(9,K_4^3)=54` has a tiny independent certificate;
- packing one has a complete elementary classification;
- any candidate can be checked from definitions in under a second; and
- the slice is small enough for exact SAT as a backstop.

The nearest alternatives were materially worse on the one-week objective:

- #149 (the strong chromatic-index bound) and #701 (Chvátal's down-set
  conjecture) are famous, heavily attacked, and widely believed true; finite
  witnessability alone is not a live counterexample signal.
- #11 and #985 admit finite numerical counterexamples in principle, but
  existing computation and heuristics push plausible witnesses far outside a
  one-week search.
- #470's odd-weird-number question is actively searched beyond enormous
  ranges, and a witness would not answer every question grouped on its page.
- The remaining high-scoring formalized targets require infinite families,
  asymptotic proofs, or per-parameter constructions; a finite computation
  cannot end them.

The selection is therefore not a claim that #719 is likely false. It is the
best available product of uncertainty, full-solution leverage, reachable
geometry, cheap verification, and low collision risk after removing #151.

## Publication posture

The finite theorem is reproducible and useful campaign evidence, but it is not
a full-result announcement.  During this priority audit no git operation or
external outreach was made.  After the mathematical and checker audits passed,
the bounded theorem was published in an
[immutable release](https://github.com/edisonymy/erdos-lean-research/releases/tag/erdos719-n9-packing1-2026-08-02)
and [external-review issue](https://github.com/edisonymy/erdos-lean-research/issues/5).
Any future full witness must trigger a fresh recency gate before publication.
