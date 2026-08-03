# Erdős #149: structural/construction lane

Frozen date: 2026-08-03

This directory contains an independent attack on the Δ=4 case of the
Erdős--Nešetřil strong edge-colouring conjecture. It does **not** claim a full
solution.

## Main outputs

* **N11_ANALYTIC.md** — proof that every subquartic graph on at most 11
  vertices is strongly 20-edge-colourable.
* **STRUCTURAL_NOTES.md** — exact compatibility-packing reductions, connector
  localization, regularization, and structured-family results.
* **RESULTS.md** — scope, audits, and the hard pause/continue recommendation.
* **REPORT.md** — frozen executive report and exact handoff.
* **PRIORITY_AUDIT.md** — live literature and announcement check.
* **structured_pulse.py** / **structured_pulse_result.json** — reproducible
  perturbation, circulant, and n=12 catalogue checks.
* **verify_n12_networkx.py** / **n12_networkx_audit.json** — independent
  blossom matching audit.
* **12_4reg.txt** — the public catalogue of 1,544 connected 4-regular graphs
  on 12 vertices, hash-pinned in the outputs and manifest.

## Reproduce

From this directory:

~~~powershell
python structured_pulse.py --catalogue-12 12_4reg.txt --out structured_pulse_result.json
..\..\..\.venv\Scripts\python.exe verify_n12_networkx.py 12_4reg.txt --out n12_networkx_audit.json
~~~

Expected high-level results:

* candidate count 0;
* 1,544 catalogue graphs checked by each route;
* independent audit status VERIFIED;
* every order-12 catalogue compatibility graph has maximum matching size at
  least 9, hence in particular four pairwise-disjoint two-edge colour blocks.

## Exact boundaries

The analytic order-11 result depends on the published CGTT theorem but not on
SAT or catalogue enumeration. The order-12 computational theorem covers every
4-regular graph (connected graphs by catalogue; disconnected graphs by the
smaller-component argument). It does not cover nonregular order-12 graphs.

The construction families are exhaustive only within their stated parameter
families. No result here resolves Erdős problem #149.
