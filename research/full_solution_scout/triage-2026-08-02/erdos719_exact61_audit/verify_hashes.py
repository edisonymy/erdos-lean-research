#!/usr/bin/env python3
"""Verify SHA256SUMS.json against every other file in this audit bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent
    manifest_path = root / "SHA256SUMS.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {row["path"]: row for row in manifest["files"]}
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path != manifest_path
        and "__pycache__" not in path.parts
    }
    if actual_paths != set(expected):
        raise AssertionError(
            f"manifest path mismatch: missing={actual_paths-set(expected)}, "
            f"stale={set(expected)-actual_paths}"
        )
    for relative_path in sorted(actual_paths):
        path = root / relative_path
        row = expected[relative_path]
        if path.stat().st_size != row["bytes"]:
            raise AssertionError(f"size mismatch: {relative_path}")
        if sha256(path) != row["sha256"]:
            raise AssertionError(f"SHA-256 mismatch: {relative_path}")
    print(f"SHA256_MANIFEST_PASS files={len(actual_paths)}")


if __name__ == "__main__":
    main()
