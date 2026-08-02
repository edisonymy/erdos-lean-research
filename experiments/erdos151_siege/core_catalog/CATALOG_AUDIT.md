# Public catalogue audit (2026-08-02)

## Result

No public full graph6 catalogue for Bikov's 3,041 order-12 or 306,635
order-13 minimal `(3,3)`-Ramsey graphs was located in the endpoints and searches
listed below.  This is a search result, not a claim that no copy exists anywhere.
The missing full catalogue is therefore an explicit blocker to reporting full
order-12/order-13 residual-filter survivor counts.

Two exact public slices *are* reproducibly recoverable.  If `Q` has independence
number two and clique number below six, its complement is an `R(3,6)` graph.
McKay publishes all such graphs.  Complementing and independently checking the
Ramsey and edge-minimal conditions recovers the 124 order-12 and 13 order-13
independence-two cores reported by Bikov.  The derivation and verification files
in this directory do not assume that every McKay input is Ramsey.

## Bikov primary sources

- A. Bikov, *Small minimal (3,3)-Ramsey graphs*, arXiv:1604.03716,
  submitted 2016-04-13: <https://arxiv.org/abs/1604.03716>.
- Journal record, *Annual of Sofia University St. Kliment Ohridski, Faculty of
  Mathematics and Informatics* 103 (2016), pp. 123-147, published 2016-12-12:
  <https://annual.uni-sofia.bg/index.php/fmi/article/view/60>.
- ArXiv source archive SHA-256:
  `1b3b35142584ea8b8dea4dd3cd1c2712c7eefbd9829ab9c8ea97f852c4ecd645`
  (1,154,888 bytes).  The archive contains TeX/BibTeX and PDF figures, including
  drawings of selected graphs, but no graph6 file or complete graph list.
- A. Bikov, *Computation and Bounding of Folkman Numbers*, arXiv:1806.09601:
  <https://arxiv.org/abs/1806.09601>.  Source archive SHA-256:
  `ca1eb0e52a80b509544f36727caa24573a0b493be4a23dafaa955f73c0bfcc15`.
  This restates the classification but likewise contains no complete graph6 list.

The paper reports exactly 3,041 order-12 cores and 306,635 order-13 cores.  Its
order-13 decomposition is 13 graphs with independence number two plus 306,622
with independence number at least three.  Its order-12 table reports 124 graphs
with independence number two.  It classifies all minimal cores only through
order 13.  At order 14 it gives examples and restricted strata, not a complete
classification or a total count.

The same property tables give a catalogue-independent degree-cap prefilter:

- order 12: 43 cores have maximum degree 8, 1,196 have maximum degree 9, and
  1,802 have maximum degree 11.  Thus 1,239 of 3,041 pass `Delta(Q) <= 9`;
- order 13: 16 have maximum degree 8, 61,678 have maximum degree 9, 175,108 have
  maximum degree 10, and 69,833 have maximum degree 12.  Thus 61,694 of 306,635
  pass `Delta(Q) <= 9`.

These counts do not determine the residual-lemma survivor counts because the
degree pattern on each individual candidate clique is needed.

## Public endpoints checked

- ArXiv abstract, HTML, PDF/source archive, and the later thesis source archive.
- The Sofia journal article record and its galleys; only the article PDF is
  attached, with no supplementary-data entry.
- The author's public GitHub account (`asbikov`), which exposed no public
  repositories on the access date.
- House of Graphs text searches for `minimal (3,3)-Ramsey` and `Bikov`, both of
  which returned zero graphs.  Its "Minimal Ramsey graphs" meta-directory uses
  "minimal" in the different extremal `R(3,k;n,e)` sense and is not this
  edge-arrowing-minimal catalogue.
- Internet Archive CDX queries for the author's historical Sofia home-directory
  patterns; no captures were returned.
- General exact-count, graph6, filename, repository, and dataset searches.

## McKay public data and negative controls

McKay's data index states that graph files use graph6/sparse6 and that his data
files are CC BY 4.0 unless otherwise noted:
<https://users.cecs.anu.edu.au/~bdm/data/>.  Relevant source pages are:

- Ramsey graphs: <https://users.cecs.anu.edu.au/~bdm/data/ramsey.html>;
- critical graphs: <https://users.cecs.anu.edu.au/~bdm/data/graphs.html>.

`fetch_sources.py` pins the exact URLs, byte lengths, compressed and decompressed
SHA-256 digests, and record counts.  In particular:

- `r36_12.g6.gz`: 116,792 `R(3,6)` graphs;
- `r36_13.g6.gz`: 275,086 `R(3,6)` graphs;
- edge-6-critical counts at orders 10, 11, 12, 13: 22, 393, 17,036,
  1,479,809;
- edge-7-critical count at order 13: 25,355.

The critical catalogues are public supersets of a potentially useful structural
class, but they are not Bikov's catalogue.  The independent NAE-3-SAT checks in
`derive_catalog.py` retained only 1, 0, and 1 minimal Ramsey graph from the
order-10, order-11, and order-12 edge-6-critical lists, versus Bikov's totals
6, 73, and 3,041.  Explicit minimality testing retained none from the order-13
edge-7-critical list.  These runs are kept as negative controls and prevent an
unsound substitution of similarly named public data.

## How to unblock the full run

Obtain the author's complete, one-record-per-isomorphism-class graph list for
order 12 and/or 13, preferably with its original hash or canonical-label tool
version.  Then run `verify_catalog.py` followed by `filter_core_catalog.py` as
shown in `README.md`.  No change to the residual filter is needed.
