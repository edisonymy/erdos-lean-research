# Priority and prior-art audit: the finite `K4`-free `h=10` theorem

**Search cutoff:** 2 August 2026, 19:24 BST (18:24 UTC).  
**Purpose:** novelty/priority search only. This is not a mathematical audit and
does not itself authorize a public claim.  
**Primary verdict:** no public source located states either finite theorem below,
an equivalent result, or a finite verification of Erdős #151 reaching orders 40
or 41. The order-41 theorem is therefore a strong candidate for a new result.
The order-40 companion is also a strong candidate.

**Post-search correctness gate:** both proof packages have separate independent
mathematical audits with verdict `PASS`; see
[`INDEPENDENT_AUDIT.md`](INDEPENDENT_AUDIT.md) and
[`order40/INDEPENDENT_AUDIT.md`](order40/INDEPENDENT_AUDIT.md). The order-40
audit completed later on 2 August 2026. This update does not alter the search
cutoff or turn absence of a located source into proof of novelty.

Absence from the sources and indexes searched is not proof of novelty. The
publication-safe formulation is **"To the best of our targeted literature and
announcement search, we are not aware of a previous proof."** It is not safe to
say categorically that this is the first proof until expert review and the
remaining inaccessible-paper check described below.

## Claims audited

The campaign uses `beta(G)` for the largest vertex set containing no
inclusion-maximal clique of `G` of size at least two. Thus
`tau_C(G) + beta(G) = |V(G)|`.

1. **Order 41 (independently audited locally):** every `K4`-free graph `G` on
   41 vertices satisfies `beta(G) >= 10`, equivalently `tau_C(G) <= 31`.
   This theorem is unconditional; it uses only the published upper bound
   `R(3,10) <= 41`, not the unresolved choice between 40 and 41.
2. **Order 40 companion (independently audited locally):** if
   `R(3,10)=40`, every `K4`-free graph `G` on 40 vertices satisfies
   `beta(G) >= 10`, equivalently `tau_C(G) <= 30`. If `R(3,10)=41`, the #151
   requirement at order 40 is only `beta(G) >= 9`, inherited in the campaign
   from its through-order-39 result. The combined campaign consequence is the
   `K4`-free lane of #151 at order 40, not the unrestricted problem.

The proof notes under audit are
[`K4FREE_ORDER41.md`](K4FREE_ORDER41.md) and
[`order40/ORDER40_RESIDUAL.md`](order40/ORDER40_RESIDUAL.md). The independent
mathematical audits are [`INDEPENDENT_AUDIT.md`](INDEPENDENT_AUDIT.md) and
[`order40/INDEPENDENT_AUDIT.md`](order40/INDEPENDENT_AUDIT.md), respectively;
the corresponding machine-readable manifests are [`result.json`](result.json)
and [`order40/result.json`](order40/result.json).

## Bottom-line priority assessment

- **Exact order-41 theorem:** no match found in clique-transversal,
  Erdős--Rogers, clique-coloring, regular-graph, or Folkman/minimal-Ramsey
  literature; no match found in current preprints, public repositories, or
  announcement searches. **Estimated confidence that no explicit prior public
  theorem was present in the searched record: 94%.**
- **Exact order-40 companion:** no match found. **Estimated confidence: 93%.**
  This is slightly lower because its proof invokes more ingredients and has a
  conditional Ramsey-number hypothesis.
- **Proof architecture:** no source was found combining an edge-minimal
  `(3,3)`-Ramsey core, Bikov's degree-eight link classification, ambient
  maximal-clique routing, and a paired proper-color-class bound for `beta`.
  **Estimated confidence that this complete combination is new: 90%.** Several
  individual steps are elementary enough that they may be implicit elsewhere,
  so no separate novelty claim should be made for the Folkman reduction or the
  color-pair lemma alone.
- **Full Erdős #151:** neither theorem is a full solution. They are finite,
  natural-subclass advances in the very `K4`-free regime which Erdős and Gallai
  explicitly identified as out of reach.

## Exact-problem and status sources

### Original and survey sources

