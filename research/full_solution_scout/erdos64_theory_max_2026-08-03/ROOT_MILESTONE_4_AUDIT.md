# Root audit: universal six-unit cubic abundance

Date: 2026-08-03

## Verdict

**PASS.** The theorem in `MILESTONE_4_UNIVERSAL_PLUS6.md` survived two
independent line-by-line audits and two separate exact finite-kernel probes.
No computation or literature theorem is used in the proof.

For a lexicographically minimal counterexample to Erdős problem #64, let

```text
D = {v : deg(v)=3},       A = {v : deg(v)>=4},
d = |D|,                  a = |A|.
```

The verified conclusion is

```text
d >= 2a+6,
d >= ceil((2n+6)/3) = ceil(2n/3)+2,
a <= floor((n-6)/3).
```

This is a necessary condition on a hypothetical counterexample and does
**not** resolve the Erdős--Gyárfás conjecture.

## Inherited chain rechecked

1. Minimum order and then minimum size imply that every proper subgraph has
   minimum degree at most two.
2. The high-degree set `A` is independent and every vertex has a cubic
   neighbour.
3. Suppressing each cubic vertex with two `A`-neighbours produces a simple,
   dyadic-free, 2-degenerate incidence kernel `J` on `A`.
4. A simple `C4`-free 2-degenerate graph on `a>=4` vertices has at most
   `2a-4` edges, and at most `2a-5` for `a>=6`.
5. The exact incidence identities first yield `d>=2a+4` universally and
   `d>=2a+6` for `a>=6`.

The earlier root audit and an independent agent both passed this chain.

## Two-step lemma

Put `R=G[D]` and color each `D_1` vertex by its unique neighbour in `A`.
If `u-z-w` is an `R`-path with `u,w in D_1`, then equal colors give the
four-cycle through their common `A`-neighbour. If distinct colors
`alpha,beta` have a common kernel neighbour `gamma`, the two `D_2` vertices
encoding `alpha-gamma` and `beta-gamma` complete a simple eight-cycle.
Distinctness is sound because a `D_2` vertex has degree one in `R` and cannot
be the middle vertex `z`.

## Slack-five arithmetic

For the only remaining candidate equality `d=2a+5`, define

```text
x = e(A,D)-4a,
y = 2d-e(A,D).
```

Then

```text
x+y=10,
d_2=2a-5+d_0+x,
d_1=10-x-2d_0.
```

The internal degree sum is `d+y`, so `y` is odd because `d` is odd; hence
`x` is odd. Simplicity and the kernel edge bounds leave exactly the profiles
listed in Milestone 4.

## Highest-risk finite case

For `a=2` with one kernel edge, `R` has one degree-three vertex `z`, one
degree-one vertex `e`, and seven degree-two colored vertices. Component
parity puts `z,e` in one unicyclic component. Separate colored cycles are
excluded by their distance-two graphs. The pendant path from `e` to `z` has
exactly one colored internal vertex, leaving the cycle

```text
z,c1,c2,c3,c4,c5,c6,z.
```

The colored distance-two constraints form precisely the path

```text
c2-c4-c6-c1-c3-c5.
```

Every non-alternating two-coloring gives a same-colored distance-two pair
and hence a `C4`. In either alternating coloring, `c2,c3` have the same
color. Their complementary arc has six edges; adjoining the two edges
through their common `A`-neighbour gives a simple `C8`. An independent
exhaustion of all `2^6` colorings confirmed this dichotomy.

## Capacity cases

- For `J=P3`, the internal `D_1` degree count forces at least seven vertices
  with two `D_1` neighbours, but the at most three middle-colored vertices
  have total degree capacity six.
- For `J=K3`, no vertex can have two `D_1` neighbours. Seven required
  outside incidences face capacity four from `D_2` and `D_0`.
- For the paw, at least five vertices need the unique allowed centre--leaf
  neighbour-color pair, but at most two centre-colored vertices have total
  capacity four.
- For the friendship kernel, no vertex can have two `D_1` neighbours. Nine
  required outside incidences face capacity six from `D_2`.

The audit explicitly checked that an edge serving two counted endpoints is
charged twice on both sides, so none of these bounds loses a factor of two.

## Computational corroboration

`slack4_finite_probe.py` and `slack5_finite_probe.py` independently encode
the classified finite kernels with exact degrees and lazy `C4/C8/C16`
blocking. The former returns UNSAT on all seven slack-four cases. The latter
enumerates all twelve non-isomorphic excess placements for `a=1,...,5` and
returns UNSAT on all twelve. No `C16` cut was required. These solver results
are corroboration only and are not premises of the theorem.

## Priority boundary

The primary source comparison is Avery Carr, *Every Minimal Counterexample
to the Erdős--Gyárfás Conjecture is Predominantly Cubic*, arXiv:2605.22844
(13 May 2026), which proves a `4/7` cubic proportion. Exact-constant,
exact-title, arXiv, and broad web searches on 3 August 2026 found no prior
`2a+6`, `ceil(2n/3)+2`, or incidence-kernel statement in this setting. This
is a search-relative noncollision check, not a guarantee about unpublished
or unindexed work.
