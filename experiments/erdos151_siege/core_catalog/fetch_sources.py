#!/usr/bin/env python3
"""Fetch and pin the public McKay graph6 inputs used by this audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path

from catalog_lib import iter_graph6, sha256_decompressed, sha256_path


SOURCES = {
    "crit_10_6.g6": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/crit/crit_10_6.g6",
        "bytes": 220,
        "sha256": "2b78b194725a4a28c208bf996e575d43fcb6ce5ca2e0a755012e7e30b16714c3",
        "decompressed_sha256": "2b78b194725a4a28c208bf996e575d43fcb6ce5ca2e0a755012e7e30b16714c3",
        "records": 22,
    },
    "crit_11_6.g6": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/crit/crit_11_6.g6",
        "bytes": 4716,
        "sha256": "9c118696aa02a36cc8526cf7243ee5927b283b86d14ee545d65591a5b3824093",
        "decompressed_sha256": "9c118696aa02a36cc8526cf7243ee5927b283b86d14ee545d65591a5b3824093",
        "records": 393,
    },
    "crit_12_6.g6": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/crit/crit_12_6.g6",
        "bytes": 221468,
        "sha256": "c2f81aa14e4353167ca9b1becea7abfc426c28ddc5ed38f141f9dd04e02de710",
        "decompressed_sha256": "c2f81aa14e4353167ca9b1becea7abfc426c28ddc5ed38f141f9dd04e02de710",
        "records": 17036,
    },
    "crit_13_6.g6.gz": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/crit/crit_13_6.g6.gz",
        "bytes": 12496183,
        "sha256": "76e08215ebf9a054aa08d6af9f7fc801dad4874025ac2650e7752a852179d3b6",
        "decompressed_sha256": "64849b59c6e2fad1fb77ade191ebdec3215dfef41933f562b6b95b26be28d07e",
        "records": 1479809,
    },
    "crit_13_7.g6": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/crit/crit_13_7.g6",
        "bytes": 380325,
        "sha256": "2ec8eafd16e48434890278a23476586182f4b138ccf4b9fe0dc2bad2146b1208",
        "decompressed_sha256": "2ec8eafd16e48434890278a23476586182f4b138ccf4b9fe0dc2bad2146b1208",
        "records": 25355,
    },
    "r36_12.g6.gz": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/ramsey/r36_12.g6.gz",
        "bytes": 633408,
        "sha256": "17e176a0f7e7397dbca7c9cb6295034dd74cf529ca62e7e717226dc1b0b7b96d",
        "decompressed_sha256": "0c9d8264d2e423ed16cb2ddbe8c8c846637d7e7aba277aacbb9af134d4738297",
        "records": 116792,
    },
    "r36_13.g6.gz": {
        "url": "https://users.cecs.anu.edu.au/~bdm/data/ramsey/r36_13.g6.gz",
        "bytes": 1645859,
        "sha256": "12d94cdedc18c56f55cc1fc08ddad4852f43e5d3ea20bf0e00cdbedfc5036604",
        "decompressed_sha256": "bf59b7a5c3cb6d018f40b35928aeb30473d4491a8e6311eec10129bde741e0d1",
        "records": 275086,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--only", nargs="+", choices=tuple(SOURCES))
    return parser.parse_args()


def validate(path: Path, expected: dict[str, object]) -> dict[str, object]:
    observed = {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "decompressed_sha256": sha256_decompressed(path),
        "records": sum(1 for _ in iter_graph6(path)),
    }
    for key in ("bytes", "sha256", "decompressed_sha256", "records"):
        if observed[key] != expected[key]:
            raise ValueError(
                f"{path.name}: observed {key}={observed[key]!r}, "
                f"expected {expected[key]!r}"
            )
    return observed


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    chosen = args.only or list(SOURCES)
    manifest: dict[str, object] = {
        "accessed_utc_date": "2026-08-02",
        "license_note": (
            "McKay's data index states that his data files are CC BY 4.0 unless "
            "otherwise indicated. Check the live index before redistribution."
        ),
        "files": {},
    }
    for name in chosen:
        expected = SOURCES[name]
        destination = args.output_dir / name
        if not destination.exists() or sha256_path(destination) != expected["sha256"]:
            temporary = destination.with_name(destination.name + ".download")
            request = urllib.request.Request(
                str(expected["url"]),
                headers={"User-Agent": "erdos151-core-catalog-audit/1.0"},
            )
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open(
                "wb"
            ) as output:
                while block := response.read(1 << 20):
                    output.write(block)
            os.replace(temporary, destination)
        observed = validate(destination, expected)
        manifest["files"][name] = {**expected, **observed}
        print(f"validated {name}: {observed['records']} records")

    manifest_path = args.output_dir / "fetch_manifest.json"
    temporary_manifest = manifest_path.with_name(manifest_path.name + ".tmp")
    with temporary_manifest.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary_manifest, manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
