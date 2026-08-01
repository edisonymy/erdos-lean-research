# Erdős problem 196: Rethlas negative attempt

## Outcome

**No proof or counterexample was obtained.** Rethlas used three attempts. Attempt
3 consumed **252,802 tokens**, wrote an unverified working blueprint, and produced
no accepted verifier verdict and no `blueprint_verified.md`. The agent did not
submit a completed proof to the verifier; the runner nevertheless auto-called
the verifier after attempt 3 and wrote `verification_attempt_3.json` containing
`Internal Server Error`. That failed call does not change the mathematical outcome.

This directory is a corrected audit of that attempt. It makes no novelty claim,
no Lean claim, and no claim that Erdős problem 196 has been solved.

The target is intrinsically infinite: a negative solution must give one
bijective infinite permutation avoiding both orientations, while a positive
solution must handle every infinite permutation. Finite avoiding prefixes,
random search, or an unproved compactness/extension assertion cannot resolve it.

## Target and the natural-number convention

Formal Conjectures states

```lean
∀ (f : ℕ ≃ ℕ), HasMonotoneAP f 4
```

where Lean's `ℕ` is `ℕ₀ = {0,1,2,…}`. The Rethlas prompt and blueprint mostly
use `ℕ₊ = {1,2,3,…}`. The two versions are equivalent by conjugating a
permutation with the translation `n ↦ n+1`; shifting every index and value by
one preserves strict index order and arithmetic progressions. They are not,
however, interchangeable inside formulas without applying that conjugacy.

Conventions used below:

- formal convention: `ℕ₀`, with an affine ray `u+n d` normalized to `n`;
- positive convention: `ℕ₊`, with the same ray normalized to `n+1`;
- every ray or progression difference satisfies `d ≥ 1`.

This distinction corrects several statements in the ignored blueprint.

## Lemma-by-lemma audit

### Inverse-position order — accepted

For a bijection `f`, let `p=f⁻¹`. A monotone four-term AP exists exactly when
there are `x` and `d≥1` for which

```text
p(x) < p(x+d) < p(x+2d) < p(x+3d)
```

or all inequalities reverse. In the formal target a nominal zero difference is
impossible because the four strictly increasing indices have four distinct
images under the injective `f`.

### Affine-ray inheritance — accepted after correction

The induced order on any ray `{u+n d : n≥0}`, `d≥1`, is again an
omega-enumeration and inherits avoidance. The blueprint omitted the essential
`d≥1` qualifier and normalized to `n+1` while calling the codomain simply
`ℕ`. Use `n` for `ℕ₀` and `n+1` for `ℕ₊`.

### Normalize the first two values — accepted only in its matching convention

Under the positive convention, the two ray restrictions in the blueprint
correctly show that a hypothetical counterexample can be normalized to begin
`1,2`. Under the formal `ℕ₀` convention, the corresponding conclusion is that
it can begin `0,1`: first restrict to a ray from the first value and normalize
to start at zero; if the second normalized value is `b>0`, restrict to
`{n b:n≥0}`. Therefore the literal `1,2` claim is rejected as a statement about
the unshifted Lean target, though its translated positive version is valid.

### Late monotone three-term progression — valid in `ℕ₊`; translated for `ℕ₀`

The statement for the numerical tail `{M,M+1,…}` with `M≥1` is true. The
blueprint consistently normalizes its affine ray to the positive convention
`n+1`; in that convention its first value is positive and its division step is
valid. The proof cannot merely be reinterpreted in unshifted `ℕ₀`, where the
first normalized value may be zero.

For an `ℕ₀` presentation, first translate back to the original positive tail.
Read that tail in occurrence order and let `a≥M` be its first value. Restrict to
`{a,2a,3a,…}` and divide by `a`; this positive permutation begins with `1`.
If its second value is `b>1`, then `2b-1` occurs later, and
`1,b,2b-1` is a monotone three-term AP. Scaling back by `a` keeps every term
in the tail.

### Endpoint obligations — accepted after explicit hypotheses

With `d≥1`, the first implication is immediate: after three increasing
positions, the fourth AP endpoint must occur before the third. For the reverse
extension, `x>d` is the correct positivity condition in `ℕ₊`. In `ℕ₀` it may
be weakened to `x≥d`, allowing endpoint `x-d=0`. The blueprint's stronger
inequality remains valid but is convention-specific.

