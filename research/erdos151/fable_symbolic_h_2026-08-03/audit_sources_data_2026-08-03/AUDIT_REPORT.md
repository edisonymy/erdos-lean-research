# Adversarial audit: Fable items 6-7

Date: 2026-08-03.  Scope: `RESEARCH_LOG.md`, `PROGRAM_ALPHA.md`,
`chitf_landscape.py`, `anchor_pin.py` and the unaccompanied `anchor_pin2`
output, `mt_threshold.py`, and `glauber_tf.py`.  The audited source logs were
not edited.

## Executive verdict

**FAIL WITH MATERIAL CORRECTIONS.**  The main published asymptotic inputs are
real and the corrected clique-colouring implication is sound.  However:

1. R1's order-of-magnitude clique-transversal connection was publicly written
   down before this campaign, in *A note on the clique-transversal number*
   (dated 21 April 2026).  It cannot carry a novelty or priority claim.
2. `anchor_pin.py`'s reported 10-class partition is invalid.  A deterministic
   replay of restart 0 gives exactly 10 purported classes, all 10 contain
   triangles, with 3,227 monochromatic triangles in total.
3. The claimed lower bounds `chi_tf >= ceil(n/tf_lower)` and the brackets
   `[6,10]`, `[6,9]` reverse the relevant inequality.  A found triangle-free
   set, or the sound floor `alpha_tf >= Delta`, is a **lower** bound on the
   largest class size and gives no such lower bound on `chi_tf`.
4. The Glauber averages neither certify stationarity nor yield a fractional
   cover on a non-transitive graph from mean density alone.
5. The table itself has four of eight capped-process records at or above
   `C_emp=1/2`, contradicting “below 1/2 everywhere/every family measured.”

No complete solution, finite counterexample, or publishable new theorem follows
from the audited ledger.

## 6. Literature and constant ledger

### HHKP: pass, with normalization caution

Hefty--Horn--King--Pfender, arXiv:2510.19718v3 (submitted 22 October
2025; revised 19 February 2026), prove

`R(3,k) >= (1/2+o(1)) k^2/log k`.

Their abstract and introduction also record the best known upper bound
`R(3,k) <= (1+o(1)) k^2/log k` and say the coefficient `1/2` is conjectured
to be tight by multiple groups.  This verifies the ledger's source claim.

It does **not** prove that a limit `c_R` exists.  Safe language is that the
proved lower coefficient is `c_0=1/2`; expressions such as
`c_H=1/sqrt(2c_R)` are conditional on an asymptotic Ramsey constant existing.
Unconditionally,

`(1/sqrt(2)+o(1)) sqrt(n log n) <= H(n) <= (1+o(1)) sqrt(n log n)`.

### MSV: pass

Morris--Sahasrabudhe--Verstraete, arXiv:2607.16118v1 (17 July 2026),
prove `f_{s,s+1}(n)=Theta(sqrt(n log n))` for every fixed `s>=2`.  Their
construction and the campaign's use of it for an upper bound are directionally
correct.  The paper itself invokes JMRS for the matching lower bound.

For the minimum of `beta` over **all** graphs, MSV is not needed: a
triangle-free Ramsey graph already has `beta=alpha=O(sqrt(n log n))`.  MSV is
useful for the analogous fixed-clique/pure-triangular faces.

### JMRS: theorem passes; “coefficient 1 is tight” does not

Joret--Micek--Reed--Smid, arXiv:2006.11353v2 / EJC 28(3):P3.51 (2021),
prove, for every fixed epsilon and sufficiently large maximum degree,

`chi_c(G) <= (1+epsilon) Delta/log Delta`,

and derive `chi_c(G)=O(sqrt(n/log n))`.  A clique-colour class is exactly an
admissible set here, so `beta(G)>=n/chi_c(G)` is valid.  Their corollary's
specific decomposition also yields the asymptotic explicit floor
`beta(G)>=(1/3-o(1))sqrt(n log n)`.

The paper calls its results tight because their **orders** are tight on
triangle-free graphs.  It does not prove that leading coefficient `1` in the
maximum-degree theorem is attained or optimal.  The log's statement that the
“general-graph value C=1 is tight” is unsupported and should not be used.

### R1 and priority: theorem correct, novelty claim fails

The order statement

`min_{|V(G)|=n} beta(G) = Theta(sqrt(n log n))`

is correct.  But the public PDF *A note on the clique-transversal number*,
dated 21 April 2026, proves exactly the equivalent statement
`max tau(G)=n-Theta(sqrt(n log n))`, explicitly via JMRS and triangle-free
Ramsey graphs.  Its final remark explicitly identifies the stronger EGT
speculation `tau(G)<=n-f(n)` and says it remains open.  The PDF exposes no
author or version metadata, so it is bibliographically weak, but it is still a
prior public disclosure.  The campaign must not claim priority for R1 or say
that published/public work had not made the connection.

The narrower constant optimizations and Folkman-class restrictions may still
be new, but this audit did not establish novelty.  They require a separate,
scholarly prior-art review before any claim escalation.

### R2': conditionally sound only for genuine clique colouring

Let a least counterexample at jump `h` have `n=R(3,h)`, `beta=h-1`, and
`Delta<=h-1`.  If every such graph has a genuine clique colouring satisfying

