# Rethlas stage-one campaign

> Historical note (2026-08-01): the #617 fixed-`r=5` prompt in this wave was
> superseded by Zenodo DOI `10.5281/zenodo.21535386`. Its search was stopped;
> see `research/recency-audit.md`.

This campaign uses the public Rethlas runner at pinned commit 622bc663d4212333ade4c4802af1db3da92262c0 as an idea-generation and informal-referee harness. It is deliberately non-blind (BLIND_RUN=0) because the targets are currently open and no historical benchmark isolation is being claimed.

The first wave contains exact statements for Erdős problems 196, 273, 366, 488, 617, and 699. Each prompt accepts only a proof of the full quantified statement or a complete counterexample/construction as a solution. Smaller subcases are retained as research progress but are not promoted as solutions.

The three #196 attempts ended without an accepted verifier verdict or verified blueprint; the
third attempt used 252,802 tokens. The agent made no complete-proof submission, although the
runner subsequently made a failed automatic verifier call. Its useful reductions and convention
errors are recorded in `experiments/erdos196/RESULTS.md`. A later counterexample-oriented #64
run was launched as a separate exploratory wave, then stopped after it entered a repeated
patch-transcript loop without producing a proof, counterexample, or verifier submission. These
outcomes are negative research records, not solution claims.

A Rethlas verifier verdict is not a formal proof. Any promising blueprint must survive independent mathematical checking, provenance/novelty review, translation to the faithful Lean target, and a clean kernel build with no sorry, added axioms, or trusted external oracles.
