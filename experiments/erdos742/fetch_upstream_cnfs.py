"""Fetch byte-pinned canonical-LF CNFs from the public upstream commit."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path


COMMIT = "57fd4b41913670227f7bc86708297d695af7823e"
FILES = {
    "5.cnf": "970d03d5d7625728dacce419e12f57b90946c4750bb58f4f8c8d79a85c3cbdff",
    "6.cnf": "91d0cea090decf6652a680c34efd05acde6951d318dcbd892dc532f78fc48bc9",
    "25.cnf": "f43f7d69fc204d7be37da4e869c1771fe516dac7995175f16c49b7f4990c0c25",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".research-cache/diameter2critical-lf"),
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        target = args.output / name
        if target.exists():
            raise SystemExit(f"refusing to overwrite {target}")
        url = (
            "https://raw.githubusercontent.com/BrianLi009/diameter2critical/"
            f"{COMMIT}/{name}"
        )
        with urllib.request.urlopen(url) as response:
            data = response.read()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise RuntimeError(f"SHA-256 mismatch for {name}: {actual}")
        target.write_bytes(data)
        print(f"{actual}  {target}")


if __name__ == "__main__":
    main()
