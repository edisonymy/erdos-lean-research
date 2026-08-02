# Addendum: triangle-free finish for order-41 `omega=5` row D

**Date:** 2 August 2026.  **Status: post-audit strengthening.**

This addendum preserves the independent PASS audit of
[`ORDER41_K5_DOUBLE_SATURATION.md`](ORDER41_K5_DOUBLE_SATURATION.md) as a
point-in-time audit while recording a strictly shorter dependency chain.
It does not edit or supersede the audit.  The original repaired 17-core
route remains valid independent corroboration.

## Point-in-time binding

The PASS audit examined these immutable revisions:

```text
ORDER41_K5_DOUBLE_SATURATION.md
  277b65c4956b56298c76a5e08ed3daf31af040033b4fb001550db3831f7955ca
checks/double_saturation/check_double_saturation.py
  be3cf20744516eaac13e0bb29dee47377ea4b66a33269c659dd0639a8a865951
ORDER41_K5_DOUBLE_SATURATION_AUDIT.md
  760a2a904e6416e907fac2c569298704a41f216f2a3b53e5321820f3163d6d4d
```

The strengthened source and new isolated checker are:

```text
ORDER41_K5_DOUBLE_SATURATION.md
  8353be6fde22d8e6edeb455187169b5eae4f6093ae971debcae353e7debddebd
checks/double_saturation_trianglefree/check_trianglefree_12_profile.py
  68a73ad39d1a4f3857b512b23bb85b90b3cfc73a58784f4c82d5a5e53eb1a325
```

The addendum intentionally does not state its own hash.

## Strengthening

The audited saturation argument proves unconditionally under row D that

```text
e(U)<=10.
```

The new elementary lemma proves:

> Every triangle-free graph on 12 vertices with independence number at most
> five has at least 11 edges.  Equality occurs exactly for
> `C5 disjoint-union C5 disjoint-union K2`.

Its proof uses only component count, total cyclomatic number, parity, the
tree and unicyclic independence bounds, and the theta/figure-eight/dumbbell
classification of a bicyclic 2-core.

Conditional on completeness of the pinned seven-record Ramsey `(3,6;17)`
catalogue, the already proved order-17 residual lemma makes each full row-D
residual triangle-free.  Therefore its induced common core `U` is
triangle-free; residual beta five also gives `alpha(U)<=5`.  The new lemma
forces `e(U)>=11`, contradicting the audited `e(U)<=10`.

Thus the strengthened exclusion depends on catalogue completeness only
through the order-17 triangle-freeness lemma.  It does **not** depend on
enumerating dominating partitions, common-core isomorphism classes,
automorphism-closed degree patterns, or the 17 D survivors.

## Independent corroboration retained

The earlier route remains sound:

```text
catalogue completeness + repaired D17 overlap enumeration
  => e(U) in {20,21,22}
  => contradiction with e(U)<=10.
```

It is logically independent of the new 12-vertex sparse lemma after the
shared premises and provides finite corroboration; it is no longer required
for the row-D exclusion.

## CHECKED boundary

The new standard-library checker exhausts 150 sparse component profiles, 16
two-component equality profiles, 30 two-unicyclic profiles, and 165
bicyclic order profiles.  It directly verifies that
`C5 disjoint-union C5 disjoint-union K2` has order 12, 11 edges, no triangle,
and independence number five.  It prints `status: CHECKED`.

The checker is a finite guard for the proof profiles, not an all-graph
enumeration.  The bicyclic 2-core dichotomy is proved analytically in the
source.  Neither the source nor this addendum proves external catalogue
completeness, a whole-graph UNSAT statement, the full order-41 theorem, or
Erdos problem #151.  No Git, publication, novelty, or priority claim is
made.
