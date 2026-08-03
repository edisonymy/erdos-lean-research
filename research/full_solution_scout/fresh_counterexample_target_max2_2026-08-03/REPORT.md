# Erdős #203: all-order-direction and algebraic-cell scout

Date: 2026-08-03

Status: **stopped at the precommitted gate; no solution claimed**.

## Exact problem

Find an integer `m >= 1`, coprime to 6, such that

```text
2^k 3^l m + 1
```

is composite for every pair of nonnegative integers `k,l`.

The public statement is Erdős Problems #203, citing Erdős--Graham (1980),
page 27.  The current Formal Conjectures endpoint has the same existential
`m`, coprimality condition, universal natural `k,l`, and negated primality.
Unlike a universal conjecture, a positive answer is the desired resolution.

## Priority and recency audit before computation

The live problem page was last edited 20 January 2026.  Its indexed snapshot
still says `OPEN`, reports no partial or complete solution in the comments,
and lists two users as currently working on it.  Consequently database status
alone is not treated as novelty evidence.  Announcement-level searches on
2026-08-03 covered the exact formula and problem number across web search,
arXiv-indexed results, GitHub, dissertations/repositories, and the named active
users.  They found no proof or explicit `m`.  A public May 2026 AI attempt
associated with `epassports` is not a solution: its asserted axiom assumes the
substance of the conclusion, and the present campaign had already corrected
ten alleged primes in a partial computation to explicit semiprimes.

Collision risk is nevertheless **medium/high** because the page identifies
active workers and a positive certificate can be announced quickly.  Repeat
this audit immediately before any public claim.

## Definition-level finite certificate

For a prime `q > 3`, let `H_q=<2,3>` in `F_q^*`.  The map

```text
phi_q(k,l) = 2^k 3^l (mod q)
```

is a homomorphism from `Z^2` onto `H_q`.  Select one value `c_q` in `H_q` and
impose

```text
m = -c_q^(-1) (mod q).
```

Then every lattice point in the fibre `phi_q(k,l)=c_q` gives
`q | 2^k 3^l m+1`.  If finitely many selected fibres cover `Z^2`, CRT gives
`m`; adding the product of all certificate primes makes `m` exceed each `q`,
so every divisor is proper, and adjoining `m=1 (mod 6)` gives `(m,6)=1`.
Thus the public problem is completely resolved by a finite fibre-cover plus
its CRT witness.  No search output is promoted without exhaustive cover
verification and an independent checker.

## Why this lane is not the old flat search

The existing campaign search fixed one common period (principally 720720)
and primes `q <= 10^6`.  It found 99 maps of total fibre-density 1.248958 and
still left 20.6004% of a 250,000-point sample uncovered after phase descent.
The present test instead enumerates **every** prime whose actual image order
is at most `R`, whether or not that order divides 720720.  Completeness is
elementary: if `|H_q|=r<=R`, then

```text
q | gcd(2^r-1, 3^r-1).
```

Factoring those gcds for every `r<=R` is therefore a complete small-order
census, not a prime cutoff.  An independent prime scan checks the census.

The complementary algebraic variant writes `m=A^N` for odd `N`.  For every
odd prime `p|N`, cells with `p|k` and `p|l` are automatically composite:

```text
2^k 3^l A^N + 1 = X^p + 1.
```

For a certificate prime `q`, a phase remains legal exactly when
`-c_q^(-1)` is an `N`th power modulo `q`.  Since `N` is odd, `-1` itself is an
`N`th power, so in primitive-root exponents this is the exact test
`gcd(N,q-1) | d_q * phase`.  In particular `N=3` automatically covers the
`k=l=0 (mod 3)` cell, while every `q=2 (mod 3)` retains full phase freedom.

## Precommitted kill criterion

After the promising pilot, the renewal gate was made stricter before the
robust run: continue to exact residual decomposition only if a fixed phase
assignment leaves **less than 5% uncovered on multiple independent seeds**
and the residual has a visible low-modulus/coset hierarchy.  Otherwise stop,
without enlarging the order bound or period.

The original screening rule had been:

1. the complete census through image order 1000, unioned with the old
   720720-period pool, leaves more than 5% of a robust random lattice sample
   uncovered after multi-start coordinate descent for the direct and tested
   odd-power variants; and
2. the residual has no low-modulus/coset concentration suggesting a finite
   recursive cover.

A sub-5% structured near miss is a renewal signal, not a theorem.  A zero on
a random sample is also not a theorem: it triggers exact hierarchical cover
verification.  No further order/period expansion is authorized merely because
the objective improved slightly.

## Exact census result

`pilot_order1000.json` records complete factorizations and product
reconstructions for

```text
gcd(2^r-1, 3^r-1),  1 <= r <= 1000.
```

It found 238 distinct primes with actual image order at most 1000, of total
reciprocal fibre density

