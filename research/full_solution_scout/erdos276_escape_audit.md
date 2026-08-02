# Erdős 276: exact audit of the Ismailescu--Son escape gap

## Status

This note does **not** solve Erdős problem 276.  It verifies the finite part of
the 2014 Ismailescu--Son construction, isolates the missing infinite statement,
and records why a tempting modern covering-system reduction does not apply.

The public Formal Conjectures statement is faithful.  It asks for a Fibonacci-
like sequence of composite natural numbers satisfying

```text
for every N > 1, some sequence term is coprime to N.
```

This is much stronger than merely requiring the two seeds to be coprime.

## Exact zero-class reduction

Let `a_(n+2)=a_(n+1)+a_n` and suppose consecutive terms are coprime.  If a
prime `p` divides `a_r`, the addition formula gives

```text
a_(r+t) = F_(t-1) a_r + F_t a_(r+1)  (mod p).
```

Since `p` does not divide `a_(r+1)`, the indices of terms divisible by `p`
are exactly

```text
r modulo z(p),
```

where `z(p)` is the Fibonacci rank of apparition of `p`.  Therefore the
Formal Conjectures escape condition is equivalent to saying that no finite
collection of these particular residue classes covers the integers.  It is
also equivalent to the least prime factor being unbounded along a subsequence.

## What the 2014 construction proves

Ismailescu and Son take `p=1` and an explicit 129-digit `q`, with

```text
a_0 = 1 + q^2,   a_1 = 2q + q^2.
```

Every odd-index term factors as

```text
a_(2n+1) = (F_n + q F_(n+1)) (L_n + q L_(n+1)).
```

Their 30 prime congruences cover every even index modulo 5040.  The companion
checker verifies exactly that all 30 listed divisors are prime, divide the
stated Fibonacci numbers, satisfy every CRT/seed congruence, and cover every
even residue.  It also verifies that the seeds are coprime and that `a_5` is
coprime to the product of the 30 covering primes.  Thus the construction is
not invalidated by its own finite cover, but none of this proves escape from
an arbitrary finite set of other primes.

## Why the 616,000 theorem does not finish the proof

Restrict to an index progression `n=s+5040t` left uncovered by the 30-prime
system.  A compatible zero class modulo `z(p)` induces a class in `t` with
modulus

```text
z(p) / gcd(z(p),5040).
```

For `s=27`, exact computation gives `gcd(a_27,F_5040)=1`, so no induced
modulus is one.  However, distinctness already fails at induced modulus 13:

| prime | zero class | Fibonacci rank | induced class in `t` |
|---:|---:|---:|---:|
| 103 | 35 mod 104 | 104 | 11 mod 13 |
| 1951 | 357 mod 390 | 390 | 2 mod 13 |
| 3329 | 91 mod 208 | 208 | 10 mod 13 |

All primality, divisibility, and first-zero/rank claims in this table are
recomputed by the checker.  Consequently the theorem that every **distinct-
modulus** covering system has least modulus at most 616,000 cannot be applied.
Bounded-multiplicity results also do not help: no uniform multiplicity is
known here, and several ranks `13*g` with `g | 5040`, each potentially with
several prime divisors, collapse to the same induced modulus.

## A second closed route

For arbitrary seeds `A=a_0`, `B=a_1`, the binary quadratic forms describing
the odd and even doubled subsequences have discriminants

```text
4(A^2+AB-B^2)  and  4(B^2-AB-A^2).
```

They are negatives of one another.  Both can split over the rationals only
when both discriminants vanish, which would require `B/A` to be the irrational
golden ratio (apart from the zero seed).  Hence the odd factorization cannot
simply be mirrored to factor the even subsequence algebraically.

## Reproduction and sources

Run:

```powershell
.venv\Scripts\python.exe experiments\erdos276\audit_escape.py
```

Primary sources:

- Ismailescu--Son, [*A New Kind of Fibonacci-Like Sequence of Composite
  Numbers*](https://cs.uwaterloo.ca/journals/JIS/VOL17/Ismailescu/ism8.html)
- [Erdős problem 276](https://www.erdosproblems.com/276)
- Hough, [*Solution of the minimum modulus problem for covering
  systems*](https://annals.math.princeton.edu/2015/181-1/p06)

The campaign's recency audit through 2 August 2026 found no proof or
counterexample.  A public annotation that labels Graham's 1964 coprime-seed
construction as a solution conflates coprime seeds with the much stronger
escape quantifier: Graham's finite covering primes themselves give an integer
having a common factor with every term.
