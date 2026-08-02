# Recency and collision audit — 2 August 2026

This audit was completed before the certificate-backed computation. It is a
search record, not a proof of novelty and not evidence about private or
unindexed work.

## Current status

- The live [Erdős Problems #742](https://www.erdosproblems.com/742) page was
  fetched on 2026-08-02. It labels the problem `DECIDABLE`, meaning resolved
  only up to a finite check, and reports **0 claimed proofs**. The retrieved
  HTML had SHA-256
  `d1ae78f381ff30da6c7e97722c04fa8c283f2d75b01887d73cfb41f04b9a6cbe`.
- The [VibeMathed](https://vibemathed.com) dataset generated
  `2026-08-02T01:00:41.357Z` contained 250 entries, including the 1 August
  OpenAI/Astra announcements, but no problem 742, Murty–Simon, or
  diameter-2-critical entry. The retrieved JSON had SHA-256
  `f896bd7df8104f5b628f18c252299eef0577e92bf6beb7bb2ff19da1abdfd633`.
- The pinned Formal Conjectures statement is commit
  `735aee074327b8e78b0d92bb1ee8ea00937c3f51`, file
  `FormalConjectures/ErdosProblems/742.lean`. Issue
  [#2132](https://github.com/google-deepmind/formal-conjectures/issues/2132)
  and its linked pull requests concern formalization of the statement, not a
  proof. Issue
  [#4358](https://github.com/google-deepmind/formal-conjectures/issues/4358)
  mechanically interprets the site's `DECIDABLE` label as solved; it supplies
  no mathematical resolution.

## Announcement-level search

Exact-title, keyword, and problem-number searches were repeated across arXiv,
Zenodo, GitHub repositories and code, SciNet/Constellate, and the general web.
Queries included `Murty Simon`, `diameter 2 critical`, `Erdos 742`, and
combinations with `proof`, `counterexample`, `SAT`, and `order 25`.

The relevant hits were:

- Dailly–Foucaud–Hansberg,
  [*Strengthening the Murty–Simon conjecture on diameter 2 critical graphs*](https://arxiv.org/abs/1812.08420),
  which closes the dominating-edge case but not the conjecture.
- Lin–Wang's 2025
  [restricted high-density classification](https://doi.org/10.1016/j.dam.2025.06.025),
  which continues to describe the full problem as the Murty–Simon conjecture.
- Brian Li's public
  [`diameter2critical`](https://github.com/BrianLi009/diameter2critical)
  CNF repository, which supplies instances through order 30 but no order-25
  SAT/UNSAT verdict.
- A 24 July 2026
  [order-25 structural audit](https://github.com/txmy/ultra-mathematician/tree/d52f81ad64dfc77e9a89dee8ae97db983ac6d5f7/runs/run-2026-07-24-001/tasks/audit-murty-n25-structural),
  which reports no SAT/UNSAT verdict and studies a different heuristic
  injection route.

No public proof, counterexample, certificate-backed order-25 closure, or
order-five-automorphism exclusion matching the result in this directory was
found as of the stated date. No priority or novelty claim is made from this
non-discovery alone.
