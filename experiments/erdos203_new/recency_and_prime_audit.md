# Erdős #203 recency and claimed-prime audit

Audit date: 2026-08-02 (Europe/London).

## Current public status

- The live Erdős Problems page still labels #203 **OPEN** and reports **0
  claimed proofs**.  Its discussion page has 14 comments.
- The newest substantive comment is Animish Sharma's post at 07:36 on
  21 June 2026.  It explicitly calls its result partial and says that neither
  existence nor nonexistence has been proved.
- Announcement-level searches of arXiv, Zenodo, VibeMathed, and GitHub found
  no later full-solution claim.  The GitHub artifacts found were explicitly
  finite, partial, axiomatized, or open.  In particular, Vela's current
  verifier names its #203 witness type `CrtPartialCover` and contains no valid
  full-cover witness.

Live sources inspected:

- https://www.erdosproblems.com/203
- https://www.erdosproblems.com/forum/discuss/203
- https://github.com/Animish-Sharma/Erdos/tree/main/203

## Error in the 21 June 2026 phase-6 extension

The public report/WIT file calls the following ten integers "new primes" in
the interval `(1,000,000, 50,000,000]`.  Exact factorization shows that every
one is composite:

| Claimed prime | Exact factorization |
|---:|:---|
| 2,035,153 | 1,009 × 2,017 |
| 2,543,689 | 1,009 × 2,521 |
| 3,391,249 | 1,009 × 3,361 |
| 5,084,857 | 2,017 × 2,521 |
| 6,779,137 | 2,017 × 3,361 |
| 8,473,081 | 2,521 × 3,361 |
| 13,561,969 | 1,009 × 13,441 |
| 27,110,497 | 2,017 × 13,441 |
| 33,884,761 | 2,521 × 13,441 |
| 45,175,201 | 3,361 × 13,441 |

All factors displayed in the right column are prime.  The ten composites are
exactly pairwise products drawn from
`{1009, 2017, 2521, 3361}` and `13441`.

Independent checks used `sympy.isprime` and `sympy.factorint`; direct
multiplication verifies every equality.  There is also a compact global
cross-check: the complete factorization of

`gcd(2^5040 - 1, 3^5040 - 1)`

is only 68 decimal digits and its distinct prime factors are precisely the
31 genuine primes in the earlier 5040 list (with exponents 2 on 5 and 7 and
exponent 1 on the others).  After dividing out those factors the quotient is
exactly 1.

## Scope of the correction

This invalidates the ten phase-6 integers **as prime fibres** and invalidates
any covering experiment that treats them as ten additional allowable prime
divisors.  It does **not** by itself invalidate the whole partial note:

- the note explicitly leaves #203 open;
- its earlier 31-prime list is genuine;
- overcounting these composites in a reciprocal-density upper bound is
  conservative, so the stated `< 1` obstruction below period 5040 may still
  be correct if the underlying scan did not omit genuine primes;
- no full witness or full-solution claim depends on these ten rows.

No statement here is a solution of Erdős #203.
