# Successor audit of the sigma=19 hunt

**Date:** 2026-08-03.  **Status:** the persisted blocks and their variable
mapping pass; the hunt has been resumed with a hardened wrapper.  This note
makes no solution claim.

## 1. Exact persisted-state replay

`blocks_pure19.jsonl` at takeover contained 512 records and had SHA-256

`B0A854F41974C2FE740E5B9B80425D7238C07ADB3B292A32AB50854DCF15D9F1`.

The independent standard-library audit `audit_pure19_blocks.py` checks every
record from first principles.  All 512 records are simple alternating
16-cycles.  For each record, its clause is exactly the disjunction of the 16
negated incidence variables on the stored cycle.  No record or clause is
duplicated, and no malformed vertex or literal occurs.  The machine-readable
result is `audit_pure19_blocks.json` (`status: PASS`).

The variable reconstruction does not rely on a discovery model.  The live
`sat_search.build(19)` allocates the 19*57 variables `X[p,j]` first, giving

`X[p,j] = 1 + 57p + j`.

The `U` constraints make used lines a prefix, and `U[j]` forces line `j` to
have at least three points.  Therefore line vertex `19+j` in a stored cycle
really is original line `j`.  A live build independently confirmed all 1,083
`X` identifiers, 85,498 total variables, and 381,346 base clauses.

Each block is semantically safe even without trusting that it was discovered
from a SAT model: it only says that at least one incidence of a displayed
simple C16 must be absent.  Thus it is satisfied by every C16-free graph.

## 2. Hostile encoding check

The base variables and clauses encode:

- at most 57 used lines, from the linearity pair budget
  `3m <= binom(19,2)`;
- every point degree at least three and every used line size at least three;
- used-line prefix padding;
- exact pair-collinearity and triple-collinearity definitions;
- linearity (so no C4);
- the exact quadrilateral obstruction (so no C8);
- row/column double-lex symmetry breaking.

The C8 clause is exact under linearity: four cyclic collinear point pairs
give four distinct line vertices unless some consecutive point triple lies
on one line; the four positive triple literals are precisely those
degeneracy excuses.  Conversely a simple incidence C8 has no such excuse.

The symmetry constraints do not interact with the later blocks in a way that
can remove a survivor.  Every C16/C32-free incidence structure satisfies
every cycle block under every labeling.  Hence its canonical double-lex
representative remains feasible if the structure exists.

The cycle enumerator in the hardened wrapper roots each cycle at its unique
minimum-labeled vertex, explores all simple paths of the target length, and
uses only a safe shortest-distance prune.  It deduplicates by undirected edge
set rather than merely by vertex set.

## 3. Correction: total-order range

The handover's `38 <= n <= 50` and LEDGER Entry 13's `38..54` are both
unsupported carryovers from the earlier `sigma <= 15` lane.  The actual
sigma=19 encoding has

`M = floor(binom(19,2)/3) = 57`,

so the safe total-order range of a survivor is **38 through 76**, not 50 or
54.  The lower endpoint uses the already certified statement that each side
of a bipartite minimum-degree-three C4/C8-free graph has at least 19
vertices; the upper endpoint is 19+57.

This correction does not weaken the counterexample implication.  Every
bipartite cycle uses equally many vertices from the two sides, so a graph
with a 19-vertex side has no cycle longer than 38 regardless of its total
order.  Therefore C4, C8, C16, and C32 remain the only dyadic lengths that
must be excluded.

The 38-vertex `sigma19_model.json` construction is also **not new**.  The
root hostile priority audit found an exact isomorphism to Gordon Royle's graph
posted on MathOverflow on 2009-11-02.  The self-contained mapping and source
record are in
`root_independent_audit_2026-08-03/royle_2009_isomorphism.json`.  The search
phase transition remains useful computational calibration, but neither that
object nor its order can support a novelty claim.

## 4. Resumption and evidence classes

`pure19_hunt_hardened.py` resumes the same base CNF and saved blocks in one
incremental CaDiCaL instance.  It audits the block file before loading it,
fsyncs new blocks after every round, and writes an atomic status JSON.

- A survivor is frozen before any checks and then sent to the two existing
  raw-edge verifiers.  It is not published by the runner.
- Incremental UNSAT is labeled `SOLVER_UNSAT` and the exact final CNF is
  frozen.  A separately supervised command-line CaDiCaL replay must regenerate
  a uniquely named proof, and `drat-trim` must print `s VERIFIED`, before any
  report can call the result `CERTIFIED_UNSAT`.
- A timeout preserves all accumulated audited blocks and remains resumable.

The root audit additionally supplies independent checks of the static C8
equivalence, symmetry constraints, the sigma=19 model, and local DRAT tooling
under `root_independent_audit_2026-08-03/`.
