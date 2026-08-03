# Prior-art audit: Erdős #701 / Chvátal's downset conjecture at n=8

Audit date: 2026-08-03 (Europe/London)

## Bottom line

The n=8 finite case is not an open priority target. Leon Eifler's public 2025 TU Berlin
doctoral dissertation reports an exact-rational SCIP solution of the reduced n=8 model and
explicitly states that Chvátal's conjecture is thereby proved for ground sets of size at most
8. The Erdős Problems page is still correct in marking the *general* conjecture open, but it
does not currently mention this improved finite bound.

No campaign result should be described as the first solution of the n=8 case.

## Primary sources

1. Leon Eifler, *Algorithms and Certificates for Exact Mixed Integer Programming*,
   doctoral dissertation, TU Berlin, 2025. DOI:
   https://doi.org/10.14279/depositonce-23941

   - Public repository record: https://depositonce.tu-berlin.de/items/93bbd38c-2f50-47ed-9aaa-88428406cc67
   - DepositOnce date: 2025-06-25; issued 2025.
   - German National Library PDF: https://d-nb.info/1370379641/34
   - Thesis overview, pp. 9–10: explicitly says the improved techniques "allow us to
     prove Chvátal's conjecture for ground sets of size up to 8 elements."
   - Section 8.1.2 / Table 8.1, p. 134: the reduced model `Pred(8)` is solved by the new
     exact SCIP in about 450,000 seconds (described in the text as roughly 5.2 days).
   - Important verification boundary, p. 134: certification was not enabled for n=8
     because the projected VIPR certificate exceeded 1 TB and was impractical for the
     then-current verification tools. Thus this is an exact-rational solver result publicly
     claimed as a proof, but not accompanied by a solver-independent certificate replay.

2. Leon Eifler, Ambros Gleixner, and Jonad Pulaj, *A Safe Computational Framework for
   Integer Programming applied to Chvátal's Conjecture*, arXiv:1809.01572 (2018):
   https://arxiv.org/abs/1809.01572

   This older certified result proves the conjecture for all downsets whose union contains
   at most 7 elements. Its independently checkable rational branch-and-bound result was
   the finite frontier before the dissertation's n=8 exact-SCIP computation.

3. Erdős Problems #701: https://www.erdosproblems.com/701

   The page marks the general conjecture open and warns that its status may lag literature.
   It mentions the covering-number-2 case of Frankl and Kupavskii but not Eifler's 2025 n=8
   finite computation. The page's statement that the general problem cannot be resolved by
   finite computation is consistent with the finite n=8 result.

## Cross-checks and interpretation

- The dissertation uses the same witness variables and strict star inequalities as this
  campaign's direct formulation.
- Its optimality formulation already records the lossless reduction to a downset generated
  by an intersecting family (credited there to Olarte–Santos–Spreer). Therefore our
  independently rederived minimal-downclosure normal form is useful as an audit but is not
  a novelty claim.
- Its Proposition 14 is the same induction principle behind our full-support restriction:
  once n<=7 is known, a first n=8 counterexample can be assumed to contain all singletons
  (and, in the generated-witness form, the witness must use all eight elements).
- The lack of a published >1 TB VIPR artifact is a reproducibility limitation, not a basis
  for claiming priority over the dissertation. A new compact independently checked proof
  could be useful, but it would be an independent verification/improvement rather than the
  first n=8 solution and is outside this bounded campaign lane.

## Search lesson

The initial audit found the 2018 n<=7 paper but missed the 2025 dissertation because the
finite n=8 result appears in a thesis conclusion/performance study rather than in a paper
title or the Erdős Problems bibliography. Future target acquisition should search theses,
institutional repositories, exact-computation software pages, citations by the last-known
authors, and full-text phrases such as "ground sets of size up to 8" before launching a
finite-order computation.
