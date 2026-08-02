# Bounded benchmark report (2026-08-02)

No production run was started.  Measurements used fresh in-memory solvers;
the live v1 journals were opened read-only only long enough to copy stable
candidate records into memory.  Time limits are checked between outer models,
so a nominal five-second trial can finish slightly late.

## Terminal smoke

On the N=7 fixed-K3/K4-free analogue, both strategies reached outer UNSAT in
all 30 fresh trials.  No proof certificate was emitted.

| strategy | outer models | median wall time | mean wall time |
|---|---:|---:|---:|
| v1 one-cut | 69 | 0.06492 s | 0.06510 s |
| v2 batch | 30 | 0.04397 s | 0.04394 s |

Median terminal speedup was **1.48x** (mean 1.48x), with 56.5% fewer outer
models.

## Five-second order-41 trials

“Cuts/s” counts independently hashed logical cuts inside batches, not journal
records.  Solver trajectories diverge after the first batch, so this is a
bounded throughput comparison rather than a predicted exhaustion ratio.

| lane | v1 models / cuts/s | v2 models / logical cuts/s | throughput ratio |
|---|---:|---:|---:|
| F3_N41 | 881 / 175.8 | 98 / 407.7 | **2.32x** |
| F4_N41 | 750 / 149.7 | 86 / 336.9 | **2.25x** |
| F5_N41 | 503 / 100.2 | 70 / 248.0 | **2.47x** |

The v2 trials respectively added 2,200, 1,845, and 1,334 logical cuts.  F4's
1,845 comprised 1,493 forbidden-clique clauses and 352 admissibility cuts;
F5's 1,334 comprised 982 and 352.

## Read-only live-journal sample

An evenly spaced sample of 512 forbidden-candidate records from each stable
journal prefix gave:

| run snapshot | stable records | forbidden records | all forbidden cliques per candidate (median / mean / p90 / max) | enumeration cost |
|---|---:|---:|---:|---:|
| F4_N41 | 8,409 | 5,994 | 6 / 10.20 / 22 / 888 | 117 μs/candidate |
| F5_N41 | 4,906 | 1,887 | 2 / 4.76 / 8 / 715 | 76 μs/candidate |

Thus the full forbidden-clique enumeration cost is negligible beside the SAT
calls, while one-cut v1 discards a median 5 additional F4 cuts or 1 additional
F5 cut already visible in the same model.  Maxima reflect early dense models.

## Eager F4 assessment

Eager F4 adds 749,398 ten-literal K5 clauses: static clauses rise from 36,906
to 786,304.  In the five-second trial it required 3.40 s just to initialize,
then processed 47 models and 376 admissibility cuts (73.4 cuts/s).  Lazy v2
initialized in 0.075 s and processed 86 models with 352 admissibility cuts plus
1,493 useful encountered K5 cuts.

In a separate 20-second comparison, eager took 3.23 s to initialize and then
added 736 admissibility cuts in 20.26 s.  Lazy initialized in 0.056 s and in
20.18 s added 776 admissibility cuts plus 1,958 encountered K5 cuts.  Dynamic
CNF sizes were already similar (660,192 versus 698,030 clauses), so eager's
extra 749,398 static clauses bought neither lower wall time nor more
admissibility progress in this window.  **Recommendation: migrate F4 to lazy
complete batching; retain eager only as an experimental cross-check.**

Reproduce the bounded suite with `benchmark.py`; its JSON records separate
initialization/search times, static hashes and clause counts, cut kinds, and
the caveats above.

