# Erdős #701 n=8 bounded counterexample-search report

Date: 2026-08-03

Final status: **closed because of prior art; no new counterexample and no new n=8 proof**.

## Outcome first

The campaign's n=8 search was stopped after locating Leon Eifler's public 2025 TU Berlin
dissertation, which reports an exact-rational SCIP proof of Chvátal's conjecture through
ground-set size 8. See `PRIOR_ART.md` for the primary-source audit and its important
certificate boundary. Continuing this lane would not optimize for first credit.

Before that discovery, the bounded work produced an independently checked exact equality
extremizer and useful negative search evidence, but nothing that resolves the general
conjecture or improves the known finite bound.

## Definition and quantifier audit

For a downset F on [8], let `star_x={S in F:x in S}`. A counterexample exists exactly
when there is one intersecting family A contained in F such that

`|A| >= |star_x| + 1` for every x in [8].

Using one witness A is exact: if each star is smaller than the maximum intersecting-family
size, choose a maximum intersecting family. The empty set is in every nonempty downset but
is excluded from A under the standard non-vacuous intersecting convention.

The following solver strengthenings were audited as lossless:

1. A may be extended to an inclusion-maximal intersecting subfamily of fixed F.
2. Therefore, if S is in A and S is contained in T in F, T may be required to lie in A.
3. F may be replaced by `down(A)` plus all eight singletons. This preserves A, remains a
   downset with union [8], and can only decrease every star.
4. Given the independently certified n<=7 theorem, a normalized first n=8 witness must
   use all eight elements.
5. Element labels may be permuted so star sizes are nonincreasing.

The later prior-art audit found that item 3 is already in the literature and item 4 mirrors
the induction reduction in Eifler's formulation. They are not claimed as new theorems.

## Exact discovery engines

Two independent direct encodings were implemented:

- `search_cpsat.py`: OR-Tools CP-SAT, immediate-subset downclosure.
- `search_z3.py`: Z3 SMT, all subset-pair downclosure.

Both encode Boolean membership variables `f_S,a_S`, pairwise-disjoint exclusions for A,
containment, and all eight strict star gaps. Their 60-second strengthened runs and
600-second bare definition-level runs all ended `UNKNOWN_TIMEOUT` with no incumbent. No
UNSAT claim follows from these timeouts.

The strengthened normal-form/full-support ten-minute runs were terminated as soon as the
2025 prior result was confirmed. No partial output from those killed processes is used.

## Exact equality extremizer

Gap optimization found a full-support family F of size 225 and an intersecting family A of
size 105, with all eight stars also of size 105. This is equality, not a counterexample.

Its structure is transparent. Partition [8] into

- L={1,2,3,5},
- R={4,6,7,8}.

Then F consists of all sets that omit at least one point of L and at least one point of R.
Hence F is `(2^L minus {L}) x (2^R minus {R})`, of size 15*15=225. Each star has
size 7*15=105. The recorded A lifts a 7-member maximum intersecting equality family on
the R factor across all 15 L choices.

Two exact fixed-family replays independently verified that its maximum intersecting-family
size is exactly 105:

- `equality_nearmiss_exact_audit.json`: CP-SAT, 3,120 disjointness constraints, optimal
  value and bound 105.
- `root_verify_equality_rc2.result.json`: PySAT RC2 with CaDiCaL 1.9.5, cost 120,
  optimum 105, status `VERIFIED_EQUALITY`.

## Bounded local mutation evidence

With the lossless normal-form, maximality, and full-support constraints active, CP-SAT
searched for a strict gap-1 witness in combined `(F,A)` Hamming annuli around the equality
model:

| Combined Hamming radius | Result | Time | Claim boundary |
|---|---:|---:|---|
| 1–8 | UNSAT | 0.32 s | CP-SAT solver result; no external proof certificate |
| 9–32 | UNSAT | 17.12 s | CP-SAT solver result; no external proof certificate |
| 33–96 | UNKNOWN_TIMEOUT, no model | 180.05 s | no exhaustive claim |

An auxiliary heuristic sampled 5,215 distinct pairwise-intersecting facet antichains and
computed the exact maximum intersecting family of each sampled downset with RC2. The best
gap was 0; no positive hit occurred. This is heuristic coverage only and is not exhaustive.

## Claim boundary

- No counterexample to Erdős #701 was found.
- No new proof of the n=8 case was produced.
- No full solution of Erdős #701 was produced.
- The equality family is exact but does not improve the conjecture's status.
- The two small Hamming annuli are solver-UNSAT, not independently certificate-checked.
- The campaign hard-stopped at n=8 and did not widen to n=9.

## Recommendation

Do not allocate first-credit resources to n=8. If #701 remains attractive, perform a new
priority audit before considering n=9 or a genuinely general theorem. A compact,
independently checkable n=8 certificate might be useful to the literature, but it conflicts
with the current campaign objective of being first to solve an open Erdős problem.
