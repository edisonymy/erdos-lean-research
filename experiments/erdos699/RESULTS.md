# Erdős Problem 699: audit and attack results

Date: 2026-08-01

## Outcome

No proof or counterexample to the full problem was found.  The problem remains
open.  This directory contains two fully proved reductions, a Lean-checked
sufficient condition, and two reproducible finite searches.  None of those is
presented as a solution.

## Exact target and fidelity

The pinned source is
`FormalConjectures/ErdosProblems/699.lean` at Formal Conjectures commit
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`.  Its main theorem asks whether

> for every `n i j : ℕ` with `1 ≤ i`, `i < j`, and `j ≤ n / 2`, there is a
> prime `p` with `i ≤ p` and
> `p ∣ gcd (choose n i) (choose n j)`.

This is faithful to Conjecture 1 on page 97 of Erdős--Szekeres (1978): they
write the same range `1 ≤ i < j ≤ n/2` and ask whether the greatest prime
factor of the gcd is at least `i`.  Natural-number division by two correctly
implements the floor implicit in the informal statement.  Since the hypotheses
make the gcd nontrivial, the greatest-prime-factor formulation and the
existential-prime formulation agree.

Primary source:

- P. Erdős and G. Szekeres, *Some number theoretic problems on binomial
  coefficients* (1978), <https://www.renyi.hu/~p_erdos/1978-46.pdf>.
- Current problem record: <https://www.erdosproblems.com/699>.

As of 2026-08-01, the problem record labels the problem **FALSIFIABLE** and
open.  It explicitly warns that the open label reflects the site owner's
current belief.  The site reports five comments and no accepted resolution.

### Audit trap

The same Lean file contains a different theorem, `sylvester_schur`: every
individual `choose n i` has a prime divisor `p > i`.  That auxiliary theorem is
linked to a formal proof.  It does **not** prove that the same prime divides
`choose n j`.  A recent automated fidelity dashboard consequently marks #699
"done" by selecting `Erdos699.sylvester_schur`; that status is not a proof of
`Erdos699.erdos_699`.  This is a theorem-selection/scope error, not a defect in
the main Lean statement.  Audit record:
<https://erdos.constellate.science/finding.html?n=699>.

## Rigorous reductions

Write

`G = gcd(C(n,i), C(n,j))`.

### 1. The weak/strict boundary reduction

For every fixed triple `(n,i,j)`, purely by trichotomy of natural numbers,

`(∃ prime p ≥ i, p ∣ G)`

is equivalent to

`(∃ prime p > i, p ∣ G) ∨ (i is prime ∧ i ∣ G)`.

This is formally proved as `weak_iff_strong_or_boundary` in `Sanity.lean`, with
no `sorry` and only Lean's standard foundational axioms reported by
`#print axioms`.

Consequences:

- When `i` is composite, the weak and strict statements are identical.
- A strict-form exception can satisfy the weak conjecture only through the
  boundary prime `p=i`.
- A weak counterexample is exactly a strict counterexample for which `i` is
  composite or `i` does not divide the common gcd.

All eight currently known strict exceptions have prime `i` and are rescued by
the boundary prime:

| `(n,i,j)` | exact gcd | `n mod i²` |
|---|---:|---:|
| `(10,3,5)` | `12` | `1` |
| `(16,2,6)` | `8` | `0` |
| `(28,3,14)` | `36` | `1` |
| `(28,5,14)` | `1080` | `3` |
| `(244,3,122)` | `324` | `1` |
| `(512,2,147)` | `256` | `0` |
| `(2048,2,713)` | `1024` | `0` |
| `(2188,3,1094)` | `2916` | `1` |

In every row `n mod i² < i`, exactly as the boundary Kummer criterion predicts.

### 2. Exact Kummer criteria at and above the boundary

Kummer's theorem says that a prime `p` divides `C(n,k)` exactly when subtracting
`k` from `n` requires a borrow in base `p`; equivalently, for some `a ≥ 1`,

`k mod p^a > n mod p^a`.

It gives two useful exact simplifications.

- If `p > i`, then `i < p`, so
  `p ∣ C(n,i) ↔ n mod p < i`.
- If `p = i` is prime, then
  `i ∣ C(n,i) ↔ n mod i^2 < i`.

The second equivalence follows because the base-`i` representation of the
lower index `i` is `10`: the units digit cannot cause a borrow, and the
`i`-digit causes one exactly when the last two digits of `n` encode a number
smaller than `i`.  If this fails at `i^2`, it fails at all higher powers as
well.

Thus the open problem is reduced exactly to a digit-covering assertion: for
each admissible `(n,i,j)`, either a prime `p>i` satisfies

`n mod p < i`

