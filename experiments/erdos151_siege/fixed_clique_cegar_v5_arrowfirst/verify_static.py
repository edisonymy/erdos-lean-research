#!/usr/bin/env python3
"""Independent static-clause checker adapter for schema-v5-arrowfirst metadata.

V4 deliberately has the same static CNF as pinned v3.  This adapter loads the
independent v3 reconstruction (which imports no search engine), pins its bytes,
and changes only the schema, engine, approved cases, and complete source map.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
V3_DIR = HERE.parent / "fixed_clique_cegar_v3"
EXPECTED_V3_CHECKER = "b93588581b6b6b2a440c01f5dedc54c477894b5a0f97d668e44d635213d77c97"


def _load() -> object:
    path = V3_DIR / "verify_static.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_V3_CHECKER:
        raise RuntimeError("the pinned v3 independent static checker has drifted")
    name = "_erdos151_v3_static_checker_readonly_for_v5_arrowfirst"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned v3 static checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.SCHEMA_VERSION = 5
    module.ENGINE = "fixed_clique_cegar_v5_arrowfirst"
    module.SOURCE_PATHS = {
        "v5-arrowfirst/cegar.py": HERE / "cegar.py",
        "v5-arrowfirst/verify_candidate.py": HERE / "verify_candidate.py",
        "v5-arrowfirst/verify_static.py": HERE / "verify_static.py",
        "v5-arrowfirst/cases.json": HERE / "cases.json",
        "v5-arrowfirst/requirements.txt": HERE / "requirements.txt",
        "pinned-v3/cegar.py": V3_DIR / "cegar.py",
        "pinned-v3/verify_candidate.py": V3_DIR / "verify_candidate.py",
        "pinned-v3/verify_static.py": V3_DIR / "verify_static.py",
        "pinned-v3/cases.json": V3_DIR / "cases.json",
        "pinned-v3/requirements.txt": V3_DIR / "requirements.txt",
    }
    return module


_checker = _load()
_pinned_verify_metadata = _checker.verify_metadata


def verify_metadata(path: Path) -> dict[str, object]:
    metadata = _checker.read_hashed_json(path)
    implementation = metadata.get("implementation")
    if (
        not isinstance(implementation, dict)
        or implementation.get("engine") != "fixed_clique_cegar_v5_arrowfirst"
        or implementation.get("schema") != 5
    ):
        raise ValueError("metadata implementation engine/schema binding is invalid")
    result = _pinned_verify_metadata(path)
    result["pinned_v3_checker_sha256"] = EXPECTED_V3_CHECKER
    result["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    checked = result.get("checked")
    if isinstance(checked, list):
        result["checked"] = [
            "metadata content hash and v5-arrowfirst engine/schema"
            if item == "metadata content hash and v3 engine/schema"
            else item
            for item in checked
        ]
    return result


_checker.verify_metadata = verify_metadata
reconstruct_static = _checker.reconstruct_static


def main() -> int:
    return _checker.main()


if __name__ == "__main__":
    raise SystemExit(main())
