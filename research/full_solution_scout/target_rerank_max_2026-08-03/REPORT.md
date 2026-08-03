# Independent target rerank for a complete first-credit result

**Cutoff:** 3 August 2026, after the #151 hostile audit and the complete
order-22 cubic census for #64.
**Objective:** maximize the probability of a first, complete, independently
checkable Erdős-problem resolution within approximately one month.
**Scope:** existing campaign targets only.  This report starts no search and
makes no novelty or solution claim.

## Executive decision

The campaign does **not** currently have a near-complete full-resolution lane.
Several packets are near completion of a *finite case* or a *restricted
class*, but their remaining quantifier is still most of the public problem.

The best existing target remains **#64**, narrowly ahead of **#151**.  The
reason is not accumulated finite coverage.  It is that #64 has a precise,
small, terminal certificate route at the first order not already exhausted:
a marked cubic graph on 24--30 vertices satisfying the suppression criterion
would immediately compose into a full counterexample.  No other active lane
has an equally crisp next experiment whose positive output ends its whole
problem.

The single highest-leverage next action is therefore:

> Run a candidate-first, checkpointed marked-edge search for a connected
> simple cubic graph `H` of order 24, 26, 28, or 30 with a distinguished edge
> `e` such that `H-e` has no `C4`, `C8`, or `C16`, and `e` lies in no `C3`,
> `C7`, or `C15`.  Subdivide `e`, take two copies, and join the new degree-two
> vertices by a bridge.  Any hit is a full definition-level counterexample to
> #64.  Verify a hit with two independent raw-edge cycle enumerators before
> any announcement.

This is not another cubic census.  It is a direct existential search at the
first open marked order, using the exact theorem-facing criterion.  The
complete order-22 census supplies the lower boundary and validates the
checker pipeline.

Keep #151 as a bounded maintenance lane (roughly the existing 15--25% option),
not the dominant allocation, unless it produces a checked global candidate,
a genuinely global CEGAR transition, or a complete protected-core closure
with an ambient bridge.

## Ranking

The probability bands below are subjective campaign odds for a **complete,
first-credit result within one month**, not statistical confidence intervals.
They deliberately include collision risk and the probability that the target
is false or has a short proof, not just mechanical verifiability.

| Rank | Target | Subjective one-month first-credit probability | Terminal route | Allocation |
|---:|---|---:|---|---|
| 1 | #64 | 1--4% | One marked cubic graph gives a bridge-composed counterexample | One bounded direct marked-edge cycle |
| 2 | #151 | 0.5--3% | One graph with `beta(G)<H(n)`; current concrete target `(50,11)` | Maintenance plus candidate verification |
| 3 | #561 | 0.3--1.5% | One below-formula arrowing host for a cleared nonuniform star-forest tuple | Reserve; only a priority-cleared new tuple |
| 4 | #203 | 0.2--1% | One finite affine-fibre cover and CRT integer `m` | Park until a new exact recursive identity appears |
| 5 | #719 | 0.1--0.8% | One 10-vertex 82-edge 3-graph with packing number two | Park; candidate-first only |
| 6 | #982 | 0.1--0.7% | Exact strictly convex 10-point local-four-distance set | Park pending algebraic-realizability mechanism |
| 7 | #128 | 0.05--0.5% | Finite counterexample or proof of the full paired-type quotient inequality | Theory reserve only |
| 8 | #149 | 0.03--0.3% | A `Delta<=4` graph with `chi(L(G)^2)>=21` | Stop order-by-order continuation |
| 9 | #742 | 0.01--0.2% | A 157-edge order-25 diameter-2-critical graph, or full finite exhaustion | Background certificate maintenance only |

The exact endpoints are not decision-bearing.  The stable conclusions are:

1. #64 and #151 are the only existing targets that justify nontrivial option
   value.
2. #561 and #203 are credible reserves, but current collision risk and null
   evidence prevent promotion.
3. #719, #742, and #128 are **not near-complete** despite strong finite
   packets.
4. The portfolio probability remains low enough that fresh target acquisition
   should continue in parallel rather than converting either top lane into an
   indefinite siege.

## 1. Erdős #64 -- first

### Why it ranks first

One finite graph of minimum degree at least three with no power-of-two cycle
settles the full universal conjecture negatively.  Verification is direct and
small: enumerate simple cycles of lengths `4,8,16,...` up to the graph order.
The proposers are recorded as expecting a negative answer, so the answer prior
is materially less hostile than for most famous universal conjectures.

The campaign has proved the exact bridge-block reduction.  If `H` is cubic
and `e` is marked, subdividing `e` produces a one-defect block with no dyadic
cycle exactly when:

1. every dyadic cycle of `H` contains `e`, equivalently `H-e` has none; and
2. `e` lies in no cycle of length one less than a power of two.

At orders 24--30 this becomes the finite condition displayed in the executive
decision.  The complete canonical census already proves that every one of the
7,319,447 connected cubic graphs of order 22 has empty dyadic edge core, with
an independent literal replay.  Hence 24 is the honest first open marked
order, not an arbitrarily selected search size.

