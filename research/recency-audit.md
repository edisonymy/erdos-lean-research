# Announcement-level recency audit

Date: 2026-08-01

## Why this gate exists

The initial campaign treated the Erdős Problems database, VibeMathed, Formal
Conjectures, and the frozen AI-contributions wiki as the main collision screen. That was
insufficient. Erdős #617 still appeared open in the database even though a 24 July Zenodo
record already archived Robert Sneiderman's fixed-`r=5` proof and Ramazan Kara's independent
Lean verification. The fixed case was therefore not an open target.

The error was caught before any solution claim, but after avoidable search effort. The public
record is corrected rather than erased.

## Required pre-compute gate

Before a target receives material compute, search its exact number, theorem wording, and
distinctive terminology across all of the following:

1. the live problem page, edit history, and newest forum comments;
2. the live VibeMathed API, including entries labelled candidate, partial, contested, or
   retracted;
3. GitHub repository and code search, sorted for recently updated repositories;
4. Formal Conjectures issues and pull requests, not just the pinned theorem file;
5. Zenodo's records API and arXiv for recent preprints;
6. current SciNet/Constellate findings and other announcement feeds; and
7. cited primary literature and any repository named by a new announcement.

For a fixed subcase, search the fixed parameter explicitly. A database status for the
all-parameter conjecture does not establish that the subcase is open. Absence from any one
index is never positive evidence of novelty.

Repeat the gate before publishing, because status can change during a long campaign.

## Collision audit for the current wave

| Problem | Recent finding | Consequence |
|---|---|---|
| #128 | `cormundus/erdos-128-census`, commit `52e43ab4a6e9bc9a56951e113c823b340d706fe6`, updated 26 July; live page/forum and repository search repeated 1 August | compare every finite claim; the prior work covers named SRGs and heuristic searches, not the complete Ramsey-catalogue exclusion through `n=15` or the new conditional double-solver exclusion at `n=16`; no exact public `n=16` closure was found, but novelty is not claimed |
| #167 | 24 July report closes only order 9; a 26 July note discusses order-10 feasibility; current public Lean/Aristotle material still labels the full conjecture unproved | the conditional order-11 residual computation appears non-duplicative in the searched record, but is published only as a bounded result with no priority claim |
| #196 | `Sageder/erdos-196` was created/updated 27 July but is an empty repository | no mathematical collision found; retain as a monitored target |
| #273 | two July repositories give stronger range and certified finite obstructions, including period `55,440` | stop the redundant SAT siege; retain only independently useful non-overlapping obstructions |
| #366 | no matching recent Zenodo or dedicated GitHub repository found; current page and June frontier audit still describe it as open/verifiable | retain, with the public `n<10^22` exclusion as prior art |
| #488 | extensive current forum work exists; no full corrected-multiples resolution located | retain only with explicit comparison against the forum and Chojecki note |
| #617, `r=5` | Zenodo DOI `10.5281/zenodo.21535386`, deposited 24 July; exact source and preprint hashes matched | withdraw target and stop all searches; all-`r` conjecture remains open |
| #699 | public 22 July computation reaches `n=100000`; a dashboard's “done” flag selects only the auxiliary Sylvester–Schur theorem | finite search is non-novel; retain only faithful reductions/formal lemmas |

| #742 | live page, VibeMathed, recent arXiv/Zenodo/SciNet/Constellate, and Formal Conjectures issue/PR searches found statements and restricted results but no full proof, counterexample, or public order-25 verdict | retain the candidate-first order-25 search; independently check any SAT graph, and never promote uncertified UNSAT output |
| #982 | a 25 July Kominers working paper claims a stronger partial coefficient but not the conjectured `n/2` bound; public SkyDiscover `n=10`/`n=12` evaluators contain a scale-sensitive acceptance bug | retain exact family attacks, but treat neither the unverified paper claim nor floating-point benchmark output as a solution or exact certificate |

## #617 primary-record check

The Zenodo API reports record `21535386`, created `2026-07-24T14:32:45Z`, titled
*Machine verification of the fixed r = 5 case of Erdős Problem 617*. Its description names
the theorem `Erdos617.e058Problem617AtFive : Problem617At 5`, Lean 4.32.0, mathlib revision
`81a5d257c8e410db227a6665ed08f64fea08e997`, 89 LRAT certificates, and the assumption set
`propext`, `Classical.choice`, and `Quot.sound`.

The archived source and PDF were downloaded directly from Zenodo. Their computed SHA-256
hashes matched `SHA256SUMS`:

```text
5b56635df7a30b9fbee469ee5d732dadcf52ddf315fa568ea111b6b91f97c787  erdos617-r5-source.tar.xz
c248918bde85c9a0306c13e751b613760be88f02b9474b1565af8662a1d5a543  erdos617-r5-formal-verification.pdf
```

The extracted source contains the stated final theorem and pins the reported Lean/mathlib
versions. A complete clean replay is documented as taking about seven hours and was not
duplicated merely to establish priority. The record itself says the result has not yet
completed independent expert review.

## Limit

This protocol reduces collision risk; it cannot prove that no unpublished or poorly indexed
work exists. Any eventual novelty statement must therefore be phrased as a documented search
result, not as absolute priority.
