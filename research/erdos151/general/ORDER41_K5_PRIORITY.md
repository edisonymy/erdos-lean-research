# Priority audit: the order-41, clique-number-5 lane

**Search cutoff:** 2 August 2026, 22:04 BST (21:04 UTC)  
**Claim type:** prospective finite theorem; the full claim is currently catalogue- and computation-conditional  
**Purpose of this file:** literature priority and recency only. It does **not** validate the proof, the catalogue import, or the overlap enumeration.

## 1. Claim audited and present qualification

The prospective statement is

> If \(G\) has 41 vertices and \(\omega(G)=5\), then \(\beta_{vc}(G)\ge 10\). Equivalently, \(G\) has a clique transversal of order at most 31.

Here a “clique” means an inclusion-maximal nontrivial complete subgraph of the ambient graph. Thus a clique-free set is a vertex set containing no such ambient clique, \(\beta_{vc}(G)\) is its maximum order, and \(\tau_c(G)+\beta_{vc}(G)=|V(G)|\).

The local proof package currently divides the \(\omega=5\) case into three rows:

| Row | Current status in the local package | Priority consequence |
|---|---|---|
| R | analytic exclusion in [ORDER41_K5_RIGID_ATTACK.md](ORDER41_K5_RIGID_ATTACK.md) | does not depend on the order-17 catalogue |
| T | catalogue exclusion in [ORDER41_K5_RESIDUAL_OVERLAP.md](ORDER41_K5_RESIDUAL_OVERLAP.md) | conditional on completeness and correct identification of the seven \((3,6;17)\) graphs |
| D | analytic reduction plus exact overlap enumeration in [ORDER41_K5_DOUBLE_SATURATION.md](ORDER41_K5_DOUBLE_SATURATION.md) | conditional on the same catalogue and reproducibility/correctness of the finite overlap computation |

Accordingly, the full theorem must presently be described as **conditional on the published completeness of the seven-graph \((3,6;17)\) catalogue and on independent verification of the exact finite overlap computation**. An unconditional priority claim would outrun the proof status.

## 2. Bottom line

The targeted search found **no public source stating or proving the exact order-41 theorem**, any equivalent statement \(\tau_c(G)\le31\) for every 41-vertex graph with \(\omega(G)=5\), or the same result in clique-free-number notation.

It did find one exact and important piece of prior art. Bhat, Bhat, and Bhat proved in 2023 that

\[
\Delta(G)\le \beta_{vc}(G),
\]

and that if equality holds, the open neighborhood of every maximum-degree vertex is a maximum clique-free set. Therefore the proof package’s **maximum-neighborhood admissibility/maximality starting point is not new** and must be credited to their Proposition II.3.

No searched source combined that fact with the distinctive order-41 mechanism used locally:

- simultaneous saturation of five maximum neighborhoods arising from a maximum \(K_5\);
- the singleton-fibre bound \(|P_c(a)|\le1\) for vertices outside one such neighborhood;
- five large residual crosscuts followed by a degree/Turán rigidity argument;
- the residual independent-transversal obstruction in the forced \(K_3+4K_2\) structure; or
- in the double-saturation row, alignment of several order-17 Ramsey catalogue residuals over a common outside set and exact overlap enumeration.

That is negative-search evidence, not proof of novelty. The fibre bound is elementary enough that it could appear implicitly, under different language, or in an unindexed source. Safe priority wording should therefore be “we found no prior use of this combined finite architecture,” not “we introduce the first saturation lemma.”

## 3. Exact prior art that must be credited

### 3.1 Clique-free number, complementarity, and maximum neighborhoods

S. H. Bhat, Shivaraja Bhat, and Sowmya Bhat, [“Clique Free Number of a Graph”](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf), *Engineering Letters* **31**(4), 1832–1836 (December 2023). The PDF records receipt on **8 May 2023** and revision on **28 August 2023**. (Some repository metadata gives 1 November 2023; the journal issue itself is dated December 2023.)

Relevant exact overlaps are:

- Theorem III.2: \(\tau_c(G)+\beta_{vc}(G)=|V(G)|\).
- Proposition II.3: \(\Delta(G)\le\beta_{vc}(G)\); when equality holds, \(N(v)\) is a maximum clique-free set for every vertex \(v\) of maximum degree.

The local extremal regime \(\beta_{vc}=9\), together with a degree-9 vertex, is precisely the equality case of Proposition II.3. This proposition should be cited at the first use of a maximum neighborhood as a maximum clique-free set. The later, simultaneous five-neighborhood constraints are not stated in this paper.

### 3.2 The general clique-transversal problem

