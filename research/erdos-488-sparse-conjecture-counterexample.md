# A counterexample to the proposed sparse order-slack route for Erdős #488

## Result

This is **not** a counterexample to Erdős problem 488. It is a counterexample to Conjecture
6.11 in Przemysław Chojecki's 20 March 2026 partial-results note, which proposes that the
incidence inequality

    I_A(n) + |A| <= 2 F_A(n)

holds throughout the sparse regime. In the notation of that note, the inequality is the exact
sparse bottleneck (10), and Conjecture 6.11 asserts it for every primitive generator set.

Take

    A = {4, 6, 9, 10, 14, 15, 21, 22, 25, 26} and n = 91.

The set is primitive: no distinct members divide one another. Exact enumeration and independent
inclusion-exclusion both give

- F_A(91) = 45, so 2 F_A(91) = 90 < 91 and this is genuinely in the sparse regime;
- I_A(91) = sum(a in A) floor(91/a) = 82;
- |A| = 10; hence
- 2 F_A(91) - I_A(91) - |A| = 90 - 82 - 10 = -2.

The degree histogram on integers 1 through 91 is

    {0: 46, 1: 18, 2: 20, 3: 4, 4: 3}.

Thus the proposed inequality fails even with excess F_A(91)-|A| = 35, well beyond the
small-excess cases already proved in the note.

## Sanity check against the original problem

For this same A, an exact search through m = 1,000,000, with n <= 1,000, found its largest
tested density-growth ratio at (n,m)=(95,442):

    F_A(95)=46, F_A(442)=226, and
    (F_A(442)/442)/(F_A(95)/95) = 1.0559708833... < 2.

So the example kills this sufficient-condition strategy but gives no evidence against the
original density-doubling conjecture.

## Reproduction

From experiments/erdos488, import the exact routines in search488.py and evaluate
sparse_slack(A,91), which returns (45,82,35,-2). The prefix-bitset count is independently
checked by count_ie(A,91) = 45. The same module's worst_pair(A,1_000_000,1000) returns the
pair above and verifies both counts by inclusion-exclusion.

Source note: https://www.ulam.ai/research/erdos488.pdf

## Claim discipline

This campaign finding has not yet undergone a comprehensive priority search, so no novelty
claim is made. Its value here is operational: it prevents further effort from being spent on a
false intermediate conjecture.

The initially tempting weaker replacement also fails. If A consists of 2p for every odd prime
p <= 499 and n = 19960, then A has 94 primitive generators, F_A(n) = 7861 < n/2, but exact
rational arithmetic gives

    sum(a in A) 1/a = 0.798354776419... >
    2 F_A(n)/n = 7861/9980 = 0.787675350701....

Therefore the direct reciprocal-density majorant cannot prove the full problem either. The
original Erdős #488 statement remains neither proved nor refuted.
