# TARGET_LOCK — Erdős problem #149

Frozen: 2026-08-03 (Europe/London)

Scope: finite simple graphs.

For a graph `G`, a strong edge-colouring is a partition of `E(G)` into
induced matchings. Equivalently,

`chi'_s(G) = chi(L(G)^2)`.

The public Erdős-problem statement is the universal claim

`for every finite simple graph G, chi'_s(G) <= (5/4) Delta(G)^2`.

The customary parity-refined Erdős–Nešetřil formulation is

* `(5/4) Delta^2` for even `Delta`; and
* `(5 Delta^2 - 2 Delta + 1)/4` for odd `Delta`.

The two formulations agree at `Delta=4`. Therefore the following is a
decisive negative certificate for both formulations:

`there exists a finite simple graph G with Delta(G) <= 4 and
chi(L(G)^2) >= 21`.

Logical negation of the public universal statement:

`there exists a finite simple graph G such that
chi(L(G)^2) > (5/4) Delta(G)^2`.

No bounded positive theorem, including verification through any fixed order,
is a resolution of the universal statement.

This file is immutable for this lane. Its SHA-256 is recorded in
`TARGET_LOCK.sha256`; later work must not rewrite either file.
