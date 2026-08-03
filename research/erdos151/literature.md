# Priority and literature audit

**Cutoff:** 2 August 2026, with announcement-level repeats at 13:09 and
15:03 UTC.
**Conclusion:** no prior proof, counterexample, recurrence, or explicit
verification through order 18, 22, 27, or 39 specific to Erdős problem 151
was found.  This is absence of evidence, not proof of novelty.

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
- Immediately before the through-order-39 result was prepared, another sweep
  searched the exact inequality, problem number, original paper title,
  clique-free-number terminology, Ramsey values `R(3,9)` and `R(3,10)`, and
  Folkman/minimal-Ramsey formulations.  It found the original problem,
  general clique-transversal literature, and the recent asymptotic Ulam note,
  but no matching bounded theorem or proof mechanism.
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

- About **95% confidence** that no prior public full resolution was present in
  the searched venues before this publication, and about **92% confidence**
  that no explicit finite verification through order 39 was present.
- About **90% confidence** that the recurrence and Ramsey-interval strategy do
  not occur in the searched literature.
- **No novelty claim** for the complementary parameter or `tau+beta=n`.

These estimates are deliberately below certainty because not every older
paper was available for full-text inspection.  Human expert review and
additional citation checking remain welcome in the public review issue.

## 3 August 2026 targeted follow-up

Two narrower searches were repeated after the heavy-edge normalization was
developed.

- Exact combinations of `clique transversal`, `Ramsey`, triangle-free
  edge-colouring, monochromatic triangles, and Folkman/arrowing terminology
  found the original and recent clique-transversal literature but no prior
  statement of the campaign's reduction
  `G not -> (3,3) implies beta(G) >= H(n)`.  This is only a search result,
  not a novelty proof; the elementary argument should still be shown to
  specialists before a priority claim.
- Bibby, Odesky, Wang, Wang, Zhang and Zheng,
  [*Minimal flag triangulations of lower-dimensional
  manifolds*](https://arxiv.org/abs/1909.03303), prove that a minimum flag
  triangulation of the projective plane has 11 vertices and develop
  admissible edge contractions.  This is relevant background for the
  normalization lane.  It does not appear to classify the degree pattern
  `(10^3,5^18)` or the quotient/fibre constraints arising from the
  24-vertex uniform-type-5 graph.

The April 2026 Ulam note was re-opened and checked at its conclusion: it
explicitly calls `tau(G) <= n-H(n)` the stronger Erdős--Gallai--Tuza
speculation and states that its asymptotic argument does not settle it.

### Local-link classification follow-up

After the uniform type-5 class was isolated, a separate search used the exact
link descriptions `C5 wedge C5`, `C_5 vee C_5`, figure-eight/tight-handcuff
link, locally two pentagons, locally pentagonal, and 9-regular locally fixed
graph.  It found no classification or construction for graphs whose every
open neighbourhood is two induced 5-cycles sharing one vertex.

The closest directly relevant sources found were:

- Devillers--Fawcett--Praeger--Zhou's
  [locally-pentagonal result](https://research-repository.uwa.edu.au/files/74868868/on_k_connected_graphs.pdf),
  which recalls that a connected locally `C5` graph is the icosahedron; this
  applies to the individual normalized surface components, not to the
  original `C5 wedge C5` local graph; and
- [*On the clique behavior of graphs with small constant
  link*](https://xamanek.izt.uam.mx/map/papers/locally6.pdf), which treats all
  fixed links through order six and gives an order-nine example locally
  `C5 union P4`.  It does not list or classify the order-nine figure-eight
  link used here.

Thus the targeted search found no prior full classification that supersedes
the 34-case computation.  This remains an absence-of-evidence statement, not
a novelty theorem.
