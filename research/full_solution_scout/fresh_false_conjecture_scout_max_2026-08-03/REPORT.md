# Fresh finite-counterexample target scout — 3 August 2026

## Bottom line

One target passed the gate for a **bounded discovery pulse**, Erdős #583
(Gallai's path-decomposition conjecture).  It did not yield a counterexample,
and the pulse is now **closed under its precommitted kill rule**.  #583 is
demoted rather than abandoned: it should not receive more campaign compute
this week without a new structural construction or a genuinely different
solver that upgrades one of the density-correlated timeouts.  #628 is a technically clean reserve target but has low prior
probability and high current specialist activity.  #107 has a decisive finite
endpoint but fails the one-CPU-day and collision gates.

The most important campaign-infrastructure finding is independent of those
rankings: the pre-existing pool builder admitted only `status == "open"` and
therefore omitted the database's `falsifiable`, `decidable`, and `verifiable`
classes.  This systematically excluded many of the best finite-witness
problems.  The parent campaign agent owns the correction; this scout did not
edit `build_pool.py`.

All statements below distinguish public/source evidence from research
judgment.  Database status is treated as a lead, never as a priority proof.

## Candidate 1 — #583, Gallai path decomposition (bounded pulse promoted)

### Faithful quantifiers and decisive witness

**Statement.** For every finite connected simple graph `G` on `n` vertices,
the edge set of `G` can be partitioned into at most `ceil(n/2)` edge-disjoint
simple paths.

A single connected finite graph for which the minimum number of simple paths
in an edge partition exceeds `ceil(n/2)` disproves the full universal
statement, not merely a special case.

### Public evidence and priority audit

* The live [Erdős Problems #583 page](https://www.erdosproblems.com/583)
  labels the problem falsifiable and was last edited 1 April 2026.  It records
  no claimed complete solution.  This is status evidence, not proof of
  priority.
* Botler, Cano, and Sambinelli,
  [*On Computing the Path Number of a Graph*](https://doi.org/10.1016/j.entcs.2019.08.017),
  ENTCS 346 (2019), Theorem 1.2(i), computationally verified every connected
  graph of order at most 11.  Therefore the genuine first possible order is
  12.  Their theorem also covers bipartite graphs through order 16 and regular
  graphs through order 14.
* Zhang, Liu, and Hong,
  [*Gallai's conjecture for 3-degenerated graphs*](https://doi.org/10.1016/j.disc.2024.114057),
  Discrete Mathematics 347 (2024), proves the conjecture for connected
  3-degenerate graphs (with the tight exceptional graphs treated in their
  stronger floor-bound formulation).  Thus an order-12 counterexample has
  degeneracy at least four.
* The area is active: Chu, Fan, and Zhou,
  [*Gallai's conjecture and the path number of odd semi-cliques*](https://doi.org/10.1016/j.disc.2025.114725),
  and Chu and Wang,
  [*Path decompositions of Eulerian graphs*](https://doi.org/10.1016/j.disc.2025.114830),
  both appeared in the February 2026 issue of *Discrete Mathematics*.  They
  prove additional classes, not the full conjecture; their recency increases
  collision risk.
* The displayed code in Till Heller's
  [2024 blog computation](https://www.till-heller.de/blog/gallais-path-conjecture)
  is not by itself a certificate for the stated simple-path problem: its
  greedy walk does not track visited vertices, while its displayed ILP neither
  forces connected color classes nor ties every participating-vertex variable
  to an incident selected edge.  This does **not** reopen orders at most 11,
  because the independent 2019 theorem already closes them.
* The VibeMathed API snapshot generated 2 August 2026 contained no record for
  #583.  The local llm-hunter entry contained only a failed elementary attempt,
  not a claim.  Searches are non-exhaustive; private and unindexed work remains
  possible.

### Exact first probe and result

The probe works only at order 12 and rejects instances already covered by
sound published classes: connectedness, degeneracy at least four, maximum
degree at least six, nonplanarity, nonbipartiteness, nonregularity, and an
even-degree induced subgraph of maximum degree at least four.

The exact decision model represents each of the six allowed paths as a length
and a sequence of distinct vertices.  Consecutive active vertices must form a
graph edge, and every graph edge must occur as exactly one active step across
the six sequences.  A separate plain-Python checker validates every SAT
decomposition without trusting Z3's encoding.

Artifacts:

* `search_gallai_n12_random.py` — deterministic-seed restricted random probe;
* `erdos583_n12_random_seed58312026.json` — 373 graphs generated, 200
  passed the published-class filters, 114 returned SAT decompositions that the
  independent checker accepted, and 86 reached the deliberately short
  1.5-second solver timeout.  There was no UNSAT candidate.  The unknowns are
  strongly concentrated at high density and are treated as encoding timeouts,
  not counterexample evidence;
* `search_gallai_n12_clique_extensions.py` — the eleven isomorphism types
  obtained by attaching one nonisolated vertex to the tight base `K11`;
* `erdos583_n12_k11_extensions.json` — two types returned checked SAT within
  20 seconds each and nine timed out; no UNSAT candidate.  A timeout is an
  encoding-performance observation, not mathematical evidence;
* `search_gallai_small.py`, `erdos583_n7.json`, and `erdos583_n8.json` — an
  independent simple-path exact-cover smoke test over 853 and 11,117 graphs.
  These reproduce already-published small-order territory and are not new
  results.  The order-9 run was stopped immediately when the 2019 theorem was
  located.

### Two-checker plan if a candidate appears

1. Preserve the graph both as a canonical graph6 string and an explicit edge
   list; check connectedness, order, simplicity, and isomorphism-independent
   hashes.
2. Re-encode the claim using a separately written CNF positional-path model,
   obtain an UNSAT proof (DRAT/LRAT), and verify that proof with an independent
   proof checker.  The current Z3 model is discovery-only for an UNSAT answer.
3. Independently enumerate all simple paths and solve bounded exact cover with
   a different branching implementation where the candidate's density makes
   that feasible.  Agreement of two implementations is still secondary to the
   checked CNF proof.

### One-CPU-day estimate and kill criterion

**Evidence.** The 200 accepted-instance pulse took 443 seconds.  Easy SAT
instances often took below 1.5 seconds; 86 denser instances hit that cap, and
dense structured cases often hit the separate 20-second cap.

**Judgment.** One CPU-day can test roughly `10^4–10^5` diversified order-12
instances if easy SAT witnesses dominate, but cannot exhaust the order-12
space.  Expected value is moderate only as a candidate hunt.

**Kill/demotion rule.** Demote after the structured `K11`-extension family and
the bounded 200-instance restricted random pulse if there is no independently
confirmed UNSAT graph and no timeout that survives a materially different
solver for at least 30 seconds.  Do not turn solver timeouts into a long
exhaustion project this week.

## Candidate 2 — #628, Erdős–Lovász Tihany (reserve; not launched)

### Faithful quantifiers and decisive witness

**Statement.** For every finite graph `G` with `chi(G)=k` and no `K_k`, and
all integers `a,b >= 2` with `a+b=k+1`, there are vertex-disjoint subgraphs of
chromatic numbers at least `a` and `b`.

A `K6`-free double-critical 6-chromatic graph is a full counterexample for
`(a,b)=(2,5)`: for every edge `uv`, `G-u-v` is 4-colorable, so no subgraph of
chromatic number at least two can be disjoint from a 5-chromatic subgraph.  It
satisfies the required `omega(G)<chi(G)` hypothesis by the explicit `K6`-free
condition.  This is the clean first open polarity of the `(2,k-1)` case.

### Evidence, exact first probe, and verification plan

* The [#628 discussion/page](https://www.erdosproblems.com/forum/thread/628)
  records the faithful Tihany statement and no complete claim.
* Kawarabayashi, Pedersen, and Toft's
  [double-critical graph work](https://arxiv.org/abs/0810.3133) implies a
  noncomplete double-critical 6-chromatic graph is 6-connected; their paper
  also notes that such a graph has at least 11 vertices.  Known structural
  results give strong degree constraints.
* Song's very recent
  [even-hole-free result](https://arxiv.org/abs/2607.20376) (22 July 2026)
  proves Tihany for another large class.  This is positive progress and a
  strong current-collision signal, not evidence for a counterexample.

The first probe would be a graph-CEGAR search on 11 vertices for a K6-free,
6-chromatic double-critical graph, with explicit 4-color witnesses for every
edge deletion.  Candidate checking would use two independent chromatic-number
engines, exhaustive K6 checking, validation of every edge-deletion coloring,
and a separately checked SAT UNSAT certificate for non-5-colorability.

**One CPU day:** enough for a serious order-11 CEGAR pulse, not enough to infer
nonexistence without a global certificate.  **Kill:** if diversified order-11
searches produce no candidate, do not expand to order 12 this week.  **Judgment:**
the conjecture is famous, strongly believed, and currently active; this is a
reserve lane rather than a top-probability attack.

## Candidate 3 — #107, Happy Ending (rejected at time/collision gates)

### Faithful quantifiers and decisive witness

Let `f(r)` be the least `N` such that every `N` points in the real plane in
general position contain `r` points in convex position.  The conjecture is
`f(r)=2^(r-2)+1` for every `r`.  A realizable 33-point configuration in general
position with no seven points in convex position would prove `f(7)>33` and
therefore disprove the full formula.

### Evidence, first probe, and why it is rejected

The first open case is `f(7)=33`.  Dumitru's
[*Notes on the 33-point Erdős–Szekeres problem*](https://arxiv.org/abs/2512.24061)
(30 December 2025) already gives a triple-orientation SAT encoding, checked
UNSAT certificates for anchored subfamilies, and reports heavy-tailed runs.
That is direct active collision at the exact endpoint.

The exact counterexample-first probe is to seek a SAT chirotope at order 33 and
then realize it by rational coordinates.  A chirotope alone is insufficient:
nonrealizable oriented matroids do not give point configurations.  The two
checkers would be (i) exact rational determinant/general-position checks plus
exhaustive seven-subset convexity checks, and (ii) an independent orientation
and forbidden-convex-seven checker.

**One CPU day:** the public paper reports anchored subcases with weeks-scale,
heavy-tailed behavior, so a one-day clone has poor odds.  **Kill:** immediate
for this campaign unless a genuinely new realization-aware encoding or
published near-SAT model is acquired.  **Judgment:** decisive endpoint, but
bad collision and compute economics.

## Status-coverage audit

The local snapshot's special finite-facing classes are not synonyms for
settled problems:

* `falsifiable` means a finite counterexample can settle the universal claim;
* `decidable` means a finite procedure is known in principle;
* `verifiable` means finite verification could establish the requested claim.

Filtering exclusively on literal `open` therefore biased the campaign away
from its counterexample-first objective.  The omitted lists also contain many
bad targets — e.g. enormous verified ranges, famous active conjectures, or
astronomical finite spaces — so the correction must feed the same literature,
collision, one-day, and two-checker gates rather than auto-promoting them.

## Recommendation

The #583 pulse is closed.  Ranked redeployment is:

1. Re-run target acquisition over the corrected finite-facing status pool,
   with the same priority/collision and one-day gates.  This is more likely to
   uncover a better endpoint than scaling #583 random search.
2. Keep #628's order-11 double-critical CEGAR specification ready as the next
   concrete finite attack only if the corrected sweep finds nothing better.
   Its famous/active status makes it a reserve, not an automatic launch.
3. Do not allocate this week's compute to #107 without a new realization-aware
   encoding; the public order-33 SAT effort already occupies that exact lane.

`PULSE_CLOSURE.json` records the exact close decision and result counts.
