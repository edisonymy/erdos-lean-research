# Erdős #203: projective-power and recursive-cover theory lane

Date: 2026-08-03 (Europe/London)

Status: **stopped after one deep pass; no solution or CRT certificate claimed**.

This lane was deliberately complementary to the complete small-image-order
census in `../fresh_counterexample_target_max2_2026-08-03/`.  It did not
repeat that census or the flat phase searches.  It tested whether the fibres
could instead be assembled by a proof-shaped hierarchy: perfect-power
factorisation cells, projective refinement, or a lifted one-dimensional
Sierpiński covering.

## 1. Exact affine-fibre formulation

For a prime `q>3`, fix a primitive root `g`, write

```text
2 = g^e2,  3 = g^e3,
d = gcd(q-1,e2,e3),  h=(q-1)/d,
a=e2/d, b=e3/d.
```

Then `H_q=<2,3>=<g^d>` has order `h`, and one phase `t mod h`
covers exactly

```text
a k + b l = t (mod h).
```

Imposing `m = -g^(-dt) (mod q)` makes `q` divide the target term on
that fibre.  Distinct certificate primes give independent CRT conditions.
A finite cover of `Z^2` therefore gives a full positive solution after
choosing the CRT representative larger than every certificate prime and
congruent to `1 mod 6`.

This is a sufficient route to #203, not a claim that every possible solution
must have a finite set of recurring prime divisors.

## 2. Perfect-power rootability and the projective hierarchy

### Lemma P1 (exact rootability condition)

Suppose `m=A^R`.  Phase `t` at `q` is attainable by a choice of `A mod q`
if and only if

```text
gcd(R,q-1) | ((q-1)/2 - d t).
```

Indeed, writing `A=g^x`, the CRT condition is equivalent to

```text
R x = (q-1)/2 - d t (mod q-1),
```

and the displayed divisibility condition is the standard solvability
criterion for a linear congruence.  If `R` is odd, `gcd(R,q-1)` is odd and
already divides `(q-1)/2`, so the condition simplifies to

```text
gcd(R,q-1) | d t.
```

### Lemma P2 (projective localisation for a prime power)

Let an odd prime `p` divide `R`.  If `p|(q-1)` and `p` does not divide `d`,
then P1 forces `t=0 mod p`.  Hence the whole `q`-fibre lies inside the
homogeneous line

```text
a k + b l = 0 (mod p)
```

in `F_p^2`.  Meanwhile `p|k,l` is automatically composite because

```text
2^k 3^l A^R + 1 = X^p + 1.
```

Thus the power construction has a canonical first layer: the origin of
`F_p^2` is handled algebraically and the restricted prime fibres are sorted
among the `p+1` projective lines through it.  This is the precise connection
to refinement constructions in two-dimensional covering systems.

For `p=3`, the old 99-map pool has restricted global fibre densities

| normalised line | restricted density |
|---|---:|
| `(0,1)` | 0.075932401 |
| `(1,0)` | 0.085780886 |
| `(1,1)` | 0.195251970 |
| `(1,2)` | 0.233742646 |

and unrestricted density 0.658251.  Since the algebraic origin occupies one
third of each projective line, these figures do not create a coarse density
obstruction.  The same check on the enlarged 281-map pool also has ample
coarse capacity.  The obstruction is at finer levels, not at `F_3^2`.

### Lemma P3 (hard ceiling for the automatic odd-power cells)

If the odd prime divisors of `R` form `S`, their automatic cells have exact
density

```text
1 - product_{p in S} (1 - 1/p^2).
```

Even allowing every odd prime, this is at most

```text
1 - 8/pi^2 = 0.1894305...
```

because `product_{p odd}(1-1/p^2)=8/pi^2`.  So perfect-power factorisation
can remove at most about 18.94% of the exponent lattice by the `X^p+1`
mechanism.  The Sophie Germain identity adds the cell
`k=2 mod 4, l=0 mod 4` when `m` is a fourth power, but then fourth-power
rootability sharply restricts the usable prime phases.  The bounded tests in
`../erdos203_algebraic_cells_max_2026-08-03/` show that this trade did not
improve the direct construction.

## 3. A rigorous obstruction to the common-shear transplant

The cleanest proposed recursive construction was to transplant a standard
one-dimensional Sierpiński cover in the sheared coordinate `k+E l`.  A prime
map can participate in one common shear only when `3` is a power of `2`
modulo `q`.  In the notation above this is exactly `gcd(a,h)=1`, and its
required shear is

```text
e_q = b/a (mod h).
```

All selected maps must satisfy `E=e_q (mod h)`.  Reducing only modulo 12
already gives an exact density obstruction for the audited 281-map pool.
For a fixed residue `E0 mod 12`, a map can occur only if

```text
E0 = e_q (mod gcd(h,12)).
```

