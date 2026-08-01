# Erdos Problem 196

## Target Statement

Prove or disprove the following exact statement: every permutation f of the natural numbers contains indices b1 < b2 < b3 < b4 such that f(b1),f(b2),f(b3),f(b4) form a four-term arithmetic progression in increasing or decreasing order.

Equivalently, for some positive d, the four values are x,x+d,x+2d,x+3d in this order or in reverse order.

## Research Contract

A positive solution must work for every infinite permutation of N. A negative solution must construct and prove bijective an infinite permutation avoiding both orientations. A long finite avoiding permutation, a randomized search, or a compactness claim without a compatible infinite construction is only partial progress.

The public Lean target is FormalConjectures/ErdosProblems/196.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. Its predicate HasMonotoneAP f 4 means there is a strictly increasing list of four indices whose image is an arithmetic progression of length four. Source: https://www.erdosproblems.com/196.

## Requested Output

Seek a complete structural proof or an explicit infinite construction. Test any claimed invariant on finite prefixes, but distinguish finite avoidance from the infinite theorem. If blocked, state the exact extension or compactness lemma that fails.

