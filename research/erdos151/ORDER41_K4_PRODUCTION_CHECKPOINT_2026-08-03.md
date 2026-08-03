# Order-41 K4 production checkpoint

**Recorded:** 3 August 2026, 00:02 UTC.  **Decision:** end the current
Erdős #151 production cycle and reallocate most research effort.  This is an
allocation result, not a theorem about #151.

## Claim boundary

Neither run found a counterexample, proved nonexistence, or produced an UNSAT
certificate.  The observations below concern the behavior of two audited CEGAR
relaxations only.  They are not evidence that the conjecture is true or false.

## Residual-first run

The schema-4 run began at `2026-08-02T21:45:07Z`.  Its pre-registered gate was
1,500 committed models or two wall-clock hours, whichever came first, provided
that no global-admissibility or arrowing cut had appeared.  Model 1,500 was
committed at `23:44:36Z`; two additional atomic commits landed while the
operator verified the lock and issued the stop request.

The exact preserved prefix is therefore:

- 1,502 outer models and 1,502 batch records;
- 244 forbidden-K5 batches, comprising 1,197 logical K5 cuts;
- 1,258 residual-admissibility batches, comprising 5,032 logical cuts;
- zero global-admissibility cuts and zero arrowing cuts;
- no candidate and no `result.json`.

PID 7184 was externally terminated at `2026-08-02T23:45:11Z` because this old
engine had no operator stop channel.  It is not described as a graceful pause.
The process was confirmed dead; the stale lock is intentionally preserved, and
the directory must not be resumed automatically.

Before replay, the journal was checked to contain exactly 1,502 newline-ended,
JSON-decodable records, ending at sequence 1,501/model 1,502, in agreement with
`progress.json`.  Full replay returned `AUDIT_OK`, rechecking all stored
candidates, witnesses, regenerated cuts, record hashes, hash chain, source
bindings, static encoding, and progress linkage.

| Preserved file | Bytes | SHA-256 |
|---|---:|---|
| `.cegar-write.lock` | 355 | `1aec9c26f26c3a380bd81920e7fb8c4c28c432108298bbb08cc4e2c3ca52a5f0` |
| `cuts.jsonl` | 8,711,676 | `2c083622c6b0c340193a9086acb5772e1c44d436015d0d62c8c28e18bc8c09f7` |
| `metadata.json` | 19,621 | `cf00f69cbe1996796a9365f3be4e0bb7e89c0717388b1a76b827975e692948cf` |
| `progress.json` | 19,673 | `bd0fba060e1a27d4fbcc1cd24df8af90a36ee3619494dfeed7eeed56571677c7` |

The replayed journal head is
`feaf4e6b9c573efbcbd5e979b715235a8a95fd52a8d7781450887b3f9843905d`.

## Arrowing-first final experiment

The independently tested schema-5 engine began in a fresh directory at
`2026-08-02T23:46:34Z`, with both limits passed to the process itself:
1,500 outer models and 7,200 seconds.  Its static metadata was independently
reconstructed clause by clause and returned `STATIC_CLAUSE_STREAM_VERIFIED`.
The run reached its model limit cleanly at `2026-08-03T00:00:42Z`, wrote
`PAUSED_AT_LIMIT`, removed its writer lock, and exited normally.

The final state is:

- 1,500 models and 1,500 hash-chained records;
- 580 forbidden-K5 batches, comprising 1,445 logical K5 cuts;
- 920 arrowing cuts;
- zero residual-admissibility cuts and zero global-admissibility cuts;
- no candidate, no result, and no UNSAT claim.

Full replay returned `AUDIT_OK` across 16 audit classes.  The journal head is
`2bf54fd2b3da0d2e413fe3b88e57b32f2328958e86596c59e235e9b02d937f2e`.

The pre-registered fixed-bin telemetry is:

| Models | K5 batches | Arrowing cuts | Residual cuts | Global cuts | Arrowing fraction |
|---|---:|---:|---:|---:|---:|
| 1--500 | 176 | 324 | 0 | 0 | 64.8% |
| 501--1000 | 208 | 292 | 0 | 0 | 58.4% |
| 1001--1500 | 196 | 304 | 0 | 0 | 60.8% |

There is no downstream penetration and no 25% middle-to-final improvement.
Changing oracle order exposed the same underlying issue from the other side:
the relaxation is not approaching graphs that simultaneously satisfy the
Ramsey-arrowing and four-residual constraints.

| Preserved file | Bytes | SHA-256 |
|---|---:|---|
| `metadata.json` | 19,752 | `e5b2b00e41b48bc131080dbf2c642881785266473aa3e6f0a30b705e51f86498` |
| `progress.json` | 19,784 | `b1a882ee6ed212733c8228b824911ead25d065d5edef1c57ac1c12295e64269b` |
| `cuts.jsonl` | 3,862,835 | `16af5892c5afdce6a7c6e62a18c1e03ce3593c72c245adcf710c8cb03e942f46` |
| stdout log | 201 | `a41f41b99230b45187d6ca2637db8f3f76a03781f7dde453902eacab87a03a26` |
| stderr log | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Allocation consequence

The live-cycle stopping condition in `ALLOCATION_CHECKPOINT.md` has fired.
No further #151 production run, separator reordering, local-template SAT probe,
or automatic resume is authorized by momentum from this cycle.  Allocate
approximately 15--25% to maintenance: the already obtained order-41 omega-5
result, expert review, candidate readiness, and genuinely new global evidence.
Allocate the remaining effort to independent full-resolution targets.

#151 can earn another bounded cycle only through the published renewal signals:
a verified candidate, substantial certified profile elimination, a global
family theorem with measured search reduction, removal of the catalogue
premise, or a genuinely uniform theorem.  Merely proposing another encoding or
another local lemma does not reopen the cycle.

At recording time the C drive had 92.09 GiB free, above the 80-GiB cleanup
threshold.  No proof or candidate artifact was deleted.