Summing `1/h` over every compatible linear map gives the following twelve
upper bounds:

| `E0 mod 12` | density upper bound |
|---:|---:|
| 0 | 0.490868 |
| 1 | 0.462867 |
| 2 | 0.519857 |
| 3 | 0.628838 |
| 4 | 0.574842 |
| 5 | 0.418335 |
| 6 | 0.523601 |
| 7 | **0.672498** |
| 8 | 0.502346 |
| 9 | 0.449512 |
| 10 | 0.492132 |
| 11 | 0.611879 |

Every row is strictly below 1, so no common-shear subfamily from this pool
even satisfies the elementary density necessary condition for a cover.
This kills the simplest exact one-dimensional transplant, including any
choice of its residue classes.  The calculation uses exact rational sums;
`verify_common_shear_bound.py` reconstructs them and
`common_shear_bound.json` records the exact numerators and denominators.

Scope is important: this does **not** rule out multiple shears, torsion-class
branching, primes beyond the audited pool, or the full affine-fibre ansatz.

## 4. Cylinder/refinement probe and why it did not renew

A second proposed hierarchy fixes `l mod T` and covers `k` within each row.
For a prime to be row-periodic it is natural to require `ord_q(3)|T`; the
required one-dimensional moduli then come from factors of
`gcd(3^T-1,2^n-1)`.  A directional scan through `q<=10^6` found the first
substantial raw capacities at `T=5040` (70 primes, reciprocal fibre density
1.05257) and `T=55440` (122 primes, density 1.19583).  These are search-pool
figures, not completeness claims.  They do not yield a small exact-cover
identity: the periods in the `k` direction remain heterogeneous, and the
common-shear subcase is ruled out above.  A genuine mixed-shear recursion
would therefore be at least as hard as the global phase problem, rather than
a short transplant of a known Sierpiński cover.

The independent compute lane supplied the decisive allocation evidence:

- the complete image-order-at-most-1000 census plus the legacy pool has 281
  maps and total density 1.8426865;
- the attractive 6.756% pilot residual overfit;
- a fresh 250,000-point multi-start run bottomed out at 8.862% in-sample;
- a fixed refined phase vector left 10.9900%, 11.0360%, and 10.9804%
  uncovered on three independent 250,000-point samples;
- the cube and other tested odd-power variants were worse.

The residual's missing cells modulo 4 are exactly one low-order affine stripe
(the stripe already covered by the unique order-4 map `q=5`), and analogous
low-modulus structure is dominated by the already-selected small fibres.
It is not a new uncovered coset that a factorisation identity can patch.

This fails the preregistered sub-5% renewal gate by more than a factor of two.
No exact cover identity, CRT witness, or rigorous obstruction to *all*
one-prime-one-fibre covers emerged.  Expanding another order bound would be a
return to the stopped flat-search regime, so this lane stops here.

## 5. Priority and source audit

The live Erdős Problems entry still states the exact problem as open, was
last edited 20 January 2026, and lists active workers; database status alone
is not novelty evidence.  Searches of the exact formula, problem number,
arXiv-indexed results, and current public repositories found no explicit `m`
or full certificate as of this audit.

Relevant adjacent work:

- A. Granville and F. Pappalardi, *Two dimensional covering systems and
  possible prime producing a^m-b^n*, arXiv:2601.10296 (15 January 2026),
  develops the two-dimensional covering framework and explicit homogeneous
  examples, but does not solve #203.
- J. E. Cremona and P. Koymans, *Lattice coverings and homogeneous covering
  congruences*, arXiv:2601.03212 (6 January 2026), proves the refinement
  structure for prime-power-index homogeneous lattice covers.  Its lattices
  are adjacent to P2, but #203 needs affine fibres with prime-realizability
  and one phase per prime.
- The public June 2026 #203 package by Animish Sharma is explicitly partial.
  Its inherited claim that the 5040 phase problem had been shown UNSAT is not
  certified: its CBC run found neither a feasible point nor an infeasibility
  proof, while greedy and simulated annealing are heuristic.  That status
  correction is preserved here.

Sources:

- https://www.erdosproblems.com/203
- https://arxiv.org/abs/2601.10296
- https://arxiv.org/abs/2601.03212
- https://github.com/Animish-Sharma/Erdos/tree/main/203

## Claim ledger

- **Full #203 result:** none.
- **Proved here:** P1, P2, P3, and the exact finite-pool common-shear density
  obstruction.
- **Exact computation here:** the rational modulo-12 capacity table, checked
  from all 281 serialized maps.
- **Heuristic only:** directional pool capacities and all residual/phase
  optimisation figures.
- **Allocation conclusion:** stop this lane; retain the lemmas as reusable
  construction filters if a qualitatively new mixed-shear identity appears.
