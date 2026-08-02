#!/usr/bin/env python3
"""Exhaustive small-instance checks for the schema-v2 batching changes."""

from __future__ import annotations

import itertools
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

import cegar as v2


HERE = Path(__file__).resolve().parent


def graph_from_mask(n: int, mask: int) -> v2.GraphSnapshot:
    count = n * (n - 1) // 2
    return v2.GraphSnapshot(n, tuple(bool((mask >> i) & 1) for i in range(count)))


def brute_cliques(adj: tuple[int, ...], size: int) -> list[tuple[int, ...]]:
    return [
        vertices
        for vertices in itertools.combinations(range(len(adj)), size)
        if v2.is_clique(vertices, adj)
    ]


class ExhaustiveOracleTests(unittest.TestCase):
    def test_all_graphs_n5_clique_enumeration_matches_brute_force(self) -> None:
        n = 5
        for mask in range(1 << math.comb(n, 2)):
            adj = graph_from_mask(n, mask).adjacency()
            for size in range(2, n + 1):
                self.assertEqual(
                    v2.enumerate_cliques_exact(adj, size),
                    brute_cliques(adj, size),
                    (mask, size),
                )

    def test_all_graphs_n5_admissibility_batch_equals_brute_force(self) -> None:
        n = 5
        target = 3
        limit = math.comb(n, target) + 1
        for mask in range(1 << math.comb(n, 2)):
            graph = graph_from_mask(n, mask)
            adj = graph.adjacency()
            expected = {
                vertices
                for vertices in itertools.combinations(range(n), target)
                if v2.set_is_admissible(vertices, adj)
            }
            actual = v2.admissibility_oracle_batch(graph, target, limit)
            if not expected:
                self.assertIsNone(actual, mask)
            else:
                assert actual is not None
                self.assertTrue(actual.enumeration_exhausted, mask)
                self.assertEqual(set(actual.vertex_sets), expected, mask)
                self.assertEqual(len(actual.vertex_sets), len(set(actual.vertex_sets)))


class ExhaustiveProjectionTests(unittest.TestCase):
    def test_forbidden_batch_projection_on_all_n5_graphs(self) -> None:
        n = 5
        edges = v2.EdgeVariables(n)
        cliques = [(0, 1, 2), (0, 3, 4), (1, 2, 4)]
        clauses = [
            [-edges.var(u, v) for u, v in itertools.combinations(vertices, 2)]
            for vertices in cliques
        ]
        for mask in range(1 << math.comb(n, 2)):
            graph = graph_from_mask(n, mask)
            adj = graph.adjacency()
            clause_value = all(
                any(
                    not graph.edge_bits[abs(literal) - 1]
                    for literal in clause
                )
                for clause in clauses
            )
            expected = all(not v2.is_clique(vertices, adj) for vertices in cliques)
            self.assertEqual(clause_value, expected, mask)

    def test_admissibility_batch_projection_on_all_n4_graphs(self) -> None:
        n = 4
        edges = v2.EdgeVariables(n)
        pool = v2.IDPool(start_from=edges.count + 1)
        sets = [(0, 1, 2), (1, 2, 3)]
        items = [
            v2.make_batch_item("admissibility", {"vertices": list(vertices)})
            for vertices in sets
        ]
        clauses, item_summaries = v2.encode_admissibility_batch(
            edges, pool, items, "projection-test"
        )
        self.assertEqual(len(item_summaries), len(sets))
        with v2.Cadical195(bootstrap_with=clauses) as solver:
            for mask in range(1 << math.comb(n, 2)):
                graph = graph_from_mask(n, mask)
                assumptions = [
                    index + 1 if bit else -(index + 1)
                    for index, bit in enumerate(graph.edge_bits)
                ]
                actual = solver.solve(assumptions=assumptions)
                expected = all(
                    not v2.set_is_admissible(vertices, graph.adjacency())
                    for vertices in sets
                )
                self.assertEqual(actual, expected, mask)

    def test_eager_forbidden_static_cnf_on_all_n5_graphs(self) -> None:
        config = v2.CaseConfig(
            name="TEST_EAGER",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=0,
            degree_max=4,
            target_set_size=3,
            scope="test",
            forbidden_mode="eager",
            admissibility_batch_size=2,
        )
        problem = v2.OuterProblem(config)
        try:
            self.assertEqual(
                problem.static_encoding["eager_forbidden_clause_count"],
                math.comb(5, 3),
            )
            for mask in range(1 << math.comb(5, 2)):
                graph = graph_from_mask(5, mask)
                assumptions = [
                    index + 1 if bit else -(index + 1)
                    for index, bit in enumerate(graph.edge_bits)
                ]
                actual = problem.solver.solve(assumptions=assumptions)
                adj = graph.adjacency()
                expected = bool(graph.edge_bits[0]) and not brute_cliques(adj, 3)
                self.assertEqual(actual, expected, mask)
        finally:
            problem.close()


