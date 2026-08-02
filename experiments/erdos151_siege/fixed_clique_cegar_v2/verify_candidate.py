#!/usr/bin/env python3
"""Schema-v2 entry point for the pinned independent candidate verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parent / "fixed_clique_cegar" / "verify_candidate.py"
EXPECTED_SHA256 = "2979e842e681b66c1a0c82c590b037c80a0457196fd6c4889b4e85ad1413d363"
SCHEMA_VERSION = 2


def _source_provenance() -> dict[str, str]:
    return {
        "v2_wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "upstream_a167ff8_verifier_sha256": EXPECTED_SHA256,
        "cases_json_sha256": hashlib.sha256((HERE / "cases.json").read_bytes()).hexdigest(),
        "requirements_sha256": hashlib.sha256(
            (HERE / "requirements.txt").read_bytes()
        ).hexdigest(),
    }


def _load() -> object:
    if hashlib.sha256(UPSTREAM.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("the pinned a167ff8 independent verifier has drifted")
    name = "_erdos151_fixed_clique_verifier_a167ff8_readonly"
    spec = importlib.util.spec_from_file_location(name, UPSTREAM)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load independent verifier from {UPSTREAM}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    module.SCHEMA_VERSION = 2
    module.HERE = HERE
    module.CASES_PATH = HERE / "cases.json"
    upstream_verify = module.verify_candidate

    def verify_candidate(candidate_path: Path, **kwargs: object) -> dict[str, object]:
        data = json.loads(Path(candidate_path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("candidate has an unsupported schema")
        result = upstream_verify(candidate_path, **kwargs)
        provenance = _source_provenance()
        result["verifier_source_sha256"] = provenance
        emit_cnf = kwargs.get("emit_cnf")
        manifest = result.get("formula_manifest")
        if emit_cnf is not None and isinstance(manifest, dict):
            manifest["verifier_source_sha256"] = provenance
            module.atomic_write_json(Path(emit_cnf) / "manifest.json", manifest)
        return result

    module.verify_candidate = verify_candidate
    return module


def main(argv: Sequence[str] | None = None) -> int:
    return _load().main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
