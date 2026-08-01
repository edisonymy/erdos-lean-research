# Erdos Problem 273

## Target Statement

Prove or disprove the following exact statement: there exists a finite strict covering system of the integers whose moduli are all of the form p - 1 for a prime p >= 5.

Here a strict covering system is a finite family of residue classes a_i (mod m_i) whose union is all of Z, with every m_i > 1 and all m_i pairwise distinct. Thus an affirmative solution must give finitely many distinct integers m_i = p_i - 1 (p_i prime, p_i >= 5) and residues a_i such that every integer lies in at least one class. A negative solution must prove that no such finite family exists.

## Research Contract

This is an open research problem, not a request for a known textbook proof. Solve the full quantified statement. A construction with repeated moduli, a covering of only a finite test interval without a common-period certificate, or a proof for only a restricted family is not a solution. Computation is encouraged, but every affirmative certificate must be independently checkable over one common period and every load-bearing general claim must be proved.

The public Lean target is FormalConjectures/ErdosProblems/273.lean in google-deepmind/formal-conjectures at commit 735aee074327b8e78b0d92bb1ee8ea00937c3f51. The source problem is https://www.erdosproblems.com/273. The closely related p >= 3 variant is known affirmative; do not silently use modulus 2, because the target requires p >= 5 and hence even moduli at least 4.

## Requested Output

Write the strongest rigorous blueprint available. If complete, include the exact construction or the complete impossibility proof. If incomplete, identify the smallest precise missing lemma, failed approaches, and falsification tests; do not label partial progress as a solution.

