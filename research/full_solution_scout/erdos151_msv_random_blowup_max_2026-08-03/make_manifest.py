"""Regenerate the package's byte-count and SHA-256 manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXCLUDED = {"MANIFEST.json"}


def main() -> None:
    records = []
    for path in sorted(p for p in ROOT.iterdir() if p.is_file() and p.name not in EXCLUDED):
        data = path.read_bytes()
        records.append({
            "path": path.name,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    manifest = {
        "generated": "2026-08-03",
        "status": "COMPLETE",
        "excluded": sorted(EXCLUDED),
        "files": records,
        "total_bytes": sum(record["bytes"] for record in records),
    }
    (ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
