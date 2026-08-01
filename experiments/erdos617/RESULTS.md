# Erdős 617, first open case `r = 5`: computational handoff

## Bottom line

No balanced 5-coloring of `K_26` was found. No certificate passed the exhaustive
checker. Consequently these experiments do **not** prove or disprove Erdős 617,
even for `r = 5`.

What is rigorous here is limited to several explicitly restricted UNSAT results,
plus a useful general edge-count lemma and reproducible unrestricted near-misses.

## Audit of the Lean statement

At `r = 5`, negating `erdos_617` asks for a coloring of all 325 edges of `K_26`
with colors `0,...,4` such that every 6-vertex set contains at least one edge of
each color. Equivalently, if `G_c` is the graph of color `c`, then

```
alpha(G_c) <= 5    for every c.
```

There are `C(26,6) = 230,230` six-sets, hence 1,151,150 coverage constraints.

## General necessary edge bound: 59 edges per color

In any putative solution, every color graph `G_c` is `K_6`-free: a monochromatic
`K_6` would miss the other four colors. Its complement is also `K_6`-free, since
`alpha(G_c) <= 5`.

If `e(G_c) <= 58`, then its complement has at least `325 - 58 = 267` edges.
Brouwer's exact stability theorem says that a non-5-partite `K_6`-free graph on
26 vertices has at most

```
t(26,5) - floor(26/5) + 1 = 270 - 5 + 1 = 266
```

edges. Thus the complement would be 5-partite. Its five independent parts are
five cliques in `G_c`; one part has at least 6 vertices, contradicting that `G_c`
is `K_6`-free. Therefore every color class has at least 59 edges. In particular,
the five edge counts have only 30 edges of total slack above this lower bound.

Reference for the precise form used: Brouwer's theorem is quoted as Theorem 1.1
in [Exact stability for Turán's Theorem](https://people.maths.ox.ac.uk/scott/Papers/turanstability.pdf).

## Exact restricted UNSAT results

### Fixed affine slopes; 75 free edges

Use the 25 affine points `F_5^2`. Color every nonvertical affine edge by its
slope in `F_5`. Leave all 50 vertical edges and all 25 edges to a new vertex
free. This restricted family is UNSAT.

- Variables: 75 categorical edge variables, five colors each.
- Essential coverage clauses: 15,625. They enumerate, for each slope/color,
  all `5^5 = 3125` transversals of the five parallel lines.
- Solver: PySAT CaDiCaL 1.9.5 (`cadical195`).
- Result: `UNSAT` in 0.074051 seconds.
- Reproduction:

  ```powershell
  python experiments\erdos617\structured_sat.py
  ```

- Log: `structured_sat.log`.

### Hamming radius around the fixed affine slopes

`full_sat.py --affine-budget b` permits all 75 vertical/new-vertex edges to be
free and permits at most `b` changes among the other 250 slope-colored edges.
The coverage clauses are added lazily but UNSAT is exact when returned.

| Budget `b` | Result | Time | Log |
|---:|:---|---:|:---|
| 0 | UNSAT | 1.375 s | `near_affine_b0.log` |
| 1 | UNSAT | 10.469 s | `near_affine_b1.log` |
| 2 | UNKNOWN (timeout) | 91.750 s | `near_affine_b2.log` |

Solver for this table: PySAT Glucose 4.2. Budget 1 is the strongest completed
statement: at least two of the 250 nonvertical slope edges must change in any
solution extending this labeled affine setup.

## Unrestricted search

### SAT

`full_sat.py` is a one-hot exact SAT encoding with optional lazy constraint
generation, sound star-color symmetry breaking, affine or JSON phase hints,
cardinality neighborhoods, and the 59-edge necessary bound.

No unrestricted run completed SAT or UNSAT:

- CaDiCaL lazy run: after three models, 159,687 distinct coverage clauses had
  been added; the fourth solve did not finish in 120 seconds (`lazy_sat_120s.log`).
- Glucose run phased from the 796-violation near-miss: after 93,493 clauses,
  the sixth solve timed out at 120 seconds (`lazy_sat_phase796_120s.log`).

These timeouts are merely `UNKNOWN`, not evidence of global UNSAT.

### Local search

`local_search.cpp` maintains all 1,151,150 color/six-set counts incrementally.
It supports min-conflicts, breakout weights, color-count-preserving swaps,
balanced affine initialization, and a minimum number of edges per color.

Best unrestricted near-miss:

- Seed: `621`.
- Command parameters: affine initialization, breakout, noise `0.001`, three
  restarts of 100,000 steps.
- Missing `(six-set,color)` incidences: **786**, across 772 distinct six-sets.
- Edge counts: `[55, 64, 80, 63, 63]`.
- File: `near_candidate_621.json`.
- Log: `breakout_621_noise001.log`.

The 55-edge color class is exactly five clique components of sizes
`6,5,5,5,5`, showing why this point is not close to feasible under the new
59-edge lemma. Enforcing at least 59 edges per color gave a worse best of 870
violations in the tested run (`breakout_622_min59.log`, seed 622).

A separate 796-violation point (`near_candidate_617.json`, seed 617) was checked
by exact cardinality SAT. No valid coloring exists within 13 edge recolorings of
that particular point:

| Radius | Result | Log |
|---:|:---|:---|
| 5 | UNSAT | `near796_radius5.log` |
| 10 | UNSAT | `near796_radius10.log` |
| 11 | UNSAT | `near796_radius11.log` |
| 12 | UNSAT | `near796_radius12.log` |
| 13 | UNSAT | `near796_radius13.log` |
| 15 | UNKNOWN after 90 s | `near796_radius15.log` |

This is only a local-neighborhood statement about that labeled near-miss.

## Files

- `structured_sat.py`: exact 75-free-edge affine-extension encoding.
- `full_sat.py`: unrestricted/lazy SAT and restricted-radius variants.
- `local_search.cpp`: incremental unrestricted heuristic.
- `verify_candidate.py`: independent exhaustive JSON checker; a real candidate
  must report `PASS ... six_sets_checked=230230`.
- `affine_lines_sat.py`: experimental family in which each affine line is
  monochromatic. Runs were unresolved, so they provide no UNSAT conclusion.

The Lean source under `third_party/formal-conjectures` was not modified.

The C++ heuristic can be rebuilt with:

    g++ -O3 -std=c++17 local_search.cpp -o local_search.exe
