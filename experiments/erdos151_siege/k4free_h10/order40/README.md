# Order-40 K4-free checks

The proof note is
`research/erdos151/general/k4free_h10/order40/ORDER40_RESIDUAL.md`.

## Proof arithmetic

`check_order40_reduction.py` uses only the Python standard library.  It
exhausts the integer fibre-size funnel and verifies that only the two
equality rows `r=8` and `r=10` survive, together with the numerical counts
used to eliminate them.  Its output is preserved in
`check_order40_reduction.result.json`.

This checker does not verify the cited Bikov or Borodin--Kostochka theorems
and does not encode an arrowing core.  Those are proof-audit obligations.

## Adversarial projection probe

`weight_outside_probe.py` is a PySAT/RC2 probe built before the analytic
funnel was found.  It additionally searches `G[R]` under necessary degree
and `K4`-free constraints and maximizes the number of outside triangle-free
edges.  Its current output independently leaves the same `r=8` and `r=10`
weight rows.  It is explicitly projection-only: a SAT witness is not a
counterexample to #151 and an UNSAT projection is not used as a proof.
