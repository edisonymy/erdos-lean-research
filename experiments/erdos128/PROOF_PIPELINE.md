# Proof-producing SAT contingency for the order-16 search

## Symmetry premise

For `n = 16`, Razborov's published reduction requires any counterexample to
satisfy `alpha(G) < 2n/5 = 6.4`, hence `alpha(G) <= 6`. The complete published
Ramsey `(3,6,16)` catalogue contains every triangle-free graph with
`alpha(G) <= 5`; the local manifest and checker reproduce its 2,576 records
and rule all of them out. Conditional on that external catalogue-completeness
claim, every remaining counterexample therefore has `alpha(G) = 6`.

Any such graph has an independent six-set. Relabelling one to vertices `0..5`
justifies `--fix-independent-size 6`; `--alpha-upper 6` forbids independent
seven-sets. The combination is a complete symmetry reduction of the remaining
case, not an extra graph-theoretic assumption.

## Encoding audit

`cnf_search.py` uses one Boolean for each unordered edge. It adds:

1. one negative three-edge clause for every vertex triple (triangle-free);
2. negative units on the fixed independent set;
3. for every seven-set, a clause requiring at least one internal edge
   (`alpha <= 6`);
4. a sequential-counter CNF requiring at least
   `floor(n^2/50) + 1 = 6` edges in every eight-set.

The last integer threshold is exactly the strict inequality
`e(S) > n^2/50`. The PySAT `IDPool` gives every sequential counter disjoint
auxiliary variables. `--build-only` writes this deterministic formula without
starting an in-process solver.

At `n = 16` the recorded build has 1,698,960 variables and 3,203,775 clauses.
The DIMACS itself is expected to be on the order of 0.1 GB. The proof size is
not safely predictable: hard SAT proofs commonly exceed their input by orders
of magnitude, and the current active non-proof run had already consumed more
than 2,200 CPU seconds without terminating when this contingency was built.
With only about 14 GB free on the available Windows volumes, an order-16 proof
run is unsafe now. The wrapper refuses it while the PID in
`.tmp/erdos128_n16_maple.pid` is alive and requires both an explicit
`-AcknowledgeLargeRun` and at least 50 GB free on the output volume. Fifty GB is
a launch floor, not a proof-size guarantee.

## Pinned tools and trust boundary

- CaDiCaL 1.9.5, commit `146207318796f094dcded87349a64f0c6927309e`,
  emits binary DRAT.
- `drat-trim`, commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`,
  independently checks DRAT and translates its verified core to LRAT.
- `lrat-check` from the same pinned checker repository independently checks the
  LRAT trace.

They are compiled under the existing Alpine WSL2 distribution. No Docker
daemon or container is started. The solver and checkers are independent
programs, but `drat-trim` and `lrat-check` share an upstream repository and are
not formally verified. A future theorem-level claim should additionally use a
formally verified checker such as CakeML `cake_lpr`, preferably on a separate
machine, and retain hashes of the DIMACS, proof, binaries, source commits, and
logs.

The build script fixes `SOURCE_DATE_EPOCH` and sorts CaDiCaL's compilation
inputs. Two consecutive local rebuilds produced the identical CaDiCaL SHA-256
`0ffcd0bb1265203c8744b677dcd8d37185d24cbe00f723d53f2431ade02d0750`.
This controls the observed local build; reproducing the binary hash elsewhere
also requires the same compiler and libraries. The generated `summary.json`
records all three executable hashes, their source commits, and the generator
and proof-artifact hashes.

The build writes `third_party/erdos128-proof-tools.json`. Before a proof run,
the wrapper verifies that manifest, both source commits and clean tracked
compilation inputs, the absence of untracked source/make inputs, and all three
observed binary hashes. It refuses to attach pinned commit labels to replaced
or locally modified tools.

## Build and smoke test

From the workspace root:

```powershell
python -m pip install -r experiments/erdos128/requirements-proof.txt
powershell -ExecutionPolicy Bypass -File experiments/erdos128/build_proof_tools.ps1
powershell -ExecutionPolicy Bypass -File experiments/erdos128/proof_pipeline.ps1
```

The Python dependency is pinned to `python-sat==1.9.dev7`. The scripts support
local drive-letter paths visible in the default Alpine WSL distribution under
`/mnt/host`; UNC paths and other mount layouts are rejected explicitly. Paths
containing spaces or apostrophes are transported as base64 positional data and
decoded inside fixed stdin-fed shell scripts, rather than interpolated into
shell commands.

The default smoke case is the known-UNSAT `n = 8`, `alpha <= 3` instance with
one independent triple fixed. It generates DIMACS, obtains a binary DRAT proof,
checks and converts it with `drat-trim`, then checks the LRAT file separately.
All generated files remain under `.tmp/erdos128-proof-smoke/`.

The smoke test was run twice independently and was byte-for-byte stable. Its
CNF had 588 variables, 1,109 clauses, and 14,323 bytes. CaDiCaL returned
UNSAT/exit 20; `drat-trim` reported `s VERIFIED` and emitted a 6,484-byte LRAT
file; `lrat-check` independently reported `c VERIFIED`. The repeated hashes
were:

- CNF: `af06e060c2d91767accf7e81b285bc4dfc00068af5af1e8103c650e2c5e6ede6`
- DRAT: `13ccba655d94ccd530e9a47416b211554e6b6cf2ada506ff33a2f7e1df20503a`
- LRAT: `740a72f4e9eb1181768b7793d0bffc7864ddf68f5e7b3cc21ce86d13f5b27202`

As a separate encoder sanity check, all 64 assignments of the six-input,
bound-two smoke-test counter were checked, plus 1,029 deterministic boundary
and pseudorandom assignments of the order-16 28-input, bound-six counter. In
each case the CNF was satisfiable exactly when the literal count met the bound.
The retained `audit_cardinality_encoding.py` reruns this test before every
pipeline execution and records its output and hash.

The wrapper refuses inconsistent parameters such as a fixed independent set
larger than the advertised independence bound. Large runs accept only the
audited `(N, alpha, fixed) = (16,6,6)` contract. It also requires a new, empty
output directory unless `-OverwriteExisting` is supplied explicitly; no proof
artifact is silently replaced.

Only after the active search has ended and a volume with ample free space is
available should the order-16 command even be considered:

```powershell
powershell -ExecutionPolicy Bypass -File experiments/erdos128/proof_pipeline.ps1 `
  -N 16 -AlphaUpper 6 -FixIndependentSize 6 `
  -OutputDirectory X:\erdos128-proof -AcknowledgeLargeRun
```

This command is a contingency, not a recommendation to launch immediately.