- Zsolt Tuza, [“Covering all cliques of a graph”](https://doi.org/10.1016/0012-365X(90)90354-K), *Discrete Mathematics* **86** (1990), 117–126; published **14 December 1990**. This is foundational clique-cover/transversal work, with a principal result for chordal graphs, but it does not give the order-41 \(\omega=5\) theorem.
- Paul Erdős, András Gyárfás, and Zsolt Tuza, [“Covering the cliques of a graph with vertices”](https://doi.org/10.1016/0012-365X(92)90681-5), *Discrete Mathematics* **108** (1992), 279–289; published **28 October 1992**. This is the primary source for the general pointwise clique-transversal question underlying Erdős Problem 151.
- Zsolt Tuza, [“Unsolved Combinatorial Problems, Part I”](https://www.brics.dk/LS/01/1/BRICS-LS-01-1.pdf), BRICS Lecture Series LS-01-1 (**May 2001**), section “Covering and coloring maximal complete subgraphs.” This records the surrounding open-problem programme, not the finite order-41 lane.

These sources establish that the invariant and global problem are old. Neither their general formulation nor the elementary complement identity is a priority point for the present work.

### 3.3 Nearby variants that are not the same theorem

- Laxmana, Shivaraja Bhat, Sowmya Bhat, and S. H. Bhat, [“Some Studies on Clique-free Sets of a Graph with respect to Clique Degree Conditions”](https://www.iaeng.org/IJAM/issues_v54/issue_8/IJAM_54_8_25.pdf), *International Journal of Applied Mathematics* **54**(8), 1689–1693 (**August 2024**), studies strong and weak clique-free variants and degree conditions. It does not state the order-41 result or the singleton-fibre architecture.
- Shivaraja Bhat and Sowmya Bhat, [“Clique Transversal-Critical, Fixed, Free and Totally Free Elements”](https://www.iaeng.org/IJAM/issues_v54/issue_11/IJAM_54_11_29.pdf), *International Journal of Applied Mathematics* **54**(11), 2425–2430 (**November 2024**); received **23 April 2024**, revised **26 September 2024**. Its deletion/contraction and fixed/free-element theory is adjacent terminology, not local extension saturation.
- Algorithmic work on “maximum clique transversals,” “upper clique transversals,” or \(s\)-clique-free vertex sets concerns different parameters. Search hits using those phrases were not counted as exact overlaps.

## 4. Most recent direct status evidence

The most recent substantive source located is Ulam AI, [“A note on the clique-transversal number”](https://www.ulam.ai/research/erdos610.pdf), dated **21 April 2026**. It derives

\[
T(n)=n-\Theta(\sqrt{n\log n})
\]

from known clique-colouring/Ramsey ingredients. Its Remark 8 explicitly distinguishes this extremal function from the stronger pointwise Erdős–Gyárfás–Tuza speculation and says the latter is not settled. It supplies current global context, but no order-41 or \(\omega=5\) analysis.

Two live problem indexes were also checked:

- [ErdősProblems.com, Problem 151](https://www.erdosproblems.com/151) was indexed as **OPEN**, with the page last edited **2 December 2025**; the indexed page reported no partial or complete solution in its comment activity. The site itself warns that status labels are provisional, so this is recency evidence only.
- [SciNet’s Problem 151 record](https://api.scinet.pub/p/c6a62326-c92a-4fe7-8a01-5f7f55ad883a) says the problem text was fetched **13 July 2026** and, as checked on 2 August 2026, displayed zero published investigations, agents, and runs. It is announcement/index evidence, not a scholarly priority authority.

Neither index contained the prospective \(\omega=5\), order-41 theorem or linked a competing preprint.

## 5. Ramsey catalogue and Folkman literature

### 5.1 The exact catalogue dependency is prior work

The finite proof’s order-17 input is not new:

- Stanisław Radziszowski and Donald Kreher, [“On \((3,k)\) Ramsey graphs: Theoretical and computational results”](https://combinatorialpress.com/jcmcc/vol4/), *Journal of Combinatorial Mathematics and Combinatorial Computing* **4** (1988), 37–52, reports the catalogue of all \((3,k)\)-Ramsey graphs for \(k\le6\). The [RIT repository record](https://repository.rit.edu/article/1423/) supplies the abstract and 1988 bibliographic record; its auto-generated citation contains an apparent “Oct 1998” typo, so the journal volume/year should be used.
- Brendan McKay’s [Ramsey graph data page](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html), checked **2 August 2026**, lists **2,576** order-16 and **7** order-17 Ramsey\((3,6)\) graphs.

The priority claim, if any, lies in the way the seven graphs are constrained and overlapped—not in their enumeration. Publication wording should pin the exact data file/hash used and make the computational certificate independently replayable. This audit does not certify either.

The new upper bound [\(R(3,10)\le41\)](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v32i4p30) by Vigleik Angeltveit, *Electronic Journal of Combinatorics* **32**(4), #P4.30, was published **3 November 2025** (submitted **14 May 2024**, accepted **29 April 2025**; [DOI](https://doi.org/10.37236/12936)). It motivates the order 41 frontier but does not imply the clique-number-5 statement.

### 5.2 Folkman catalogues are adjacent, not exact prior art

The search checked the small Folkman-graph literature because it combines clique-number restrictions with exhaustive graph generation:

- Aleksandar Bikov, [“Small minimal \((3,3)\)-Ramsey graphs”](https://arxiv.org/abs/1604.03716), submitted **13 April 2016**.
- Aleksandar Bikov and Nedyalko Nenov, [“The edge Folkman number \(F_e(3,3;4)\) is greater than 19”](https://arxiv.org/abs/1609.03468), submitted **12 September 2016**.
- Aleksandar Bikov and Nedyalko Nenov, [“On the independence number of the graphs that arrow \((3,3)\) and the Folkman number \(F_e(3,3;4)\)”](https://arxiv.org/abs/1904.01937), submitted **3 April 2019**.
- Raid Hassan, Stanisław Radziszowski, and Herman Van Overberghe, [“On Small Folkman Graphs Arrowing \(K_2\) or \(K_3\)”](https://arxiv.org/abs/2605.16542), submitted **15 May 2026**.

These sources provide neighbouring classification techniques and bounds, but no clique-transversal theorem at order 41, no \(\beta_{vc}\ge10\) statement for \(\omega=5\), and no five-neighborhood singleton-fibre argument was located in them. Any elementary Folkman reduction or catalogue fact used locally should be described as an application of known machinery, not itself as novel.

## 6. Structural overlap audit

| Local ingredient | Literature status found | Safe treatment |
|---|---|---|
| Clique-free set / clique-transversal complementarity | exact prior art in Bhat–Bhat–Bhat (2023), and implicit in earlier transversal work | cite; do not claim novelty |
| \(\Delta(G)\le\beta_{vc}(G)\) | exact prior art, Proposition II.3 (2023) | cite exactly |
| At equality, a maximum-degree open neighborhood is maximum clique-free | exact prior art, Proposition II.3 (2023) | cite exactly; this is not the new saturation step |
| Maximality implies an outside vertex completes an ambient maximal clique inside the set | basic consequence of maximality; related extension language is widespread | prove for clarity, make no independent novelty claim |
| Singleton fibre \(|P_c(a)|\le1\) for each anchor \(a\), simultaneously for five neighborhood cuts | no exact or implicit match located in the searched sources | possible distinctive lemma; say “not found,” not “first” |
| Five crosscut lower bounds plus degree/Turán forcing \(G[U]=K_3+4K_2\) | no match located | candidate new finite rigidity argument |
| Residual independent transversal contradicts \(\beta\le9\) | transversal theory is classical; this exact residual deployment was not found | describe the combination, not the generic concept, as distinctive |
| Alignment/overlap of multiple \((3,6;17)\) catalogue residuals on a common \(U\) | catalogue itself is prior work; no matching overlap computation located | publish code, hashes, and certificates; novelty only in the constrained overlap use |

## 7. Search record and negative-hit evidence

The following exact or near-exact queries were run through general web search and, where named, the indicated repository. Quotation marks were retained where supported.

### 7.1 Exact statement and notation

```text
"41 vertices" "clique transversal" graph
"41-vertex" graph "clique transversal" 31
"41 vertex" graph "clique transversal" 31
"clique transversal number" "31" "41" graph
"order 41" "clique transversal number"
"omega(G)=5" "clique transversal"
"omega = 5" graph "clique-free number"
"clique-free number" "41" graph
"beta_vc" "41" graph clique
"β_vc" "ω" "clique free number"
"Erdős problem 151" "order 41"
```

**Result:** no source stating the prospective theorem. Searches using \(\tau\) without “clique transversal” were too noisy to count as evidence.

### 7.2 Proof architecture

```text
"singleton fibre" graph clique
"singleton fiber" graph "maximal clique"
"exact fibre" graph "clique transversal"
"exact fiber" graph maximal clique transversal
"maximum clique free set" "N(v)" graph
"maximum clique-free set" "open neighborhood"
"clique-free set" "N(v)" "maximum" maximal clique
"clique free number" neighborhood saturation graph
"disjoint union of cliques" "clique-free number"
"independent transversal" "maximal clique" clique-free set
"clique-free set" "independent transversal" graph
```

**Result:** the maximum-neighborhood queries surfaced Bhat–Bhat–Bhat Proposition II.3. No source with the singleton-fibre inequality, five simultaneous cuts, forced \(K_3+4K_2\) residual, or the same residual transversal contradiction was located.

### 7.3 Repository/index sweep

- [arXiv](https://arxiv.org/search/): `("41 vertices" OR "order 41") ("clique transversal" OR "clique-free number")`, `"Erdős problem 151"`, `"omega(G)=5" "clique transversal"`, and `"tau(G)" "n-H(n)" clique`. No exact hit.
- [Google Scholar](https://scholar.google.com/scholar?q=%2241+vertices%22+%22clique+transversal%22): `"41 vertices" "clique transversal"`, `"Erdős problem 151"`, `"omega(G)=5" "clique transversal"`, and `"clique-free number" "41"`. No exact indexed result. Scholar access and indexing are incomplete, so this is weak negative evidence.
- [GitHub code search](https://github.com/search?q=%22Erd%C5%91s+%23151%22+%22clique+transversal%22&type=code): `"Erdos 151" "clique transversal"`, `"Erdős #151" graph clique`, `"omega(G)=5" "clique-free"`, and `"ORDER41" "K5" "clique transversal"`. Hits were copied open-problem databases, including [gpt-erdos](https://github.com/neelsomani/gpt-erdos/blob/main/data/unsolved.jsonl), rather than a proof or computation.
- [Zenodo](https://zenodo.org/search?q=%22Erd%C5%91s%20problem%20151%22): `"clique transversal" "41" graph`, `"Erdős problem 151"`, `"clique-free number" graph`, and `"Ramsey(3,6)" catalogue graph`. No exact record.
- ErdősProblems/SciNet: the live records discussed in Section 4 and searches `site:erdosproblems.com/151 clique transversal 2026`, `site:erdosproblems.com/151 "last edited"`, and `site:erdosproblems.com/151 "open" clique`. No claimed solution or finite \(\omega=5\) result was found.
- Ramsey/Folkman: searches for `Ramsey(3,6) catalogue 17 vertices`, `all (3,6;17) graphs`, `Folkman graph clique transversal`, and the authors/titles in Section 5. These located the catalogue and adjacent enumeration literature, not the target theorem.

Negative searches cannot cover private drafts, unindexed conference notes, alternate-language terminology, or work posted after the cutoff. They do, however, make a direct same-statement collision less likely and identify the main attribution that the local exposition must add.

## 8. Safe novelty and announcement wording

### For a proof draft before all finite verification is independently complete

> The proof package supports the following prospective, finite statement: conditional on the published completeness of the seven Ramsey \((3,6;17)\) graphs and on independent verification of the exact residual-overlap computation, every 41-vertex graph with clique number 5 has a clique-free set of order at least 10, equivalently a clique transversal of order at most 31. A targeted literature and repository search through 2 August 2026 found no previous proof of this finite \(\omega=5\) statement.

### For describing the method

> Bhat, Bhat, and Bhat already proved that equality in \(\Delta(G)\le\beta_{vc}(G)\) makes every maximum-degree neighborhood a maximum clique-free set. Our additional finite argument imposes this maximality simultaneously at the five vertices of a maximum \(K_5\), extracts singleton-fibre and residual-cut constraints, and combines them with degree rigidity and a pinned Ramsey \((3,6;17)\) catalogue computation. We found no prior source using this combination.

### Wording to avoid

- “We solve Erdős Problem 151.” The prospective result is only the \(n=41,\omega=5\) lane, not the global pointwise problem.
- “We introduce maximum-neighborhood saturation.” The crucial maximum-neighborhood equality fact is Proposition II.3 of Bhat–Bhat–Bhat (2023).
- “This is the first singleton-fibre lemma.” The search cannot establish categorical firstness, and the observation may be implicit elsewhere.
- “Unconditional” or “computer-free” for the full theorem while rows T and D retain catalogue/overlap dependencies.
- “The seven graphs are complete because the data page lists seven.” Completeness should be tied to the published enumeration, exact imported data, and an independently replayed certificate.

## 9. Residual priority risks and recommended final checks

Before any public priority claim:

1. Independently replay the T/D enumeration from the pinned seven-record input and archive hashes, software versions, command lines, and a human-checkable certificate.
2. Cite Bhat–Bhat–Bhat Proposition II.3 where maximum neighborhoods first enter; distinguish ordinary maximality from the new simultaneous five-neighborhood deductions.
3. Search forward citations of the 2023 paper and author publication lists again immediately before posting. Those are the likeliest homes for the same local extension observation.
4. Search MathSciNet, zbMATH, and full-text institutional repositories for alternate phrases such as “clique-independent set,” “clique-free vertex set,” “maximum neighborhood,” “private clique,” and “irredundant clique transversal.” These were not fully accessible in the present web sweep.
5. State the conditional premise in the title or abstract until the catalogue provenance and overlap certificate have both passed independent audit.

**Priority assessment at the cutoff:** no exact prior theorem found; one important inherited structural proposition found; several broad or computationally adjacent literatures found; the strongest defensible novelty claim concerns the *combined finite five-neighborhood/residual-overlap architecture*, not the invariant, the maximum-neighborhood starting point, Ramsey cataloguing, or generic transversal ideas.
