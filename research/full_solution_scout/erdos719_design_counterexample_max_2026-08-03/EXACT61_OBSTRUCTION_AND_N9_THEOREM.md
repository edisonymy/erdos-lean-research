# Certified exact-61 obstruction and the `n=9` theorem for Erdős #719

**Date:** 3 August 2026
**Theorem 1:** Every 61-edge 3-uniform hypergraph on nine vertices contains
three edge-disjoint copies of `K_4^3`.
**Theorem 2:** Every 3-uniform hypergraph `G` on nine vertices has a
decomposition into at most `ex_3(9,K_4^3)=54` pieces, each a triple or a
tetrahedron.

Theorem 2 settles the `n=9` instance of Erdős #719.  It is **not a full
solution of #719**, whose statement ranges beyond this one order.

## 1. Exact-61 core proof

For a 3-graph `G`, let `nu(G)` be the largest number of edge-disjoint
tetrahedra and let `q(G)` be the number of all present tetrahedra.

The independently audited deletion inequality

```text
|G| <= 4 nu(G) + 53
```

shows that a 61-edge graph has `nu(G)>=2`.  Suppose for contradiction that
`nu(G)=2`, and choose a maximum core `P={P1,P2}`.  The two four-sets have
intersection size 0, 1, or 2; these are the complete isomorphism types under
permutations of the nine vertices.

Every four-set meeting both core members in at most two vertices is
edge-disjoint from the core, so maximality forces it to contain a missing
triple.  The same explicit 18-block packing / `SQS(10)` averaging argument
used for exact 64 gives

```text
q(G)/7 <= nu(G)=2, hence q(G)<=14.                  (1)
```

For each of the three intersection types, a deterministic CNF encodes:

```text
exactly 23 missing triples;             61 present edges
the eight core triples are present;
every core-compatible tetra is dirty;  core maximality
c_B iff B is clean for all 126 B;
sum_B c_B <= 14.                        equation (1)
```

All three formulas are UNSAT.  Hence `nu(G)=2` is impossible, proving
`nu(G)>=3` at 61 edges.

The independent replay enumerates all 6,615 compatible unordered pairs of
four-sets and partitions them as

```text
intersection 0:  315
intersection 1: 2520
intersection 2: 3780
```

so no core type is omitted.

## 2. From the two obstructions to the `n=9` theorem

The audited all-edge-count reduction in
`../erdos719_window_audit_2026-08-03/AUDIT.md` proves that any nine-vertex
counterexample to

```text
phi(G)=|G|-3nu(G) <= ex_3(9,K_4^3)=54
```

would have to lie in exactly one of two windows:

```text
(|G|,nu(G))=(64,3) or (61,2).
```

`EXACT64_OBSTRUCTION.md` certifies that every 64-edge graph has `nu>=4`.
The exact-61 argument above certifies that every 61-edge graph has `nu>=3`.
Both exhaustive windows are therefore empty, proving `phi(G)<=54` for every
nine-vertex 3-graph.

## 3. Certificate status

The exact-61 package is

```text
certificates_exact61_glucose4/
```

The three proof traces were generated only after fixing and smoke-testing the
Windows UCRT proof-buffer flush described in `EXACT64_OBSTRUCTION.md`.  Native
`drat-trim` independently accepted all three traces and their hashed CNFs;
the audit also replayed the three core orbits and inspected the all-126 clean
equivalences and maximality clauses.

```text
audit_report.json SHA-256
2cc545400a3c8507ac2439461431cf3f8cacab92ede0d9bdd63938656cd73195

manifest.generated.json SHA-256
1af646b0aa29f9ac576ee34cda1960651e10a42baae30b94b45193cade92cb9d

drat-trim.exe SHA-256
0d4f4684f2bc492ad7fe48b4fa24cf1c50d7c91e33c16c0183c20f2d3ae50ddc
```

Per-type hashes are recorded in the manifest and audit report.  The audit
status is exactly

```text
ALL_3_DRAT_VERIFIED_AND_ORBITS_REPLAYED
```

Reproduction:

```powershell
.\.venv\Scripts\python.exe -B `
  research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\audit_exact61_obstruction.py `
  --certdir research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\certificates_exact61_glucose4 `
  --checker tools\proof_checkers\windows_drat\bin\drat-trim.exe `
  --output research\full_solution_scout\erdos719_design_counterexample_max_2026-08-03\certificates_exact61_glucose4\audit_report.replay.json
```

## 4. Claim boundary

### Established

* Exact packing lower bounds `nu>=4` at 64 edges and `nu>=3` at 61 edges.
* No `n=9` counterexample exists.
* The proposed inequality of Erdős #719 holds at `n=9`.

### Not established

* The inequality for every order in Erdős #719.
* A full solution of Erdős #719.
* A priority claim beyond the dated artifacts and a renewed literature check.

The active exact-61 static solve became redundant after this independently
checked core-orbit proof; it should be stopped only by the process owner after
freezing any already-produced metadata.
