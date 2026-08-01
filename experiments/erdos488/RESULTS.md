# Erdős #488 (corrected multiples version): research log

Date: 2026-08-01.  FormalConjectures commit:
`735aee074327b8e78b0d92bb1ee8ea00937c3f51`.

## Exact target

For finite nonempty `A ⊆ {2,3,...}`, put

`F_A(x) = #{t ∈ [1,x] : a | t for some a ∈ A}`.

The target is `F_A(m)/m < 2 F_A(n)/n` for every
`m > n ≥ max A`.  This is the corrected multiples version, not the obsolete
non-multiples transcription.

## Prior results used (not new)

The March 20, 2026 Ulam/Chojecki note *Signed Transport, Pair–Tail
Reduction, and Low Layers in an Erdős Density-Doubling Problem* proves:

- primitive reduction and exact grouped-lcm inclusion-exclusion;
- an explicit fixed-`A` large-`n` criterion;
- primitive sets of size at most three;
- all layers `F_A(n)-|A| ≤ 5`, hence all `F_A(n) ≤ 9`;
- the dense case `F_A(n) ≥ n/2`;
- the triple-overlap-free criterion;
- singleton-vs-one-tail and pair-vs-one-tail split inequalities.

The note identifies pair-vs-two-tail as the first unresolved local split
case and proposes, in Conjecture 6.11, that the incidence inequality

`I_A(n)+|A| ≤ 2F_A(n)`, where `I_A(n)=Σ_a floor(n/a)`,

should hold in the sparse regime `F_A(n)<n/2`.

The June 2026 forum thread also proves the complete `min A = 2` case and
records a split-core tripod family.  Neither is used as a new claim here.

## New exact negative result: Conjecture 6.11 fails sparsely

Take

`A = {4,6,9,10,14,15,21,22,25,26}` and `n=91`.

This `A` is primitive.  Direct enumeration gives the 45 covered integers

`4,6,8,9,10,12,14,15,16,18,20,21,22,24,25,26,27,28,30,32,36,40,42,44,45,48,50,52,54,56,60,63,64,66,68,70,72,75,76,78,80,81,84,88,90`.

Thus `F_A(91)=45<91/2`.  Independently,

`I_A(91)=22+15+10+9+6+6+4+4+3+3=82`.

Therefore

`2F_A(91)-I_A(91)-|A| = 90-82-10 = -2`.

The excess is 35, so this is outside the known small-excess layers.  A
second audit by divisibility degree gives the histogram

`deg 0:46, deg 1:18, deg 2:20, deg 3:4, deg 4:3`.

It reproduces `F=18+20+4+3=45`, `I=18+40+12+12=82`, and the nongenerator
slack `Σ(2-deg)=-2`.

Z3 exact optimization with the constraints `2F<n` and `F-|A|≥6` found
nonnegative optimum for each `20≤n≤90` and optimum `-2` at `n=91`.
This establishes the displayed witness, but the claimed minimality is only
a computational result over the encoded range.

This does **not** refute Erdős #488.  For this same `A`, exhaustive direct
counting through `m=10^6` and `n≤1000` finds its largest tested density ratio
at `(n,m)=(95,442)`:

`F_A(95)=46`, `F_A(442)=226`, ratio `=95·226/(442·46)=1.055970883...`.

## Two tempting stronger routes that also fail

1. The unconditional incidence inequality already fails densely, e.g. the
   exact optimizer gives negative slack at `n=60`.

2. The weaker reciprocal majorant

   `Σ_{a∈A}1/a ≤ 2F_A(n)/n`

   also fails even while `F_A(n)<n/2`.  One structured exact example takes
   `A={2p : p≤499 is an odd prime}` (94 generators), `n=19960`, and has
   `F_A(n)=7861`, while

   `Σ 1/a ≈ 0.7983547764 > 2·7861/19960 ≈ 0.7876753507`.

   Direct bitset counting and exact rational summation were used.  This
   family explains the obstruction: many generators sharing a core can make
   reciprocal mass much larger than the actual multiples density.

3. The intermediate upper-half incidence lemma

   `Σ_a (floor(n/a)-floor(floor(n/2)/a)) ≤ F_A(n)`

   fails in the dense regime (an exact optimizer finds a failure at `n=120`).
   It survived sparse optimization through `n=150`, but no proof is known
   and it should not be treated as established.

## Computation and validation

- `search488.py`: direct bitset counting, independent grouped
  inclusion-exclusion, exact integer comparison, randomized exploration.
- `optimize_slack_z3.py`: exact optimization of the incidence slack.
- `optimize_counterexample_z3.py`: exact fixed-`(n,m)` SAT/optimization.
- `optimize_reciprocal_z3.py`: exact reciprocal-majorant experiments.
- `optimize_half_z3.py`: upper-half incidence experiments.
- `anneal_reciprocal.py`: randomized stress test only.

All witness comparisons use integers or `fractions.Fraction`; floating point
is used only for reporting/ranking.  `search488.py` checks bitset counts
against independent inclusion-exclusion for small generator sets.

## Status

The exact corrected theorem remains open in this investigation: no
counterexample and no complete invariant was found.  The concrete progress
is a sparse counterexample to the note's proposed exact bottleneck, which
removes one advertised route to a proof and shows that any successful
compression must exploit floor-position information more finely than total
incidence duplication.
