# Priority and literature audit

**Cutoff:** 2 August 2026, with an announcement-level repeat at 13:09 UTC.
**Conclusion:** no prior proof, counterexample, recurrence, or explicit
verification through order 18, 22, or 27 specific to Erdős problem 151 was
found.  This is absence of evidence, not proof of novelty.

## Current status and recent-claim sweep

- The live [Erdős Problems entry](https://www.erdosproblems.com/151) marks the
  problem open, records zero proof claims, and was last edited on 2 December
  2025.  Its sole discussion comment supplies the 1992 original reference.
- The [SciNet problem entry](https://api.scinet.pub/p/c6a62326-c92a-4fe7-8a01-5f7f55ad883a),
  created 14 July 2026, reported zero investigations, agents, or runs before
  this campaign result.  That is a platform record, not independent proof of
  novelty.
- Searches of GitHub, Formal Conjectures, VibeMathed, Mathlib, arXiv, Ulam,
  general web indexes, and date-restricted July--August 2026 results found no
  #151 solution or finite-order claim.
- Immediately before the order-24 result was prepared for publication, a
  fresh exact-title/formula/problem-number sweep again found no matching
  preprint or announcement.  The database warning that its status can lag was
  treated as a reason to search, not as evidence of novelty.
- The April 2026 Ulam note
  [*A note on the clique-transversal number*](https://www.ulam.ai/research/erdos610.pdf)
  concerns the asymptotic problem #610.  It explicitly leaves the stronger
  pointwise #151 speculation open.

## Exact prior art for the complementary parameter

The parameter reformulation itself is not new.

1. Surekha Ravishankar Bhat, Ravishankar Bhat, and Smitha Ganesh Bhat,
   [*Clique Free Number of a Graph*](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf),
   Engineering Letters 31(4) (2023), 1832--1836, define the maximum size
   `beta_vc(G)` of a vertex set containing no nontrivial inclusion-maximal
   clique and prove `tau_c(G)+beta_vc(G)=|V(G)|`.  A complete-page inspection
   found no closed-neighborhood recurrence, Ramsey interval, #151 statement,
   or finite-order theorem.  The paper also contains the already-known lower
   bound `beta_vc(G)>=Delta(G)`.
2. Colin McDiarmid, Dieter Mitsche, and Paweł Prałat,
   [*Clique coloring of binomial random graphs*](https://arxiv.org/abs/1611.01782),
   Random Structures & Algorithms 54(4) (2019), 589--614, DOI
   [10.1002/rsa.20804](https://doi.org/10.1002/rsa.20804), use the equivalent
   maximum maximal-clique-free parameter `mcf(G)` for random-graph clique
   coloring.  They do not discuss #151, the recurrence, or Ramsey-critical
   finite orders.

The original problem sources are Erdős (1988), p. 82, and Erdős--Gallai--Tuza
(1992), Problem 1 on p. 280; exact references and links are in
[`README.md`](README.md).

## Other citation trails inspected

Targeted searches covered clique-transversal algorithm and graph-class papers,
including Bacsó--Tuza (2009), Cooper--Grzesik--Král (2016), and
Milanič--Uno (2023).  Searches used exact variants of `tau(G)<=n-H(n)`,
`maximal-clique-free`, `beta_vc`, `N[I]`, closed-neighborhood deletion,
minimal counterexample, and `R(3,h-1)+h-1`.  No searched source contained the
campaign recurrence

```text
beta(G) >= |I| + beta(G-N[I]),
```

the resulting minimal-counterexample interval, the order-24
triangle-edge-coloring argument, or the finite verification recorded here.

## Calibrated novelty assessment

- About **95% confidence** that no prior public full resolution or explicit
  finite verification through order 18, 22, or 27 was present in the searched
  venues before this publication.
- About **90% confidence** that the recurrence and Ramsey-interval strategy do
  not occur in the searched literature.
- **No novelty claim** for the complementary parameter or `tau+beta=n`.

These estimates are deliberately below certainty because not every older
paper was available for full-text inspection.  Human expert review and
additional citation checking remain welcome in the public review issue.
