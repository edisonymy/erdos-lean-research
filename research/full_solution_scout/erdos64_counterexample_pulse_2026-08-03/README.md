# Erdős #64: bounded order-32 counterexample pulse

**Date:** 3 August 2026
**Outcome:** no counterexample; lane stopped at its precommitted renewal gate.

This directory records a candidate-first attempt to disprove the
Erdős--Gyárfás conjecture.  It is exploratory evidence, not a theorem or a
new finite-order exclusion.

## Claim boundary

Erdős #64 asks whether every finite graph of minimum degree at least three
contains a simple cycle whose length is a power of two.  A single graph with
no such cycle would settle the problem negatively.

No such graph was found here.  Every retained best graph has minimum degree
three and no 4- or 8-cycle, but an independent definition-level checker finds
both a 16-cycle and a 32-cycle in each one.

## Why this pulse was run

The live problem page still described the conjecture as open on 3 August
2026, and records that Erdős and Gyárfás themselves expected a negative
answer.  Public work already reports general exclusions through order 31,
heuristic AlphaEvolve searches through order 40, and a much larger bound in
the cubic-bipartite family.  This pulse therefore targeted only two unresolved
Carr-shaped order-32 degree profiles:

```text
h=4: four independent degree-four vertices and 28 degree-three vertices
h=6: six independent degree-four vertices and 26 degree-three vertices
```

The search did not claim either profile was novel or exhaustive.

Relevant public records:

* <https://www.erdosproblems.com/64>
* <https://arxiv.org/abs/2605.22844>
* <https://github.com/ArjunBalaji79/erdos-gyarfas-min-degree-3>
* <https://github.com/google-deepmind/alphaevolve_repository_of_problems>

## Search methods

### Exact lazy SAT pulse

The existing `general_cegar.py` model fixes the degree sequence, forbids every
4-cycle statically, and blocks each subsequently decoded forbidden cycle by
the negation of its complete edge set.  In the captured `h=6` run, 60,225
distinct 8-cycle clauses were learned in 600 seconds without reaching the
16-cycle stage.  The run timed out and has no mathematical conclusion.

### Degree-preserving annealing

`anneal_cycles.py` is a separate stochastic witness generator.  It uses
degree-preserving two-switches, exact simple-cycle counts at lengths 4 and 8,
and a lazy penalty family made from fully decoded 16-cycle witnesses.  It
writes a candidate only after the existing independent cycle finder returns
no witness at lengths 4, 8, 16, and 32.

Primitive checks passed:

```text
verify_graph.py --self-test: PASS (K4, Petersen, C7)
cycle_count(K4,4)=3
cycle_count(C8,8)=1
batch collector finds the unique C16 in C16
```

The five-second smoke run reduced an initial `h=4` seed to a graph with
exactly one 8-cycle and no 4-cycle.  That positive near-miss justified two
bounded 300-second waves.

The first, one-witness-at-a-time wave repeatedly reached `C4=C8=0`, then
learned 70, 1,037, and 801 distinct 16-cycle witnesses in its three runs.
None reached a 16-cycle-free graph.

The corrected final wave added 64 distinct exact 16-cycle witnesses whenever
a state survived all current penalties:

| file | profile | exact-check events | learned `C16` blocks | final live blocks |
|---|---:|---:|---:|---:|
| `best_batch_h4_a.json` | `h=4` | 13 | 832 | 2 |
| `best_batch_h4_b.json` | `h=4` | 244 | 15,616 | 10 |
| `best_batch_h6_a.json` | `h=6` | 1 | 64 | 64 |

All three retained graphs have exact short-cycle score `C4=C8=0`.  The large
and continually replenished `C16` family is the observed obstruction.  No run
ever reached the 32-cycle-only frontier.

## Independent rejection of the retained best graphs

Run:

```powershell
.\.venv\Scripts\python.exe -B experiments\erdos64\verify_graph.py `
  research\full_solution_scout\erdos64_counterexample_pulse_2026-08-03\best_batch_h4_a.json
```

and analogously for `best_batch_h4_b.json` and `best_batch_h6_a.json`.

For every file the standard-library checker reports:

```text
minimum_degree = 3
C4 witness      = none
C8 witness      = none
C16 witness     = present
C32 witness     = present
is_counterexample = false
```

Thus none is even an unverified candidate.

## Artifact hashes

```text
47ef361ed6d92a05b2112870089bae8afe029afe0303c52f05a6740081c1ff3b  anneal_cycles.py
74f50594a48be439bf7a4507f6628ac0477bcd1d985787a3deb95af5bd60bd8c  seed_n32_h4.json
9acf0164c357a30b4b7df6a867c86ec72be8c4134244db354e404c5cc45e6a51  seed_n32_h6.json
dfce64b79cf99673a60404246b77d1dceaabc49407fbaa81260cb600c21931a6  best_batch_h4_a.json
a33fc21d850918cb86d4855e7b65b5aac4c97f181b184a09ec0262c184bca18d  best_batch_h4_b.json
d511b7cd542d2eb94d43dea80a0f701d3bf164c8f8b6e976c3807bfa9e02011a  best_batch_h6_a.json
```

## Allocation decision

Stop this order-32 annealing/CEGAR lane.  The final renewal was conditioned on
reaching a graph with no 4-, 8-, or 16-cycle.  Despite thousands of exact
16-cycle witnesses and a batched learner, no run did so.  Resume #64 only for
a qualitatively different construction that controls the entire cycle-length
spectrum algebraically; additional two-switch or one-cycle CEGAR time is not
justified by these results.
