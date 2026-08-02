#!/usr/bin/env python3
"""Schema-v5-arrowfirst entry point for the pinned independent candidate verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
V3_WRAPPER = HERE.parent / "fixed_clique_cegar_v3" / "verify_candidate.py"
EXPECTED_V3_WRAPPER = "df776a5c79ac438fd59c8e98447dd961059613a861bf12f8a563ab5dddfff5c4"


def _load() -> object:
    if hashlib.sha256(V3_WRAPPER.read_bytes()).hexdigest() != EXPECTED_V3_WRAPPER:
        raise RuntimeError("the pinned v3 candidate-verifier wrapper has drifted")
    name = "_erdos151_v3_candidate_wrapper_readonly_for_v5_arrowfirst"
    spec = importlib.util.spec_from_file_location(name, V3_WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned v3 candidate verifier")
    wrapper = importlib.util.module_from_spec(spec)
    sys.modules[name] = wrapper
    spec.loader.exec_module(wrapper)
    wrapper.HERE = HERE
    wrapper.SCHEMA_VERSION = 5
    module = wrapper._load()
    upstream_verify = module.verify_candidate

    def verify_candidate(candidate_path: Path, **kwargs: object) -> dict[str, object]:
        result = upstream_verify(candidate_path, **kwargs)
        provenance = result.get("verifier_source_sha256")
        if isinstance(provenance, dict):
            provenance["v5_arrowfirst_wrapper_sha256"] = hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest()
            provenance["pinned_v3_wrapper_sha256"] = EXPECTED_V3_WRAPPER
        return result

    module.verify_candidate = verify_candidate
    return module


def main(argv: Sequence[str] | None = None) -> int:
    return _load().main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