and also triggers a Kummer borrow for `j`, or `i` is prime,
`n mod i^2 < i`, and `i` triggers a Kummer borrow for `j`.

This is a reformulation, not a resolution; the hard step is proving that the
required prime covers every `j`.

### 3. A Lean-checked sufficient short-interval condition

If `(n-i,n]` contains a prime `p`, then the full target holds for every
`i<j≤n/2`.  Indeed, these inequalities imply

`i < p`, `j < p`, `n-i < p`, and `n-j < p`.

The standard prime-divisibility lemma for binomial coefficients then gives
`p ∣ C(n,i)` and `p ∣ C(n,j)`.  This is proved in `Sanity.lean` as
`target_of_prime_in_final_interval`, via the more general lemma
`large_prime_suffices`.  It uses no result from the benchmark's sorry-bearing
problem file.

This condition is useful but cannot settle the problem: prime gaps can be
longer than a given small `i`.

## Exact computations

Finite verification is evidence only.  It does not prove the universal claim.

### Independent arbitrary-precision reference run

`verify_exact.py` constructs the binomial row with Python arbitrary-precision
integers.  For each `i` it tests every prime `p` with `i≤p≤n` that divides the
literal integer `C(n,i)`, and checks divisibility of the literal integer
`C(n,j)`.  It computes the literal gcd for every reported exception.  (No prime
larger than `n` can divide a binomial coefficient, since it is a quotient of
factors from `n!`.)

Command:

```powershell
python experiments\erdos699\verify_exact.py --max-n 1000 \
  --output experiments\erdos699\exact_N1000.json
```

Result:

- all `41,541,750` admissible pairs with `n≤1000` checked;
- zero weak counterexamples;
- exactly six strict exceptions:
  `(10,3,5)`, `(16,2,6)`, `(28,3,14)`, `(28,5,14)`,
  `(244,3,122)`, `(512,2,147)`;
- their exact gcds are recorded in `exact_N1000.json`.

### Independent Kummer run

`kummer_search.cpp` uses only the exact residue/borrow criterion above.  Its
output agrees identically with the arbitrary-precision implementation through
`n=1000`.  A larger run gave:

- all `1,123,875,250` admissible pairs with `n≤3000` checked;
- zero weak counterexamples;
- exactly eight strict exceptions, adding
  `(2048,2,713)` and `(2188,3,1094)` to the preceding six.

The log is `kummer_N3000.log`.

Rebuild and run on Windows:

```powershell
$compileLine = '"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul && cl /nologo /std:c++17 /O2 /EHsc /W4 experiments\erdos699\kummer_search.cpp /Fe:experiments\erdos699\kummer_search.exe'
cmd /d /s /c $compileLine
cmd /d /c "experiments\erdos699\kummer_search.exe 3000 > experiments\erdos699\kummer_N3000.log 2>&1"
```

### Novelty and collision check

These finite ranges are not novel.  A public SciNet finding dated 2026-07-22
reports an exhaustive Kummer-based run through `n=100000` (about 41.7 trillion
pairs), zero weak counterexamples, and the same eight strict exceptions:
<https://api.scinet.pub/f/76626b5c-caf4-4c69-bb03-4507e376a274>.
That finding supplies code and data but was still marked as awaiting independent
review when inspected.  Our smaller arbitrary-precision implementation is
algorithmically independent and reproduces its initial exception census; it
does not improve the published bound.

## Formal verification

`Sanity.lean` contains:

- `weak_iff_strong_or_boundary`;
- `large_prime_suffices`;
- `target_of_prime_in_final_interval`;
- a kernel-checked certificate that the famous strict exception
  `(28,5,14)` satisfies the weak target with `p=5`.

Compile from the Formal Conjectures checkout:

```powershell
& "$env:USERPROFILE\.elan\bin\lake.exe" env lean \
  '..\..\experiments\erdos699\Sanity.lean'
```

The proof file contains no `sorry`, no custom axioms, and no `native_decide`.
The explicit certificate computes
`gcd(C(28,5),C(28,14)) = 1080 = 2^3·3^3·5` inside Lean.

## Remaining barrier

Sylvester--Schur supplies at least one prime `p>i` dividing `C(n,i)`, but it
does not say that this `p` divides `C(n,j)`.  If `p>j`, the Kummer criterion
makes common divisibility automatic; therefore a counterexample must force all
useful Sylvester--Schur primes into the narrow range `(i,j]` and make every one
miss `C(n,j)`.  Ruling out that simultaneous digit-avoidance condition is the
unresolved core.

The reductions here are elementary and are not claimed as new mathematics.
The Lean packaging of them is new to this local campaign, but no priority or
publication claim is made.
