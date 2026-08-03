# Primary-source, live-priority, and target audit

**Date:** 3 August 2026.

## Original statement

The original source located in the Erdős archive is:

* P. Erdős, *Problems and results in combinatorial analysis*,
  <https://renyi.hu/~p_erdos/1976-35.pdf>, pp. 12–13 of the scan.

Erdős first recalls the Erdős–Goodman–Pósa graph result, then states that he
and Sauer conjecture the analogous assertion for an `r`-graph, using
edge-disjoint `K_{r+1}^r`'s and single `r`-edges.  The source explicitly says
that already `r=3` seems difficult.

The live problem page was checked on 3 August 2026:

* <https://www.erdosproblems.com/forum/thread/719>

It marked #719 open, contained no claimed partial or complete solution, and
showed only an unverified comment about a finite `n=6,r=3` computation.  This
is not proof of priority, so any complete result still requires a renewed
Scholar/MathSciNet/zbMATH and expert check.

## Modern literature boundary

The modern decomposition-number notation is standard.  Kang, Ni and Shan,
*Decomposing uniform hypergraphs into uniform hypertrees and single edges*,
Discrete Mathematics 344 (2021), 112454, define

```text
phi_r(G,H)=e(G)-(e(H)-1)p(G,H)
```

and emphasize that uniform-hypergraph decomposition numbers remain broadly
open outside special decomposing hypergraphs.  Their result concerns
hypertrees, not `K_{r+1}^r`, and does not resolve #719.

## Smallest full-counterexample target

The smallest promising target beyond the now-certified `r=3,n=9` case is

```text
r=3, n=10.
```

The exact Turán input is published:

```text
T(10,4,3)=45,
ex_3(10,K_4^3)=C(10,3)-45=75.
```

The primary finite computation is R. G. Stanton and J. A. Bate,
*A computer search for B-coverings*, Lecture Notes in Mathematics 829
(1980), 37–50, MR 82h:05015.  Füredi's survey *What we know and what we do
not know about Turán numbers* explicitly records that Stanton–Bate established
the Turán construction at `n=10`.

Therefore an 82-edge 3-graph with packing number two would have

```text
phi(G)=82-3*2=76>75
```

and would disprove the universal conjecture outright.  This is why the bounded
computation in this directory targets a counterexample rather than another
finite positive verification.

## Search boundary

No announcement or paper claiming an `r=3,n=10` counterexample was found in
exact-phrase searches for the decomposition function, `K_4^3` packing, and the
Erdős–Sauer conjecture.  Search results instead led to the 2021 hypertree paper
and graph-only `H`-decomposition literature.
