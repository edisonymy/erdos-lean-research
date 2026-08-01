# Erdős Problem 366: exact audit and restricted power-subfamily exclusions

## Bottom line

No witness was found, and there is no global negative proof. Erdős Problem 366
remains open.

The completed new work here consists of two **restricted** exact exclusions:

- no solution with `n + 1 = x^3` for `2 <= x <= 2^32 - 1`;
- no solution with `n + 1 = x^4` for `2 <= x <= 2^32 - 1`.

Thus the excluded ranges inside those families extend respectively through

```
x^3 = 79,228,162,458,924,105,385,300,197,375
x^4 = 340,282,366,604,025,813,516,997,721,482,669,850,625.
```

These statements say nothing about general 3-full values of `n+1` which are
not perfect cubes or fourth powers.

## Statement audit

The pinned Lean source defines the right-hand side as

```lean
∃ n > 0, (2).Full n ∧ (3).Full (n + 1)
```

and `Nat.Full k n` is

```lean
∀ p ∈ n.primeFactors, p^k ∣ n
```

so the mathematical content is faithful: every prime exponent in `n` is at
least 2 and every prime exponent in `n+1` is at least 3. The `answer(sorry)`
wrapper records that this is a yes/no question; proving the existential would
settle it affirmatively.

The orientation matters. The familiar examples

```
8 = 2^3,        9 = 3^2
12167 = 23^3,  12168 = 2^3 * 3^2 * 13^2
```

have the 3-full integer first and the 2-full integer second, opposite to the
existential sought here.

## Known public computation, not new work

As of 2026-08-01, the [Erdős Problems entry](https://www.erdosproblems.com/366)
still marks #366 `VERIFIABLE Open`. It records, via
[OEIS A060355](https://oeis.org/A060355), an exhaustive list of consecutive
powerful pairs below `10^22`, with no pair in the orientation required here.

That unrestricted `n < 10^22` exclusion is prior public work. It is broader
than the computations in this directory below `10^22` and is not claimed as a
new result here. The only range extension in this package is for the explicitly
restricted perfect-cube and fourth-power subfamilies.

## Exact reductions used by the new searches

An integer is powerful exactly when it has the unique canonical form

```
a^2 b^3,  with b squarefree.
```

This gives an exhaustive, duplicate-free generator for powerful integers up to
a bound.

### The perfect-cube subfamily

Set `n + 1 = x^3`. Then

```
n = x^3 - 1 = (x - 1)(x^2 + x + 1)
gcd(x - 1, x^2 + x + 1) = gcd(x - 1, 3).
```

Away from the prime 3, the two factors must separately be powerful. If
`3 ∤ x-1`, both factors must be powerful. If `3 | x-1`, then
`v_3(x^2+x+1)=1`; after removing their powers of 3, both factors must be
powerful, while the combined 3-adic exponent is automatically at least 2.

Consequently every possible `x-1` is in exactly the searchable union

```
{powerful A} ∪ {3u : u powerful and 3 ∤ u}.
```

For each such value the adjusted factor `(x^2+x+1)` or
`(x^2+x+1)/3` was factored exactly and tested for powerfulness.

### The perfect-fourth-power subfamily

Set `n + 1 = x^4`. Then

```
n = (x-1)(x+1)(x^2+1).
```

The three factors are pairwise coprime away from 2. Therefore the odd part of
each factor must be powerful. Conversely, those three conditions suffice:
when `x` is even all factors are odd, while when `x` is odd

```
v_2(x^4-1) = v_2(x-1) + v_2(x+1) + v_2(x^2+1) >= 4.
```

The search thus exhaustively generates `x-1 = 2^e u` with `u` odd and
powerful, tests the odd part of `x+1`, and then tests the odd part of `x^2+1`.

## Exact runs

The executable uses:

- canonical `a^2 b^3` generation with an explicit squarefreeness sieve;
- deterministic Miller–Rabin bases valid for every unsigned 64-bit integer;
- exact Pollard-rho splitting, followed by a complete exponent check;
- fixed seed `366` (the seed affects factor-finding order, not the result).

Compilation:

```powershell
$compileLine = '"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul && cl /nologo /std:c++17 /O2 /EHsc experiments\erdos366\cube_subfamily.cpp /Fe:experiments\erdos366\power_subfamilies.exe'
cmd /d /s /c $compileLine
```

Runs:

```powershell
experiments\erdos366\power_subfamilies.exe --power 3 --xmax 4294967295 --seed 366 --hits experiments\erdos366\cube_hits_u32max.txt
experiments\erdos366\power_subfamilies.exe --power 4 --xmax 4294967295 --seed 366 --hits experiments\erdos366\fourth_hits_u32max.txt
```

| Family | Canonical powerful values | Candidates checked | Hits | Time |
|:--|--:|--:|--:|--:|
| `n+1=x^3` | 140,008 | 185,335 | 0 | 36.527 s |
| `n+1=x^4` | 140,008 | 176,737 | 0 | 0.296 s |

Exact output is preserved in `cube_subfamily_u32max.log` and
`fourth_subfamily_u32max.log`.

## Independent cross-check

`verify_subfamilies_small.py` does not use the C++ candidate reductions or its
factorizer. It directly asks SymPy to factor `x^3-1` and `x^4-1` for every
`2 <= x <= 10,000`. It independently found no hits in either family, agreeing
with the large search. See `verify_subfamilies_small.log`.

This is a sanity check, not an independent re-run of the full `2^32-1` range.

## Announcement-level collision audit

A narrow web audit was performed on 2026-08-01 using exact-phrase and
problem-number searches across general web results, GitHub-oriented results,
Zenodo-oriented results, and the public Erdős-problem trackers.

- The official/community [problem database](https://github.com/teorth/erdosproblems)
  still labels #366 `verifiable`, not solved.
- The Erdős Problems page, last edited 2026-04-15, still labels it open.
- No recent Zenodo deposit, GitHub repository, preprint, or AI-contribution
  announcement claiming a full solution to #366 was found in those searches.

This is only an announcement-level collision check, not a systematic literature
review and not evidence that unpublished or poorly indexed work does not exist.

## Files

- `cube_subfamily.cpp`: exact C++ search for powers 3 and 4.
- `verify_subfamilies_small.py`: independent direct-factorization cross-check.
- `verify_full.py`: exact SymPy verifier for a proposed unrestricted witness.
- `cube_subfamily_u32max.log`, `fourth_subfamily_u32max.log`: final run logs.

No file under `third_party/formal-conjectures` was modified.
