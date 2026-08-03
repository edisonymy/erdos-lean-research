# Certified exclusion of the exact-64 window for Erdős #719

**Date:** 3 August 2026
**Scoped theorem:** Every 3-uniform hypergraph on nine vertices with 64 edges
contains four edge-disjoint copies of `K_4^3`.

Equivalently, the `(m,nu)=(64,3)` counterexample window for Erdős problem
#719 is empty.  This is **not a full solution of #719**: the independently
audited reduction still leaves `(m,nu)=(61,2)`.

## 1. Why a three-block core is legitimate

Write `nu(G)` for the maximum number of edge-disjoint tetrahedra.  The audited
packing-one deletion inequality says

```text
m <= 4 nu(G) + 53.
```

Thus a 64-edge graph has `nu(G)>=3`.  To exclude `nu(G)<=3`, it is enough to
suppose `nu(G)=3` and choose a maximum packing

```text
P={P1,P2,P3}.
```

Its members are four-sets with pairwise intersection at most two.  Their 12
constituent triples are present.  Any other four-set meeting each `Pi` in at
most two vertices is edge-disjoint from the whole core; maximality therefore
forces it to contain a missing triple.

## 2. The global `q<=21` bound

Let `q` be the number of **all** present tetrahedra of `G`.  The following
explicit family consists of 18 pairwise edge-disjoint tetrahedra:

```text
0134 0158 0167 0235 0247 0268
0378 0456 1236 1245 1278 1357
1468 2348 2567 3467 3568 4578
```

It is the deletion of one point from an `SQS(10)`.  Under a uniformly random
permutation of the nine vertices, each one of the 126 four-sets occurs in the
relabeled family with probability `18/126=1/7`.  The expected number of
present members is consequently `q/7`.  Every relabeling is an edge-disjoint
family and can contain at most `nu(G)=3` present members.  Hence

```text
q/7 <= 3, so q <= 21.                              (1)
```

This counts every present tetrahedron, not only those near the core.

## 3. Complete core-orbit reduction

For a labeled three-core, record the sizes of the eight Venn cells indexed by
membership patterns in `P1,P2,P3`.  This vector completely classifies the
three subsets up to a permutation of the nine ground vertices.  Taking the
lexicographic minimum over the six permutations of the core members removes
the core labels.

An exhaustive enumeration of all triples of four-sets with pairwise
intersection at most two gives 190,260 cores in exactly ten orbits.  An
independently written replay obtains the same ten keys and these orbit sizes:

```text
15120, 7560, 7560, 11340, 45360,
45360, 3780, 22680, 30240, 1260.
```

They sum to 190,260.  Because Venn-cell counts are a complete invariant here,
one representative per key is an exhaustive case split.

## 4. Exact CNF for each orbit

For each representative core, the certificate generator creates one CNF with

* 84 variables `z_e`, where `z_e=1` means triple `e` is missing;
* 126 variables `c_B`, one for every four-set `B`, with clauses enforcing
  `c_B` iff all four triples of `B` are present;
* standard totalizer auxiliary variables.

The hard constraints are:

```text
sum_e z_e = 20;                         exactly 64 present triples
z_e = 0 for the 12 core triples;         the chosen core is clean
OR_{e subset B} z_e for every B
  compatible with all three core blocks; the core is maximal
sum_B c_B <= 21.                         equation (1), over all 126 B
```

There are 2,178 variables and between 17,523 and 17,535 clauses, depending on
the number of core-compatible blocks.  Every one of the ten formulas is
UNSAT.

Conversely, a 64-edge graph with `nu=3`, relabeled so that a maximum core is
the chosen representative, would satisfy every displayed constraint.  Thus
the ten UNSAT results exclude all possibilities.

## 5. Certificate verification

The final proof package is

```text
certificates_glucose4_complete/
```

It was generated with Python 3.12.4, PySAT 1.9.dev7, and Glucose4.  A Windows
proof-export buffering issue was found during the audit: without an explicit
UCRT flush, PySAT returned a buffer-aligned prefix missing the terminal empty
clause.  Those first CaDiCaL and Glucose traces are preserved as **failed,
unverified artifacts** in separate directories.  The final generator flushes
the native UCRT stream, requires a literal terminal empty clause, and never
repairs a truncated trace.

All ten final DRAT files were checked from their hashed CNFs by the independent
native `drat-trim` binary.  Every check returned zero and printed `s VERIFIED`.
The independent audit simultaneously replayed the ten-orbit partition and
checked that each CNF contains the clean-equivalence clauses for all 126
four-sets and the correct maximal-core clauses.

```text
audit_report.json SHA-256
31548e300113fdb62182ff2f743140de0ae4188515e377d3ee057774e7d4f476

manifest.generated.json SHA-256
1ff6312495d6504b618b8ec45827411aeae4bd265f8a4c6b171ed9e515464966

drat-trim.exe SHA-256
0d4f4684f2bc492ad7fe48b4fa24cf1c50d7c91e33c16c0183c20f2d3ae50ddc
```

As an additional independent proof-format check, type 1 was converted to LRAT
and accepted by `lrat-check`:

```text
type_01.lrat SHA-256
26732fac2a630a991eabf2629c437ed68957912c8bb16dccd22f616264266e3b

lrat-check.exe SHA-256
e0a8eb3c7f5e917ad5e049623671a465d4119ec4704077a3762a7ed8ae2c8fd9

c VERIFIED
Added clauses = 321998; deleted clauses = 321912;
max live clauses = 17527.
```

Re-run the semantic/orbit audit and all ten native DRAT checks with:

```powershell
.\.venv\Scripts\python.exe -B `
  research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\audit_exact64_obstruction.py `
  --certdir research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\certificates_glucose4_complete `
  --checker tools\proof_checkers\windows_drat\bin\drat-trim.exe `
  --output research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\certificates_glucose4_complete\audit_report.replay.json
```

## 6. Claim boundary and next target

### Established here

* The ten core orbits are exhaustive.
* No 64-edge nine-vertex 3-graph has packing number at most three.
* Therefore every such graph has four edge-disjoint tetrahedra.
* The exact-64 branch of the audited `n=9` counterexample reduction is closed.

### Not established here

* Existence or nonexistence of a 61-edge graph with packing number at most two.
* A full proof or counterexample for Erdős #719.
* Any priority claim beyond the dated campaign artifacts.

The highest-value continuation is now solely the `(61,2)` exact search/proof
lane; running more exact-64 construction searches would duplicate a certified
empty case.
