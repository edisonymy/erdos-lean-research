# Erdős–Lean research campaign

This repository records an AI-assisted attempt to identify and, if realistically possible,
solve a genuinely open Erdős problem with a kernel-checked Lean 4 proof.

> **Status: active research. No open problem is claimed solved.**

The project prioritizes statement fidelity, novelty checks, reproducible computation, and
formal verification over producing a dramatic claim. A successful Lean compilation will not
be treated as a solution unless the formal theorem is independently audited against the
original mathematical problem.

## Current campaigns

- **Erdős #273:** search for a strict covering system whose distinct moduli are all `p - 1`
  for primes `p ≥ 5`.
- **Erdős #488:** attack the density-doubling inequality for unions of multiples.
- **Erdős #617:** search for a finite edge-colouring certificate at the first open case.

The source programs and retained search logs live in [`experiments/`](experiments/). Results
are provisional until independently checked and summarized in the research notes.

## Pinned upstream inputs

- Google DeepMind Formal Conjectures:
  `735aee074327b8e78b0d92bb1ee8ea00937c3f51`
- Erdős-focused Rethlas runner:
  `622bc663d4212333ade4c4802af1db3da92262c0`
- Lean toolchain: `leanprover/lean4:v4.27.0`
- Mathlib: `v4.27.0`

The large upstream checkouts, Lean caches, virtual environments, and compiled search binaries
are intentionally excluded from Git. See [`research/environment.md`](research/environment.md)
for the reproducible setup.

## Research standards

Any eventual solution package must include all of the following:

1. an unchanged or explicitly audited public theorem statement;
2. evidence that the exact informal problem was open before the work;
3. a fresh literature and priority search;
4. a sorry-free Lean proof in the pinned environment;
5. complete axiom output and unfinished-proof scans;
6. concrete tests of the formal definitions and hypotheses;
7. an independent human-readable proof; and
8. a clear account of AI and computational involvement.

The current candidate survey is in
[`research/candidate-survey.md`](research/candidate-survey.md).

