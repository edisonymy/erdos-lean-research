# Clique-residual exclusion for a least counterexample

**Status (2 August 2026): independently verified by two campaign agents.**
This is a structural reduction, not a full solution of Erdos #151, and no
claim of literature priority is made.

## Lemma

Let `G` be a least-order counterexample on `n` vertices, let `h=H(n)`, and
put `r=h-1`, so `Delta(G)<=r`. Suppose `G` contains a clique `C` of size
`s>=2`. If

`n-s-(s-1)(r-s+1) >= R(3,h-s+1)`,                   (1)

then `G` cannot be a counterexample.

## Proof

Fix `c in C` and put `P=C\{c}`, so `|P|=s-1`. Each vertex of `P` already
has `s-1` neighbours in `C`, and hence has at most `r-s+1` neighbours
outside `C`. Therefore at least

`A=n-s-(s-1)(r-s+1)`

vertices outside `C` are anticomplete to `P`.

Under (1), choose exactly `R(3,h-s+1)` such vertices and let `F` be their
induced graph. It has fewer than `n` vertices, so least-order minimality gives

`beta(F) >= H(R(3,h-s+1)) >= h-s+1`.

Take an `F`-admissible set `S` of exactly `h-s+1` vertices. The set
`P union S` has size `h` and is admissible in `G`:

- a clique contained in `P` extends by `c`, so is not maximal in `G`;
- there is no mixed clique because `P` is anticomplete to `S`;
- if a `G`-maximal clique contained in `S`, then it would also be maximal in
  the induced graph `F` (an extender in `F` would be an extender in `G`),
  contradicting the admissibility of `S` in `F`.

This contradicts `beta(G)<=h-1`.

## Immediate window consequences

For `h=8`, `r=7`, `n in {28,29,30}`, and `s=5`, the left side of (1) is
`n-17`, namely 11, 12, or 13, while `R(3,4)=9`. Therefore every least
counterexample in the first open window is `K5`-free:

`omega(G) <= 4`.

This strengthens the earlier `omega(G)<=6` bound in `N28_NOTES.md` and is a
sound static constraint for the order-28/29 search.

For the next top window `h=9,n=36,r=8`, the same choice `s=5` gives
`36-5-4*4=15 >= R(3,5)=14`, again forcing `omega(G)<=4`. Combined with the
Ramsey-core ceiling `Delta(Q)<=6` from `TOP_WINDOW_RAMSEY_CORE.md`, this
eliminates a `K6` Ramsey core and leaves the sharp 6-chromatic critical case.
