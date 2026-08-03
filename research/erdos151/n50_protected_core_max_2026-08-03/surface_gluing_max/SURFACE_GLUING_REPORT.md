# Exact surface-to-quotient gluing audit

**Status (2026-08-03):** the complete `m=2` surface list has no quotient
survivor in a corrected 540-branch symmetry-reduced exhaustive computation,
independently replayed with CaDiCaL 1.9.5 and Glucose 4.2.  Independent scripts
reconstruct the input, fibre, orbit, factor, and branch-key coverage.  A
label-order bug was found in the first SAT runs; those termination artifacts
are explicitly invalidated below, and all branches were rerun after the fix.
The supplied `m=3` projective-plane block is excluded more strongly by a
direct fixed-`K4` obstruction.  The corrected SAT branch results do not have
DRAT/LRAT certificates, so the `m=2` result is a two-solver,
coverage-audited computational exclusion, not a proof-certified theorem.

## 1. Exact inverse fibre form

Let `S` be a simple resolution of a hypothetical 24-vertex uniform-type-5
graph `G`, and let `pi:S -> G` be the quotient map.  At a split endpoint,
the inverse image of the original vertex consists of two degree-five surface
vertices.  At an unsplit endpoint it is one degree-ten surface vertex.  Thus,
for `m` mismatched heavy edges,

```text
48-2m degree-five vertices form 24-m two-element fibres;
m degree-ten vertices form m singleton fibres.
```

This gives exactly 24 quotient fibres.  Every light edge of `G` has one
surface preimage, while every heavy edge has two.  Mark the 24 surface edges
lying over the twelve heavy edges.  Every degree-five surface vertex is
incident with one marked edge and every degree-ten vertex with two.

At a degree-ten singleton `z`, its two marked neighbours must be antipodal in
the induced `C10` link.  They form the two-element fibre of the heavy mate of
`pi(z)`.  The two vertices may have no other common surface neighbour: such a
neighbour would be incident with two preimages of the same quotient edge.

After removing these exceptional marked spokes, the remaining marked edges
are disjoint `K2` components.  An ordinary heavy quotient edge pairs two such
components.  There are exactly two endpoint identifications for a pair of
marked `K2`s.  An identification is admissible only when:

1. the two vertices in each quotient fibre are nonadjacent and have no common
   surface neighbour;
2. the two surface edges are the only edges crossing the two new fibres; and
3. no other two selected fibres have surface-edge multiplicity greater than
   one.

Conversely, any complete selection satisfying these fibre conditions defines
a 24-vertex quotient.  The implementation then directly checks that the
quotient has 108 edges, is 9-regular and `K4`-free, has twelve multiplicity-two
edges forming a perfect matching, has exact codegree four on those edges and
two on every other edge, and has every link isomorphic to `C5 vee C5`.

This establishes the soundness and completeness of the finite reconstruction
relative to the simple-resolution theorem.  It does not assume the desired
quotient exists.

## 2. Marked-factor and symmetry reduction

Each icosahedron has 125 perfect matchings.  Its automorphism group has order
120 and has five perfect-matching orbits, in the deterministic search order

```text
30, 60, 20, 5, 10                       (sum 125).
```

The two icosahedral components are interchangeable.  Hence their ordered
factor choices reduce to the fifteen unordered pairs of these five orbits.
The sphere or projective-plane block is reduced independently under the
stabilizer of its exceptional singleton-mate configuration.

For a fixed set of marked factors, a SAT variable represents a block pairing
two marked `K2`s.  Exact-one constraints cover every ordinary marked surface
edge.  Binary clauses exclude accidental parallel quotient edges.  Models
with a spurious quotient triangle or a quotient `K4` generate a sound local
blocking clause; a locally clean model receives the full redundant quotient
audit above.  The solver continues until a valid quotient is found or the
finite branch is exhausted.

## 3. Complete `m=2` result

The complete flag-sphere census supplies exactly two 22-vertex blocks.  Their
graph6 records and SHA-256 hashes of the record without a newline are:

| block | graph6 | SHA-256 |
|---:|---|---|
| 1 | `U|fIJCpCG_a@C@C?b?G[@?_[ABGCKGCWCAW@?{?G` | `9c6150562421f74518524a0549ebc3869ef8dc6e378a87a4b91280643e6a0e7c` |
| 2 | `U|fIID@OI?g@W@K?b?G[X?oC@_G@_G?oc?Fo??Fo` | `4d421d408cc98a891f890b638ba521f828aba1a5931c4b5954ee697083eedabd` |

The independent coverage audit obtained:

| quantity | block 1 | block 2 |
|---|---:|---:|
| automorphism group order | 40 | 8 |
| raw disjoint antipode configurations | 25 | 23 |
| exact common-neighbour-filtered configurations | 25 | 9 |
| exact configuration orbit sizes | `10,10,5` | `2,4,2,1` |
| immediately invalid orbit size | 10 | 2 |
| canonical marked-factor branches | 210 | 330 |
| weighted valid raw factor cases | 3,359,375 | 1,484,375 |
| exhausted branches | 210 | 330 |
| quotient survivors | 0 | 0 |