- P. Erdős, *Problems and results in combinatorial analysis and graph theory*,
  Discrete Mathematics 72 (1988), 81--92, p. 82,
  [DOI](https://doi.org/10.1016/0012-365X(88)90196-3). This is the source of
  the remark that no progress was known even under the `K4`-free hypothesis.
- P. Erdős, T. Gallai, and Zs. Tuza, *Covering the cliques of a graph with
  vertices*, Discrete Mathematics 108 (1992), 279--289, published 28 October
  1992, [publisher record](https://www.sciencedirect.com/science/article/pii/0012365X92906815).
  This is the exact vertex/maximal-clique problem, not a triangle edge-cover
  problem.
- Zs. Tuza, *Unsolved Combinatorial Problems, Part I*, BRICS Lecture Series
  LS-01-1, last update 28 May 2001,
  [full PDF](https://www.brics.dk/LS/01/1/BRICS-LS-01-1.pdf). Problem 66 asks
  whether the maximum `tau_C` at every order is attained by a triangle-free
  graph; Problem 68 separately asks for large induced triangle-free subgraphs
  in `K4`-free graphs. This separation is important: the latter parameter is
  adjacent to, but not identical with, `beta` in an arbitrary ambient graph.
- The older UCSD problem page still records only the 1992 general bound and the
  open conjecture:
  [Estimate the clique transversal number of a graph](https://mathweb.ucsd.edu/~erdosproblems/erdos/newproblems/CliqueTransversal.html).
- The live [Erdős Problems #151 page](https://www.erdosproblems.com/151) was
  last edited 2 December 2025 and, in the copy indexed at the cutoff, remained
  open with no partial or complete solution in its comments. Database status
  was treated only as a lead: its own warning says that the literature may lag.

### Most recent adjacent status evidence

- *A note on the clique-transversal number*, 21 April 2026,
  [full PDF](https://www.ulam.ai/research/erdos610.pdf), proves the asymptotic
  statement `max tau_C(G) = n - Theta(sqrt(n log n))`. Its Remark 8 explicitly
  says the stronger Erdős--Gallai--Tuza pointwise speculation is not settled.
  This is the most recent directly relevant mathematical status statement
  located.
- The [SciNet #151 record](https://api.scinet.pub/p/c6a62326-c92a-4fe7-8a01-5f7f55ad883a),
  posed 14 July 2026, still showed zero investigations and zero runs in the
  indexed record and described a proved `K4`-free subclass as a meaningful
  advance. This is useful for the announcement sweep, not mathematical evidence
  of novelty.
- The public [teorth/erdosproblems repository](https://github.com/teorth/erdosproblems)
  and exact GitHub searches exposed no #151 formalization, proof, or finite
  order-40/41 claim. A generic dataset entry in `gpt-erdos` merely reproduces
  the open problem statement.

## Closest clique-transversal literature

### Regular and bounded-degree graphs

The most serious possible overlap is E. Shan, T. C. E. Cheng, and L. Kang,
*Bounds on the clique-transversal number of regular graphs*, Science in China
Series A 51 (2008), 851--863, published 19 April 2008,
[publisher page](https://link.springer.com/article/10.1007/s11425-007-0157-6).
Its abstract states general bounds for regular graphs and sharp results for
claw-free cubic graphs. Later papers describe its general contribution as an
upper bound and a sharp lower bound for connected `k`-regular graphs. No
available abstract, citation excerpt, index record, or later application gives
the order-41 statement, an arbitrary `K4`-free 8-regular-core result, a Folkman
reduction, or the `q <= 4 beta(Q)` argument used here.

**Residual literature risk:** the full 13-page 2008 article was subscription
only in every source located and was not read end-to-end in this audit. This is
the single most important paper to obtain from a library or author before a
categorical novelty statement. The evidence available makes exact overlap
unlikely: subsequent work still sought tight upper bounds even for cubic
graphs, and the paper's advertised special hypotheses do not cover the present
8/9-degree `K4`-free Ramsey core.

Other bounded-degree results are substantially narrower:

- G. Bacsó and Zs. Tuza, *Clique-transversal sets and weak 2-colorings in
  graphs of small maximum degree*, DMTCS 11(2) (2009), 15--24,
  [full PDF](https://dmtcs.episciences.org/453/pdf), proves a subcubic
  transversal bound and weak 2-colorability for claw-free graphs of maximum
  degree at most four. It even notes that the 8-regular line graph of `K6` is
  not weakly 2-colorable. It does not cover arbitrary `K4`-free degree-8/9
  graphs.
- D. G. Wang, E. F. Shan, and Z. S. Liang, *On the Clique-Transversal Number
  in (Claw, K4)-Free 4-Regular Graphs*, Acta Mathematica Sinica 30 (2014),
  505--516, [journal record](https://actamath.cjoe.ac.cn/Jwk_sxxb_en/EN/lexeme/showArticleByLexeme.do?articleID=22216),
  and F. Xu, B. Wu, and Q. Li, *The clique-transversal number of a
  {K1,3,K4}-free 4-regular graph*, Discrete Mathematics 338 (2015),
  1126--1130,
  [publisher record](https://www.sciencedirect.com/science/article/pii/S0012365X1500059X),
  impose both claw-freeness and 4-regularity. Their exact formulas do not apply
  to the present core.
- Planar, chordal, line-graph, comparability, and clique-perfect results found
  in the citation trail all impose graph-class hypotheses absent here. None
  states a finite verification of #151.

### Complementary-parameter and variant terminology

- S. R. Bhat, R. Bhat, and S. G. Bhat, *Clique Free Number of a Graph*,
  Engineering Letters 31(4) (2023), 1832--1836,
  [full PDF](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf),
  defines the complementary clique-free number `beta_vc` and records
  `tau_C + beta_vc = n`. It has no #151 recurrence, Ramsey/Folkman reduction,
  or finite order theorem. The complementary parameter itself is therefore not
  novel.
- M. Milanič and Y. Uno, *Upper Clique Transversals in Graphs*, submitted
  25 September 2023, [arXiv](https://arxiv.org/abs/2309.14103), and E. Boros
  et al., *Conformal Hypergraphs: Duality and Implications for the Upper Clique
  Transversal Problem*, [arXiv](https://arxiv.org/abs/2309.00098), concern the
  **maximum size of a minimal** clique transversal. That is a different
  invariant from minimum `tau_C` and its complement `beta`.
- In several algorithmic papers, "clique independence number" means a maximum
  family of pairwise vertex-disjoint maximal cliques, not the largest vertex
  subset containing no maximal clique. Searches were repeated with
  `clique-free`, `maximal-clique-free`, `beta_vc`, and `mcf(G)` to avoid this
  terminology trap.

## Induced triangle-free / Erdős--Rogers literature

For a `K4`-free graph, the largest induced triangle-free vertex set is the
Erdős--Rogers parameter `alpha_3(G)`. This is close to the campaign core, where
every edge lies in a triangle and admissibility is exactly induced
triangle-freeness. It is **not** equivalent to `beta(G)` for an arbitrary
ambient graph: an induced triangle-free set may contain an ambient-maximal
edge, which makes it inadmissible.

The audit covered G. Wolfovitz, *K4-free graphs without large induced
triangle-free subgraphs*, Combinatorica 33 (2013), 623--631,
[publisher page](https://link.springer.com/article/10.1007/s00493-013-2845-x),
T. Gowers and O. Janzer, *Improved bounds for the Erdős--Rogers function*,
Advances in Combinatorics (2020),
[journal page](https://www.advancesincombinatorics.com/article/12048-improved-bounds-for-the-erdos-rogers-function),
and subsequent generalized Erdős--Rogers work. These sources give asymptotic
bounds. Searches for exact `f_{3,4}(41)`, `K4`-free order 41, and an induced
triangle-free 10-set found no small-order result that implies either audited
theorem. No source combined Erdős--Rogers bounds with ambient maximal-edge
control.

## Folkman and minimal-Ramsey literature

- A. Bikov, *Small minimal (3,3)-Ramsey graphs*, submitted 13 April 2016,
  [arXiv](https://arxiv.org/abs/1604.03716), contains the degree-eight link
  classification used by the order-41 proof. This is a cited ingredient. A
  full-text search found no occurrence of clique transversals and no finite
  `beta` theorem.
- A. Bikov and N. Nenov, *On the independence number of (3,3)-Ramsey graphs
  and the Folkman number Fe(3,3;4)*, submitted 4 April 2019,
  [arXiv](https://arxiv.org/abs/1904.01937), bounds ordinary independence in
  `K4`-free arrowing graphs. It is adjacent but points in a different parameter
  direction.
- K. Hassan, S. Radziszowski, and J. Van Overberghe, *On Small Folkman Graphs
  Arrowing K2 or K3*, submitted 15 May 2026,
  [arXiv](https://arxiv.org/abs/2605.16542), is the newest Folkman preprint
  located. Searches within it for `transversal`, `maximal clique`, and `Brooks`
  gave no match relevant to the audited claims.

Exact searches combining `clique transversal` with `Folkman`,
`edge-Folkman`, `minimal (3,3)-Ramsey`, `monochromatic triangle`, and
`arrowing` found no prior use of the campaign reduction. The reduction itself
is elementary and should be cited as an observation rather than advertised as
independently novel unless an expert confirms priority.

## Coloring ingredients and the order-40 companion

The order-41 use of Brooks' theorem is classical. No source was found using
the same pair-of-proper-color-classes summation for clique-free sets in a
minimal `(3,3)`-Ramsey core. The summation is elementary, however, and should
not carry a strong standalone novelty claim.

The order-40 note uses the 1977 Borodin--Kostochka consequence that a graph
with `chi=Delta=9` contains `K5`:

- O. V. Borodin and A. V. Kostochka, *On an Upper Bound of a Graph's
  Chromatic Number, Depending on the Graph's Degree and Density*, JCTB 23
  (1977), 247--250,
  [publisher record](https://www.sciencedirect.com/science/article/pii/0095895677900375).
- R. Galindo and J. McDonald, *On graphs with chromatic number and maximum
  degree both equal to nine*, submitted 22 August 2024,
  [arXiv](https://arxiv.org/abs/2408.12693), explicitly records this known
  `chi=Delta=9 => K5` fact on p. 2.

These are prior ingredients, not overlap with the finite clique-transversal
theorem. A current Ramsey-number check found V. Angeltveit's
`R(3,10) <= 41` theorem, [journal PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v32i4p30/pdf/),
and no later resolution: at the cutoff `R(3,10)` remained 40 or 41. A January
2026 structural preprint still quoted the superseded 40--42 range and was not
used as a status authority.

## The similarly named edge-version is not this problem

Searches for "Erdős--Gallai--Tuza conjecture" are dominated by a different
edge problem concerning triangle-independent edges and triangle edge covers:

- G. Puleo, *On a Conjecture of Erdős, Gallai, and Tuza*, submitted
  18 November 2013, [arXiv](https://arxiv.org/abs/1311.5332).
- G. Puleo, *Extremal aspects of the Erdős--Gallai--Tuza conjecture*,
  submitted 22 August 2014, [arXiv](https://arxiv.org/abs/1408.5176).

Those papers concern an inequality of the form `alpha_1 + tau_1 <= n^2/4`
for **edges in triangles**. They neither state nor imply the vertex/maximal-
clique inequality in #151.

## Announcement and preprint sweep

The final sweep searched exact theorem strings and their complements across
general web indexes, arXiv, GitHub, the Erdős database, SciNet, and indexed
LinkedIn pages. Representative exact queries included:

```text
"K4-free" "41 vertices" "clique transversal"
"K_4-free" "41" "clique-transversal"
"tau_C(G)" "31" "K4-free"
"beta(G)" ">=10" "K4-free"
"clique-free number" "10" "41" graph
"Erdős Problem #151" proof
"tau(G) <= n-H(n)" finite
"clique transversal" "through order"
"K4-free" "41 vertices" "triangle-free induced"
"f_{3,4}(41)"
"minimal (3,3)-Ramsey" "clique transversal"
"edge-Folkman" "clique transversal"
"Brooks" "clique transversal"
site:arxiv.org "clique-transversal" 2026
site:github.com "Erdős #151" "clique transversal"
site:linkedin.com "Erdős" "clique transversal"
```

The searches returned the sources catalogued above, generic problem mirrors,
and unrelated uses of `tau`/`beta`, but no exact or stronger finite theorem.
Because web indexes can lag brand-new posts and private circulation is
invisible, this sweep should be repeated immediately before public release.

## Recommended publication wording and remaining checks

1. Both finite theorems have passed separate independent mathematical audits
   and have hash-recorded result manifests. Treat the order-41 theorem as
   unconditional and the order-40 companion as conditional on `R(3,10)=40`;
   keep that hypothesis explicit in every title and announcement. Final
   source/hash reproduction and one expert graph-theory read remain prudent.
2. No public announcement or categorical priority claim was made by this
   audit. The defensible novelty wording remains the qualified formulation at
   the start of this report.
3. Before any categorical first-proof assertion, obtain and inspect the full
   Shan--Cheng--Kang 2008 paper and, if practical, send a narrowly worded
   private priority query to a clique-transversal expert. Private outreach was
   not performed by this audit.
4. Use the wording "we found no previous finite verification or theorem of
   this form" and cite the adjacent regular-graph, Erdős--Rogers, and Folkman
   literatures. Do not claim novelty for `tau+beta=n`, Brooks' theorem, the
   Bikov classification, the Borodin--Kostochka consequence, or the
   edge-Folkman definition.
5. State the scope prominently: this advances the `K4`-free finite lane at the
   `h=10` jump; it does not solve all of #151 and does not settle
   `R(3,10)`.