### First-two forcing on a ray — accepted after clarification

Assume `h≥1`, `A` is the earliest occurring member of its ray, and `A+h` is
the earliest occurring ray member other than `A`. Then both `A+2h` and
`A+3h` occur later. Their order cannot be `A+2h` then `A+3h`, so avoidance
forces

```text
p(A) < p(A+h) < p(A+3h) < p(A+2h).
```

The blueprint's phrase “earliest later ray member” needed this precise meaning.

### Parity coupling — valid in `ℕ₊`; translated formulas for `ℕ₀`

Each parity subsequence inherits avoidance. The displayed formulas in the
blueprint are the **positive-integer** coordinates and need their domain
constraints:

- odd first `2a-1`, even second `2b`, with `b≥a`, gives
  `(a,b,2b-a+1,3b-2a+1)`;
- even first `2a`, odd second `2b-1`, with `b≥a+1`, gives
  `(a,b,2b-a-1,3b-2a-1)`.

For the formal `ℕ₀` coordinates the signs attach to the opposite starting
parity:

- odd first `2a+1`, even second `2b`, with `b≥a+1`, gives
  `(a,b,2b-a-1,3b-2a-1)`;
- even first `2a`, odd second `2b+1`, with `b≥a`, gives
  `(a,b,2b-a+1,3b-2a+1)`.

Thus the blueprint formulas are valid in their positive convention once the
domain constraints are explicit. A direct statement about the formal target
must instead use the displayed `ℕ₀` formulas. Neither algebraic encoding by
itself links the two subsequence orders strongly enough to solve the problem.

## Exact obstruction: global linkage

The surviving local arguments force patterns such as `1,2,4,3` on individual
affine rays. They do not force those reversals to interact in a common bounded
rank region. Infinitely many forced reversals may, for all the lemmas show, lie
in pairwise disjoint position intervals that move successively upward. This
produces neither

- an infinite strictly descending chain of natural-number positions, nor
- infinitely many distinct predecessors of one fixed value.

Restricting again to a parity class or affine ray only recreates an isomorphic
copy of the original problem; it supplies no smaller well-founded parameter.
The missing theorem would have to turn the overlapping *value* structure of
the rays into unavoidable overlap in *position* rank. No such global-linkage
lemma was proved, and asserting it by compactness would simply assume the hard
part.

## Finite computations retained

`finite_checks.py` is a small standard-library-only falsification harness. It
reproduces the useful negative finite observations without copying the large
ignored Rethlas logs. Its AP detector accepts Lean's zero-based naturals; the
retained dyadic and greedy constructions intentionally use positive values:

- two dyadic-folding candidate prefixes already contain explicit monotone
  four-term APs;
- the numbers of avoiding whole-block orders for 1 through 8 levels are
  `1,2,4,6,8,10,12,14`;
- repeatedly appending the newly largest block has no survivor from level 3;
- a least-safe increasing greedy sequence avoids a monotone 4-AP for 200
  selected values but permanently misses `4` and 752 other values below its
  maximum, so it is not a permutation.

Run from the workspace root:

```powershell
python experiments/erdos196/finite_checks.py
```

These are finite rejection tests only. They provide no infinite extension or
surjectivity result.

## Recency and prior-work boundary

The announcement-level audit dated 2026-08-01 found that
`Sageder/erdos-196`, created/updated on 27 July, was empty. It found no
mathematical collision and retained #196 only as a monitored target. The
candidate survey likewise flags the principal boundary: finite avoidance data
cannot resolve this intrinsically infinite problem.

That audit is not evidence of priority. Its protocol requires rechecking the
live problem page/history/comments, VibeMathed, recent GitHub code and
repositories, Formal Conjectures issues/PRs, Zenodo, arXiv, SciNet/Constellate,
and primary literature before any publication. Absence from one index cannot
support a novelty claim, and unpublished or poorly indexed work may exist.

## Formal-verification status

No lemma above was translated into a tracked Lean proof in this attempt. There
was no kernel build, no `#print axioms` audit, and no formal theorem. The public
Formal Conjectures file remains an `answer(sorry)` research statement. The
audited reductions should be treated as informal mathematics until separately
formalized and reviewed.
