# Source audit for Erdős #628 order 11

Checked 2026-08-03.

## Live problem and current activity

- Erdős Problems #628, faithful public statement and current remarks:
  https://www.erdosproblems.com/628
- Discussion thread, including Quanyu Tang's 2025-10-25 pointer to the survey
  and recent progress:
  https://www.erdosproblems.com/forum/thread/628?order=newest
- Longbrake and Tariq, *Some Cases of the Erdős-Lovász Tihany Conjecture for
  Claw-free Graphs*, arXiv submission dated 2024-06-21:
  https://arxiv.org/abs/2406.15164

## Decisive priority collision

- Kawarabayashi, Pedersen, and Toft, *Double-Critical Graphs and Complete
  Minors*, Electronic Journal of Combinatorics 17(1), R87, published
  2010-06-07, DOI 10.37236/359:
  https://www.combinatorics.org/ojs/index.php/eljc/article/view/v17i1r87
- Primary PDF.  The order-11 exclusion is on printed page 8, PDF extraction
  lines 297--305 in the web audit:
  https://www.combinatorics.org/ojs/index.php/eljc/article/download/v17i1r87/pdf/
- Earlier arXiv version, submitted 2008-10-17:
  https://arxiv.org/abs/0810.3133

The paper states, in particular, that a non-complete double-critical
6-chromatic graph must have at least 12 vertices, and gives the short
order-11 contradiction reproduced in `REPORT.md`.

## Independent later finite computation

- Kriesell and Pedersen, *On graphs double-critical with respect to the
  colouring number*, Discrete Mathematics & Theoretical Computer Science 17:1
  (2015), pp. 49--62:
  https://dmtcs.episciences.org/2129/pdf

Its introduction states that Sage and `geng` verified the Double-Critical
Graph Conjecture for all graphs on at most 12 vertices (PDF lines 39--46 in the
web audit).  This is corroboration; the 2010 analytic proof is already enough
to kill the assigned order-11 search.
