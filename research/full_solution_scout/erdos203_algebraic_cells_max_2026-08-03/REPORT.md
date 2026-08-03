# Erdős #203: algebraic-power / CRT hybrid

**Date:** 2026-08-03  
**Outcome:** bounded lane stopped; no cover and no sub-5% residual.  
**Claim boundary:** the algebraic classification below is exact for binomials
of the form `2^r 3^s X^R + 1`.  The phase-search percentages are heuristic
sample results, not lower bounds and not a solution of #203.

## Question attacked

Seek an integer `m >= 1`, `gcd(m,6)=1`, such that

```text
2^k 3^l m + 1
```

is composite for every `k,l >= 0`.  This lane imposed `m=A^R`, used symbolic
factorization on some exponent cells, and used ordinary prime fibres on the
remaining cells, with their phases restricted by the requirement that `m`
be an `R`-th power modulo every certificate prime.

## Exact algebraic classification

Write `k=Ru+r`, `l=Rv+s`, and `X=2^u 3^v A`.  The relevant polynomial is

```text
2^r 3^s X^R + 1.
```

Taking the reciprocal reduces its reducibility over `Q` to that of
`X^R + 2^r 3^s`.  Capell's binomial criterion says that this is reducible
exactly when one of the following holds:

1. `p | R` for an odd prime `p`, and `2^r 3^s` is a `p`-th power;
2. `4 | R`, and `2^r 3^s` is four times a fourth power.

Unique factorization makes these conditions respectively

```text
k = l = 0 (mod p), for some odd prime p | R,
```

and

```text
k = 2 (mod 4),  l = 0 (mod 4),  with 4 | R.
```

They give explicit integer factorizations.  In the first case, put
`Y=2^(k/p) 3^(l/p) A^(R/p)` and use

```text
Y^p + 1 = (Y+1)(Y^(p-1)-Y^(p-2)+...-Y+1).
```

In the second, put
`Y=2^((k-2)/4) 3^(l/4) A^(R/4)` and use Sophie--Germain:

```text
4Y^4 + 1 = (2Y^2-2Y+1)(2Y^2+2Y+1).
```

Choosing the CRT representative `A>1` makes both factors proper.  This also
shows that there is no additional cyclotomic or Aurifeuilian residue cell for
this monomial-plus-one ansatz: the Sophie--Germain cell is precisely Capell's
exceptional `-4` case.

If `S` is the set of odd prime divisors of `R`, the exact density of automatic
cells is

```text
1 - product_{p in S}(1-1/p^2)                         if 4 does not divide R,
1 - (15/16) product_{p in S}(1-1/p^2)                if 4 divides R.
```

Repeated prime powers in `R` create no new algebraic cells.  Thus, for any
chosen mechanisms, the least restrictive exponent is the product of the
selected odd primes, multiplied by `4` only if the exceptional cell is used.

## Exact CRT phase restriction

For a prime `q` not dividing `6`, choose a primitive root `g` and write

```text
2 = g^u,  3 = g^v,
d = gcd(q-1,u,v),  h=(q-1)/d,
a=u/d, b=v/d.
```

The fibre with label `t = ak+bl (mod h)` has
`2^k3^l = g^(dt)`.  It can be selected for `m=A^R` exactly when

```text
gcd(R,q-1) divides ((q-1)/2 - d t).
```

This is necessary and sufficient for
`A^R = -g^(-dt) (mod q)`.  A modular linear equation supplies an explicit
root `A mod q`; roots for distinct primes combine by CRT, together with
`A=1 (mod 6)`.  In particular, for an odd prime `p | R` and `q=2 (mod p)`,
the `p`-th-power map is bijective and every phase survives, exactly as the
initial cube-map observation suggested.

## Computation

`search_algebraic_power_cover.py` implements the algebraic mask, the exact
phase predicate, explicit modular roots, coordinate descent, and a Z3 exact
uncovered-cell query that is triggered if a sampled cover is ever reached.
`audit_algebraic_power_cover.py` independently checks the implementation.

Audit result: **PASS**.

- 204 direct CAS irreducibility comparisons for all cells through `R=8`;
- 26,224 brute phase-membership comparisons;
- 10,619 explicit modular-root checks;
- exact automatic-cell counts for twelve representative exponents through
  `R=420`.

The main new pilot reused, without recomputing, the other lane's exact union
of 281 prime maps (all image orders at most 1000, together with the legacy
period-720720 pool).  It used 50,000 deterministic sampled exponent pairs,
five restarts, and at most twenty coordinate sweeps.

| `R` | exact automatic density | usable maps | best sampled residual |
|---:|---:|---:|---:|
| 1 | 0 | 281 | 6.606% |
| 4 | 1/16 = 6.25% | 242 | 12.194% |
| 12 | 1/6 = 16.67% | 242 | 14.674% |
| 20 | 1/10 = 10% | 242 | 12.814% |
| 28 | 4/49 = 8.16% | 242 | 12.456% |
| 60 | 1/5 = 20% | 242 | 15.124% |
| 420 | 53/245 = 21.63% | 242 | 15.268% |

The independent odd-power pilot on the identical 281-map census likewise
gave 8.012% (`R=3`), 7.082% (`R=5`), 7.002% (`R=7`), and 7.438--8.942% for
the tested mixed odd exponents.  Its unrestricted 50,000-point result was
6.756%; a separate 250,000-point unrestricted run left 8.862%.  These are
optimizer outputs on different samples, so their role is directional only.

An earlier 99-map period-720720 pilot told the same story: its best power
variant was `R=5` at 20.103% residual versus 20.600% for the prior flat run;
`R=3` left 22.046%, and `R=12` left 26.763%.

## Decision

This ansatz fails the predeclared continuation gate.  It produced neither an
exact cover nor a structured residual below 5%.  The automatic algebraic
coverage is more than offset by lost CRT phase freedom; even powers are
especially damaging, eliminating every phase for 39 of the 281 maps.

Because Capell's criterion exhausts the binomial factorization mechanisms,
trying larger `R`, repeated factors, or more combinations of the same cells
is not a new angle.  This lane should remain stopped.  A future restart would
need a genuinely non-binomial global form for `m`, or a recursive/non-flat
cover exploiting structure not represented by one independently chosen fibre
per prime.

## Files

- `search_algebraic_power_cover.py` -- hybrid optimizer and exact-candidate
  checker;
- `census_even_pilot.json` -- 281-map even/mixed-power run;
- `smoke.json` -- initial 99-map survey;
- `audit_algebraic_power_cover.py`, `audit.json` -- independent checks.

