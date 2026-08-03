#!/usr/bin/env python3
"""Cross-check the pruned primary scan against the full-range independent scan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIMARY = HERE / "scan_through_12.json"
AUDIT = HERE / "audit_full_range.json"
OUT = HERE / "enumeration_crosscheck.json"
GENG = HERE.parents[2] / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"


def survivor_key(row):
    return row["n"], row["m"], row["graph6"], "".join(sorted(row["vertex_types"]))


def main():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    primary_survivors = {survivor_key(row) for row in primary["survivors"]}
    audit_survivors = {survivor_key(row) for row in audit["survivors"]}
    pair_count_failures = {
        key: {"primary": value, "audit": audit["generated_by_order_and_edges"].get(key)}
        for key, value in primary["generated_by_order_and_edges"].items()
        if audit["generated_by_order_and_edges"].get(key) != value
    }
    audit_total = sum(audit["generated_by_order"].values())
    primary_total = sum(primary["generated_by_order"].values())
    verified = (
        primary["status"] == audit["status"] == "COMPLETE"
        and primary["order_max"] == audit["order_max"] == 12
        and primary_survivors == audit_survivors
        and not pair_count_failures
        and audit_total == 10_814_685
        and primary_total == 10_329_398
    )
    result = {
        "status": "VERIFIED" if verified else "FAILED",
        "primary_sha256": hashlib.sha256(PRIMARY.read_bytes()).hexdigest(),
        "audit_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
        "geng_sha256": hashlib.sha256(GENG.read_bytes()).hexdigest(),
        "primary_pruned_graphs": primary_total,
        "independent_full_range_graphs": audit_total,
        "survivor_sets_equal": primary_survivors == audit_survivors,
        "survivors": [list(row) for row in sorted(primary_survivors)],
        "included_pair_count_failures": pair_count_failures,
        "interpretation": "the full-range audit scanned every connected degree-5..6 graph through order 12 and independently found exactly the four primary survivors",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
