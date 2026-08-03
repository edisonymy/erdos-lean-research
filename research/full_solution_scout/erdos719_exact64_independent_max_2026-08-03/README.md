# Independent exact-64 obstruction audit

**Date:** 3 August 2026.

**Exact-64 verdict: PASS.** There is no 3-graph on nine vertices with 64 edges and
packing number at most three.  This independently closes the exact-64 branch
of the audited `n=9` window reduction.

The independent `exact61/` packet now closes the other surviving branch too.
Consequently the audited window theorem gives the complete `r=3,n=9`
instance of Erdős #719: every nine-vertex 3-graph decomposes into at most
`ex_3(9,K_4^3)=54` single triples and edge-disjoint tetrahedra.  This remains a
bounded theorem, not a full solution of the all-`r,n` problem.

This directory does not import the CEGAR search or the first core-certificate
generator.  Every one of the ten independently generated Glucose DRAT proofs
passed native `drat-trim`, was converted to LRAT, and the LRAT then passed the
separate native `lrat-check` executable.

## Mathematical chain being audited

Let `G` be a 3-graph on nine vertices with 64 edges and `nu(G)<=3`, and let
`q` be its number of tetrahedra.

1. In fact `nu(G)=3`; the full exclusion of `nu<3` is given below.
2. Select a maximum packing `P` of three tetrahedra.  Its members are pairwise
   edge-disjoint, and every tetrahedron edge-disjoint from all three must be
   dirty: otherwise it extends `P` to a four-packing.
3. Up to relabeling the nine vertices and permuting the three members, there
   are ten possible cores.  The sizes of the eight membership-pattern cells
   are a complete invariant for a labeled three-set family; minimization over
   the six member permutations removes their labels.  The script enumerates
   every compatible triple of four-sets and obtains exactly ten signatures.
4. An explicit 18-block triple packing on nine vertices gives `q<=7nu=21`:
   after a uniform random vertex permutation, its expected number of present
   blocks is `18q/126=q/7`, while every relabeling contains at most `nu=3`
   present blocks.
5. For each of the ten core types, `independent_certificate.py` asserts exactly
   20 missing triples, the core's presence and maximality, and `q<=21`.  It
   uses an independently implemented signed sequential counter.  UNSAT for
   all ten formulas closes the exact-64 window.

### Why `nu<3` is impossible

The audited finite input is `ex_3(9,K4^3)=54`.  The needed packing-one bound
has a short self-contained derivation.  When `nu(J)=1`, its family of present
tetrahedra is pairwise 3-intersecting as four-subsets.  Choose two distinct
members `S∪{a}` and `S∪{b}` sharing the triple `S`.  Either every member
contains `S`, or a member not containing `S` is forced to have the form
`(S∖{s})∪{a,b}`.  In the latter case, a member using a vertex outside the
five-set `S∪{a,b}` would be forced to equal `S∪{x}`, which intersects that
exceptional member in only two points.  Hence the family either has a common
triple or is contained in one five-set.

In the common-triple case, deleting that one triple destroys every
tetrahedron, so `e(J)<=55`.  In the five-set case, the missing triples already
hit every four-set outside it.  Three internal triples suffice to hit its five
four-subsets, so adjoining them gives a full nine-vertex hitter of size at
least 30.  Thus `J` already has at least 27 missing triples and `e(J)<=57`.

Now `nu(G)=0` would imply `e(G)<=54`, and `nu(G)=1` would imply `e(G)<=57`.
If `nu(G)=2`, delete the four triples of one member of a maximum two-packing.
The remaining graph has 60 edges, still contains the other member, and cannot
contain two edge-disjoint tetrahedra: together with the deleted member they
would form a three-packing in `G`.  Its packing number is therefore one,
contradicting the bound 57.  Since `nu(G)<=3` was assumed, `nu(G)=3`.

### Why `q<=21`

