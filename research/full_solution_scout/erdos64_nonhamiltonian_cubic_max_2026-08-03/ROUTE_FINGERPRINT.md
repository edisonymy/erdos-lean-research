# Successor route fingerprint

| Field | Frozen value |
|---|---|
| ID | `S-NONHAM-CUBIC-CANONICAL` |
| Mathematical objects | connected simple cubic unlabeled graphs |
| Exact parameter space | all even orders `4 <= n <= 20` |
| Generator language | canonical augmentation / isomorph-free generation |
| Primary filter | exact Hamiltonian-cycle decision; retain non-Hamiltonian graphs |
| Acceptance statistic | dyadic edge core `I(H)` and subsequent Mersenne-edge exclusion |
| Candidate gate | raw-edge survivor plus subdivided block plus two-copy bridge composition, independently parsed and cycle-checked twice |
| Negative gate | exact per-order census agreement, hashes, complete stream accounting, and independent replay |
| Precommitted prediction | every graph has empty dyadic edge core through order 20 |
| Renewal boundary | if negative, move to a structural edge-core theorem or a separately fingerprinted multigraph/adjacent-terminal mechanism; do not repeat Hamiltonian encodings or generic search |

## Successor structural cycle

| Field | Value |
|---|---|
| ID | `S-ADJACENT-TERMINAL-TRIANGLE` |
| Mathematical objects | exact one-defect blocks whose terminal neighbours are adjacent |
| New reduction | forced-square dichotomy, then replace the terminal triangle gadget by one marked edge of a smaller simple cubic graph |
| Cycle map | avoiding cycles retain length; marked cycles of length `L` become cycles of lengths `L+2` and `L+3` |
| Acceptance criterion | marked edge meets every dyadic cycle and lies in no cycle of length `2^k-2` or `2^k-3` |
| Exact consequence | empty cubic cores through order 20 exclude adjacent-terminal blocks through order 23 |
| Status | theorem proved; finite consequence independently census-backed |
