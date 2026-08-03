"""Independent data-semantics audit for Fable's Program Alpha outputs.

This checker does not modify the source logs.  It records hashes, extracts
high-risk claims, checks arithmetic fields, and deterministically replays the
first ``anchor_pin.py`` restart while validating every reported colour class.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import pathlib
import random
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(__file__).with_name("audit_data_semantics.result.json")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def line_hits(path: pathlib.Path, patterns: list[str]) -> list[dict]:
    regexes = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    hits = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if any(regex.search(line) for regex in regexes):
            hits.append({"line": lineno, "text": line})
    return hits


def class_triangle_count(adj: list[int], mask: int) -> int:
    total = 0
    vertices = [v for v in range(len(adj)) if (mask >> v) & 1]
    for i, u in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            v = vertices[j]
            if not ((adj[u] >> v) & 1):
                continue
            for w in vertices[j + 1 :]:
                if ((adj[u] >> w) & 1) and ((adj[v] >> w) & 1):
                    total += 1
    return total


def replay_anchor_first_restart(anchor) -> dict:
    adj, n = anchor.build_L785()
    rng = random.Random(99)
    classes = anchor.greedy_partition(adj, n, rng)
    initial_count = len(classes)
    initial_triangles = [class_triangle_count(adj, mask) for mask in classes]
    successful_eliminations = 0
    while True:
        result = anchor.try_eliminate(adj, n, classes, rng, 4000)
        if isinstance(result, tuple) and result[1] is True:
            classes = result[0]
            successful_eliminations += 1
        else:
            break

    class_triangles = [class_triangle_count(adj, mask) for mask in classes]
    union = 0
    multiplicity_sum = 0
    for mask in classes:
        union |= mask
        multiplicity_sum += mask.bit_count()
    full_mask = (1 << n) - 1
    return {
        "seed": 99,
        "restart": 0,
        "initial_class_count": initial_count,
        "initial_triangle_counts": initial_triangles,
        "successful_eliminations": successful_eliminations,
        "reported_class_count_replay": len(classes),
        "class_triangle_counts": class_triangles,
        "invalid_triangle_bearing_class_count": sum(x > 0 for x in class_triangles),
        "total_monochromatic_triangles": sum(class_triangles),
        "covers_all_vertices": union == full_mask,
        "classes_are_disjoint": multiplicity_sum == union.bit_count(),
        "valid_triangle_free_partition": (
            union == full_mask
            and multiplicity_sum == union.bit_count()
            and not any(class_triangles)
        ),
    }


def main() -> None:
    targets = [
        "RESEARCH_LOG.md",
        "PROGRAM_ALPHA.md",
        "chitf_landscape.py",
        "anchor_pin.py",
        "mt_threshold.py",
        "glauber_tf.py",
        "chitf_landscape.jsonl",
        "anchor_pin.json",
        "anchor_pin2.json",
        "mt_threshold.jsonl",
        "glauber_tf.jsonl",
    ]
    hashes = {name: sha256(ROOT / name) for name in targets}

    claim_patterns = [
        r"lower bound",
        r"upper bound",
        r"bracket",
        r"tf_found",
        r"tf_lower",
        r"stationary",
        r"implied",
        r"every family",
        r"everywhere measured",
        r"empirical class constant",
    ]
    claim_hits = {
        name: line_hits(ROOT / name, claim_patterns)
        for name in ("RESEARCH_LOG.md", "PROGRAM_ALPHA.md")
    }
    script_patterns = [
        r"upper bound",
        r"lower bound",
        r"tf_lower",
        r"chi_tf_lower",
        r"implied_frac_cover",
        r"implied_C",
        r"stationary",
        r"break\s+# smaller c",
    ]
    script_hits = {
        name: line_hits(ROOT / name, script_patterns)
        for name in (
            "chitf_landscape.py",
            "anchor_pin.py",
            "mt_threshold.py",
            "glauber_tf.py",
        )
    }

    landscape = [
        json.loads(line)
        for line in (ROOT / "chitf_landscape.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    landscape_checks = []
    for rec in landscape:
        expected_c = round(rec["k_greedy"] * math.log(rec["Delta"]) / rec["Delta"], 3)
        expected_floor = math.ceil(rec["n"] / rec["k_greedy"])
        landscape_checks.append(
            {
                "n": rec["n"],
                "seed": rec["seed"],
                "C_emp_stored": rec["C_emp"],
                "C_emp_expected": expected_c,
                "beta_floor_stored": rec["beta_floor_from_k"],
                "beta_floor_expected": expected_floor,
                "C_emp_below_half": rec["C_emp"] < 0.5,
                "arithmetic_pass": (
                    rec["C_emp"] == expected_c
                    and rec["beta_floor_from_k"] == expected_floor
                ),
            }
        )

    anchor_json = json.loads((ROOT / "anchor_pin.json").read_text(encoding="utf-8"))
    anchor2_json = json.loads((ROOT / "anchor_pin2.json").read_text(encoding="utf-8"))
    anchor = load_module("fable_anchor_pin_audit", ROOT / "anchor_pin.py")
    replay = replay_anchor_first_restart(anchor)

    mt_records = [
        json.loads(line)
        for line in (ROOT / "mt_threshold.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    glauber_records = [
        json.loads(line)
        for line in (ROOT / "glauber_tf.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    result = {
        "audit": "Fable Program Alpha literature/data items 6-7: data-semantics component",
        "status": "FAIL_WITH_MATERIAL_CORRECTIONS",
        "source_hashes_sha256": hashes,
        "claim_grep": claim_hits,
        "script_grep": script_hits,
        "landscape": {
            "record_count": len(landscape),
            "all_arithmetic_fields_pass": all(x["arithmetic_pass"] for x in landscape_checks),
            "records_below_half": sum(x["C_emp_below_half"] for x in landscape_checks),
            "records_not_below_half": sum(not x["C_emp_below_half"] for x in landscape_checks),
            "checks": landscape_checks,
            "interpretation": (
                "k_greedy is an upper bound when the constructed partition is valid; "
                "the stored table itself contradicts 'below 1/2 everywhere measured'."
            ),
        },
        "anchor": {
            "stored_anchor_pin": anchor_json,
            "stored_anchor_pin2": anchor2_json,
            "deterministic_restart0_replay": replay,
            "direction_check": {
                "premise": "tf_lower <= alpha_tf (a found triangle-free set or Delta floor)",
                "valid_consequence": "none of the form chi_tf >= ceil(n/tf_lower)",
                "needed_for_that_consequence": "an upper bound alpha_tf <= U",
                "stored_chi_tf_lower_is_certified": False,
                "stored_anchor_brackets_are_certified": False,
            },
        },
        "moser_tardos": {
            "record_count": len(mt_records),
            "converged_count": sum(bool(x["converged"]) for x in mt_records),
            "budget_failure_count": sum(not bool(x["converged"]) for x in mt_records),
            "semantics": {
                "convergence": "constructive instance-specific upper-bound evidence",
                "budget_failure": "not a lower bound and not evidence of impossibility",
                "uniform_threshold_claim": "not certified by one seeded run per point",
            },
        },
        "glauber": {
            "record_count": len(glauber_records),
            "single_chain_steps_per_point": 400000,
            "mixing_or_error_certificate_present": False,
            "stationarity_certified": False,
            "mean_density_to_fractional_cover_valid_in_general": False,
            "reason": (
                "A fractional cover from a distribution needs a positive lower bound on "
                "every vertex marginal (or transitivity); the script records only the mean "
                "density.  It also provides no mixing-time or sampling-error bound."
            ),
            "vertex_transitive_exception": (
                "For the exact stationary Gibbs measure on the L(785,53) circulant, "
                "symmetry makes marginals uniform, but the finite single-chain estimate "
                "is still not a certificate."
            ),
        },
        "verdicts": [
            "The landscape arithmetic is internally consistent, but 4/8 stored records are >= 1/2.",
            "The deterministic anchor_pin restart-0 replay must be validated before its k value is used.",
            "tf_lower and Delta lower bounds were inverted into invalid chi_tf lower bounds.",
            "Moser-Tardos failures are budget outcomes only.",
            "Glauber mean-density fields do not certify fractional covers on non-transitive graphs.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
