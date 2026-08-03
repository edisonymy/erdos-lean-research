# Root hostile audit: exclusion of the `a=10` equality layer

Date: 2026-08-03

## Verdict

**PASS for the exact stated scope.**  Conditional only on the already audited
incidence-kernel theorem and the named Győri--Li--Salia--Tompkins--Varga--Zhu
extremal theorem, the packet
`POSTPUBLICATION_PLUS7_A10_GATE_2026-08-03.md` proves

```text
d=2a+6  ==>  a<=9.
```

Consequently a lexicographically minimum counterexample of order `n>=34`
would satisfy

```text
d>=2a+7,
d>=ceil((2n+7)/3),
a<=floor((n-7)/3).
```

This is a stronger necessary condition on a hypothetical counterexample.  It
does **not** resolve Erdős problem #64 and it does not eliminate the seven
remaining equality orders `15,18,21,24,27,30,33`.

## Dependency chain

I rechecked the new argument against the previously audited public
incidence-kernel packet and the prior `+7` finite-window audit.  The relevant
established inputs are:

1. every minimum counterexample satisfies `d>=2a+6`;
2. under equality and `a>=6`, only the deficit-five and deficit-six kernel
   patterns survive;
3. the named extremal theorem excludes deficit-five kernels from order nine
   onward and deficit-six kernels from order eleven onward; and
4. the incidence kernel is simple, 2-degenerate, `C4`-free and `C8`-free.

At `a=10`, the deficit-five case is therefore already impossible.  The sole
remaining branch has a ten-vertex, fourteen-edge connected kernel `J`, with
minimum degree two, maximum degree four, and exactly twelve residual `D1`
vertices.  The multiplicity of color `v` is exactly `4-deg_J(v)`.  The
minimum-degree-two step is sound: deleting a degree-one kernel vertex would
leave a nine-vertex, thirteen-edge hereditary deficit-five graph, contrary to
the previously checked extremal bound.

## Kernel enumeration

The auditor invokes nauty `geng` with

```text
-q -c -d2 -D4 10 14
```

and independently parses graph6, tests 2-degeneracy, and searches for literal
cycles of lengths four and eight.  I inspected these routines and checked the
filter direction and graph6 bit order.  The cycle routine chooses the least
vertex of a cycle as its start; its `nxt > start` restriction therefore loses
no cycle.

The reproduced filter counts are

```text
4,502 raw connected records
4,427 2-degenerate records
124 additionally C4-free
4 additionally C8-free.
```

The four graph6 kernels, their degree sequences, and the exact raw-stream hash
agree with the frozen certificate.  The executable hash is
`64FA2D95BDAFF155CE0FC748D4CBA83A50E5FFB03E3ACC5F41D86581C0BBA7EF`.

## Residual-topology audit

In the remaining branch, `G[D]` has fourteen degree-one `D2` vertices and
twelve degree-two `D1` vertices.  Hence it is exactly seven paths, whose
endpoints are the fourteen distinct `D2` vertices, together with zero or more
`D1`-only cycles.  The independent integer-partition generator correctly
enumerates all nondecreasing path-internal lengths and all simple cycle
lengths summing to twelve.  Direct `C4` and `C8` residual cycles are excluded.
It produces 166 topologies with canonical hash
`A12E2D3EC56B46898D04335ED3F60418908C71269AAE8F1CFC16F3D56D426FC2`.

I checked the one-segment closure lemma at all endpoint types.  A residual
segment has internal vertices only in `D1`; a fixed-skeleton path has internal
vertices only in `A union D2`.  They are therefore internally disjoint, and
their union is a simple cycle.  This remains valid for zero-internal-vertex
paths and for equal colors, where the implementation uses two distinct `D1`
leaves attached to the same `A` vertex.  At order 36 the complete relevant
dyadic set is exactly `{4,8,16,32}`.

The implementation's distance conventions are also correct:

- a path with `lambda` internal `D1` vertices has endpoint distance
  `lambda+1`;
- a `D2` endpoint to internal position `i` has distance `i+1` from the left
  and `lambda-i` from the right;
- two internal positions have distance `|i-j|`; and
- on a residual cycle both complementary segment distances are tested.

All simple paths in the literal subdivided kernel are enumerated.  Rejecting
an assignment when *any* such skeleton path closes a dyadic cycle is a
necessary condition, not an unjustified sufficiency assumption.

The component-signature quotient retains exactly the used `D2` endpoint set
and the color-count vector.  Because different residual components share no
segment constraint, the final disjoint-set and exact-multiplicity dynamic
program is an exact join over this relaxed assignment space.  An empty relaxed
space therefore excludes every actual residual graph.

The transparent terminal obstruction matches the JSON:

- all cycle tables and all path tables of length at least three are empty;
- the two potential length-one paths for kernels 0 and 1 necessarily reuse
  the same endpoint pair, while kernels 2 and 3 have no length-one path; and
- in the sole remaining topology `(0,2,2,2,2,2,2)`, the legal length-two
  signatures omit a color whose target multiplicity is positive, separately
  for each of the four kernels.

## Reproduction and integrity

I replayed the frozen standard-library auditor against the pinned `geng.exe`.
It returned `VERIFIED_COMPLETE_NO_ASSIGNMENT` on all four kernels and all 166
topologies per kernel.  The replay output is byte-identical to the canonical
certificate.

```text
theorem packet
429345C2AACBF1B9294930716D827288169FF288D84123BFA6B57F7CE0AC6774

auditor
58C9CD0A105D593D9007D062617A48313E823380512F7942E6782E91F2DB42E5

canonical certificate and root replay
F3E39B881120A2B0FFDD7BCFE76E6778FDD2A38D2D3F66AE59745367E4767A25
```

The exploratory Z3 program is not used as a premise.

## Priority and status check

On 2026-08-03 I rechecked the live [Erdős problem #64
page](https://www.erdosproblems.com/64), exact-constant searches for
`2a+7` and `ceil((2n+7)/3)`, arXiv-focused searches for cubic abundance in
minimal Erdős--Gyárfás counterexamples, GitHub-focused searches, and broad
2026 proof/counterexample announcements.  The page still labels the problem
open.  The only directly overlapping structural paper found was Avery Carr,
[Every Minimal Counterexample to the Erdős-Gyárfás Conjecture is Predominantly
Cubic](https://arxiv.org/abs/2605.22844), which proves the earlier `4/7`
fraction and does not contain this exact strengthening.  No prior `+7`,
`a<=9`, or `n>=34` result was found.  This is a dated search-relative priority
check, not proof that unpublished or unindexed work does not exist.

## Publication boundary

The result is suitable for a narrowly scoped timestamped campaign update once
the frozen artifacts and this audit are committed.  Any public wording must
say that the equality layer at `a=10` has been excluded and that the general
problem remains open; it must not call this a solution of #64.
