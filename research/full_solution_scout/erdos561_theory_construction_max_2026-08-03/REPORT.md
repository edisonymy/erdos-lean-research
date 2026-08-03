# Erdős #561 — mathematical construction attack

Date: 2026-08-03  
Outcome: **KILL / NO FULL CANDIDATE**

## Executive outcome

The lane found no below-formula arrowing host and therefore no full negative
resolution of Erdős #561.  The parent campaign's complete small-host sweep is
also null at formula values 8, 9, and 10.  In accordance with the predeclared
stop rule, this construction lane stops here and does not expand to larger
tuples.

There is one rigorous consolation result: a short analytic proof of the
formula for the asymmetric tuple

\[
(K_{1,3}\sqcup K_{1,2},\;K_{1,2}\sqcup K_{1,1}),
\]

whose exact value is 9.  The proof is in `CLAIMS.md`.  It is not a full
solution, and novelty remains subject to the independent priority audit.

## Why this tuple was selected

For \(a=(3,2)\), \(b=(2,1)\), the formula gives

\[
(\ell_2,\ell_3,\ell_4)=(4,3,2),\qquad \sum\ell_k=9.
\]

It is the smallest clean two-by-two target in which both forests are
nonuniform and which avoids the published-case filters we could verify:

- the 1978 uniform-pair theorem;
- Győri–Schelp's numerical sufficient condition;
- Cheng's 2010 family in which every component after the first is an edge;
- the 2025 cases `s=1`, two equal stars on one side, all star degrees odd,
  and the stated uniform-odd extension; and
- the July 2026 v3 paper, which is explicitly restricted to uniform star
  forests and their Ramsey-minimal graphs.

The live problem page is still open, but that status is not treated as a
substitute for literature review.

## Mathematical mechanism

The key simplification is stronger than checking all colorings.

For any graph with at most eight edges:

1. A vertex of degree at least four supplies an avoiding coloring by making
   its whole star blue; only four red edges remain.
2. In a subcubic graph, a matching always saturates all cubic vertices at
   this edge budget.  Coloring that matching blue makes the blue graph a
   matching and drops the red maximum degree to two.

The only nontrivial part is the matching lemma.  Counting edges incident
with the degree-three set reduces it to at most five marked vertices.  Four
marked vertices force two disjoint internal edges; five force the unique
degree pattern whose complement is `P3 disjoint-union K2`.  This closes the
entire eight-edge region without graph enumeration.

## Construction searches

### Named families

`construction_sweep.py` uses the exact Hall/allocation characterization of a
star-forest embedding and a SAT test for an avoiding coloring.  It generated
named hosts from:

- complete bipartite and multipartite graphs;
- theta graphs;
- paths and cycles;
- wheels and fans;
- windmills;
- cliques with pendant leaves; and
- small disjoint unions of these atoms.

The saved run tested the first 20 conservatively filtered targets through
formula bound 13.  Depending on the tuple, 131 to 750 eligible named hosts at
the top two below-bound edge levels were tested.  There were zero candidates.
The catalogue is construction-driven and explicitly not exhaustive.

### Stochastic fixed-edge design

`stochastic_construction.py` minimizes the exact number of avoiding
colorings under one-edge swaps at the bound minus one.  In the final focused
run for `(3,2)` versus `(2,1)`, order 10 and eight edges:

- seed: `5610817`;
- 120 restarts;
- 700 steps per restart;
- 63,267 distinct labelled hosts evaluated;
- best exact avoiding-coloring count: 8 of 256;
- arrowing candidates: 0.

The saved best graph and one avoiding red mask are in
`stochastic_construction_result.json`.  `verify_obstruction.py` independently
confirmed that this mask avoids both targets.

## Independent checks

`verify_obstruction.py` does not import either discovery program.  It:

- enumerates the finite induced degree patterns needed in the matching
  lemma (22 eligible four-vertex patterns and 30 eligible five-vertex
  patterns, zero failures);
- checks all 512 colorings of
  `K1,4 disjoint-union K1,3 disjoint-union K1,2`, with zero avoiding
  colorings; and
- independently checks the stochastic near-host's saved avoiding coloring.

Result: `VERIFIED`.

## Stop decision

This lane has no plausible full-resolution signal:

- no candidate in the principled host families;
- no candidate after a substantial exact-score stochastic pulse;
- the smallest attractive tuple is now analytically closed positively;
- the parallel complete meta-sweep is null through formula value 10; and
- an active 2026 group is working directly beside the remaining boundary.

The expected value of moving to larger bounds is therefore lower than fresh
target acquisition.  **Do not launch a larger #561 tuple from this lane.**

## Primary sources checked

- Live statement and listed cases: https://www.erdosproblems.com/561
- Burr–Erdős–Faudree–Rousseau–Schelp (1978), original paper scan:
  https://combinatorica.hu/~p_erdos/1978-38.pdf
- Győri–Schelp (2002), DOI:
  https://doi.org/10.1016/S0012-365X(01)00238-2
- Yen-Jen Cheng (2010), thesis PDF:
  https://tdr.lib.ntu.edu.tw/jspui/bitstream/123456789/10630/1/ntu-99-1.pdf
- Davoodi–Javadi–Kamranian–Raeisi, arXiv:2111.02065:
  https://arxiv.org/abs/2111.02065
- Fu–Luo–Ni, arXiv:2606.04439v3 (4 July 2026):
  https://arxiv.org/html/2606.04439v3

All were checked on 2026-08-03.  The 2026 v3 restriction is important: its
title and main theorem concern *uniform* star forests, unlike the arbitrary
nonuniform formula in #561.

## Reproduction

From the repository root, using the campaign virtual environment:

```powershell
.\.venv\Scripts\python.exe research/full_solution_scout/erdos561_theory_construction_max_2026-08-03/construction_sweep.py --max-bound 14 --max-targets 20
.\.venv\Scripts\python.exe research/full_solution_scout/erdos561_theory_construction_max_2026-08-03/stochastic_construction.py --target-index 0 --n-min 10 --n-max 10 --restarts 120 --steps 700 --seed 5610817
.\.venv\Scripts\python.exe research/full_solution_scout/erdos561_theory_construction_max_2026-08-03/verify_obstruction.py
```

The stochastic run is deterministic for the recorded Python, NetworkX, and
solver environment, but it is a search pulse rather than a completeness
certificate.

