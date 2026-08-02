# Erdős problem 151: structural reduction and the first live order

**Public status (2 August 2026):** the full Erdős--Gallai--Tuza conjecture
remains open.  This package proves the conjectured inequality for all graphs
on at most 22 vertices.  The proof reduces the only live order below 23 to a
constrained order-18 graph and then excludes that graph analytically.  It does
**not** claim a solution of problem 151.

For a graph `G`, let `tau(G)` be the minimum number of vertices meeting every
inclusion-maximal clique of size at least two.  Let `H(n)` be the minimum
independence number among triangle-free graphs on `n` vertices.  The open
question is

```text
tau(G) <= n - H(n).
```

Define `beta(G)` to be the largest size of a vertex set containing no
nontrivial maximal clique of `G`.  Then `tau(G) = n - beta(G)`.  The key
recurrence found in this campaign is

```text
beta(G) >= |I| + beta(G - N[I])
```

for every independent set `I`.  The maximality direction is important: if a
clique contained in the residual is maximal in `G`, then it is maximal in the
residual; the converse is neither used nor generally true.

Together with `beta(G) >= Delta(G)` and the exact small Ramsey numbers, this
gives a short proof that `beta(G) >= H(n)` for every `n <= 17`.  A smallest
counterexample with `h=H(n)` can exist only when

```text
R(3,h) <= n <= R(3,h-1) + h - 1.
```

The first surviving order is `n=18`.  The detailed argument in
[`proof.md`](proof.md) excludes it: mixed degree-4/5 sequences contradict a
local link count, while a 5-regular candidate yields a triangle-free auxiliary
graph whose Ramsey independent six-set avoids every maximal clique.  The
minimal-counterexample interval and parity then exclude orders 19--22.

## Evidence and audit

- [`proof.md`](proof.md) gives the complete human-readable argument through
  order 22.
- [`audit.md`](audit.md) records the independent maximality, induction, Ramsey,
  and computation checks.
- [`literature.md`](literature.md) records the current priority search and the
  exact boundary between known parameter prior art and the present proof method.
- [`result.json`](result.json) records the exact claim, dependency thresholds,
  and the disposition of the superseded order-14 computation.
- A second agent independently checked every use of inclusion-maximality, the
  base cases, the induction, and the Ramsey thresholds before publication.
- As a computational sanity check, two separate implementations exhaustively
  processed all 274,668 unlabeled graphs on nine vertices and found maximum
  `tau=5` and no counterexample.  The analytic proof supersedes this census.

The earlier order-14 SAT hunt was stopped after the first structural proof was
verified.  A later order-18 q=0/2/4 portfolio was likewise stopped when the
analytic order-18 contradiction passed a fresh Sol/max audit.  These
proof-free runs produced no solver conclusion; they are recorded as
`STOPPED_AFTER_STRUCTURAL_PROOF`, never as `UNSAT`.  All local artifacts were
preserved and nothing was deleted.

## Novelty boundary

The live [Erdős Problems entry](https://www.erdosproblems.com/151) still marks
the full question open.  Bhat, Bhat, and Bhat (2023) already define the same
`beta` parameter (under the name clique-free number) and prove its duality
with the clique-transversal number; McDiarmid, Mitsche, and Prałat (2019) use
the equivalent maximal-clique-free parameter in random graphs.  Targeted
searches have not found the independent-set recurrence,
minimal-counterexample interval, or through-22 result, but the older-literature
comparison is not exhaustive.  This is a timestamped, independently derived
research note offered for expert review, not an assertion that every lemma is
new to the literature.

AI systems performed the discovery, audit, computation, documentation, and
publication preparation under Edison Yi's direction.  Independent-agent
agreement is a bug-finding measure, not peer review.

## References

- [Erdős problem 151](https://www.erdosproblems.com/151)
- P. Erdős,
  [*Problems and results in combinatorial analysis and graph theory*](https://doi.org/10.1016/0012-365X(88)90196-3),
  Discrete Mathematics 72 (1988), 81--92, p. 82.
- P. Erdős, T. Gallai, and Zs. Tuza,
  [*Covering the cliques of a graph with vertices*](https://doi.org/10.1016/0012-365X(92)90681-5),
  Discrete Mathematics 108 (1992), 279--289.
- S. Radziszowski,
  [*Small Ramsey Numbers*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1),
  Dynamic Survey 1, Electronic Journal of Combinatorics.
- S. R. Bhat, R. Bhat, and S. G. Bhat,
  [*Clique Free Number of a Graph*](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf),
  Engineering Letters 31(4) (2023), 1832--1836.
- C. McDiarmid, D. Mitsche, and P. Prałat,
  [*Clique coloring of binomial random graphs*](https://arxiv.org/abs/1611.01782),
  Random Structures & Algorithms 54(4) (2019), 589--614.
