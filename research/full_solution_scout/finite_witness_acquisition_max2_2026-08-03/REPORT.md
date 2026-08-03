# Finite-witness acquisition sweep 2 — 2026-08-03

## Executive decision

No candidate found in this sweep justifies a long compute campaign aimed at a
full Erdős resolution within one week.  The strongest bounded launch was on
Problem 149.  It produced a clean new small-order boundary—no counterexample
exists on at most 11 vertices in the first open degree case—but no signal that
the full conjecture is false.  Stop #149 here.  Do not scale to order 12 without
a new structural reduction comparable to the order-11 compatibility lemma.

The ranked acquisition result is:

1. **#149, strong chromatic index:** best finite refuter and best verifier;
   bounded order-11 gate completed negatively, then killed.
2. **#701, Chvátal's downset conjecture:** an excellent finite refuter in
   principle, but certified through seven ground elements and first-open order
   eight is not a one-day unstructured search.
3. **#1160, maximum number of groups at powers of two:** a finite numerical
   refuter exists in principle, but the relevant exact group counts are the
   hard mathematical object; no one-week acquisition gate was found.

This ranking is about probability of a **full** resolution, not mathematical
importance.  All three conjectures are strongly supported and classical.  The
recommendation after the completed #149 pulse is therefore to return resources
to fresh target acquisition, not to continue down this list by default.

## Scope and exclusions

The refreshed 554-candidate pool in
`research/full_solution_scout/pool-2026-08-03.json` was used.  Active #151 and
#982, published #719, closed/demoted #583, #580, and every campaign-touched
problem were excluded.  The screen was counterexample-first: a finalist had to
have a finite object that, after priority checking, would resolve the faithful
public statement rather than merely one parameter case.

## 1. Problem 149 — strong chromatic index

### Faithful quantifiers and decisive witness

For every finite simple graph `G` of maximum degree `Delta`, the public entry
asks whether

`chi'_s(G) <= (5/4) Delta^2`,

where `chi'_s(G) = chi(L(G)^2)`.  A decisive negative witness is one explicit
finite graph `G` for which the exact chromatic number of `L(G)^2` exceeds the
bound.  At `Delta=4`, this means an explicit graph not strongly 20-edge-
colourable.

### Fresh priority/frontier audit

- The live page is open and was last edited **10 April 2026**.  It records the
  sharp `Delta<=3` result and the Huang--Santana--Yu upper bound 21 for
  `Delta=4`, so 20 versus 21 is the first open degree case.
- Huang--Santana--Yu's paper was published **24 August 2018**.
- Searches through **3 August 2026** found July 2026 work on general strong
  edge-colouring and the strong clique index, but no claimed `Delta=4`
  settlement or counterexample.  In particular, arXiv:2607.17421 is an
  asymptotic general bound and arXiv:2607.02698 concerns the clique index.
- The `C5` blow-up attains 20, which is positive evidence for sharpness.

Sources are itemised in `SOURCES.md`.  Database status was not treated as the
priority check by itself.

### Order-11 reduction

The first possible order is 11: a graph with at most 20 edges is trivially
strongly 20-edge-colourable by singleton colours.

At 11 vertices and 21 edges, a failure of 20-colourability would require all 21
edge-vertices of `L(G)^2` to have distinct colours.  Equivalently, `G` would
have no two strongly independent edges.  The Chung--Gyárfás--Tuza--Trotter
edge theorem recorded on the live page gives such a pair once a maximum-
degree-4 graph has at least 20 edges, excluding this case.

At 22 edges the graph is 4-regular.  Define the compatibility graph `J` on
`E(G)`: two vertices of `J` are adjacent when the corresponding edges of `G`
form an induced matching.  Since `|E(G)|=22`, a strong 20-colouring exists if
and only if one can save two colours from the all-singleton colouring.  This
happens exactly when:

- `J` contains a triangle (one induced matching of size 3), or
- `J` contains a matching of size 2 (two induced matchings of size 2).

The converse is also exact: any 20-colouring saving two colours has either a
colour class of size at least 3 or two colour classes of size at least 2.
Therefore a counterexample has triangle-free `J` with matching number at most
1.  The edge theorem ensures `J` is nonempty, so `J` must be a star.

By relabelling, fix the star centre to the graph edge `01` and one compatible
leaf to graph edge `23`.  The exact SAT encoding imposes:

- simple 4-regularity on 11 labelled vertices;
- edges `01` and `23` present;
- the four cross-edges between `{0,1}` and `{2,3}` absent;
- for every two disjoint present graph edges other than `01`, at least one of
  their four cross-edges is present.

The last clause is exactly the assertion that every compatibility edge of `J`
involves `01`.

### Bounded launch result

`exact_149_n11_star_sat.py` generated a CNF with **583 variables and 2,016
clauses**.  Glucose4 and CaDiCaL 1.9.5 independently returned **UNSAT** in
0.081 and 0.113 seconds.  The discovery Glucose text trace is invalid
(`drat-trim` reported no conflict) and is explicitly excluded from the core
manifest.  It must not be cited as a certificate.

The root campaign regenerated the same hash-pinned CNF with pinned CaDiCaL
1.9.5 proof logging.  Its 226,875-byte DRAT certificate has SHA256
`32c57573f9b6c0ae911cbf95439405e2ee26dfaa0243a2edeb5a5e016047963f`
and was **VERIFIED** by a pinned Linux `drat-trim`.  Conversion produced the
1,384,084-byte LRAT certificate with SHA256
`e1e63c016f3f5b20fa55a5baa1b3419c80149dec06695930151e632def91531a`,
independently **VERIFIED** by native Windows `lrat-check` (10,972 additions,
10,951 deletions, maximum 2,016 live clauses).  Exact metadata are in
`CERTIFICATION.json`.