The union therefore has exactly 540 canonical branch keys, all recorded as
exhausted, and no quotient survivor.  The coverage checker independently
reconstructs the automorphism groups, exceptional configurations, stabilizers,
perfect matchings, factor orbits, weighted raw coverage, and every branch key;
it does not import the discovery search.

### 3.1 Label-order correction and permanent regression

The initial search helper constructed adjacency masks by iterating NetworkX
node insertion order, but callers indexed the resulting list by integer vertex
label.  The built-in icosahedron has insertion order

```text
0,1,2,3,4,5,7,8,9,10,11,6
```

so the old helper could emit unsound accidental-parallel-edge clauses.  The
four old `m=2` SAT result files are invalid as termination evidence.  The bug
did not enter the automorphism, matching, exceptional-configuration, or branch
construction routines.  `audit_label_order_correction.py` permanently
reconstructs the nonnumeric insertion order and checks every adjacency mask by
label.  It also projects all old and corrected result files onto their
canonical branch inputs.  All projections agree byte-for-byte:

| block | canonical JSON bytes | projection SHA-256 |
|---:|---:|---|
| 1 | 43,022 | `9c17b6194cbf9c58ee273bee81bd5735bfc87f9073b51f96d552476efb846166` |
| 2 | 67,250 | `4b64e66c54f717defbbd2b24ddc46c929960f0fcf0877f44705b67b7f3a95141` |

Thus the independently audited 540-key manifest was unchanged, while the SAT
termination layer required and received a full rerun.

### 3.2 Corrected two-solver result

| solver | block 1 branches/models/time | block 2 branches/models/time | survivors |
|---|---:|---:|---:|
| CaDiCaL 1.9.5 | 210 / 89,404 / 337.148 s | 330 / 140,729 / 566.351 s | 0 |
| Glucose 4.2 | 210 / 87,987 / 354.586 s | 330 / 138,370 / 532.203 s | 0 |

Fresh independent coverage audits of both corrected solver families match
exactly all 540 canonical branch keys and the weighted raw-factor counts in the
table above.  Glucose is a different SAT engine applied to the same encoding
and search implementation; this reduces solver-specific risk but is not an
independent encoding and is not a proof certificate.

Subject to ordinary trust in the incremental SAT computation, this excludes
`m=2`: the plantri sphere list is complete and both possible blocks have been
exhausted.  Because no proof traces were retained, the formally safe statement
is **coverage-audited computational exclusion of `m=2`**.

## 4. Supplied `m=3` projective-plane block

The supplied graph6 block is

```text
TAheJ@peD?WWMKgRW?D[?GABOObG?S?PP??j
```

Its no-newline SHA-256 is
`a4ba704e9b19d9e85b3beb2c1c1992d00b9974f0de9b8034b67f7777e32b1d6a`.
Both the search and the independent audit check order 21, 60 edges, degree
multiset `(10^3,5^18)`, 40 triangles, codegree two on every edge, connected
cycle links, clique number three, and Euler characteristic one.

Here the inverse fibre form is:

```text
3 singleton degree-ten fibres + 21 paired degree-five fibres = 24;
3 exceptional antipode fibres consume 6 RP2 degree-five vertices;
18 remaining marked surface edges pair into 9 ordinary heavy edges.
```

The block has automorphism group order four.  There are 75 raw disjoint
antipode triples.  Requiring each pair to have its designated degree-ten
vertex as its unique common neighbour leaves four configurations, in two
orbits of size two.  Each representative has stabilizer order two and a
unique residual perfect matching.  Crossing these two cases with the fifteen
icosahedral factor-orbit pairs gives 30 canonical branches.

All 30 corrected branches were exhausted, inspecting 682 solver models and
finding no quotient survivor.  The independent audit exactly reconstructs the
30 branch keys and their weighted coverage of 62,500 valid raw factor cases.
This rerun records the SHA-256 of the corrected shared search dependency.

There is also a stronger solver-free obstruction.  For the two configuration
orbit representatives, respectively,

```text
{2}, {9,13}, {3,5},  {12,16}
{2}, {9,13}, {7,20}, {12,16}
```

are four fixed quotient fibres in local RP2 labels.  In each row every pair
of fibres has at least one surface edge between it, so the four quotient
vertices induce a `K4` before any ordinary marked edge is paired.  Explicit
edge witnesses are retained in `m3_gluing_coverage.audit.json`.  Since the
four exact exceptional configurations form precisely the two audited orbits,
this fixed `K4` excludes every quotient of the supplied block independently
of the 30 SAT branches.

This excludes quotients of **this supplied projective-plane block only**.  It
does not exclude `m=3` unless a complete census proves that this is the only
eligible `(10^3,5^18)` flag projective-plane block.

## 5. Artifact hashes