`chi_c <= (C+o(1)) Delta/log Delta`

with `C<1/2`, then

`n <= (C+o(1)) h^2/log h`,

contradicting HHKP's `n >= (1/2-o(1))h^2/log h`.  This conditional deduction
is sound (bounded `Delta` is even easier via a proper colouring).

Two corrections are essential:

- use the proved coefficient `1/2`, not an assumed existing `c_R`;
- `chi_tf` (partition into triangle-free sets) is a clique colouring only on
  the pure-triangular `K4`-free face.  In a graph with maximal edges, a
  triangle-free class can contain a maximal edge and be inadmissible.
  Consequently Program Alpha's `chi_tf`/occupancy program, as presently
  formulated, does **not** settle the maximal-edge face and hence does not by
  itself settle all of #151.

Similarly, the displayed equivalence based only on a `liminf` constant
`c*>=c_H` is too strong: strict separation of the relevant liminf/limsup is a
safe sufficient statement; equality and oscillation do not imply the exact
pointwise conjecture.

### The `F_e(3,3;4)<=50` implication: pass

If the `(50,11)` K4-free CEGAR produces a graph with no admissible 11-set,
`R(3,11)<=50` makes it a #151 counterexample.  The audited Folkman reduction
then forces edge-arrowing `(3,3)`.  By the definition of the edge Folkman
number, this immediately gives `F_e(3,3;4)<=50`.  The implication is sound.

The current range is `21 <= F_e(3,3;4) <= 786`, not `[20,786]`: Hassan,
Radziszowski and Van Overberghe, arXiv:2605.16542v1 (15 May 2026), record the
updated range.  This stale bound does not affect the implication.

## 7. Data hygiene

### `chitf_landscape.py`

The greedy insertion test is directionally correct: it constructs
triangle-free colour classes, so a successful `k_greedy` is an instance-level
**upper** bound on `chi_tf`.  All stored arithmetic fields recompute exactly.

The interpretation does not match the data.  Of eight stored capped-process
records, only four are below `1/2`; the two `n=200` records have `0.562` and
the two `n=400` records have `0.542`.  Claims that every measured family or
every measured instance is below `1/2` are false.

### `anchor_pin.py` and `anchor_pin2.json`

The repair routine inserts `v` after ejecting one endpoint of one violating
edge, without checking whether other violating edges remain.  The independent
checker replays seed 99, restart 0:

- initial valid greedy partition: 18 classes;
- eight reported eliminations: 10 classes;
- triangle counts in those classes:
  `[299,261,370,373,304,338,264,231,410,377]`;
- total monochromatic triangles: 3,227.

Thus `anchor_pin.json`'s `chi_tf_upper=10` is not an upper bound.  No
`anchor_pin2.py`, colour assignment, or independently checkable partition is
present for `anchor_pin2.json`; its `k<=9` claim is therefore unverifiable and
must not be used.

Independently, `tf_lower<=alpha_tf` cannot imply
`chi_tf>=ceil(n/tf_lower)`.  Such a lower bound on `chi_tf` would require an
**upper** bound on `alpha_tf`.  Therefore the stored lower endpoints and both
anchor “brackets” are invalid even if a corrected upper partition is later
found.

### `mt_threshold.py`

When the routine terminates with no monochromatic triangle, it gives
instance-specific constructive upper-bound evidence.  Exhausting 300,000
resamples gives no lower bound and no impossibility certificate.  One seeded
run per point cannot justify a uniform “critical threshold”; the results may
be described only as calibration runs.  The early-break assumption that a
smaller `c` will also fail is not a valid stochastic monotonicity argument.

### `glauber_tf.py`

The files contain single-chain time averages after 400,000 steps, with no
mixing theorem, convergence diagnostic, replication, or error interval.
Calling them stationary densities is therefore unverified.

More seriously, a fractional cover obtained from a distribution over
triangle-free sets requires a lower bound on **every vertex marginal**.  The
script records only mean density and sets `implied_frac_cover=1/mean`.  That
conversion is invalid on the non-transitive process and synthetic CBU graphs.
For the exact stationary measure on vertex-transitive `L(785,53)`, symmetry
would make exact marginals uniform, but the finite Monte Carlo estimate still
is not a certificate.

### Grep conclusion

The earlier `tf_found` use in `RESEARCH_LOG.md` is directionally sound: a
found triangle-free set of size at least `h` kills that candidate family.  The
material direction error is the later conversion of `tf_lower` into a lower
bound on `chi_tf`, plus the unsupported Glauber fractional-cover conversion.

## Safe carry-forward

- Keep HHKP, MSV, JMRS, the asymptotic sandwich for `H`, the genuine
  clique-colouring conditional R2', and the `F_e<=50` implication.
- Retire all anchor brackets and anchor `C` readings until a colour assignment
  is saved and independently checked.
- Treat `chitf_landscape` values as upper-bound experiments, with the actual
  above/below-half rows reported.
- Treat MT failures and all Glauber values as heuristic diagnostics only.
- Do not claim novelty for the order-of-magnitude R1 observation.

Machine evidence: `audit_data_semantics.py` and
`audit_data_semantics.result.json`.  Source metadata and dates:
`literature_sources.json`.