Separately, the campaign root reports checking all **265 connected 4-regular
graphs on 11 vertices** from an independent catalogue route; every graph had
a matching-of-size-2 compatibility certificate.  This agrees with the SAT
result.  That catalogue and its hashes live outside this subtask, so its report
should be cited from the root campaign record rather than this manifest.

The stochastic 2-switch pulse evaluated 379,911 proposals, found no target
star, and recorded a closest graph with an independently checked explicit
20-colouring.  It is corroboration only; the exact SAT gate is the substantive
result.

### Exact claim boundary

The checked certificate and independent catalogue route support:

> Every simple graph on at most 11 vertices with maximum degree at most 4 is
> strongly 20-edge-colourable.

The 21-edge case is analytic; the only 22-edge shape is excluded by a
DRAT/LRAT-certified UNSAT result and an independent complete catalogue
traversal.  Before a public theorem announcement, package the exact checker
commands/container identity and the catalogue input provenance alongside this
mathematical reduction.

This does **not** solve #149, does not verify order 12, and does not imply that a
minimal counterexample is regular at larger orders.

### Hard kill and next move

The precommitted kill fires now: the first possible order has been eliminated
without a near-witness, while the global conjecture is classical and strongly
supported.  Do not launch generic order-12 graph generation or 20-colouring.
Reopen only if a theorem forces a minimal counterexample into a sharply
specified order/degree/criticality class, or if a near-21 construction appears
from independent theory.

## 2. Problem 701 — Chvátal's downset conjecture

### Faithful quantifiers and decisive witness

For every finite ground set `X` and every downset `F` of subsets of `X`, there
is an element `x` such that every intersecting `A subseteq F` satisfies

`|A| <= |{S in F : x in S}|`.

A full negative resolution is one explicit finite downset `F` and one
intersecting subfamily `A` whose size exceeds every star of `F`.  Verification
is direct twice over: check downward closure/intersection/star counts, then
independently solve maximum independent set in the disjointness graph of `F`.

### Current frontier and fresh search

- The live page remained open when crawled in June 2026.  Its May 2026 forum
  activity concerns the silent finite-ground-set convention, not a finite
  solution.
- Eifler--Gleixner--Pulaj's exact rational integer-programming framework
  proves the conjecture for ground sets of at most **seven** elements.  The
  preprint is dated **5 September 2018** and the safe-framework publication is
  from 2022.
- Frankl--Kupavskii (2023) prove the covering-number-two case.
- Chang--Liu--Liu, arXiv:2606.32024 dated **30 June 2026**, prove a related
  sharp spectral correlation inequality, showing current specialist activity
  but not the full conjecture.

Thus the first finite ground-set order is 8, not 6.  An unstructured search
over all downsets is far outside a one-day gate.

### One-day probe and hard kill

Only launch if the published certified framework yields a symmetry-reduced,
certificate-producing order-8 subproblem estimated below one CPU-day.  A
useful probe would target a mathematically justified minimal-counterexample
class and require an explicit downset hit to continue.  Kill immediately if
the proposal is merely enumeration of Dedekind families or reproduces a class
covered by the 2018/2022 or 2023 results.

No compute was launched here.

## 3. Problem 1160 — group-count maximum at powers of two

### Faithful quantifiers and decisive witness

Let `g(n)` be the number of isomorphism classes of groups of order `n`.  The
entry asserts: for every `m` and every `n <= 2^m`, `g(n) <= g(2^m)`.
A decisive negative witness is a concrete pair `(n,m)` together with exact,
independently certified counts satisfying the reverse strict inequality.

### Current frontier and fresh search

- The live page is open and was last edited **26 January 2026**.  No solution
  is claimed in its comments.
- The corrected exact value at order 1024 is 49,487,367,289 (Burrell's 2021
  correction, discussed in the 2024 computational-group-classification
  survey).
- Exact numbers for `2^m` are tabulated through `m=10`; the full number for
  order 2048 is unknown.  The survey gives only a very large exact subclass
  count at 2048.
- Databases cover most orders up to 20,000, but database lookup is not an
  independent mathematical certification of every count and does not remove
  the unknown power-of-two denominator beyond 1024.

### One-day probe and hard kill

A safe probe would ingest two independent exact group-count sources, compare
every common order against the relevant power-of-two count or rigorous lower
bound, and stop immediately unless an actual numerical crossover appears.
The hard kill is the present situation: the known power-of-two counts dominate
the tractable exact range, while computing the first missing counts is itself a
major group-enumeration project.  No compute was launched.

## Rejected after fresh checking

- **#65:** the live page explicitly says the surviving cycle-length minimizer
  question cannot be resolved by a finite computation; it is asymptotic and
  currently active.
- **#389:** a fixed failed `n` would require proving nonexistence for all `k`,
  not a finite witness; the live page explicitly labels it non-finite.
- **#470:** one odd weird number would settle the first displayed question,
  but the same database entry also asks about infinitely many primitive weird
  numbers.  Moreover Fang's 2022 search excludes odd weird numbers below
  `10^21`.  It is not a clean full-entry one-week target.
- **#686:** current 2026 forum activity is already attacking `N=4` across
  several `k`; proving nonrepresentation is not a direct finite witness and
  priority collision is high.

## Recommended bounded launch

The one recommended bounded launch from this sweep was the exact #149 order-11
star-compatibility SAT gate.  It is complete and negative.  The correct next
allocation is **fresh target acquisition**, with the same full-resolution and
priority filters, rather than an automatic order-12 continuation or an
unstructured #701/#1160 computation.
