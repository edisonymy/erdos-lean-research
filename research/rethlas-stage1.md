# Rethlas stage-one campaign

This campaign uses the public Rethlas runner at pinned commit 622bc663d4212333ade4c4802af1db3da92262c0 as an idea-generation and informal-referee harness. It is deliberately non-blind (BLIND_RUN=0) because the targets are currently open and no historical benchmark isolation is being claimed.

The first wave contains exact statements for Erdős problems 196, 273, 366, 488, 617, and 699. Each prompt accepts only a proof of the full quantified statement or a complete counterexample/construction as a solution. Smaller subcases are retained as research progress but are not promoted as solutions.

A Rethlas verifier verdict is not a formal proof. Any promising blueprint must survive independent mathematical checking, provenance/novelty review, translation to the faithful Lean target, and a clean kernel build with no sorry, added axioms, or trusted external oracles.
