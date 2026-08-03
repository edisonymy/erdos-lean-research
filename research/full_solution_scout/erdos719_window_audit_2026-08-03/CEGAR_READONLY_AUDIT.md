# Read-only audit of the prepared exact-64 CEGAR

**Audited file:** `research/full_solution_scout/erdos719_exact64_codex/search_exact64.py`
**Verdict:** **PASS; no production-blocking clause or oracle issue found.**

No modification was made to that file or its run directory.

## Clause polarity

The variables `c_e` mean “triple `e` is missing.”  If the oracle finds four
present, edge-disjoint tetrahedra, all 16 variables on their edge union are
false in the current model.  The added clause is

```text
OR_{e in the 16-edge union} c_e.
```

The implementation returns positive literals `edge_index+1`, verifies that
the 16 edge IDs are distinct, asserts that none is missing in the violating
model, appends exactly that positive clause, and adds it to the live solver.
The direction is correct: the current model violates the cut, while every
future model must delete at least one edge of that particular four-packing.

Journal replay regenerates each clause from the stored tetrahedron indices and
rejects a polarity/content mismatch.

## Packing oracle

`present_tetrahedra` includes a four-set exactly when none of its four triple
IDs is in the missing set.  `find_packing_four` recursively chooses four such
tetrahedra whose 84-bit edge masks are disjoint.  Mask-disjointness is exactly
edge-disjointness of the `K_4^(3)` copies.  Its only pruning condition is the
sound “too few candidates remain” bound, so a `None` return is exhaustive.

In addition to the built-in self-test, a separate 200-trial randomized
differential check compared its result with direct enumeration of all
four-tuples of present four-sets using the independent condition
`|A intersect B|<=2` for every pair.  All 200 trials agreed.  Every returned
packing also generated a 16-literal clause violated by the sampled exact-20
complement.

## Nonblocking operational caveat

`--time-limit-seconds` is checked between calls to `solver.solve()`, not inside
a solve call.  It is therefore a soft invocation limit rather than a hard wall
clock limit; a difficult final SAT/UNSAT call can overrun it.  This does not
affect clause validity, candidate correctness, or resumability, and it need
not block a deliberately supervised launch.  The script correctly labels an
incremental UNSAT response `UNSAT_NO_CERTIFICATE` and makes no proof claim.
