# Erdős #64: bounded SMS frontier at order 32

This directory records a candidate-first computation, not a solution of
Erdős problem #64.  The search forbids simple cycles of lengths 4, 8, 16, and
32 using SMS with the Glasgow forbidden-subgraph propagator.

An unrestricted minimum-degree-three first-solution run was interrupted after
1375.52 seconds without emitting a graph.  It is a timed candidate-search
frontier only; no UNSAT conclusion follows.

For each even `h` in `{4,6,8,10,12}`, the structured family has exactly `h`
independent degree-four vertices and `32-h` degree-three vertices.  Every
vertex is required to have a cubic neighbour, following Carr's necessary
conditions for a minimal counterexample.  SMS is given the partition
`[h,32-h]`, so its permutations preserve the two fixed degree classes.

The results are:

| h | result | wall time |
|---:|:---|---:|
| 4 | timeout / unknown | 900.01 s |
| 6 | timeout / unknown | 900.01 s |
| 8 | UNSAT in this family | 201.26 s |
| 10 | UNSAT in this family | 0.25 s |
| 12 | UNSAT in this family | 0.38 s |

No graph was emitted.  In particular, the timeouts for `h=4,6` are not
negative mathematical results.  The UNSAT labels rely on the tested SMS and
Glasgow binaries; no independently checked LRAT certificate was produced.
The static `h=10` degree/Carr CNF was independently found SAT and decoded by
local PySAT/CaDiCaL.  Its model has 53 edges, exactly ten degree-four and 22
degree-three vertices, an independent high set, and a cubic neighbour at every
vertex.  This guards against the possibility that the quick SMS UNSAT came
from a trivially contradictory or misnumbered degree encoding.  The packaged runner was also
replayed end to end at `h=12`; its generated DIMACS, command record, and raw
output are retained under `replay_h12/`.

The exact tested commits are in `results.json`.  They are deliberately stated
instead of claiming byte-for-byte identity with older runs mentioned by the
public `ArjunBalaji79/erdos-gyarfas-min-degree-3` driver.

Reproduce from this directory:

```powershell
docker build -t erdos64-sms .
docker run --rm -v "${PWD}:/work" erdos64-sms python /work/sms_search.py --high 8 --timeout 900 --output /work/replay_h8
```

If a run emits `candidate.json`, check it outside the search stack with:

```powershell
python ..\verify_graph.py replay_h8\candidate.json
```

A narrow web/GitHub audit on 2 August 2026 found no public computation with
this exact order-32 fixed-degree/Carr scope.  The closest public collision is
the general SMS exclusion only through order 31; AlphaEvolve's searches
through order 40 are heuristic rather than exhaustive.  This is not a formal
priority or novelty claim.
