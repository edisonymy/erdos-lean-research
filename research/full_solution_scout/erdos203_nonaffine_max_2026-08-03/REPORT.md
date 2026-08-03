# Erdős #203: bounded non-affine / structural escape audit

**Date:** 2026-08-03 (Europe/London)  
**Outcome:** stopped after the predeclared single high-effort pass; no solution
or construction emerged.  The apparent new Vela signal is an old partial
certificate, and its displayed modulus has an exactly certified prime term.

This lane was deliberately disjoint from the stopped flat affine-fibre search,
the complete image-order-at-most-1000 census, the `m=A^R` algebraic-cell lane,
and the common-shear / recursive-cover theory lane.  It asked whether composite
moduli, prime powers, interacting congruences, variable algebraic divisors, or
an infinite-prime construction could genuinely escape affine fibres.

## 1. Recency audit: `vela-verify` contains no newer #203 solution

The public crate `vela-verify` 0.914.1 (published 2026-07-24) includes a
`CrtPartialCover` verifier.  That is a verifier release, not a result.

Two public repositories were inspected at their current 2026-08-03 heads:

- `vela-science/vela`, commit
  `a546f89d62e908ca2b335a70767dd7d26892310c`;
- `vela-science/erdos-frontier`, commit
  `4509a731317b040a8e4031a704c16a03076ae89f`.

The latter contains exactly one #203 witness,
`witnesses/erdos203-crt-partial-cover.witness.json`, SHA-256
`a657efb1e0d5bc01b92824c59ed1b20b8dfa56d9c51154d99bf9b59ddb8c9c8b`.
It has the modulus

```text
m = 8168305011630835886634520238999
```

and 20 prime rows.  Its retained claim was created on 2026-06-10 and says
explicitly that the rows cover only about 0.7467 of the exponent lattice.  The
current Observatory target says "nothing currently claimed" and asks to extend
the verified rows to a full cover.  No newer #203 witness, proposal, or accepted
construction appears in either current repository.

There is a stronger exact kill.  The point `(k,l)=(1,8)` lies on none of the 20
retained affine lines, and

```text
2 * 3^8 * m + 1
  = 107184498362619828504418174576144879
```

is prime.  `audit_nonaffine_boundary.py` independently rechecks all 20 rows and
then verifies a complete recursive Lucas certificate for this 117-bit prime.
It uses only Python integer arithmetic, modular exponentiation, and gcd; it does
not invoke SymPy or a probable-prime test.  Thus the retained `m` is definitely
not a solution of #203, rather than merely lacking a full-cover proof.

Primary records:

- <https://docs.rs/crate/vela-verify/0.914.1>
- <https://github.com/vela-science/vela>
- <https://github.com/vela-science/erdos-frontier>
- <https://app.constellate.science/targets>

## 2. Finite-prime collapse theorem

Put

```text
T(k,l) = m 2^k 3^l + 1,   gcd(m,6)=1.
```

### Lemma N1 (one fixed prime is one affine fibre)

If a prime `q>3` divides some `T(k,l)`, then `q` divides neither `6` nor `m`,
and

```text
q | T(k,l)  iff  2^k 3^l = -m^(-1) (mod q).
```

The map `(k,l) -> 2^k 3^l mod q` is a homomorphism from `Z^2` to
`F_q^*`.  Therefore its inverse image of `-m^(-1)` is either empty or one
coset of its kernel: exactly an affine fibre.

### Corollary N1a (prime powers and composite moduli add no geometry)

- A certificate `q^a | T(k,l)` is contained in the same fibre modulo `q`.
- A certificate `d | T(k,l)` is an intersection of the fibres of the prime
  divisors of `d`, hence is stronger, not broader.
- A certificate `gcd(D,T(k,l))>1` is the union of the fibres for primes
  dividing the fixed integer `D`.

Consequently **every proof using only finitely many fixed candidate divisors,
even if packaged as prime powers, composite moduli, interacting congruences, or
finite Boolean case splits, collapses to the existing finite affine-cover
problem.**  The harmless boundary exceptions are `q=2` (all `k=0` terms are
even once a solution necessarily has `m>1`) and a possible `q=3` divisor on
the `l=0` boundary.

### Lemma N2 (profinite escape point)

Each affine fibre is clopen in the profinite completion `Z_hat^2`.  If an
arbitrary family of prime fibres covers all of `Z_hat^2`, compactness supplies
a finite subcover.  Hence any genuine solution that has no finite covering set
of primes must leave at least one profinite exponent pair outside **every**
prime fibre, even though all ordinary nonnegative exponent pairs are covered.

This does not rule out an infinite-prime solution, because `N^2` is dense but
not compact.  It identifies its required pathology precisely: an infinite
cover with no profinite extension, not a clever repackaging of finite CRT.

