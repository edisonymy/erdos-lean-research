#!/usr/bin/env python3
"""Exhaustively test the proposed #719 completion inequality on small instances.

For H subset of the s-subsets of [n], U(H) consists of the (s-1)-sets that
are contained in no member of H.  We compute exactly

    tau_s(U): minimum number of s-sets whose lower shadows cover U;
    rho(U):   maximum subfamily with pairwise intersection <= s-3.

The conjectured completion inequality is tau_s(U(H)) <= (n-s) rho(U(H)).
This program exhausts all H when requested, deduplicating the induced U.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path


def subsets(n: int, k: int) -> list[tuple[int, ...]]:
    return list(itertools.combinations(range(n), k))


def bitset(xs: tuple[int, ...]) -> int:
    out = 0
    for x in xs:
        out |= 1 << x
    return out


class Instance:
    def __init__(self, n: int, s: int):
        if not (2 <= s <= n - 2):
            raise ValueError("this audit assumes r=n-s>=2 and s>=2")
        self.n = n
        self.s = s
        self.small = subsets(n, s - 1)
        self.large = subsets(n, s)
        self.small_bits = [bitset(x) for x in self.small]
        self.large_bits = [bitset(x) for x in self.large]
        self.shadow_masks: list[int] = []
        self.star_masks = [0] * len(self.small)
        for j, b in enumerate(self.large_bits):
            mask = 0
            for i, a in enumerate(self.small_bits):
                if a & b == a:
                    mask |= 1 << i
                    self.star_masks[i] |= 1 << j
            self.shadow_masks.append(mask)

        # Compatibility means the pair can coexist in a rho-packing.
        self.compat = [0] * len(self.small)
        for i, a in enumerate(self.small_bits):
            for j, b in enumerate(self.small_bits):
                if (a & b).bit_count() <= s - 3:
                    self.compat[i] |= 1 << j

    def uncovered(self, hmask: int) -> int:
        out = 0
        for i, star in enumerate(self.star_masks):
            if hmask & star == 0:
                out |= 1 << i
        return out

    @lru_cache(maxsize=None)
    def rho(self, umask: int) -> int:
        """Maximum clique in the compatibility graph, by exact recursion."""
        if not umask:
            return 0
        # Pick a high-conflict vertex to reduce the recursion.
        choices = [i for i in range(len(self.small)) if umask >> i & 1]
        v = max(choices, key=lambda i: (umask & ~self.compat[i]).bit_count())
        without = self.rho(umask & ~(1 << v))
        with_v = 1 + self.rho((umask & ~(1 << v)) & self.compat[v])
        return max(without, with_v)

    @lru_cache(maxsize=None)
    def tau(self, umask: int) -> int:
        """Minimum lower-shadow set cover, by exact branching."""
        if not umask:
            return 0
        # Branch on the uncovered element with the fewest useful containers.
        elems = [i for i in range(len(self.small)) if umask >> i & 1]
        def containers(i: int) -> list[int]:
            return [j for j, sm in enumerate(self.shadow_masks) if sm >> i & 1]
        i = min(elems, key=lambda x: sum(bool(umask & self.shadow_masks[j]) for j in containers(x)))
        return 1 + min(self.tau(umask & ~self.shadow_masks[j]) for j in containers(i))

    def decode_small(self, mask: int) -> list[list[int]]:
        return [list(a) for i, a in enumerate(self.small) if mask >> i & 1]

    def decode_large(self, mask: int) -> list[list[int]]:
        return [list(a) for i, a in enumerate(self.large) if mask >> i & 1]


def exhaustive(n: int, s: int, stop_first: bool = False, all_u: bool = False) -> dict:
    ins = Instance(n, s)
    total_h = 1 << len(ins.large)
    seen: set[int] = set()
    violations: list[dict] = []
    worst_gap = -10**9
    worst = None
    source = ((None, umask) for umask in range(1 << len(ins.small))) if all_u else (
        (hmask, ins.uncovered(hmask)) for hmask in range(total_h)
    )
    for hmask, umask in source:
        if umask in seen:
            continue
        seen.add(umask)
        tau = ins.tau(umask)
        rho = ins.rho(umask)
        gap = tau - (n - s) * rho
        rec = {
            "H_mask": hmask,
            "H": ins.decode_large(hmask) if hmask is not None else None,
            "U_mask": umask,
            "U": ins.decode_small(umask),
            "tau": tau,
            "rho": rho,
            "gap": gap,
        }
        if gap > worst_gap:
            worst_gap, worst = gap, rec
        if gap > 0:
            violations.append(rec)
            if stop_first:
                break
    return {
        "n": n,
        "s": s,
        "r": n - s,
        "mode": "all_U" if all_u else "realizable_U_from_all_H",
        "H_count": total_h if not all_u else None,
        "distinct_U_checked": len(seen),
        "violation_count": len(violations),
        "first_violation": violations[0] if violations else None,
        "worst_gap": worst_gap,
        "worst_instance": worst,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--s", type=int, required=True)
    ap.add_argument("--stop-first", action="store_true")
    ap.add_argument("--all-u", action="store_true", help="test all U, not just realizable U(H)")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = exhaustive(args.n, args.s, args.stop_first, args.all_u)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
        digest = hashlib.sha256(payload.encode()).hexdigest()
        print(json.dumps({"out": str(args.out), "sha256": digest, **{k: result[k] for k in result if k not in ("first_violation", "worst_instance")}}, sort_keys=True))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