```text
1.8304875993372494.
```

The old `period=720720, q<=10^6` pool has 99 primes and density
`1.2489579864579865`.  Their overlap has 56 primes.  The union therefore has
281 maps and density `1.8426865115361615`: an exact net gain of **182 maps**
and **0.593728525078175** density over the old pool.

No census prime exceeds 67,033.  Thus the gain did not come from removing the
one-million prime cutoff; it came entirely from image orders that do not
divide 720720.  The factorisations reconstruct every gcd and every displayed
factor is prime.  A separate scan over all primes through 67,033 reproduced
the same order-at-most-1000 prime set.  The factorisation argument, rather
than the scan limit, proves that no larger prime is omitted.

One status correction matters.  Earlier inherited notes called a roughly 72%
restricted-pool coverage value a proved ILP ceiling.  It was not certified:
the underlying CBC run established neither feasibility nor infeasibility, and
the remaining figures were greedy/simulated-annealing values.  This package
does **not** use or repeat that claim as a theorem.

## Bounded heuristic results and stop decision

The 50,000-point pilot gave the following best in-sample uncovered fractions:

| form of `m` | uncovered |
|---|---:|
| unrestricted (`N=1`) | 6.756% |
| `A^3` | 8.012% |
| `A^5` | 7.082% |
| `A^7` | 7.002% |
| `A^15` | 8.510% |
| `A^21` | 8.450% |
| `A^35` | 7.438% |
| `A^105` | 8.718% |
| `A^1155` | 8.942% |

The algebraic automatic cells did not compensate for their restricted CRT
phases, so those variants were retired.  The direct 6.756% pilot was close
enough to justify exactly one robust refinement.

That refinement falsified the apparent signal:

- a fresh 250,000-point, 25-restart direct run reached only 8.862% in-sample;
- the exact 6.756% pilot phase vector left 11.2864% uncovered on a new
  250,000-point sample, demonstrating substantial sample overfitting;
- bounded warm-start, perturbation, coordinate, and pair refinement reached
  9.0388% on its training sample;
- the fixed refined vector then left respectively **10.9900%**, **11.0360%**,
  and **10.9804%** uncovered on three fresh 250,000-point seeds;
- 120 eligible two-map refinement attempts produced no strict improvement.

The residual is not perfectly featureless: it occupies 12 of 16 cells modulo
4, 48 of 64 modulo 8, and 82 of 144 modulo 12 in the recorded validation
profile.  But the strict renewal gate required both such structure and a
cross-seed fraction below 5%.  The latter fails by more than a factor of two.
Accordingly the lane is **stopped**.  No exact cover candidate, CRT witness,
or full result exists, and no further order/period expansion is justified for
the one-week objective.

## Reproduction map

- `enumerate_and_optimize.py`: exact gcd-factor census, independent prime scan,
  legacy-pool union, and sampled direct/odd-power phase search.
- `pilot_order1000.json`: factor audit, all 281 maps, pilot phase vectors, and
  all odd-power pilot results.
- `robust_direct_order1000.json`: fresh 250,000-point direct multi-start run.
- `refine_direct.py`: bounded warm-start, perturbation, pair descent,
  cross-seed evaluation, and residual profiles.
- `warm_refine_direct.json`: decisive cross-seed failure and the first 5,000
  residual coordinates for possible theory-only reuse.
- `MANIFEST.json`: byte sizes and SHA-256 hashes.

The workspace-local temporary SymPy install
`.tmp/pydeps203` (74,233,579 bytes) and generated package `__pycache__`
(35,232 bytes) were removed after the run.  They contained no research data;
the JSON outputs and source scripts are retained.  Reproduction requires the
runtime versions recorded in `MANIFEST.json`.

## Claim ledger

- **Full result:** none.
- **Proved reduction:** a finite fibre cover and CRT witness imply a complete
  affirmative resolution, with the proper-divisor and coprimality safeguards
  above.
- **Proved census principle:** all primes with image order at most `R` occur
  among prime factors of `gcd(2^r-1,3^r-1)` for some `r<=R`.
- **Proved algebraic cells:** the odd-power factorisation described above.
- **Exact computational result:** complete image-order-at-most-1000 census,
  factor reconstructions, independent prime-scan agreement, and exact pool
  counts/density sums as recorded above.
- **Heuristic only:** every phase optimization, uncovered fraction, modular
  residual profile, and the allocation conclusion inferred from them.
- **Negative package:** the small-order direction expansion and tested
  algebraic-power masks did not pass the renewal gate; this is not evidence
  that #203 has a negative answer.

## Sources

- https://www.erdosproblems.com/203
- https://github.com/teorth/erdosproblems
- https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/203.lean
- P. Erdős and R. L. Graham, *Old and New Problems and Results in
  Combinatorial Number Theory* (1980), p. 27.
