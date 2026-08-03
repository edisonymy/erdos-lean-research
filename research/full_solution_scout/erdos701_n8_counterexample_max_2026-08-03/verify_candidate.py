#!/usr/bin/env python3
"""Definition-level independent checker for any #701 search model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    args = ap.parse_args()
    data = json.loads(args.result.read_text(encoding="utf-8"))
    if data.get("family_masks") is None:
        raise SystemExit("NO_MODEL")
    f = set(map(int, data["family_masks"]))
    a = set(map(int, data["witness_masks"]))
    assert all(0 <= s < 256 for s in f | a)
    assert 0 in f and 0 not in a
    assert a <= f
    assert set().union(*({i for i in range(8) if s & (1 << i)} for s in f)) == set(range(8))

    for s in f:
        t = s
        while True:
            assert t in f
            if t == 0:
                break
            t = (t - 1) & s
    alist = sorted(a)
    for i, s in enumerate(alist):
        assert s != 0
        for t in alist[i + 1:]:
            assert s & t
    stars = [sum(1 for s in f if s & (1 << x)) for x in range(8)]
    assert all(len(a) > z for z in stars)
    print(json.dumps({
        "verified": True,
        "family_size": len(f),
        "witness_size": len(a),
        "star_sizes": stars,
        "minimum_gap": min(len(a) - z for z in stars),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
