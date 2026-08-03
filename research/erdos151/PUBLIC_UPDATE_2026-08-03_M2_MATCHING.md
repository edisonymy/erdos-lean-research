## 3 August 2026, 16:20 BST — corrected finite checkpoint (not a solution)

This update records two narrow advances and one audit correction.  It does
**not** resolve Erdős #151, exclude the full order-50 face, or close the
24-vertex protected-core class.

### 1. Coverage-audited exclusion of the `m=2` normalization stratum

For the uniform type-5 protected-core subclass, the heavy-edge resolution
theorem reduces exactly two partition mismatches to two complete 22-vertex
flag-sphere blocks.  Their quotient reconstruction has 540 canonical
symmetry-reduced marked-factor branches (210 + 330).  After a full corrected
rerun:

- CaDiCaL 1.9.5 exhausted all 540 branches, with zero quotient survivor;
- Glucose 4.2 independently gave the same result;
- fresh coverage audits rebuilt the two inputs, automorphism groups, matching
  and configuration orbits, weighted raw-factor coverage, and the exact
  540-key union; and
- a third implementation, using neither NetworkX nor PySAT, recursively
  replayed the same canonical branch manifests and found no exact cover or
  survivor.

An important correction was caught before publication: the first SAT helper
constructed adjacency masks in NetworkX insertion order and later indexed
them by integer vertex label.  Those four historical SAT termination files
are explicitly invalidated.  The canonical input projections were unchanged,
and all four SAT computations were rerun after the fix.  The permanent
regression/invalidation audit and both fresh coverage replays return `PASS`.
No DRAT/LRAT traces were retained for this search, so the claim is a
**coverage-audited computational exclusion of `m=2`**, not a
proof-certified theorem.

Full report and hashes:
[`SURFACE_GLUING_REPORT.md`](https://github.com/edisonymy/erdos-lean-research/blob/codex/full-resolution-campaign/research/erdos151/n50_protected_core_max_2026-08-03/surface_gluing_max/SURFACE_GLUING_REPORT.md).

### 2. A finite maximal-edge matching burden

Let `G` be `K4`-free on `n` vertices with `beta(G)<=b`, and let `M` be the
graph of ambient-maximal edges (edges lying in no triangle).  Put

```text
q = 3 ceil((b+1)/4),
P_q(b) = b + (q-2) floor(b/2).
```

The audited argument gives

```text
nu(M) >= ceil((n-P_q(b))/2).
```

It colors `G-M` using Lovász decomposition plus Brooks, then deletes the
endpoints of a maximum matching of `M` and aggregates pairs of color classes.
At `(n,b)=(50,10)`, this forces `nu(M)>=3`: every hypothetical order-50
`K4`-free witness contains three vertex-disjoint ambient-maximal edges.  A
separate successor CEGAR encoding containing exactly this gate passed an
exhaustive six-vertex semantics audit and is running.  Its round counts are
liveness only, not evidence for either outcome.

Proof and arithmetic audit:
[`PURE_TRIANGULAR_CHROMATIC_GATE.md`](https://github.com/edisonymy/erdos-lean-research/blob/codex/full-resolution-campaign/research/erdos151/n50_protected_core_max_2026-08-03/PURE_TRIANGULAR_CHROMATIC_GATE.md).

### 3. Chromatic-gate correction and refined-case status

The valid two-class chromatic gate excludes pure-triangular jump witnesses
for `h=11,12`.  A primary-source check of the stronger
Borodin–Kostochka/Catlin bound
`chi<=floor(3(Delta+2)/4)` also excludes the pure-triangular `h=13` jump
face because `R(3,13)>=61` while the resulting threshold is 60.  It does
**not** close `h=14`: the possible jump orders 67–71 remain.  Earlier claims
of an all-large-order tail and of using upper Ramsey bounds to close `h=14`
were invalid and are withdrawn in the audit note.

Separately, proof-certified UNSAT coverage of the 34 refined symmetry cases
in the uniform type-5 class has risen to 11/34.  Every covered parent has
passed CaDiCaL, pinned Linux DRAT/LRAT checking, and the native Windows LRAT
checker.  Twenty-three cases remain; branch counts are not probabilities.

Current allocation remains bounded: finish certificate-bearing finite work
while coverage rises and monitor the two full order-50 CEGAR processes, but
do not infer proximity from cut counts or expand this result into a claim
about unrestricted higher-genus strata or #151 itself.
