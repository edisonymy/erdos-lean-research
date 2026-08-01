# Erdos Problem 617

## Target Statement

Prove or disprove the following exact statement. For every integer r >= 3, every r-edge-coloring of the complete graph K_(r^2+1) contains a set S of r+1 vertices and a color k such that no edge induced by S has color k.

Equivalently, there is no r-coloring of K_(r^2+1) in which every (r+1)-vertex set sees all r colors.

## Research Contract

A full positive proof must handle every r >= 3. A full disproof may give one explicit r and one complete coloring certificate for which every (r+1)-set sees all colors. The cases r=3 and r=4 are known positive, so r=5 (a 5-coloring of K_26 with every 6-set seeing all five colors) is the first natural counterexample target. A heuristic construction, incomplete SAT run, or coloring verified on only sampled subsets is not a solution.

The public Lean target is FormalConjectures/ErdosProblems/617.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. The source problem is https://www.erdosproblems.com/617 and the original reference is Erdos--Gyarfas, Split and balanced colorings of complete graphs (1999).

## Requested Output

If disproving, provide an explicit symmetric edge-color matrix or concise construction plus an exhaustive verification argument. If proving, expose all Ramsey/extremal estimates. Otherwise report precise subcases eliminated and reusable constraints without claiming success.

