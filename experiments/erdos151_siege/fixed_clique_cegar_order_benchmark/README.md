# F4_N41 dynamic separation-order benchmark

This isolated diagnostic asks whether moving the existing arrowing separator
ahead of v4's residual separator is promising.  It imports the current v4
source and its byte-pinned v3 dependency read-only, but is **not** a
`SearchSession`: it creates no run directory, journal, lock, checkpoint, or
candidate artifact.

Both variants preserve the exact statement semantics and always first add the
complete lazy forbidden-K5 batch.  They then use v4's existing encoders:

| order | dynamic sequence after forbidden-K5 completion |
|---|---|
| current residual-first | residual induced-admissibility, generic global admissibility, arrowing |
| benchmark arrowing-first | arrowing, residual induced-admissibility, generic global admissibility |

The residual cut remains v4's exact translation of an induced `G[Z_c]`
witness to an admissible 10-set.  The generic and arrowing cuts are the
unchanged inherited encoders.  Before every benchmark cut is committed, the
script independently checks its relevant witness condition: residual/global
10-set admissibility and absence of monochromatic present triangles,
respectively.

## Command

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_order_benchmark\benchmark_orders.py --models 100 --seconds 30 --repeats 3 --output experiments\erdos151_siege\fixed_clique_cegar_order_benchmark\benchmark_results_100.json
```

The primary matched budget is 100 outer models per fresh trial.  The 30-second
wall limit is a safety cap checked between models.  Repeats alternate which
order goes first; the pinned engine exposes no configured solver seed, and all
fresh trials had the same deterministic trajectory.

## Results (three fresh 100-model trials per order)

| metric | residual-first | arrowing-first |
|---|---:|---:|
| median elapsed time | 8.733 s | 7.179 s |
| forbidden-K5 cut batches | 38 | 7 |
| forbidden-K5 logical cuts | 372 | 11 |
| K5-free outer models | 62 | 93 |
| residual batches / logical cuts | 62 / 248 | 0 / 0 |
| arrowing batches / logical cuts | 0 / 0 | 93 / 93 |
| models reaching generic admissibility | 0 | 0 |
| total logical cuts | 620 | 104 |

On the identical first K5-free outer model (`02c7e2...2474`), all three
oracles find a valid separator: residual gives four global cuts, generic gives
eight, and arrowing gives one.  The measured calls there were approximately
3.9 ms residual, 1.9 ms generic, and 27.0 ms arrowing.  Thus arrowing is not
the locally cheapest oracle, but its cut trajectory was materially smaller and
faster over the matched 100-model horizon: about 18% lower elapsed time and
83% fewer logical cuts.  It also avoided all residual and generic calls in the
arrowing-first trajectory.

The shorter 50-model, three-repeat probe is retained as
`benchmark_results.json`; it shows the same qualitative behavior.

## Recommendation and limits

Arrowing-first is a worthwhile **isolated next-engine** experiment for F4_N41:
use `forbidden -> arrowing -> residual -> generic`, with the same cut semantics
and a new schema/source binding.  Do not change, resume, or otherwise touch
the active v4 production run based on this diagnostic.

This is bounded trajectory evidence only.  Once a different valid cut is
added, future SAT models differ, so neither cut counts nor elapsed time predict
exhaustion.  It makes no candidate, UNSAT, or proof claim.