class PersistenceTests(unittest.TestCase):
    @staticmethod
    def _k6_candidate_config() -> v2.CaseConfig:
        return v2.CaseConfig(
            name="TEST_K6_CANDIDATE",
            n=6,
            fixed_clique_size=2,
            forbidden_clique_size=7,
            degree_min=5,
            degree_max=5,
            target_set_size=6,
            scope="test K6",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )

    def test_admissibility_batch_pause_resume_and_audit(self) -> None:
        config = v2.CaseConfig(
            name="TEST_ADMISSIBILITY_BATCH",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=6,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(session.run(max_iterations=1), "PAUSED_AT_LIMIT")
                finally:
                    session.problem.close()
            record = json.loads(
                (run_dir / "cuts.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(record["kind"], "admissibility_batch")
            self.assertEqual(record["witness"]["logical_cut_count"], 2)
            self.assertFalse(record["witness"]["enumeration_exhausted"])
            resumed = v2.SearchSession.from_existing(run_dir)
            try:
                self.assertEqual(
                    resumed.audit_summary()["logical_cut_counts"],
                    {"admissibility": 2},
                )
            finally:
                resumed.problem.close()

    def test_complete_forbidden_batch_pause_resume_and_audit(self) -> None:
        config = v2.CaseConfig(
            name="TEST_BATCH_JOURNAL",
            n=6,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=5,
            degree_max=5,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=4,
        )
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(session.run(max_iterations=1), "PAUSED_AT_LIMIT")
                finally:
                    session.problem.close()
            lines = (run_dir / "cuts.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["kind"], "forbidden_clique_batch")
            self.assertEqual(record["witness"]["logical_cut_count"], math.comb(6, 3))
            self.assertEqual(
                len(record["encoding"]["item_encodings"]), math.comb(6, 3)
            )
            resumed = v2.SearchSession.from_existing(run_dir)
            try:
                audit = resumed.audit_summary()
                self.assertEqual(audit["logical_cut_counts"], {"forbidden_clique": 20})
            finally:
                resumed.problem.close()

    def test_tampered_batch_item_is_rejected(self) -> None:
        config = v2.CaseConfig(
            name="TEST_TAMPER",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.run(max_iterations=1)
                finally:
                    session.problem.close()
            journal = run_dir / "cuts.jsonl"
            record = json.loads(journal.read_text(encoding="utf-8"))
            record["witness"]["items"][0]["vertices"] = [0, 1, 4]
            journal.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "record hash mismatch"):
                v2.SearchSession.from_existing(run_dir)

    def test_semantically_incomplete_forbidden_batch_is_rejected(self) -> None:
        config = v2.CaseConfig(
            name="TEST_COMPLETE_BATCH_SEMANTICS",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )
        graph = graph_from_mask(5, (1 << math.comb(5, 2)) - 1)
        cliques = v2.enumerate_cliques_exact(graph.adjacency(), 3)
        items = [
            v2.make_batch_item("forbidden_clique", {"vertices": list(vertices)})
            for vertices in cliques[:-1]
        ]
        record = {
            "kind": "forbidden_clique_batch",
            "candidate": {
                "edges_hex": graph.edges_hex,
                "graph_sha256": graph.graph_sha256,
            },
            "witness": {"items": items, "logical_cut_count": len(items)},
        }
        with self.assertRaisesRegex(ValueError, "not the exact complete list"):
            v2.validate_cut_witness(config, record)

    def test_falsely_exhausted_admissibility_batch_is_rejected(self) -> None:
        config = v2.CaseConfig(
            name="TEST_EXHAUSTED_BATCH_SEMANTICS",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=6,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=20,
        )
        graph = graph_from_mask(5, (1 << math.comb(5, 2)) - 1)
        oracle = v2.admissibility_oracle_batch(graph, 3, 20)
        assert oracle is not None and oracle.enumeration_exhausted
        items = [
            v2.make_batch_item(
                "admissibility",
                {
                    "vertices": list(vertices),
                    "candidate_nontrivial_maximal_clique_count": oracle.maximal_clique_count,
                },
            )
            for vertices in oracle.vertex_sets[:-1]
        ]
        record = {
            "kind": "admissibility_batch",
            "candidate": {
                "edges_hex": graph.edges_hex,
                "graph_sha256": graph.graph_sha256,
            },
            "witness": {
                "items": items,
                "logical_cut_count": len(items),
                "requested_batch_limit": 20,
                "enumeration_exhausted": True,
                "oracle_solver_calls": len(items) + 1,
            },
        }
        with self.assertRaisesRegex(ValueError, "exhausted admissibility batch is incomplete"):
            v2.validate_cut_witness(config, record)

    def test_second_writer_lock_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir):
                with self.assertRaisesRegex(RuntimeError, "locked by another writer"):
                    with v2.RunDirectoryLock(run_dir):
                        pass

    def test_candidate_linkage_and_independent_verifier(self) -> None:
        config = self._k6_candidate_config()
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(
                        session.run(max_iterations=1),
                        "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
                    )
                    assert session.result is not None
                    candidate = run_dir / str(session.result["candidate_file"])
                finally:
                    session.problem.close()
            audited = v2.SearchSession.from_existing(run_dir)
            try:
                self.assertEqual(audited.audit_summary()["status"], "AUDIT_OK")
            finally:
                audited.problem.close()

            wrapper_path = HERE / "verify_candidate.py"
            spec = importlib.util.spec_from_file_location("v2_independent_wrapper", wrapper_path)
            assert spec is not None and spec.loader is not None
            wrapper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(wrapper)
            independent = wrapper._load()
            verify_dir = run_dir / "verify"
            report = independent.verify_candidate(
                candidate, solve=True, emit_cnf=verify_dir
            )
            self.assertEqual(
                report["status"],
                "VERIFIED_BY_INDEPENDENT_ENCODING_NO_PROOF_CERTIFICATES",
            )
            self.assertEqual(
                report["verifier_source_sha256"]["upstream_a167ff8_verifier_sha256"],
                wrapper.EXPECTED_SHA256,
            )
            manifest = v2.load_hashed_json(verify_dir / "manifest.json")
            self.assertEqual(
                manifest["verifier_source_sha256"],
                report["verifier_source_sha256"],
            )

    def test_progress_logical_cut_tampering_is_rejected(self) -> None:
        config = v2.CaseConfig(
            name="TEST_LOGICAL_COUNTS",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.run(max_iterations=1)
                finally:
                    session.problem.close()
            progress_path = run_dir / "progress.json"
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            progress["logical_cut_counts"] = {"forbidden_clique": 1}
            v2.atomic_write_json(progress_path, progress)
            with self.assertRaisesRegex(ValueError, "logical-cut counts"):
                v2.SearchSession.from_existing(run_dir)

    def test_independent_verifier_rejects_wrong_candidate_schema(self) -> None:
        config = self._k6_candidate_config()
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.run(max_iterations=1)
                    assert session.result is not None
                    candidate = run_dir / str(session.result["candidate_file"])
                finally:
                    session.problem.close()
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            payload["schema_version"] = 1
            v2.atomic_write_json(candidate, payload)
            wrapper_path = HERE / "verify_candidate.py"
            spec = importlib.util.spec_from_file_location(
                "v2_schema_check_wrapper", wrapper_path
            )
            assert spec is not None and spec.loader is not None
            wrapper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(wrapper)
            with self.assertRaisesRegex(ValueError, "unsupported schema"):
                wrapper._load().verify_candidate(candidate, solve=False)

    def test_terminal_result_recovers_stale_progress_under_writer_lock(self) -> None:
        config = self._k6_candidate_config()
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                ready_progress = (run_dir / "progress.json").read_bytes()
                try:
                    self.assertEqual(
                        session.run(max_iterations=1),
                        "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
                    )
                finally:
                    session.problem.close()
            (run_dir / "progress.json").write_bytes(ready_progress)
            with self.assertRaisesRegex(ValueError, "progress/result terminal statuses differ"):
                v2.SearchSession.from_existing(run_dir)
            with v2.RunDirectoryLock(run_dir) as lock:
                recovered = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(
                        recovered.progress["status"],
                        "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
                    )
                    self.assertEqual(recovered.audit_summary()["status"], "AUDIT_OK")
                finally:
                    recovered.problem.close()

    def test_trailing_batch_journal_fragment_is_preserved_and_recovered(self) -> None:
        config = v2.CaseConfig(
            name="TEST_BATCH_TAIL",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=3,
            degree_min=4,
            degree_max=4,
            target_set_size=3,
            scope="test complete graph",
            forbidden_mode="lazy",
            admissibility_batch_size=2,
        )
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    session.run(max_iterations=1)
                    expected_head = session.journal.head
                finally:
                    session.problem.close()
            with (run_dir / "cuts.jsonl").open("ab") as handle:
                handle.write(b'{"crash_partial":')
            with self.assertRaisesRegex(ValueError, "invalid journal line"):
                v2.SearchSession.from_existing(run_dir)
            with v2.RunDirectoryLock(run_dir) as lock:
                recovered = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    self.assertEqual(recovered.journal.head, expected_head)
                    self.assertEqual(
                        len(list(run_dir.glob("cuts.jsonl.recovered-tail-*.bin"))), 1
                    )
                finally:
                    recovered.problem.close()

    def test_nonfinite_time_limits_are_rejected(self) -> None:
        config = self._k6_candidate_config()
        with tempfile.TemporaryDirectory(dir=HERE) as raw_dir:
            run_dir = Path(raw_dir) / "run"
            with v2.RunDirectoryLock(run_dir) as lock:
                session = v2.SearchSession(run_dir, config, run_lock=lock)
                try:
                    for value in (float("nan"), float("inf"), -float("inf")):
                        with self.assertRaisesRegex(ValueError, "limits"):
                            session.run(max_iterations=0, time_limit_seconds=value)
                finally:
                    session.problem.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
