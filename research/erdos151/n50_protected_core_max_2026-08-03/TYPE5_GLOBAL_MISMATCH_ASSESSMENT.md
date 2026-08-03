# Uniform type-5 global mismatch assessment

## Exact scope

This lane concerns the exact 24-vertex uniform type-5 matching class encoded by
`type5_full_matching_sat.py`.  For a heavy matching edge `uv`, delete `v` from
`L(u)` and `u` from `L(v)`.  Each remainder is two disjoint `P4` components and
therefore partitions the four common neighbours of `u,v` into two pairs.  The
edge is a **mismatch** when the two endpoint partitions differ, and `m` is the
number of mismatched heavy edges among the 12 fixed matching edges.

The certified result here is only:

> No graph in refined first-link case `(r,k,h,rim)=(4,0,0,0)` has global
> mismatch count `m=0`.

It does **not** exclude the full refined case `(4,0,0,0)`, any other `m`
stratum, or the full uniform type-5 class.  Accordingly it does not increase
the refined-case coverage count, which remains 10/34 at this checkpoint.

## Exact gadget and audit

The gadget assigns a Boolean color to the two components of each endpoint
link.  Triangle edges force a constant color along each component, while an
exact two-of-four constraint on colored common neighbours forces the two
components to receive opposite colors.  An edge mismatch is then equivalent
to the endpoint-color XOR being nonconstant on the four common neighbours.
The 12 exact mismatch bits are constrained by one cardinality equation.

The solver-free audit exhausts the Boolean XOR and difference-witness truth
tables and all `3 x 3` pairs of endpoint partitions.  It is `PASS`:

- `audit_type5_mismatch_gadget.result.json`
- SHA-256 `0399fc3f00269772b3c468a9e16ef0dcd5803e812d121dd245fa2b7e82d73a65`

For the center-cycle exact base, the gadget adds 6,024 variables and 36,996
clauses.  The `(4,0,0,0),m=0` CNF has 37,220 variables, 224,477 clauses, and
SHA-256 `a6aa34f0d49a7f167c8121a83cd12104a26f9abb475b4291198df7b6d6c220d1`.

## Proof gate

The `m=0` stratum was discovery-UNSAT in 79.65 seconds and then passed all four
certificate checks:

1. CaDiCaL emitted an UNSAT DRAT proof.
2. The pinned Linux `drat-trim` checked it and emitted LRAT.
3. The pinned Linux `lrat-check` checked the LRAT proof.
4. The independent native Windows `lrat-check` checked the same LRAT proof.

Compact proof coverage:

- `type5_msplit_4_0_0_0_m0_proof_coverage.result.json`
- SHA-256 `83b07f357d2bef7c9a32915745451467249ce3d0f369ada925629c56f546334d`
- DRAT SHA-256 `0718092a20992e9f32c33f6e4b201352c5f12da265b064ddd1d1567258416bd3`
  (164,876,866 bytes)
- LRAT SHA-256 `ee2b50eca0d9642be5265d5b18e5750542b5102aa1c95ef52564ec0f6d659415`
  (191,772,217 bytes)

Pinned checker hashes are recorded inside the proof-coverage JSON.  The CNF,
DRAT, and LRAT bodies are reproducibility artifacts, not part of the compact
publication packet.

## Bounded assessment and stop rule

The unsplit second-link leaf `(4,0,0,0; b=0,rim1=0)` timed out at 90 seconds
under an assumption solve.  The whole first-link `m=0` stratum closed in 79.65
seconds, but the opposite extreme `m=12` timed out at 180 seconds.  This is
evidence of heterogeneous solver behavior, not a general speedup.  Generating
all 13 large CNFs would risk relocating rather than removing the hard region.

The predeclared policy is therefore to stop after proof-certifying `m=0`:

- do not generate the remaining `m` CNFs;
- do not scale the gadget to other refined parents;
- reconsider only after independent structural gates can remove additional
  `m` strata, or after a separately authorized bounded pilot.

## Minimal compact publication set

Publish these files; omit all `.cnf`, `.drat`, and `.lrat` bodies and logs:

| File | SHA-256 | Purpose |
|---|---|---|
| `TYPE5_GLOBAL_MISMATCH_ASSESSMENT.md` | not self-hashed | scope and stop rule |
| `type5_global_mismatch_sat.py` | `2d3eacf03d0a09c0c59e61c3d6ab6370839842254fff5dc2cb713688eefb5d4c` | deterministic CNF generator and model checker |
| `audit_type5_mismatch_gadget.py` | `1b002d17b71d1b167e67d9cbd8c1beaac90012733f65f5c24a37222b607afa3f` | solver-free gadget audit |
| `audit_type5_mismatch_gadget.result.json` | `0399fc3f00269772b3c468a9e16ef0dcd5803e812d121dd245fa2b7e82d73a65` | audit result |
| `type5_msplit_4_0_0_0_m0_cases.manifest.json` | `4e8a417149e7fb7f3555806fe42ca00ac8cbe0595b472cea996d250abe388354` | regeneration target and CNF hash |
| `type5_msplit_4_0_0_0_m0_cadical.result.json` | `8da4872a7f909786ed1a68b39b58509ecf085b8ac46092620e4f7ef083999c09` | discovery timing and scope |
| `type5_msplit_4_0_0_0_m0_proof_coverage.result.json` | `83b07f357d2bef7c9a32915745451467249ce3d0f369ada925629c56f546334d` | four-check proof manifest |
| `type5_msplit_4_0_0_0_m12_timeout.result.json` | `b0cdf821222870d9a4377086bff8fde1e6bcf3c6bcc338c7df984f2d6a933f6c` | negative scaling evidence |
| `certify_type5_hard0020.sh` | `96e5352b57f0a8f831906523097bb0d79da3018306d82fec048162a01d45ec90` | Linux proof pipeline |
| `verify_type5_generic_proofs.ps1` | `256c2616a311c76f06e9bdf8c2e0d9a0b208c62a60dbb921717923e3dd7f1aa6` | native independent checker |

The exact-link dichotomy and 34-case symmetry audits remain upstream packet
dependencies and need not be duplicated in this compact lane.
