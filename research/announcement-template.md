# Witness announcement fast path

Purpose: compress the time from *verified witness* to *public timestamped
release* to under three hours.  Fill every slot; delete nothing.  A slot
that cannot be filled honestly means the announcement is not ready.

Primary timestamp venue:
[`edisonymy/erdos-lean-research`](https://github.com/edisonymy/erdos-lean-research).
Zenodo and Software Heritage are follow-on preservation routes.  Do not state
that a draft, DOI, or archive exists until its creation has been confirmed.

---

## Release package skeleton

```
erdosNNN-witness-YYYY-MM-DD/
├── README.md            # this template, filled
├── witness/             # the object itself, smallest faithful encoding
├── verify_a.(py|cs|…)   # checker 1 — written from the definition
├── verify_b.(py|cs|…)   # checker 2 — independent implementation, no shared helpers
├── logs/                # both checkers' transcripts on the witness
├── SHA256SUMS           # every file above
└── statement-audit.md   # see slot 2
```

## README slots

### 1. Claim, in one paragraph

Problem number, the exact public statement resolved, the direction
(counterexample / construction), and the sentence "This resolves the
problem as stated; it does not claim more."  State any convention
choices explicitly.

### 2. Statement fidelity audit

- Authoritative statement source(s) with URLs and access date.
- Formal Conjectures file + commit hash if formalized.  If no public formal
  statement exists, say so explicitly.  Note any divergence between the
  database wording, cited literature, and any later formalization.
- Quantifier-by-quantifier reading of the statement against the witness.

### 3. The witness

Exact object (edge list / integer tuple / set / configuration), its
encoding, and its size.  Small enough to re-check by hand where possible.

### 4. Verification

- Checker A: what it checks, from which definition, transcript hash.
- Checker B: same, plus the sentence "implemented independently; shares
  no verification code with checker A."
- Any third check (hand computation, CAS, exhaustive local audit).

### 5. Novelty and priority

- Full recency gate re-run inside the announcement window
  ([`recency-audit.md`](recency-audit.md)): live problem page +
  comments, VibeMathed live query, GitHub code/issue search,
  Formal Conjectures issues/PRs, Zenodo, arXiv, announcement feeds,
  primary literature.  Record timestamps and hashes of what was seen.
- Named prior work closest to the result and why it does not contain it.

### 6. Provenance and disclosure

- AI involvement, per the campaign's standing disclosure language.
- Compute used, wall time, and any trusted components remaining
  (solvers, catalogues, libraries) — with the statement of what does
  *not* depend on them (a positive witness should depend on nothing but
  the two checkers and the definition).

### 7. Timestamps

- Git commit + tag, GitHub release URL, Zenodo DOI, Software Heritage
  snapshot ID, and (optional) a hash posted to a public timestamping
  service.  Record all creation times in UTC.

### 8. Expert review and recognition

- Names and relevant expertise of reviewers who have agreed to be named;
  otherwise state that review is pending.
- Exact version and hash reviewed, questions raised, and resulting changes.
- Problem-database/forum submission, preprint plan, and the venue most likely
  to reach specialists in the problem's area.

---

## Order of operations on discovery day

1. Freeze the witness; hash everything.
2. Run both checkers on clean checkouts; capture transcripts.
3. Fill slots 1–4.  **Stop if anything is awkward to state honestly.**
4. Re-run the full recency gate (slot 5).  A collision found here is a
   result too — record it and stand down.
5. Commit, tag, release, Zenodo, Software Heritage — in that order.
6. Only after the timestamps exist: notify the problem database maintainers,
   relevant forum thread, and selected expert reviewers, linking the release.
7. Prepare a conventional preprint or concise research note if the result
   survives review.  Add Lean when it materially improves verification or
   communication; do not let it obscure or delay the mathematical claim.
