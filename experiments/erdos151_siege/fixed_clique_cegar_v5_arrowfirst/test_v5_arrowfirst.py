#!/usr/bin/env python3
"""Adversarial tests for schema-v5-arrowfirst separation."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v4 = load_module("_erdos151_test_v5_arrowfirst", HERE / "cegar.py")
static_checker = load_module("_erdos151_test_v5_arrowfirst_static", HERE / "verify_static.py")


def graph(n: int, pairs: set[tuple[int, int]]) -> object:
    edges = v4.EdgeVariables(n)
    normalized = {tuple(sorted(pair)) for pair in pairs}
    return v4.GraphSnapshot(n, tuple(pair in normalized for pair in edges.pairs))


def custom_config(fixed_size: int) -> object:
    return v4.CaseConfig(
        name=f"TEST_F{fixed_size}",
        n=11,
        fixed_clique_size=fixed_size,
        forbidden_clique_size=fixed_size + 1,
        degree_min=0,
        degree_max=10,
        target_set_size=10,
        scope="unit test",
        admissibility_batch_size=2,
        residual_beta_bound=None,
        residual_admissibility_target_size=11 - fixed_size,
    )


def fixed_only_graph(fixed_size: int) -> object:
    return graph(11, set(__import__("itertools").combinations(range(fixed_size), 2)))


class ResidualOracleTests(unittest.TestCase):
    def test_induced_not_ambient_maximal_cliques_are_used(self) -> None:
        # In G[{0,1,2}], {0,1} is maximal.  Ambiently it is extendible by 3,
        # so an incorrect ambient-maximal-clique oracle would accept all three.
        candidate = graph(4, {(0, 1), (0, 3), (1, 3)})
        ambient = [
            mask
            for mask in v4.maximal_cliques_bk(candidate.adjacency())
            if mask.bit_count() >= 2
        ]
        universe_mask = (1 << 0) | (1 << 1) | (1 << 2)
        self.assertFalse(any((mask & ~universe_mask) == 0 for mask in ambient))
        self.assertIsNone(v4.admissible_subset_oracle(candidate, (0, 1, 2), 3))

    def test_ambient_to_induced_maximality_direction(self) -> None:
        candidate = graph(5, {(0, 1), (0, 2), (1, 2), (3, 4)})
        universe = (0, 1, 2, 3)
        ambient = [m for m in v4.maximal_cliques_bk(candidate.adjacency()) if m.bit_count() >= 2]
        local = [m for m in v4.maximal_cliques_bk(v4._induced_adjacency(candidate.adjacency(), universe)) if m.bit_count() >= 2]
        index = {vertex: i for i, vertex in enumerate(universe)}
        for mask in ambient:
            vertices = [v for v in range(candidate.n) if (mask >> v) & 1]
            if set(vertices) <= set(universe):
                local_mask = sum(1 << index[v] for v in vertices)
                self.assertIn(local_mask, local)

    def test_exact_z_ignores_edge_to_c_but_no_other_fixed_edge(self) -> None:
        config = v4.CaseConfig(
            "TEST_Z", 7, 3, 4, 0, 6, 5, "unit", residual_admissibility_target_size=3
        )
        pairs = {(0, 1), (0, 2), (1, 2), (0, 3), (1, 5), (0, 6), (2, 6)}
        candidate = graph(7, pairs)
        self.assertEqual(v4.residual_vertices(config, candidate, 0), (3, 4))
        self.assertEqual(v4.residual_vertices(config, candidate, 1), (4, 5))
        self.assertEqual(v4.residual_vertices(config, candidate, 2), (4,))

    def test_both_approved_cases_use_requested_residual_targets(self) -> None:
        for name, expected in (("F5_N41", 6), ("F4_N41", 7)):
            with self.subTest(name=name):
                config = v4.load_cases()[name]
                candidate = graph(
                    config.n,
                    set(__import__("itertools").combinations(range(config.fixed_clique_size), 2)),
                )
                separation = v4.residual_admissibility_oracle(config, candidate)
                self.assertIsNotNone(separation)
                assert separation is not None
                self.assertEqual(len(separation.searches), config.fixed_clique_size)
                self.assertEqual(len(separation.items), config.fixed_clique_size)
                self.assertTrue(all(len(item["residual_vertices"]) == expected for item in separation.items))
                self.assertTrue(all(len(item["vertices"]) == 10 for item in separation.items))
                self.assertTrue(all(len(set(item["residual_vertices"])) == expected for item in separation.items))
                self.assertTrue(all(len(set(item["vertices"])) == 10 for item in separation.items))


class TranslationAndEncodingTests(unittest.TestCase):
    def _record(self, fixed_size: int) -> tuple[object, object, dict[str, object]]:
        config = custom_config(fixed_size)
        candidate = fixed_only_graph(fixed_size)
        separation = v4.residual_admissibility_oracle(config, candidate)
        assert separation is not None
        witness = {
            "items": list(separation.items),
            "logical_cut_count": len(separation.items),
            "searches": list(separation.searches),
            "separation_order": "after_arrowing_before_generic_global_admissibility",
        }
        record = {
            "kind": "residual_admissibility_batch",
            "candidate": {"graph_sha256": candidate.graph_sha256, "edges_hex": candidate.edges_hex},
            "witness": witness,
        }
        return config, candidate, record

    def test_sound_translation_and_cut_violation_for_both_cases(self) -> None:
        for fixed_size in (4, 5):
            with self.subTest(fixed_size=fixed_size):
                config, candidate, record = self._record(fixed_size)
                v4.validate_cut_witness(config, record)
                problem = v4.OuterProblem(config)
                try:
                    encoding = problem.build_cut(record["kind"], record["witness"], 0)
                    edge_units = [
                        [index + 1 if bit else -(index + 1)]
                        for index, bit in enumerate(candidate.edge_bits)
                    ]
                    with v4.Cadical195(bootstrap_with=[*encoding.clauses, *edge_units]) as solver:
                        self.assertFalse(solver.solve(), "candidate must violate translated global cut")
                    self.assertEqual(
                        encoding.summary["translation_encoding"],
                        "exact existing global admissibility cut generator",
                    )
                finally:
                    problem.close()

    def test_translation_tampering_is_rejected_even_when_rehashed(self) -> None:
        config, _candidate, record = self._record(5)
        item = dict(record["witness"]["items"][0])
        item["vertices"] = [int(item["fixed_clique_vertex"]), *item["vertices"][1:]]
        body = dict(item)
        body.pop("item_sha256")
        item["item_sha256"] = v4.v3._item_hash("residual_admissibility", body)
        record["witness"]["items"][0] = item
        with self.assertRaisesRegex(ValueError, "translat"):
            v4.validate_cut_witness(config, record)

    def test_stored_z_tampering_is_rejected_even_when_rehashed(self) -> None:
        config, _candidate, record = self._record(4)
        item = dict(record["witness"]["items"][0])
        item["z_vertices"] = item["z_vertices"][1:]
        body = dict(item)
        body.pop("item_sha256")
        item["item_sha256"] = v4.v3._item_hash("residual_admissibility", body)
        record["witness"]["items"][0] = item
        with self.assertRaisesRegex(ValueError, "exactly reproduce"):
            v4.validate_cut_witness(config, record)

    def test_duplicate_residual_and_nine_unique_global_cut_rejected_before_encoding_and_replay(self) -> None:
        for fixed_size in (4, 5):
            with self.subTest(fixed_size=fixed_size):
                config, _candidate, record = self._record(fixed_size)
                item = dict(record["witness"]["items"][0])
                residual = list(item["residual_vertices"])
                residual[1] = residual[0]
                residual.sort()
                item["residual_vertices"] = residual
                item["vertices"] = sorted([*item["fixed_clique_part"], *residual])
                self.assertEqual(len(item["vertices"]), 10)
                self.assertEqual(len(set(item["vertices"])), 9)
                body = dict(item)
                body.pop("item_sha256")
                item["item_sha256"] = v4.v3._item_hash("residual_admissibility", body)
                record["witness"]["items"][0] = item
                with self.assertRaisesRegex(ValueError, "distinct"):
                    v4.validate_cut_witness(config, record)
                problem = v4.OuterProblem(config)
                try:
                    with self.assertRaisesRegex(ValueError, "distinct"):
                        problem.build_cut(record["kind"], record["witness"], 0)
                finally:
                    problem.close()

    def test_existing_generic_global_witness_validation_is_preserved(self) -> None:
        config = custom_config(5)
        candidate = fixed_only_graph(5)
        generic = v4.v3.admissibility_oracle_batch(candidate, 10, 2)
        assert generic is not None
        items = [
            v4.make_batch_item(
                "admissibility",
                {
                    "vertices": list(vertices),
                    "candidate_nontrivial_maximal_clique_count": generic.maximal_clique_count,
                },
            )
            for vertices in generic.vertex_sets
        ]
        record = {
            "kind": "admissibility_batch",
            "candidate": {"graph_sha256": candidate.graph_sha256, "edges_hex": candidate.edges_hex},
            "witness": {
                "items": items,
                "logical_cut_count": len(items),
                "requested_batch_limit": 2,
                "enumeration_exhausted": generic.enumeration_exhausted,
                "oracle_solver_calls": generic.solver_calls,
            },
        }
        self.assertEqual(v4.validate_cut_witness(config, record), candidate)


class PersistenceTests(unittest.TestCase):
    @staticmethod
    def _rewrite_bound_candidate_file_hash(run_dir: Path, candidate_path: Path) -> None:
        candidate_hash = v4.v3.file_sha256(candidate_path)
        for name in ("result.json", "progress.json"):
            path = run_dir / name
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.pop("content_sha256")
            payload["candidate_file_sha256"] = candidate_hash
            v4.atomic_write_json(path, payload)

    def test_complete_forbidden_batch_precedes_arrowing_then_residual(self) -> None:
        config = custom_config(4)
        forbidden_graph = graph(config.n, set(__import__("itertools").combinations(range(5), 2)))
        with tempfile.TemporaryDirectory(dir=HERE) as raw:
            run_dir = Path(raw) / "forbidden-first"
            with v4.RunDirectoryLock(run_dir) as lock:
                session = v4.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.problem.solve = lambda: forbidden_graph
                    self.assertEqual(session.run(max_iterations=1), "PAUSED_AT_LIMIT")
                    self.assertEqual(session.journal.records[0]["kind"], "forbidden_clique_batch")
                finally:
                    session.problem.close()

    def test_arrowing_precedes_residual(self) -> None:
        config = custom_config(5)
        with tempfile.TemporaryDirectory(dir=HERE) as raw:
            run_dir = Path(raw) / "ordered-run"
            with v4.RunDirectoryLock(run_dir) as lock:
                session = v4.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(session.run(max_iterations=1), "PAUSED_AT_LIMIT")
                    self.assertEqual(session.journal.records[0]["kind"], "arrowing")
                finally:
                    session.problem.close()

    def test_generic_fallback_replayed_for_both_fixed_clique_sizes(self) -> None:
        for fixed_size in (4, 5):
            with self.subTest(fixed_size=fixed_size), tempfile.TemporaryDirectory(dir=HERE) as raw:
                config = custom_config(fixed_size)
                pairs = set(__import__("itertools").combinations(range(fixed_size), 2))
                for outside in range(fixed_size, config.n):
                    pairs.add((0, outside))
                    pairs.add((1, outside))
                candidate = graph(config.n, pairs)
                self.assertIsNone(v4.residual_admissibility_oracle(config, candidate))
                run_dir = Path(raw) / "generic-fallback"
                original_coloring = v4.coloring_oracle
                v4.coloring_oracle = lambda _graph: None
                with v4.RunDirectoryLock(run_dir) as lock:
                    session = v4.SearchSession(run_dir, config, run_lock=lock)
                    try:
                        session.problem.solve = lambda: candidate
                        self.assertEqual(session.run(max_iterations=1), "PAUSED_AT_LIMIT")
                        self.assertEqual(session.journal.records[0]["kind"], "admissibility_batch")
                    finally:
                        session.problem.close()
                        v4.coloring_oracle = original_coloring
                resumed = v4.SearchSession.from_existing(run_dir)
                try:
                    self.assertEqual(resumed.audit_summary()["status"], "AUDIT_OK")
                finally:
                    resumed.problem.close()

    def test_resume_audit_and_static_source_binding(self) -> None:
        config = custom_config(5)
        candidate = fixed_only_graph(5)
        separation = v4.residual_admissibility_oracle(config, candidate)
        assert separation is not None
        with tempfile.TemporaryDirectory(dir=HERE) as raw:
            run_dir = Path(raw) / "v5-run"
            with v4.RunDirectoryLock(run_dir) as lock:
                session = v4.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.models_seen = 1
                    session._commit_cut(
                        "residual_admissibility_batch",
                        {"items": list(separation.items), "logical_cut_count": len(separation.items), "searches": list(separation.searches), "separation_order": "after_arrowing_before_generic_global_admissibility"},
                        candidate,
                    )
                finally:
                    session.problem.close()
            resumed = v4.SearchSession.from_existing(run_dir)
            try:
                summary = resumed.audit_summary()
                self.assertEqual(summary["status"], "AUDIT_OK")
                self.assertEqual(summary["logical_cut_counts"]["residual_admissibility"], 5)
            finally:
                resumed.problem.close()

            metadata_path = run_dir / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["source_sha256"]["v5-arrowfirst/cegar.py"] = "0" * 64
            metadata.pop("content_sha256")
            v4.atomic_write_json(metadata_path, metadata)
            with self.assertRaisesRegex(ValueError, "source hashes changed"):
                v4.SearchSession.from_existing(run_dir)

    def test_v3_schema_run_is_rejected_before_writable_resume(self) -> None:
        config = custom_config(5)
        with tempfile.TemporaryDirectory(dir=HERE) as raw:
            run_dir = Path(raw) / "wrong-schema"
            run_dir.mkdir()
            v4.atomic_write_json(
                run_dir / "metadata.json",
                {"schema_version": 3, "implementation": {"engine": "fixed_clique_cegar_v3"}},
            )
            with self.assertRaisesRegex(ValueError, "not a fixed_clique_cegar_v5_arrowfirst"):
                with v4.RunDirectoryLock(run_dir) as lock:
                    v4.SearchSession(run_dir, config, run_lock=lock)

    def test_rehashed_implementation_schema_tamper_rejected_by_resume_and_static_checker(self) -> None:
        for case_name in ("F5_N41", "F4_N41"):
            with self.subTest(case_name=case_name), tempfile.TemporaryDirectory(dir=HERE) as raw:
                run_dir = Path(raw) / "schema-tamper"
                with v4.RunDirectoryLock(run_dir) as lock:
                    session = v4.SearchSession(run_dir, v4.load_cases()[case_name], run_lock=lock)
                    session.problem.close()
                metadata_path = run_dir / "metadata.json"
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                metadata.pop("content_sha256")
                metadata["implementation"]["schema"] = 3
                v4.atomic_write_json(metadata_path, metadata)
                with self.assertRaisesRegex(ValueError, "not a fixed_clique_cegar_v5_arrowfirst"):
                    v4.SearchSession.from_existing(run_dir)
                with self.assertRaisesRegex(ValueError, "engine/schema"):
                    static_checker.verify_metadata(metadata_path)

    def test_rehashed_candidate_command_without_approved_preset_rejected_for_f4_and_f5(self) -> None:
        for case_name in ("F5_N41", "F4_N41"):
            with self.subTest(case_name=case_name), tempfile.TemporaryDirectory(dir=HERE) as raw:
                run_dir = Path(raw) / "candidate-command"
                config = v4.load_cases()[case_name]
                with v4.RunDirectoryLock(run_dir) as lock:
                    session = v4.SearchSession(run_dir, config, run_lock=lock)
                    try:
                        candidate_graph = session.problem.solve()
                        assert candidate_graph is not None
                        session.models_seen = 1
                        candidate_path = session._dump_candidate(
                            candidate_graph,
                            {"target_set_size": 10},
                            {"present_edge_count": sum(candidate_graph.edge_bits)},
                        )
                    finally:
                        session.problem.close()
                candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
                candidate.pop("content_sha256")
                command = candidate["independent_verification"]["command"]
                required = f" --approved-preset {case_name}"
                self.assertIn(required, command)
                candidate["independent_verification"]["command"] = command.replace(required, "")
                v4.atomic_write_json(candidate_path, candidate)
                self._rewrite_bound_candidate_file_hash(run_dir, candidate_path)
                with self.assertRaisesRegex(ValueError, "command/preset binding"):
                    v4.SearchSession.from_existing(run_dir)

    def test_allow_code_drift_still_rejects_non_lowercase_sha256_journal_values(self) -> None:
        malformed_values: tuple[object, ...] = ("A" * 64, "0" * 63, "g" * 64, 7)
        for malformed in malformed_values:
            with self.subTest(malformed=repr(malformed)), tempfile.TemporaryDirectory(dir=HERE) as raw:
                run_dir = Path(raw) / "malformed-source"
                config = custom_config(5)
                candidate = fixed_only_graph(5)
                separation = v4.residual_admissibility_oracle(config, candidate)
                assert separation is not None
                witness = {
                    "items": list(separation.items),
                    "logical_cut_count": len(separation.items),
                    "searches": list(separation.searches),
                    "separation_order": "after_arrowing_before_generic_global_admissibility",
                }
                with v4.RunDirectoryLock(run_dir) as lock:
                    session = v4.SearchSession(
                        run_dir, config, run_lock=lock, checkpoint_ready=False
                    )
                    try:
                        source_map = dict(session.current_sources)
                        source_map["v5-arrowfirst/cegar.py"] = malformed
                        encoding = session.problem.build_cut(
                            "residual_admissibility_batch", witness, 0
                        )
                        session.journal.append(
                            {
                                "schema_version": v4.SCHEMA_VERSION,
                                "run_id": session.metadata["run_id"],
                                "kind": "residual_admissibility_batch",
                                "candidate": {
                                    "graph_sha256": candidate.graph_sha256,
                                    "edges_hex": candidate.edges_hex,
                                },
                                "witness": witness,
                                "outer_model_number": 1,
                                "implementation_source_sha256": source_map,
                                "encoding": encoding.summary,
                            }
                        )
                    finally:
                        session.problem.close()
                with self.assertRaisesRegex(ValueError, "malformed implementation source hash"):
                    v4.SearchSession.from_existing(run_dir, allow_code_drift=True)

    def test_independent_static_checker_accepts_fresh_v5_metadata(self) -> None:
        config = v4.load_cases()["F5_N41"]
        with tempfile.TemporaryDirectory(dir=HERE) as raw:
            run_dir = Path(raw) / "v5-static"
            with v4.RunDirectoryLock(run_dir) as lock:
                session = v4.SearchSession(run_dir, config, run_lock=lock)
                session.problem.close()
            report = static_checker.verify_metadata(run_dir / "metadata.json")
            self.assertEqual(report["status"], "STATIC_CLAUSE_STREAM_VERIFIED")
            self.assertEqual(report["source_sha256"], v4.collect_source_hashes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