### Hidden fatal gap

There is no surviving marked edge yet.  The order-22 result is negative
evidence for this construction, not evidence that higher orders are close.
Eight other mechanisms--generic SAT, necklace amalgams, line-tree graphs,
voltage covers, Cayley graphs, central lifts, and two kinds of cubic
sampling--also failed.  The strongest Cayley examples merely postpone the
first dyadic cycle to 32.  A larger ordinary cubic census would therefore be
poor allocation; the next cycle must search the marked criterion directly.

### Kill criterion

Run one bounded multi-order candidate-first cycle with atomic checkpoints and
two genuinely different search mechanisms (for example lazy cycle separation
and a construction/optimization engine).  Renew only on:

- a raw marked survivor;
- a recurrent state with a nonempty dyadic core that survives the Mersenne
  filter; or
- a theorem that compresses an infinite structural class.

Stop this mechanism if all tested orders return only empty cores and no
post-Mersenne survivor, or if both engines reproduce the already observed
two/three-cycle empty-intersection obstruction without a new bridge.  Do not
replace a failed existential search with an order-24 exhaustive census.

**Evidence:**
`erdos64_long_horizon_max_2026-08-03/BRIDGE_BLOCK_REDUCTION.md`,
`erdos64_nonhamiltonian_cubic_max_2026-08-03/FULL_N22_SUCCESSOR.md`, and
`erdos64_nonhamiltonian_cubic_max_2026-08-03/SUCCESSOR_RESULTS_INDEX.md`.

## 2. Erdős #151 -- second, maintenance rather than siege

### Why it remains high

Erdős explicitly doubted the conjecture, a finite counterexample would be a
complete disproof, and this lane has produced the campaign's strongest new
mathematics: the independent-set recurrence, verification through order 39,
Folkman reduction, order-41 class exclusions, and a uniform local triangle
threshold.  These are genuine information gains, not solver telemetry.

The `(50,11)` target is also crisp: a checked graph with `beta<=10` is a full
counterexample.  The maximal-edge matching and vertex-partition separators
are sound global constraints, and the protected-core work has certificate
grade subcases.

### Hidden fatal gaps

The latest hostile audit materially lowers the ranking:

- the general fractional-cover program handles only the pure-triangular
  face; maximal edges remain unpaid;
- the anchor lower bounds and advertised partitions were invalid and were
  withdrawn;
- all three order-50 CEGAR workers stopped without SAT, UNSAT, or result
  files after thousands of local cuts;
- 11/34 protected type-5 cases is not an exhaustive graph class, and even
  full 34/34 closure needs an ambient bridge;
- the positive asymptotic route meets leading-constant Erdős--Rogers/Ramsey
  questions rather than one missing elementary estimate.

Thus #151 has the most theorem momentum but not the highest terminal-result
probability.  More local lemmas can be valuable while leaving the probability
of a full solution nearly unchanged.

### Kill/renew criterion

Maintain only the exact queues already increasing certified coverage.  Renew
a dominant allocation only after one of:

- a graph passing both definition-level `beta` and arrowing checkers;
- a CEGAR model reaching genuinely global cuts with a decreasing violation
  metric;
- complete protected-core closure plus a proved implication to an ambient
  counterexample class; or
- a uniform theorem that pays for maximal edges and avoids unknown Ramsey
  constants.

If work continues to close only local signatures, surface strata, or finite
Ramsey intervals, publish it at exact scope and reallocate.

**Evidence:** `erdos151/ALLOCATION_CHECKPOINT.md`,
`erdos151/fable_symbolic_h_2026-08-03/ROOT_HOSTILE_AUDIT_SYNTHESIS_2026-08-03.md`,
and `erdos151/README.md`.

## 3. Erdős #561 -- best small-host reserve

A single graph with fewer edges than the conjectured size-Ramsey formula that
arrows one pair of star forests disproves the full formula.  The witness is
tiny and independently checkable by exhaustive two-colouring and subgraph
embedding.  The retreat of a June 2026 full-proof claim to uniform star
forests is a real uncertainty signal.

Against that, the campaign exhaustively found no counterexample for all
cleared two-component cases through formula value ten, and proved three exact
positive values.  Several apparently fresh small tuples were already in a
2010 thesis.  A current 2026 group works directly beside the boundary, so
first-credit risk is the worst among the top targets.

**Renew only** for a tuple first cleared against Cheng, the 1981/2002 results,
the 2025 paper, and every version of the 2026 preprint, together with a
principled reason a below-formula host should exist.  Kill that tuple after a
complete below-bound host census returns null with no structural obstruction
to the conjectured upper construction.

## 4. Erdős #203 -- exact certificate, but the current mechanism is spent

An explicit finite prime-fibre cover plus CRT reconstruction would settle the
existential question in full and is ideal for rapid independent verification.
The complete image-order-at-most-1000 census gives total reciprocal density
above one, so this is not a vacuous route.

