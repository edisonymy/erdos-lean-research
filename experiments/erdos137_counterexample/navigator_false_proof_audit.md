# Audit of the `erdos-navigator` claim for Erdős #137

This is a refutation of a competing proof claim, **not** a solution of Erdős
problem #137.

## Source

- Repository: <https://github.com/0bserver07/erdos-navigator>
- Claimed proof: <https://github.com/0bserver07/erdos-navigator/blob/main/.claude/examples/solution_attempt_137.md>
- Commit introducing the file:
  [`774d7430ed1eb1d867fd32a2fabac62b9ccf6a47`](https://github.com/0bserver07/erdos-navigator/commit/774d7430ed1eb1d867fd32a2fabac62b9ccf6a47)
  (2026-02-05)
- Audited against repository `main` at
  `6895cfc0d2e46dd990d1b234eeaf8f0f9c7e9a00`.

## Decisive counterexample to the key lemma

The claimed proof considers the positive solutions of

\[
v^2-2w^2=-1
\]

and asserts that every noninitial solution with
\(w\equiv\pm1\pmod 9\) has \(w\not\equiv1\pmod {25}\).  Starting with
\((v_0,w_0)=(1,1)\), enumerate the solutions by

\[
(v_{j+1},w_{j+1})=(3v_j+4w_j,\;2v_j+3w_j).
\]

After 29 recurrence steps this gives

\[
v_{29}=19175002942688032928599,
\qquad
w_{29}=13558774610046711780701.
\]

Exact integer arithmetic verifies

\[
v_{29}^2-2w_{29}^2=-1,
\qquad
w_{29}\equiv-1\pmod 9,
\qquad
w_{29}\equiv1\pmod {25}.
\]

Thus the stated key lemma is false.  The proof's appeal to a period modulo 45
cannot establish a congruence modulo 25.  A minimal reproduction is:

```python
v, w = 1, 1
for _ in range(29):
    v, w = 3*v + 4*w, 2*v + 3*w
assert v*v - 2*w*w == -1
assert w % 9 == 8
assert w % 25 == 1
```

## Other independent fatal gaps

1. The opening reduction "it suffices to prove \(k=3\)" is unsupported.
   Powerfulness is not monotone under taking subproducts: factors outside a
   three-term subblock can repair a prime that occurs to exponent one inside
   it.
2. From \(9\mid n\), the proof writes
   \(n=9\,2^a s^2\) with \(\gcd(s,6)=1\).  Necessary conditions on primes
   above 3 do not force the remaining 3-adic exponent to be even, so this
   omits the cases with odd \(v_3(n)\ge3\).
3. The assertion that the cases \(9\mid n+1\) and \(9\mid n+2\) follow by
   relabeling does not preserve the parity roles of the three terms and is not
   justified by the preceding case analysis.

Any one of the first two points is fatal; the explicit Pell value above
directly falsifies the proof's named key lemma.