| artifact | SHA-256 |
|---|---|
| `marked_factor_gluing_search.py` | `2102ff3ba4cd1b40d2f7749f01d2042c44ca9b7d0eccbe97dcb91788258d3e21` |
| `marked_candidate1_corrected_cadical195.json` | `10dd3c1814933a457efded10d0d67d3cb5ca0ef183eddc53e6da10d81079b7cf` |
| `marked_candidate2_corrected_cadical195.json` | `12d3c5daaada489a3b7c82016ec7b8ed1ca5fa5219c1fca3b495171b4b3af04e` |
| `marked_candidate1_corrected_glucose42.json` | `c5fe931dbc048d2aad4a67fb44060a53df883d57685a01f8f52308fb7e774739` |
| `marked_candidate2_corrected_glucose42.json` | `01c714bfa23f8c126c38fc4bf39cff0ded70689a0555350c1c8b9a9e19622035` |
| `audit_m2_gluing_coverage.py` | `660084adea57551630609a51ad0a87f7530a23b64c154cab1e76d3c6cbe3d211` |
| `m2_gluing_union_coverage.corrected_cadical195.audit.json` | `84930f733bbd6120c6705021b833b39bfd59fd493aa72c505f6f228ac7426bb2` |
| `m2_gluing_union_coverage.corrected_glucose42.audit.json` | `56a89538dc4b7941e171104043be5828d195d93b689ac69640d08c32f508a04b` |
| `audit_label_order_correction.py` | `f123394e759477069fe05665faca78918bb3a56e02f357a5163d4f257e49cf95` |
| `label_order_correction.audit.json` | `dc6e34fb88a53668cb0637f86c49d84a3354f4e2da30832de995a19b379a0892` |
| `marked_factor_gluing_m3.py` | `a3ac6b6fe91e59c3f052d2095279d4da9e3c767d85d85b22b23e142947b71338` |
| `m3_marked_corrected.json` | `c82a89708515c26d8cbcf33dc72ed7d4b14e7e3b3658a5876c01ec9f863a8746` |
| `audit_m3_gluing_coverage.py` | `1a51269b38c4ed72a0db331f0e5f612ae271b5c1e2d4571248f99b7aef74ec28` |
| `m3_gluing_coverage.corrected.audit.json` | `10d5ee103c733add586f8c8e516dfd78793e14b6286d9809aa7151bea331af98` |

The historical files `marked_candidate1_complete.json`,
`marked_candidate2_complete.json`, `marked_candidate1_glucose42.json`, and
`marked_candidate2_glucose42.json` are preserved for disclosure but are
**invalidated as SAT termination evidence** by
`label_order_correction.audit.json`.  Their associated historical union audit
files remain useful only for canonical-orbit metadata, not for their recorded
termination conclusion.  The old `m3_marked_complete.json` SAT record is
likewise superseded by the corrected result; the solver-free fixed-`K4`
argument was unaffected.

## 6. Reproduction

From the workspace root:

```powershell
.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_search.py `
  --candidate 1 --quiet `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_complete.replay.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_search.py `
  --candidate 2 --quiet `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_complete.replay.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\audit_m2_gluing_coverage.py `
  --candidate1 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_corrected_cadical195.json `
  --candidate2 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_corrected_cadical195.json `
  --search-script research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_search.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\m2_gluing_union_coverage.replay.json

# Use `--solver glucose42` on the two marked-factor commands above and audit
# their corrected outputs in the same way to reproduce the different-solver
# replay.

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\audit_label_order_correction.py `
  --old-cadical1 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_complete.json `
  --old-cadical2 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_complete.json `
  --old-glucose1 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_glucose42.json `
  --old-glucose2 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_glucose42.json `
  --corrected-cadical1 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_corrected_cadical195.json `
  --corrected-cadical2 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_corrected_cadical195.json `
  --corrected-glucose1 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_corrected_glucose42.json `
  --corrected-glucose2 research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_corrected_glucose42.json `
  --search-script research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_search.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\label_order_correction.replay.audit.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_m3.py `
  --quiet `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\m3_marked_corrected.replay.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\audit_m3_gluing_coverage.py `
  --result research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\m3_marked_corrected.json `
  --search-script research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_factor_gluing_m3.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\m3_gluing_coverage.replay.json
```

## 7. Claim boundary

Established as exact mathematics, conditional only on the earlier resolution
theorem: the inverse fibre counts, exceptional antipode requirement, marked
factor form, completeness of the finite gluing parameterization, and the
fixed-`K4` obstruction for both valid exceptional-configurations of the
supplied RP2 block.

Independently audited finite facts: input block properties and hashes,
automorphism groups, perfect matchings, all orbit reductions, weighted factor
coverage, and exact branch-key coverage.

Recorded corrected computation: 570 distinct canonical branches terminated
exhaustively and no exact local uniform-type-5 quotient survived.  The 540
`m=2` branches were replayed with two SAT engines with the same outcome.

Not established here:

- proof-certified UNSAT of the 570 branches;
- exclusion of `m=3` beyond the one supplied projective-plane block;
- exclusion of any `m>=4` resolution topology;
- existence or nonexistence of the unrestricted 24-vertex uniform-type-5
  graph by a route not represented by the proved simple resolution; or
- any arrowing, ambient-completion, or full Erdos-151 conclusion.