The fatal gap is structural: robust phase optimization still leaves about
11% uncovered, and the projective, perfect-power, common-shear, composite
modulus, and non-affine escape routes were all reduced or obstructed.  The
Vela modulus is only a partial cover and has an explicitly certified prime
term.  The page also lists active workers.

**Renew only** on an exact mixed-shear recursion, variable-divisor identity,
or a fixed assignment whose independently sampled residual falls below the
predeclared threshold and exhibits an exact coset hierarchy.  Do not enlarge
another flat period/order bound.

## 5. Erdős #719 -- a finite theorem is not proximity

The order-nine instance is completely certified, but the public conjecture
ranges over all orders and uniformities.  At the first negative target
`(r,n,m,nu)=(3,10,82,2)`, the best retained 14-tetrahedron objects have packing
number eight, not two, and the exact static solver did not emit a first model.
The natural global completion inequality is exactly Tuza's conjecture on its
`r=2` slice, so it is not a short bridge.

**Renew only** on a checked 82-edge/packing-two candidate, or on a proof of
the 14-tetrahedron supersaturation bound followed by a realizable equality
classification.  Another positive finite order is not a full-solution signal.

## 6. Erdős #982 -- perfect leverage, expensive exactness

One strictly convex ten-point set with at most four distances from every
point would disprove the conjecture.  But all three campaign angles stopped:
orders eight and nine were prior art, the exact H8 relaxation has no strictly
convex realization, and retained order-ten colour patterns have rank-two EDM
residuals far from zero.  Even a numerical near-hit would still require exact
algebraic coordinates and strict-convexity certification.

**Renew only** when a symbolic rank-two/convex realization mechanism is
coupled directly to the pattern search.  Do not widen global colour counts or
continue unconstrained numerical polishing.

## 7. Erdős #128 -- important theorem lane, weak terminal route

The campaign has a human order-16 bridge and a substantive arbitrary-block
theorem on the balanced saturated boundary face.  However, the full boundary
requires a paired-type Hall/discrepancy inequality, while an exact weighted
Chvátal example refutes the intended symmetrization and lets the low-type mass
tend to zero.  Finite verification through order 16 gives no bounded first
counterexample target.

**Renew only** on a proof or counterexample to the full paired-type quotient
inequality, or a stability theorem that actually forces its hypotheses.
Further local alpha/degree constants do not change full-resolution odds.

## 8. Erdős #149 -- excellent machinery, hostile answer prior

A `Delta<=4` graph with strong chromatic index at least 21 would be a perfect
finite disproof.  The campaign has instead exhaustively verified every graph
through order 16, across millions of canonical graphs and independent
replays, with no candidate.  The conjectured `C5` blow-up is a sharp equality
construction, and current evidence points toward truth rather than a small
counterexample.  Order 17 is mechanically specified but is another bounded
positive frontier, not a terminal route.

**Kill order-by-order enumeration.**  Reopen only for a construction or
criticality theorem that predicts a 21-chromatic line-graph square, not merely
because the next catalogue is available.

## 9. Erdős #742 -- decisive if SAT, but nowhere near exhaustive

The candidate is exceptionally easy to verify, and the published theory
reduces the conjecture to a finite check.  But the remaining finite range is
enormous.  The fixed-order-five certificates cover symmetry classes, not the
unrestricted/asymmetric order-25 search; three fixed-15 partitions timed out;
the unrestricted candidate search's best graph still had 25 removable edges.
The stronger nonbipartite bound in the literature also points away from a
157-edge counterexample.

**Keep certificate maintenance only.**  Renew full-resolution effort only
for a definition-level SAT graph or a new structural theorem compressing the
asymmetric order-25 space.  Completing another automorphism class does not
materially alter the full-problem probability.

## Demotions not worth reviving

- **#583:** all former timeout signals disappeared under an exact linear-
  forest encoding; the strongest structured and random cases were SAT.
- **#701:** order eight is prior art, and order nine is an unstructured
  Dedekind-family problem without a negative signal.
- **#628:** the proposed orders 11 and 12 were already covered in 2010/2015.
- **#939:** an `r=4` witness addresses only the existence subquestion, not the
  separate finiteness question in the entry.
- **#97:** numerical zeros failed convexity/distinctness and a competing
  nine-point programme creates collision risk.

## Portfolio recommendation

Allocate one main research slot to the direct #64 marked-edge search, one
bounded maintenance slot to #151 only while an exact coverage metric rises,
and keep at least one slot on fresh target acquisition.  Do not run #719,
#742, #128, or #149 merely because their next finite case is well specified.
Well-specified continuation is not the same thing as a plausible terminal
result.

Immediately before promoting any hit, rerun the live problem page, comments,
VibeMathed/AI-claim index, exact-phrase literature search, and relevant 2026
repositories.  The current priority judgments rely on same-day primary-source
audits already preserved in each packet, but they are not permanent priority
guarantees.