## 3. Exact rigidity of periodic algebraic identities

The previous algebraic lane classified cells with a common exponent period.
The following version rules out the apparent unequal-period escape as well.

### Lemma N3 (rectangular-cell binomial classification)

Fix `r,s >= 0` and periods `R,S >= 1`, let

```text
C = m 2^r 3^s,   d = gcd(R,S),
F(X,Y) = 1 + C X^R Y^S.
```

Then `F` is reducible over `Q` if and only if one of the following holds:

1. some odd prime `p|d` has `C` a `p`th power; equivalently, `m` is a
   `p`th power and `p|r,s`;
2. `4|d` and `C=4A^4`; equivalently, `m` is a fourth power,
   `r=2 (mod 4)`, and `s=0 (mod 4)`.

Proof.  Write `R=dR_0`, `S=dS_0`, where `gcd(R_0,S_0)=1`, and set the
primitive Laurent monomial `Z=X^R_0 Y^S_0`.  A unimodular change of Laurent
variables reduces irreducibility of `F` to that of

```text
1 + C Z^d.
```

Apply Capell's binomial criterion to its reciprocal scalar multiple
`Z^d-(-1/C)`.  Since `-1/C<0`, the ordinary square case is impossible.  An odd
prime `p|d` gives reducibility exactly when `C` is a `p`th power, and Capell's
exceptional `-4` case gives exactly `4|d` and `C=4A^4`.  Unique factorisation
of the integer `C=m2^r3^s` gives the displayed valuation conditions.  The
factorisations are respectively `U^p+1` and Sophie--Germain
`4U^4+1`.

Thus unequal rectangular periods, coefficient splitting, cyclotomic language,
and Aurifeuilian language do not create a new full-rank algebraic cell.  They
return exactly the perfect-power and Sophie--Germain cells already exhausted.

### Lemma N4 (there is no infinite perfect-power reservoir)

For a fixed integer `m>1`, the primes `p` for which `m` is a perfect `p`th
power are precisely among the prime divisors of the gcd of the exponents in
the prime factorisation of `m`; in particular there are finitely many.  The
only positive integer that is a `p`th power for infinitely many primes is 1,
but `m=1` fails #203 immediately at `(0,0)`, where the term is 2.

So the tempting infinite union of identities `U^p+1` cannot occur for an
admissible fixed `m`.

## 4. Adversarial survey of the remaining escape routes

The known one-dimensional precedent is Izotov's fourth-power Sierpiński
construction, explained by Filaseta--Finch--Kozek.  It deletes one congruence
class from a finite cover and handles that class with `4X^4+1`.  This is
exactly Capell's exceptional cell, already tested in the algebraic-power lane;
it does not supply a second two-dimensional mechanism.

After N1--N4, a genuinely non-affine resolution would need at least one of:

1. a variable divisor identity not arising from a two-term Laurent/binomial
   factorisation;
2. infinitely many distinct prime divisors forming a cover of `N^2` with the
   profinite escape point of N2; or
3. a global primality obstruction (for example an order or reciprocity
   contradiction) that proves compositeness without producing a fixed divisor.

One deep pass through norms, cyclotomic/Aurifeuilian variants, composite and
prime-power moduli, recursive factor candidates, and order/reciprocity
obstructions produced no exact identity or lemma on a plausible route to the
full problem.  In particular, every finite modular proposal reduced by N1,
and every two-term algebraic proposal reduced by N3.

Relevant one-dimensional source:

- M. Filaseta, C. Finch, M. Kozek, *On Powers Associated with Sierpiński
  Numbers, Riesel Numbers and Polignac's Conjecture* (JNT 2008),
  <https://people.math.sc.edu/filaseta/papers/SierpinskiEtCoPapNew.pdf>.

## 5. Decision

The continuation gate required a concrete exact identity, construction, or
structural lemma with a plausible path to a full solution.  The exact lemmas
obtained are limitation theorems, not such a path.  Together with the failed
281-map robust gate, the exact Capell classification, the common-shear
obstruction, and the Vela modulus's certified prime hit, they support stopping
#203 for the one-week full-resolution objective.

**Recommendation:** reallocate active research away from #203.  Retain N1--N4
as fast rejection tests if a future proposal claims a new non-affine mechanism;
restart only when it exhibits an explicit variable-factor identity or an exact
recursive construction that demonstrably escapes these lemmas.

## Claim ledger

- **Full #203 result:** none.
- **New exact computational result:** the Vela partial-cover modulus has the
  certified prime term at `(1,8)` displayed above.
- **Proved structural results:** N1--N4.
- **Not proved:** that every #203 solution must have a finite prime cover, or
  that no solution exists.
- **Allocation conclusion:** stop this lane and the current #203 campaign.
