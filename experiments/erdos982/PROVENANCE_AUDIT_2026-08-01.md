# Erdős 982 provenance audit — 1 August 2026

This is a status audit, not a peer review of the mathematical literature.
It was performed before the new computations in this directory.

## Current public status

- The [Erdős Problems entry](https://www.erdosproblems.com/982) still labels
  #982 open/falsifiable.  Its displayed main text was last edited 19 October
  2025 and still names the 2013 Nivasch–Pach–Pinchasi–Zerbib coefficient.
- The [SciNet problem](https://api.scinet.pub/p/cb372728-ee94-4530-a57b-2c2725158d8b),
  posed 13 July 2026, still shows state `OPEN`, zero investigations, zero
  logged runs, and no verification event.
- The formal-conjectures repository contains a statement, not a proof.

These database states are only evidence about public indexing; they are not
proof that no unpublished or unindexed solution exists.

## Kominers, 25 July 2026

Scott Duke Kominers's page currently lists
[*A (Slightly) Stronger Lower Bound on the Number of Distinct Distances from a
Vertex of a Convex Polygon*](https://www.scottkom.com/assets/articles/Kominers_Distinct_Distances_from_a_Vertex.pdf)
as a 2026 working paper.  The PDF is dated 25 July 2026 and claims

```text
f_conv(n) >= (13/36 + 3/5270)n - O(1).
```

This is a partial improvement, not the conjectured `1/2` coefficient.  The
paper says an ancillary `verify_certificates.py` recomputes its numerical
inequalities, but the PDF supplies no GitHub or download link and the
author's research page links only the PDF.  Searches for the exact title,
coefficient `3/5270`, PDF filename, and ancillary filename found no public
independent verification, journal acceptance, correction, or refutation as
of the audit date.  Accordingly this repository calls it an **unverified
working-paper proof claim**, not an established theorem and not a resolution
of #982.

The PDF bytes fetched and inspected on 1 August have SHA-256
`519c31d5cd1e2443c4528ab665774945e16b173a00f6d6f0589296ffbbf97b2b`.
This pins the audited version because the author's PDF URL is not versioned.

## Public computational benchmark

The Open-Galapagos repository at commit
[`aac2e79be773715ab35b7945f5d9028e46675f02`](https://github.com/Open-Galapagos/evolution-fine-tuning/tree/aac2e79be773715ab35b7945f5d9028e46675f02/skydiscover/benchmarks/math)
contains `n=10` and `n=12` #982 SkyDiscover benchmarks.  Its performance
document tabulates the regular-polygon baseline and no better construction for
the `n=10` benchmark.  No public run table for the `n=12` #982 benchmark was
found at this commit.

The evaluators are not sound counterexample checkers.  They divide squared
distance gaps by `max(|d1|,|d2|,1)`, making the comparison absolute below
unit scale, while their coincidence and convexity tests also use fixed
absolute tolerances.  The evaluator's own `verify_solution` accepts suitably
scaled regular polygons with reported metric `1`, although their exact metric
is `5` and `6`.  `audit_skydiscover_scale_bug.py` and
`skydiscover_scale_bug.json` reproduce this against the pinned public code.
This is a benchmark false positive, not a mathematical counterexample.

## Search perimeter

The audit used exact-title and coefficient searches over the public web,
GitHub-oriented searches, the live author page and PDF, the Erdős Problems
entry, SciNet, the pinned Open-Galapagos repository, and the local pinned
formal-conjectures checkout.  No claim beyond this public perimeter is made.
