# Erdős #149 structural lane: results and recommendation

Date: 2026-08-03

## What is proved

1. **No subquartic graph with at most 11 vertices is a counterexample.**
   The proof in `N11_ANALYTIC.md` is analytic apart from the published sharp
   CGTT theorem.  Its substantive new step eliminates the only possible
   $n=11,m=22$ compatibility-star shape by path/four-cycle parity and a
   rank-four adjacency-matrix commutation argument.
2. **Every subquartic 21-edge graph is strongly 20-edge-colourable.**
   This follows directly from CGTT.
3. **Every 4-regular graph with at most 12 vertices satisfies the 20 bound.**
   Order 11 is analytic; all 1,544 connected order-12 graphs have explicit
   four-pair savings certificates, independently checked with NetworkX's
   blossom implementation. In a disconnected 4-regular order-12 graph each
   component has order at most 7 and hence at most 14 edges, so distinct
   colours within each component (reused across components) suffice.
4. Exact compatibility-packing gates for 22, 23, and 24 edges, a connector
   localization lemma for the 22-edge star shape, and a regular-completion
   reduction for counterexample hunting are recorded in `STRUCTURAL_NOTES.md`.

None of these statements resolves Erdős #149.

## Construction pulse

Zero candidates were found among:

* 8,750 labelled one-vertex perturbations of the extremal $C_5[2]$ across
  the complete 21/22-edge cases implemented here;
* all ten 4-regular circulant parameter instances at each of orders 11 and 12;
* all 1,544 connected 4-regular order-12 catalogue graphs.

The strongest negative signal is not merely zero hits: the order-12 catalogue
compatibility graphs have maximum-matching size at least nine, while only four
pairs are needed to certify a 20-colouring. The $C_5[2]+x$, 22-edge family
also has at least 14 compatibility pairs, whereas an obstruction would require
all pairs to form one star.

## Independent audits

* This lane's discovery checker uses a custom bounded matching recursion.
* `verify_n12_networkx.py` reparses the catalogue and uses NetworkX's separate
  blossom implementation; it reports `VERIFIED` on all 1,544 records.
* A separate campaign lane checked all 265 connected 4-regular order-11
  catalogue graphs and found a two-edge matching certificate in every $J$.
  Catalogue SHA-256:
  `b24bfe74bed5dc8d3f9758ef61ae2b4503d0c4687c49d9a43ec481e2face13fd`.
* Another independent lane encoded the labelled order-11 star-$J$ shape as
  2,016 CNF clauses. The early Glucose text trace was invalid and is excluded.
  The same hash-pinned CNF was then solved with pinned CaDiCaL 1.9.5: its DRAT
  certificate was VERIFIED by pinned drat-trim, and the converted LRAT was
  independently VERIFIED by native lrat-check. This is a fully checked
  computational audit of the analytic theorem's finite obstruction.

## Hard recommendation

**Pause the negative-construction lane for #149 after preserving these
results.**  Do not expand routine catalogues beyond order 12 without a new
signal.

Reasons:

* the first two orders are now cleanly eliminated;
* the nearest structured perturbations are not near the exact compatibility
  obstruction;
* the order-12 regular census has very large certificate slack;
* the best general theorem has stood at 21 since 2018, so switching immediately
  from a failed small construction hunt to a full proof assault has poor
  one-week expected value.

Resume only if one of these triggers occurs:

1. another lane finds a graph whose compatibility packing number is genuinely
   close to the $m-21$ threshold;
2. a stability theorem strengthens CGTT enough to control the localized
   $3\times3$ connector rectangle at 22 edges;
3. a construction family (lift, voltage graph, or Cayley family) admits a
   provable upper bound on compatibility packing that stays at most $m-21$;
4. a specialist judges the order-11 analytic lemma publishably novel and sees
   a path to extend the common-neighbour matrix argument.

For the campaign's goal of a full Erdős resolution within roughly a week, the
current evidence favours reallocating compute and high-effort reasoning to a
target with an actual near-counterexample or a one-lemma proof bottleneck.
