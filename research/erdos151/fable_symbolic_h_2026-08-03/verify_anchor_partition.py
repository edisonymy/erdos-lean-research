"""Independent checker for an L(785,53) triangle-free partition artifact."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph() -> tuple[list[int], int]:
    n = 785
    steps = set()
    x = 1
    while True:
        x = (x * 53) % n
        steps.add(x)
        steps.add((-x) % n)
        if x == 1:
            break
    steps.discard(0)
    adj = [0] * n
    for u in range(n):
        for d in steps:
            adj[u] |= 1 << ((u + d) % n)
        adj[u] &= ~(1 << u)
    return adj, n


def has_triangle(adj: list[int], vertices: int) -> bool:
    remaining = vertices
    while remaining:
        u_bit = remaining & -remaining
        u = u_bit.bit_length() - 1
        remaining ^= u_bit
        neighbours = adj[u] & remaining
        scan = neighbours
        while scan:
            v_bit = scan & -scan
            v = v_bit.bit_length() - 1
            scan ^= v_bit
            if adj[v] & neighbours:
                return True
    return False


def main() -> None:
    source = pathlib.Path(sys.argv[1])
    destination = pathlib.Path(sys.argv[2])
    payload = json.loads(source.read_text(encoding="utf-8"))
    classes = [int(value, 16) for value in payload["partition_classes_hex"]]
    adj, n = graph()
    seen = 0
    triangle_free = []
    disjoint = True
    for vertices in classes:
        disjoint &= not bool(seen & vertices)
        seen |= vertices
        triangle_free.append(not has_triangle(adj, vertices))
    result = {
        "status": "PASS" if disjoint and all(triangle_free) and seen == (1 << n) - 1 else "FAIL",
        "source": source.as_posix(),
        "source_sha256": sha256(source),
        "checker_sha256": sha256(pathlib.Path(__file__)),
        "class_count": len(classes),
        "classes_pairwise_disjoint": disjoint,
        "covers_all_785_vertices": seen == (1 << n) - 1,
        "each_class_triangle_free": triangle_free,
    }
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
