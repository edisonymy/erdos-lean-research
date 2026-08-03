"""Exhaustive labelled-graph check for the incidence-kernel edge lemmas.

This is an independent, deliberately small audit aid.  It enumerates every
simple graph through order 7, keeps the C4-free 2-degenerate graphs, and reports
the maximum number of edges.  It is not used as a premise of the proof.
"""

from itertools import combinations


def is_c4_free(adj: list[int]) -> bool:
    n = len(adj)
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] & adj[v]).bit_count() >= 2:
                return False
    return True


def is_two_degenerate(adj: list[int]) -> bool:
    remaining = (1 << len(adj)) - 1
    while remaining:
        removable = -1
        for v in range(len(adj)):
            if (remaining >> v) & 1 and (adj[v] & remaining).bit_count() <= 2:
                removable = v
                break
        if removable < 0:
            return False
        remaining &= ~(1 << removable)
    return True


def audit_order(n: int) -> tuple[int, int]:
    pairs = list(combinations(range(n), 2))
    maximum = -1
    maximizers = 0
    for mask in range(1 << len(pairs)):
        edge_count = mask.bit_count()
        if edge_count < maximum:
            continue
        adj = [0] * n
        for i, (u, v) in enumerate(pairs):
            if (mask >> i) & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        if not is_c4_free(adj) or not is_two_degenerate(adj):
            continue
        if edge_count > maximum:
            maximum = edge_count
            maximizers = 0
        maximizers += 1
    return maximum, maximizers


def main() -> None:
    expected = {4: 4, 5: 6, 6: 7, 7: 9}
    for n, wanted in expected.items():
        maximum, maximizers = audit_order(n)
        print(f"n={n} max_edges={maximum} labelled_maximizers={maximizers}")
        if maximum != wanted:
            raise SystemExit(f"unexpected maximum at n={n}: {maximum} != {wanted}")
    print("VERIFIED")


if __name__ == "__main__":
    main()
