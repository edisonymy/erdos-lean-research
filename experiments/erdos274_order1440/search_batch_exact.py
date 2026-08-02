from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from functools import reduce
from operator import or_
from pathlib import Path

from analyze_spectra import analyze_spectrum


ROOT = Path(__file__).resolve().parent
ORDER = 1440
ALL = (1 << ORDER) - 1
PATTERN_NODE_CAP = 5_000_000
GROUP_SECONDS = 600


def load(gid: int):
    by_index = defaultdict(list)
    meta = {}
    representatives = defaultdict(list)
    for raw in (ROOT / f"cosets{gid}.tsv").read_text().splitlines():
        cid_s, idx_s, subgroup_s, class_s, rep_s, elements_s = raw.split("\t")
        cid = int(cid_s)
        idx = int(idx_s)
        subgroup = int(subgroup_s)
        class_id = int(class_s)
        mask = sum(1 << (int(e) - 1) for e in elements_s.split(","))
        row = (cid, mask)
        by_index[idx].append(row)
        meta[cid] = (idx, subgroup, class_id, mask)
        if rep_s == "1" and mask & 1:
            representatives[idx].append(row)
    return by_index, meta, representatives


def spectrum_for(gid: int) -> tuple[int, ...]:
    for raw in (ROOT / "solvable_subgroup_stats.tsv").read_text().splitlines():
        fields = raw.split("\t")
        if int(fields[0]) == gid:
            return tuple(int(x) for x in fields[4].split(",") if x)
    raise KeyError(gid)


def main() -> None:
    gid = int(sys.argv[1])
    start_pattern = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    by_index, meta, representatives = load(gid)
    _, patterns, _ = analyze_spectrum(spectrum_for(gid))
    patterns = sorted(
        patterns,
        key=lambda choice: (
            min(len(representatives[d]) for d in choice),
            sum(math.log2(len(by_index[d])) for d in choice),
            len(choice),
            choice,
        ),
    )
    deadline = time.monotonic() + GROUP_SECONDS
    total_nodes = 0
    max_pattern_nodes = 0
    cap_patterns = 0
    tested_patterns = 0
    fixed_cases = 0

    for pattern_no, pattern in enumerate(patterns, 1):
        if pattern_no < start_pattern:
            continue
        pattern_start_nodes = total_nodes
        # Every selected right coset can be translated to its subgroup.  Inner
        # conjugacy then reduces that subgroup to one representative per class.
        fixed_idx = min(
            pattern,
            key=lambda d: (len(representatives[d]), len(by_index[d]), d),
        )
        cap_hit = False

        def dfs(remaining, used, picked):
            nonlocal total_nodes, cap_hit
            total_nodes += 1
            if total_nodes % 100_000 == 0 and time.monotonic() >= deadline:
                raise TimeoutError
            if total_nodes - pattern_start_nodes >= PATTERN_NODE_CAP:
                cap_hit = True
                return None
            if not remaining:
                return picked
            best_idx = None
            best_avail = None
            for idx in remaining:
                avail = [(cid, mask) for cid, mask in by_index[idx] if not mask & used]
                if not avail:
                    return None
                if best_avail is None or len(avail) < len(best_avail):
                    best_idx, best_avail = idx, avail
            rest = tuple(idx for idx in remaining if idx != best_idx)
            for cid, mask in best_avail:
                result = dfs(rest, used | mask, picked + [cid])
                if result is not None:
                    return result
                if cap_hit:
                    return None
            return None

        for fixed_cid, fixed_mask in representatives[fixed_idx]:
            fixed_cases += 1
            remaining = tuple(d for d in pattern if d != fixed_idx)
            try:
                result = dfs(remaining, fixed_mask, [fixed_cid])
            except TimeoutError:
                print(
                    json.dumps(
                        {
                            "status": "TIMEOUT",
                            "group": gid,
                            "patterns": tested_patterns,
                            "total_patterns": len(patterns),
                            "fixed_cases": fixed_cases,
                            "nodes": total_nodes,
                            "max_pattern_nodes": max_pattern_nodes,
                            "cap_patterns": cap_patterns,
                        }
                    ),
                    flush=True,
                )
                return
            if result is not None:
                masks = [meta[cid][3] for cid in result]
                assert len(result) == len(pattern)
                assert len(set(meta[cid][0] for cid in result)) == len(result)
                assert sum(mask.bit_count() for mask in masks) == ORDER
                assert sum(masks) == reduce(or_, masks) == ALL
                model = {
                    "group": gid,
                    "candidate_ids": result,
                    "indices": [meta[cid][0] for cid in result],
                }
                (ROOT / f"model{gid}_batch.json").write_text(json.dumps(model, indent=2) + "\n")
                print(json.dumps({"status": "SAT", **model, "nodes": total_nodes}), flush=True)
                return
            if cap_hit:
                break
        tested_patterns += 1
        used_nodes = total_nodes - pattern_start_nodes
        max_pattern_nodes = max(max_pattern_nodes, used_nodes)
        if cap_hit:
            cap_patterns += 1

    status = "COMPLETE_UNSAT" if cap_patterns == 0 else "CAPPED"
    print(
        json.dumps(
            {
                "status": status,
                "group": gid,
                "patterns": tested_patterns,
                "total_patterns": len(patterns),
                "fixed_cases": fixed_cases,
                "nodes": total_nodes,
                "max_pattern_nodes": max_pattern_nodes,
                "cap_patterns": cap_patterns,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
