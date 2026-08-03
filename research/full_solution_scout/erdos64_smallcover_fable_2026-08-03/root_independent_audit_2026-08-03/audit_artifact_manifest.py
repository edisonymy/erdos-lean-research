#!/usr/bin/env python3
"""Audit the packet's SHA-256 ledger, accounting for Git CRLF checkout."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(packet: Path, output: Path) -> int:
    workspace = packet.parents[2]
    rows = []
    for raw_line in (packet / "CERT_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        expected, name = raw_line.split(maxsplit=1)
        name = name.strip()
        path = workspace / name if name.startswith("research/") else packet / name
        if not path.exists():
            rows.append({"name": name, "expected": expected, "status": "MISSING"})
            continue
        data = path.read_bytes()
        raw_sha = digest(data)
        lf_sha = digest(data.replace(b"\r\n", b"\n"))
        if raw_sha == expected:
            status = "MATCH_RAW"
        elif lf_sha == expected:
            status = "MATCH_AFTER_CRLF_NORMALIZATION"
        else:
            status = "MISMATCH"
        rows.append({
            "name": name,
            "expected": expected,
            "raw_sha256": raw_sha,
            "lf_normalized_sha256": lf_sha,
            "bytes": len(data),
            "status": status,
        })
    counts = Counter(row["status"] for row in rows)
    result = {"packet": str(packet), "counts": dict(counts), "artifacts": rows}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    return 1 if counts.get("MISMATCH", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