The checked list of 18 tetrahedra is a triple-packing: its 72 constituent
triples are distinct.  Under a uniformly random permutation of the nine
vertices, each listed block is uniform among the 126 four-sets.  If `q` of
those are present in `G`, linearity of expectation gives `18q/126=q/7`
present listed blocks.  Every relabeling is still a packing and hence contains
at most `nu(G)=3` present blocks.  Therefore `q/7<=3`, or `q<=21`.

The sequential counter was exhaustively tested for every assignment through
seven inputs.  Its general correctness also has the standard short induction:
the auxiliary variable `s[i,j]` is forced whenever the first `i+1` inputs
contain at least `j+1` true literals, so the overflow clauses forbid `k+1`
trues; conversely, assigning each `s[i,j]` its intended prefix-threshold value
satisfies the encoding whenever at most `k` inputs are true.  Applying this to
the positive and negated input lists gives exactly 20 misses.

The clean-block equivalence is encoded in both directions.  For every block
`B`, `c_B -> not z_e` for each of its four triples and
`(all z_e false) -> c_B`.  Thus the final at-most-21 counter constrains the
actual number of present tetrahedra, not a one-sided proxy.

## Exact finite audit

`structural_audit.py` independently checks:

- the fixed 18-block packing has 72 distinct triples;
- all 190,260 labeled three-packing cores are enumerated;
- their ten orbit counts are
  `15120, 7560, 7560, 11340, 45360, 45360, 3780, 22680, 30240, 1260`;
- those counts sum to 190,260;
- regenerating each formula gives byte-for-byte the same checked DIMACS; and
- all twenty native checker outcomes (DRAT and LRAT) are verified.

Reproduce the exact-64 structural layer with:

```powershell
.venv\Scripts\python.exe -B research\full_solution_scout\erdos719_exact64_independent_max_2026-08-03\structural_audit.py
```

The checked manifest is `certificates/manifest.verified.json`, SHA-256
`8937b0a31bb987720f302a4f393c78ca1bb4d41ca9766d07bd07ec0a3ddc7d73`.
The ten inputs total 3,094,165 bytes, the DRAT proofs 191,660,122 bytes, and
the checked LRAT proofs 532,074,406 bytes.  Checker hashes are:

```text
drat-trim.exe  0d4f4684f2bc492ad7fe48b4fa24cf1c50d7c91e33c16c0183c20f2d3ae50ddc
lrat-check.exe e0a8eb3c7f5e917ad5e049623671a465d4119ec4704077a3762a7ed8ae2c8fd9
```

One command replays both exact-64 and exact-61 packets, including all native
DRAT-to-LRAT conversions, all LRAT checks, and both structural audits:

```powershell
.venv\Scripts\python.exe -B research\full_solution_scout\erdos719_exact64_independent_max_2026-08-03\replay_n9.py
```

Success ends with `ALL_ERDOS719_N9_INDEPENDENT_AUDITS_PASS`.

## Combined provenance and storage

`PROVENANCE.json` freezes both verified-manifest hashes, every generator and
audit source hash, the Python/PySAT runtime, the bundled solver-extension hash,
the pinned native checker revision/source/binary hashes, and the exact theorem
boundary.  The certified corpus occupies exactly 2,169,611,054 bytes:

```text
             CNF          DRAT           LRAT          total
exact-64   3,094,165   191,660,122    532,074,406    726,828,693
exact-61     843,747   420,414,466  1,021,524,148  1,442,782,361
combined                                            2,169,611,054
```

Observed free space after both packets were generated was 86.529 GiB.  These
are checked certificates, not disposable timeout traces; the campaign cleanup
policy therefore requires preserving them.  The generation runtime was Python
3.12.4 with `python-sat 1.9.dev7`/`glucose4`; proof checking used the pinned
`drat-trim` revision `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` and the
separate `lrat-check` binary.  Exact hashes are in `PROVENANCE.json` rather
than duplicated here.

## Claim boundary

Established by the combined independent packet and the audited all-edge
reduction: the `r=3,n=9` instance of Erdős #719.  Not established here: the
inequality for every `r,n`, any full solution of Erdős #719, or priority over
unpublished work.  No Git or public-announcement action was taken by this
audit lane.
