"""Exhaustive six-vertex marked-neighborhood audit for (3,3)-Ramsey graphs.

An edge of the six-vertex neighborhood is absent, red, or blue.  We retain
only colorings in which both color classes are triangle-free, then test all
64 colors of the six spokes to the deleted vertex.  A coloring is marked if
none of those spoke colorings avoids a monochromatic triangle.

This is a deliberately tiny, independent local enumeration: 3^15 cases.
The published proof is analytic and does not depend on this check.
"""

from collections import Counter
from itertools import combinations
import json


N = 6
EDGES = list(combinations(range(N), 2))
TRIANGLES = list(combinations(range(N), 3))
EDGE_INDEX = {e: i for i, e in enumerate(EDGES)}
TRI_MASKS = []
for a, b, c in TRIANGLES:
    TRI_MASKS.append(
        (1 << EDGE_INDEX[(a, b)])
        | (1 << EDGE_INDEX[(a, c)])
        | (1 << EDGE_INDEX[(b, c)])
    )


def triangle_free(mask: int) -> bool:
    return all(mask & tri != tri for tri in TRI_MASKS)


ALL_SPOKE_COLORINGS = (1 << (1 << N)) - 1
RED_EDGE_FORBIDS = []
BLUE_EDGE_FORBIDS = []
for i, j in EDGES:
    red_forbids = 0
    blue_forbids = 0
    for spoke_red in range(1 << N):
        if (spoke_red >> i) & 1 and (spoke_red >> j) & 1:
            red_forbids |= 1 << spoke_red
        if not ((spoke_red >> i) & 1) and not ((spoke_red >> j) & 1):
            blue_forbids |= 1 << spoke_red
    RED_EDGE_FORBIDS.append(red_forbids)
    BLUE_EDGE_FORBIDS.append(blue_forbids)


def all_mask_ors(edge_forbids: list[int]) -> list[int]:
    ors = [0] * (1 << len(EDGES))
    for mask in range(1, len(ors)):
        low = mask & -mask
        idx = low.bit_length() - 1
        ors[mask] = ors[mask ^ low] | edge_forbids[idx]
    return ors


def degrees(mask: int) -> tuple[int, ...]:
    ds = [0] * N
    for idx, (i, j) in enumerate(EDGES):
        if mask & (1 << idx):
            ds[i] += 1
            ds[j] += 1
    return tuple(sorted(ds))


def main() -> None:
    marked_colored = 0
    marked_graphs: set[int] = set()
    marked_min_degree_2: set[int] = set()
    by_edge_count = Counter()

    triangle_free_table = [triangle_free(mask) for mask in range(1 << len(EDGES))]
    red_forbidden = all_mask_ors(RED_EDGE_FORBIDS)
    blue_forbidden = all_mask_ors(BLUE_EDGE_FORBIDS)

    # Iterating the uncolored union and its red submasks visits exactly 3^15
    # disjoint red/blue/absent edge states.
    for union in range(1 << len(EDGES)):
        red = union
        while True:
            blue = union ^ red
            if (
                triangle_free_table[red]
                and triangle_free_table[blue]
                and red_forbidden[red] | blue_forbidden[blue]
                == ALL_SPOKE_COLORINGS
            ):
                marked_colored += 1
                marked_graphs.add(union)
            if red == 0:
                break
            red = (red - 1) & union

    for graph in marked_graphs:
        by_edge_count[graph.bit_count()] += 1
        if degrees(graph)[0] >= 2:
            marked_min_degree_2.add(graph)

    report = {
        "vertices": N,
        "ternary_states": 3 ** len(EDGES),
        "marked_colored_states": marked_colored,
        "marked_labeled_uncolored_graphs": len(marked_graphs),
        "marked_labeled_uncolored_min_degree_at_least_2": len(marked_min_degree_2),
        "edge_counts": {str(k): v for k, v in sorted(by_edge_count.items())},
        "min_edges": min(map(int.bit_count, marked_graphs)),
        "min_edges_with_min_degree_2": min(
            map(int.bit_count, marked_min_degree_2), default=None
        ),
        "max_edges": max(map(int.bit_count, marked_graphs)),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
