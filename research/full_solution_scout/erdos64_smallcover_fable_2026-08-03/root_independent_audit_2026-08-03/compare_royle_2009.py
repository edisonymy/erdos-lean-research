#!/usr/bin/env python3
"""Test the packet model against Gordon Royle's 2009 MathOverflow graph.

The comparison is a self-contained exact graph-isomorphism backtrack using
adjacency and all-pairs distances; it uses no NetworkX or campaign code.
Source: https://mathoverflow.net/questions/966/ (answer of 2 Nov 2009).
"""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path


ROYLE_ADJ = {
    0: (1, 2, 3), 1: (0, 4, 7), 2: (0, 6, 9), 3: (0, 5, 8),
    4: (1, 10, 13), 5: (3, 11, 15), 6: (2, 12, 14),
    7: (1, 11, 16), 8: (3, 12, 18), 9: (2, 10, 17),
    10: (4, 9, 28), 11: (5, 7, 26), 12: (6, 8, 27),
    13: (4, 32, 35), 14: (6, 34, 37), 15: (5, 33, 36),
    16: (7, 29, 35), 17: (9, 31, 37), 18: (8, 30, 36),
    19: (29, 30, 31), 20: (27, 32, 34), 21: (28, 32, 33),
    22: (26, 33, 34), 23: (27, 30, 35), 24: (28, 31, 36),
    25: (26, 29, 37), 26: (11, 22, 25), 27: (12, 20, 23),
    28: (10, 21, 24), 29: (16, 19, 25), 30: (18, 19, 23),
    31: (17, 19, 24), 32: (13, 20, 21), 33: (15, 21, 22),
    34: (14, 20, 22), 35: (13, 16, 23), 36: (15, 18, 24),
    37: (14, 17, 25),
}


def distances(adj):
    n = len(adj)
    out = []
    for src in range(n):
        d = [-1] * n
        d[src] = 0
        q = deque([src])
        while q:
            v = q.popleft()
            for w in adj[v]:
                if d[w] == -1:
                    d[w] = d[v] + 1
                    q.append(w)
        out.append(d)
    return out


def find_isomorphism(a, b):
    n = len(a)
    da, db = distances(a), distances(b)
    mapping = {}
    inverse = {}

    def candidates(u):
        vals = []
        for v in range(n):
            if v in inverse or len(a[u]) != len(b[v]):
                continue
            if any(((x in a[u]) != (mapping[x] in b[v])) for x in mapping):
                continue
            if any(da[u][x] != db[v][mapping[x]] for x in mapping):
                continue
            vals.append(v)
        return vals

    def rec():
        if len(mapping) == n:
            return True
        choice = min((u for u in range(n) if u not in mapping),
                     key=lambda u: (len(candidates(u)), -sum(x in mapping for x in a[u])))
        for v in candidates(choice):
            mapping[choice] = v
            inverse[v] = choice
            if rec():
                return True
            del mapping[choice]
            del inverse[v]
        return False

    return dict(mapping) if rec() else None


def main(model_path: Path, output_path: Path) -> int:
    data = json.loads(model_path.read_text(encoding="utf-8"))
    model_adj = [set() for _ in range(data["n"])]
    for u, v in data["edges"]:
        model_adj[u].add(v)
        model_adj[v].add(u)
    royle_adj = [set(ROYLE_ADJ[v]) for v in range(38)]
    assert all(u in royle_adj[v] for u in range(38) for v in royle_adj[u])
    mapping = find_isomorphism(model_adj, royle_adj)
    if mapping is not None:
        assert set(mapping) == set(range(38))
        assert set(mapping.values()) == set(range(38))
        assert all((w in model_adj[v]) == (mapping[w] in royle_adj[mapping[v]])
                   for v in range(38) for w in range(38))
    result = {
        "source": "https://mathoverflow.net/questions/966/",
        "source_date": "2009-11-02",
        "isomorphic": mapping is not None,
        "model_to_royle_mapping": {str(k): v for k, v in sorted((mapping or {}).items())},
        "verdict": "PRIOR-OBJECT" if mapping is not None else "DISTINCT-OBJECT",
    }
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(mapping is None)


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
