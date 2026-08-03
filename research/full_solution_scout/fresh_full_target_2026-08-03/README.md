# Fresh full-resolution target acquisition — 2026-08-03

## Verdict

No fresh target outside Erdős #151 and #719 presently clears all five gates:
full-problem leverage, genuinely-open status, one-week reachability, low
priority collision, and definition-level independent verification.

The best-looking finite-witness outside option was Erdős #561 (the exact
size-Ramsey formula for two arbitrary star forests).  A deliberately tiny
probe of the symmetric nonuniform tuple

`F1 = F2 = K_{1,2} disjoint-union K_{1,1}`

found no host with at most five edges that arrows `(F1,F2)`.  Two independent
programs agree on all 45 isolate-free unlabelled host types.  A deeper
priority search then found that this tuple and a much larger family were
already proved by Yen-Jen Cheng in a 2010 NTU master's thesis.  The thesis
also gives the six-edge arrowing host `C5 disjoint-union K2`.  Therefore the
probe is a reproducible prior-art rediscovery, **not a new result and not a
partial solution of #561**.

This lane is stopped.  No second finite tuple is being launched.

## Pool reconstructed

The authoritative local campaign snapshot
`../pool-2026-08-02.json` contains 540 open, unclaimed candidates after the
campaign's touched-target exclusions.  The complete live-ask triage is split
into:

- 269 unformalized rows in
  `../triage-2026-08-02/unformalized-merged.json`;
- 271 formalized rows in
  `../triage-2026-08-02/formalized-merged.json`.

The unformalized pass marked only #151 and #719 as probe-grade.  The fresh
read here deliberately revisited the strongest finite-counterexample
possibilities rather than trusting that score blindly.

## Ranking after definition and recency gates

Scores are on a 0–5 scale.  `collision` is safety from a priority race, so a
higher score is better.  A recognition failure overrides the numerical sum.

| Problem | Full leverage | Counterexample plausibility | One-week reach | Collision safety | Verification | Sum | Fresh verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| #561 | 5 | 2 | 3 | 0 | 5 | 15 | Best finite-witness shape, but acute active collision; tiny base case is old |
| #701 | 5 | 1 | 1 | 2 | 4 | 13 | Certified through ground-set size 7; size 8 is an unstructured Dedekind-family search |
| #149 | 5 | 1 | 1 | 1 | 4 | 12 | Sharp blow-up evidence, small-degree positive results, and July 2026 activity |
| #778 | 3 | 2 | 1 | 0 | 4 | 10 | Composite entry; finite result in one game would not resolve the full entry; active specialists |
| #1160 | 4 | 1 | 0 | 4 | 1 | 10 | Finite disproof possible but exact group-count verification is not a one-week/two-checker object |
| #65 | 2 | 1 | 0 | 4 | 2 | 9 | Remaining ask is extremal/asymptotic and has statement-direction hazards |
| #638 | — | — | — | — | — | — | Literal statement has easy counterexamples but intended statement is unclear; recognition gate fails |

No score here is evidence that a conjecture is true or false.  It is an
allocation score for the stated one-week objective.

## Erdős #561: faithful tuple calculation

For `s=t=2` and sequences `(n1,n2)=(m1,m2)=(2,1)`, the conjecture sets

- `l2 = n1+m1-1 = 3`,
- `l3 = max(n1+m2-1,n2+m1-1) = 2`,
- `l4 = n2+m2-1 = 1`.

Thus the proposed size-Ramsey number is `3+2+1=6`.  Any arrowing host with
at most five edges would refute the universal conjecture.  Isolated vertices
are irrelevant, and an isolate-free graph with `m` edges is a multiset of
connected graphs with at most `m+1` vertices.  This is the completeness basis
for the bounded enumeration.

## Probe result and independent verification

`enumerate_probe.py` generated every connected graph type with one through
five edges, assembled every multiset of components, and tested all edge
2-colourings.  Counts were:

| Edges | Connected types | All isolate-free types |
|---:|---:|---:|
| 1 | 1 | 1 |
| 2 | 1 | 2 |
| 3 | 3 | 5 |
| 4 | 5 | 11 |
| 5 | 12 | 26 |

Every one of the 45 host types has an explicit colouring avoiding a
monochromatic `K_{1,2} disjoint-union K_{1,1}`.

`verify_catalogue.py` independently:

1. regenerated connected graphs as adjacency bitmasks rather than edge
   combinations;
2. used maximum adjacency words rather than minimum edge tuples for
   canonical labelling;
3. reconstructed all component multisets; and
4. checked the saved colouring by all injective embeddings of the labelled
   five-vertex target, rather than the first program's edge-intersection
   detector.

It returned `VERIFIED`, with zero missing or extra host types and zero failed
colouring witnesses.  This proves only the bounded lower bound for this one
tuple.  It does not solve #561.

## Priority audit: why the tuple is old

The decisive source is Yen-Jen Cheng, *Size Ramsey Numbers of Star Forests*,
National Taiwan University master's thesis, August 2010:

- Theorem 18 proves the conjecture whenever `m<=n`, `a1>=b1`, and every
  `ai,bj` after the first equals 1.  The symmetric `(2,1)` versus `(2,1)`
  tuple satisfies these hypotheses exactly.
- The same thesis explicitly records
  `C5 disjoint-union K2 -> (K_{1,2} disjoint-union K2,
  K_{1,2} disjoint-union K2)`, supplying the conjectured six-edge upper
  bound for this tuple.

The source is public at:

- https://tdr.lib.ntu.edu.tw/jspui/bitstream/123456789/10630/1/ntu-99-1.pdf
- repository metadata: https://tdr.lib.ntu.edu.tw/jspui/handle/123456789/10630?mode=full

This source did not appear in the first exact-expression searches.  It was
found only after searching the broader parameter family.  That is the main
process result of this lane.

## Current #561 status and collision risk

The arbitrary-star-forest conjecture is still presented as open in the
current literature, but it is an active priority race:

- Davoodi–Javadi–Kamranian–Raeisi, arXiv:2111.02065 (published in 2025),
  proves several broad cases: https://arxiv.org/abs/2111.02065
- Fu–Luo–Ni, arXiv:2606.04439, first circulated in June 2026 as a claimed
  full solution; version 3 dated 4 July 2026 is narrowed to *uniform* star
  forests and states only that special cases of the arbitrary conjecture are
  known: https://arxiv.org/html/2606.04439v3
- live problem page: https://www.erdosproblems.com/561

The v1-to-v3 retreat is both a mathematical difficulty signal and an acute
collision signal.  It does not imply the conjecture is true.

## Allocation conclusion

Do not extend this probe mechanically to the next tuple.  A next tuple must
first be checked against Cheng's full Theorem 18 family, the 1981
Ramsey-minimal-graphs paper, the 2002 Győri–Schelp condition, the 2025 case
theorems, and every version of arXiv:2606.04439.  It then needs a principled
small-witness reason, not merely being the next lexicographic parameters.

The present evidence says:

- #561 remains the most natural *future* counterexample-first outside option;
- it has no cleared one-week finite witness class at present;
- #701, #149 and #778 should not be revived without new structural input;
- this target-acquisition lane has reached its kill condition with no fresh
  promotion.

## Artifacts and hashes

- `enumerate_probe.py` —
  `8332d1d0fa2c0fe5bc15612ec7c82d436ffa47de666d64198f44ea486b0f692d`
- `verify_catalogue.py` —
  `65f26ec90d41ea400b0848c56f74b91c5c2980b42855d4b9ddab4dec62ba581e`
- `probe_result.json` —
  `a840398d68f1d040c5e419b30a1a6a6ed61603b0cb91f6f6012db99a46aeac8d`
- `independent_verification.json` —
  `1ed039dcf560afde6a41390412c138d0a1e45f6318918c15dcd3298583c10835`

No git operation, publication, deletion, or edit outside this subtree was
performed.
