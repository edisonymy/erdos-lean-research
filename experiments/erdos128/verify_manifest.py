#!/usr/bin/env python3
"""Verify catalogue hashes and record counts locked in MANIFEST.json."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> int:
    manifest = json.loads((HERE / "MANIFEST.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = HERE / entry["name"]
        raw = path.read_bytes()
        raw_hash = hashlib.sha256(raw).hexdigest()
        assert raw_hash == entry["sha256"], (path, raw_hash, entry["sha256"])
        decoded = gzip.decompress(raw) if path.suffix == ".gz" else raw
        if "decoded_sha256" in entry:
            decoded_hash = hashlib.sha256(decoded).hexdigest()
            assert decoded_hash == entry["decoded_sha256"], (
                path, decoded_hash, entry["decoded_sha256"]
            )
        records = len([line for line in decoded.splitlines() if line])
        assert records == entry["records"], (path, records, entry["records"])
        print(f"ok {entry['name']}: {records} records, sha256={raw_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
