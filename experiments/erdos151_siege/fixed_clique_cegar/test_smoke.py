#!/usr/bin/env python3
"""Small exhaustive and end-to-end tests for fixed_clique_cegar.

No production case is solved here.  The largest graph used is K6.
"""

from __future__ import annotations

import itertools
import json
import random
import shutil
import tempfile
import unittest
from pathlib import Path

from pysat.formula import IDPool
from pysat.solvers import Cadical195

from cegar import (
    CaseConfig,
    CutJournal,
    EdgeVariables,
    GraphSnapshot,
    RunDirectoryLock,
    SearchSession,
    atomic_write_json,
    admissibility_oracle,
    coloring_oracle,
    encode_admissibility_cut,
    encode_arrowing_cut,
    is_clique,
    maximal_cliques_bk,
    pack_bits,
)
from verify_candidate import verify_candidate


HERE = Path(__file__).resolve().parent


def smoke_k6_config() -> CaseConfig:
    return CaseConfig(
        name="SMOKE_K6",
        n=6,
        fixed_clique_size=6,
        forbidden_clique_size=7,
        degree_min=5,
        degree_max=5,
        target_set_size=6,
        scope="K6 candidate smoke test",
    )


def smoke_resume_config(name: str = "SMOKE_RESUME") -> CaseConfig:
    return CaseConfig(
        name=name,
        n=5,
        fixed_clique_size=2,
        forbidden_clique_size=6,
        degree_min=0,
        degree_max=4,
        target_set_size=3,
        scope="small resume smoke test",
    )


def create_k6_candidate(run_dir: Path) -> Path:
    with RunDirectoryLock(run_dir) as run_lock:
        session = SearchSession(run_dir, smoke_k6_config(), run_lock=run_lock)
        try:
            status = session.run(max_iterations=1)
            if status != "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION":
                raise AssertionError(status)
        finally:
            session.problem.close()
    result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    return run_dir / result["candidate_file"]


def graph_from_mask(n: int, mask: int) -> GraphSnapshot:
    count = n * (n - 1) // 2
    return GraphSnapshot(n, tuple(bool((mask >> i) & 1) for i in range(count)))


def brute_maximal_cliques(graph: GraphSnapshot) -> set[int]:
    adj = graph.adjacency()
    result: set[int] = set()
    for mask in range(1, 1 << graph.n):
        vertices = tuple(v for v in range(graph.n) if (mask >> v) & 1)
        if not is_clique(vertices, adj):
            continue
        if any(
            w not in vertices and all((adj[w] >> v) & 1 for v in vertices)
            for w in range(graph.n)
        ):
            continue
        result.add(mask)
    return result


def brute_admissible_set(graph: GraphSnapshot, size: int) -> tuple[int, ...] | None:
    maximal = [mask for mask in brute_maximal_cliques(graph) if mask.bit_count() >= 2]
    for vertices in itertools.combinations(range(graph.n), size):
        members = sum(1 << v for v in vertices)
        if all(mask & ~members for mask in maximal):
            return vertices
    return None


class StructuralTests(unittest.TestCase):
    def test_bron_kerbosch_matches_bruteforce_on_every_graph_n5(self) -> None:
        n = 5
        for graph_mask in range(1 << (n * (n - 1) // 2)):
            graph = graph_from_mask(n, graph_mask)
            self.assertEqual(set(maximal_cliques_bk(graph.adjacency())), brute_maximal_cliques(graph))

    def test_admissibility_oracle_matches_bruteforce(self) -> None:
        samples = list(range(1 << 6))  # every graph on four vertices
        rng = random.Random(151)
        samples.extend(rng.sample(range(1 << 10), 80))
        for index, graph_mask in enumerate(samples):
            n = 4 if index < 64 else 5
            graph = graph_from_mask(n, graph_mask)
            expected = brute_admissible_set(graph, 3)
            actual = admissibility_oracle(graph, 3)
            self.assertEqual(actual is None, expected is None)
            if actual is not None:
                maximal = [m for m in brute_maximal_cliques(graph) if m.bit_count() >= 2]
                members = sum(1 << v for v in actual.vertices)
                self.assertTrue(all(mask & ~members for mask in maximal))

    def test_coloring_oracle_small_and_k6(self) -> None:
        # R(3,3)=6: every graph of order four is nonarrowing.
        for graph_mask in range(1 << 6):
            graph = graph_from_mask(4, graph_mask)
            witness = coloring_oracle(graph)
            self.assertIsNotNone(witness)
        complete_k6 = graph_from_mask(6, (1 << 15) - 1)
        self.assertIsNone(coloring_oracle(complete_k6))


class ProjectionTests(unittest.TestCase):
    def test_admissibility_cut_is_exact_on_every_graph_n4(self) -> None:
        n = 4
        edges = EdgeVariables(n)
        pool = IDPool(start_from=edges.count + 1)
        cut = encode_admissibility_cut(edges, pool, (0, 1, 2), "test-adm")
        with Cadical195(bootstrap_with=cut) as solver:
            for graph_mask in range(1 << edges.count):
                graph = graph_from_mask(n, graph_mask)
                assumptions = [
                    var if graph.edge_bits[var - 1] else -var
                    for var in range(1, edges.count + 1)
                ]
                projected_sat = solver.solve(assumptions=assumptions)
                expected = not brute_admissible_set_for_fixed_s(graph, (0, 1, 2))
                self.assertEqual(projected_sat, expected, graph_mask)

    def test_arrowing_cut_is_exact_on_every_graph_n5(self) -> None:
        n = 5
        edges = EdgeVariables(n)
        # A fixed total coloring; red iff the pair index is 0 mod 3.
        colors = tuple(index % 3 == 0 for index in range(edges.count))
        pool = IDPool(start_from=edges.count + 1)
        cut = encode_arrowing_cut(edges, pool, colors, "test-arrow")
        with Cadical195(bootstrap_with=cut) as solver:
            for graph_mask in range(1 << edges.count):
                graph = graph_from_mask(n, graph_mask)
                assumptions = [
                    var if graph.edge_bits[var - 1] else -var
                    for var in range(1, edges.count + 1)
                ]
                projected_sat = solver.solve(assumptions=assumptions)
                expected = graph_has_fixed_color_mono_triangle(graph, colors)
                self.assertEqual(projected_sat, expected, graph_mask)


def brute_admissible_set_for_fixed_s(
    graph: GraphSnapshot, vertices: tuple[int, ...]
) -> bool:
    members = sum(1 << v for v in vertices)
    maximal = [mask for mask in brute_maximal_cliques(graph) if mask.bit_count() >= 2]
    return all(mask & ~members for mask in maximal)


def graph_has_fixed_color_mono_triangle(
    graph: GraphSnapshot, colors: tuple[bool, ...]
) -> bool:
    pairs = list(itertools.combinations(range(graph.n), 2))
    index = {pair: i for i, pair in enumerate(pairs)}
    for a, b, c in itertools.combinations(range(graph.n), 3):
        edge_indices = (index[(a, b)], index[(a, c)], index[(b, c)])
        if not all(graph.edge_bits[i] for i in edge_indices):
            continue
        triple_colors = [colors[i] for i in edge_indices]
        if triple_colors[0] == triple_colors[1] == triple_colors[2]:
            return True
    return False


class PersistenceAndCandidateTests(unittest.TestCase):
    def test_hash_chained_checkpoint_replays(self) -> None:
        config = CaseConfig(
            name="SMOKE_RESUME",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=6,
            degree_min=0,
            degree_max=4,
            target_set_size=3,
            scope="small resume smoke test",
        )
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            with RunDirectoryLock(run_dir) as run_lock:
                first = SearchSession(run_dir, config, run_lock=run_lock)
                try:
                    self.assertEqual(first.run(max_iterations=1), "PAUSED_AT_LIMIT")
                    self.assertEqual(len(first.journal.records), 1)
                    first_head = first.journal.head
                finally:
                    first.problem.close()

            with RunDirectoryLock(run_dir) as run_lock:
                resumed = SearchSession(run_dir, config, run_lock=run_lock)
                try:
                    self.assertEqual(resumed.journal.records[0]["record_sha256"], first_head)
                    self.assertEqual(resumed.run(max_iterations=1), "PAUSED_AT_LIMIT")
                    self.assertGreaterEqual(len(resumed.journal.records), 2)
                    summary = resumed.audit_summary()
                    self.assertEqual(summary["status"], "AUDIT_OK")
                finally:
                    resumed.problem.close()

    def test_k6_candidate_dump_and_independent_verifier(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            candidate_path = create_k6_candidate(run_dir)
            report = verify_candidate(candidate_path, emit_cnf=run_dir / "verify", solve=True)
            self.assertEqual(
                report["status"],
                "VERIFIED_BY_INDEPENDENT_ENCODING_NO_PROOF_CERTIFICATES",
            )
            self.assertTrue((run_dir / "verify" / "manifest.json").exists())
            audit = SearchSession.from_existing(run_dir)
            try:
                summary = audit.audit_summary()
                self.assertEqual(summary["status"], "AUDIT_OK")
                self.assertEqual(
                    summary["candidate"]["graph_sha256"],
                    report["candidate_graph_sha256"],
                )
            finally:
                audit.problem.close()

    def test_trailing_journal_fragment_is_preserved_and_recovered(self) -> None:
        config = CaseConfig(
            name="SMOKE_RECOVERY",
            n=5,
            fixed_clique_size=2,
            forbidden_clique_size=6,
            degree_min=0,
            degree_max=4,
            target_set_size=3,
            scope="trailing-fragment recovery smoke test",
        )
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            with RunDirectoryLock(run_dir) as run_lock:
                session = SearchSession(run_dir, config, run_lock=run_lock)
                try:
                    session.run(max_iterations=1)
                    expected_head = session.journal.head
                finally:
                    session.problem.close()
            with (run_dir / "cuts.jsonl").open("ab") as handle:
                handle.write(b'{"crash_partial":')
            with RunDirectoryLock(run_dir) as run_lock:
                resumed = SearchSession(run_dir, config, run_lock=run_lock)
                try:
                    self.assertEqual(resumed.journal.head, expected_head)
                    self.assertEqual(len(resumed.journal.records), 1)
                    self.assertEqual(
                        len(list(run_dir.glob("cuts.jsonl.recovered-tail-*.bin"))), 1
                    )
                finally:
                    resumed.problem.close()

    def test_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            path = Path(temp) / "cuts.jsonl"
            journal = CutJournal(path)
            journal.load()
            journal.append({"schema_version": 1, "kind": "test"})
            record = json.loads(path.read_text(encoding="utf-8"))
            record["kind"] = "tampered"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "record hash mismatch"):
                CutJournal(path).load()

    def test_cross_run_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            root = Path(temp)
            source_run = root / "source"
            target_run = root / "target"
            create_k6_candidate(source_run)
            config = smoke_resume_config("SMOKE_TARGET")
            with RunDirectoryLock(target_run) as run_lock:
                session = SearchSession(target_run, config, run_lock=run_lock)
                try:
                    session.run(max_iterations=1)
                finally:
                    session.problem.close()
            shutil.copyfile(source_run / "result.json", target_run / "result.json")
            with self.assertRaisesRegex(ValueError, "result.json run_id"):
                SearchSession.from_existing(target_run)

    def test_relabelled_k6_cannot_claim_an_approved_preset(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            candidate_path = create_k6_candidate(run_dir)
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            candidate["config"]["name"] = "F5_N40"
            atomic_write_json(candidate_path, candidate)
            with self.assertRaisesRegex(ValueError, "exactly match approved preset"):
                verify_candidate(
                    candidate_path,
                    solve=False,
                    approved_preset="F5_N40",
                )

    def test_candidate_graph_n_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            candidate_path = create_k6_candidate(run_dir)
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            candidate["graph"]["n"] = 5
            atomic_write_json(candidate_path, candidate)
            with self.assertRaisesRegex(ValueError, "graph.n does not match config.n"):
                verify_candidate(candidate_path, solve=False)

    def test_progress_journal_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            config = smoke_resume_config("SMOKE_PROGRESS")
            with RunDirectoryLock(run_dir) as run_lock:
                session = SearchSession(run_dir, config, run_lock=run_lock)
                try:
                    session.run(max_iterations=1)
                finally:
                    session.problem.close()
            progress_path = run_dir / "progress.json"
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            progress["journal_head_sha256"] = "f" * 64
            atomic_write_json(progress_path, progress)
            with self.assertRaisesRegex(ValueError, "progress.json journal head"):
                SearchSession.from_existing(run_dir)

    def test_run_directory_lock_is_exclusive_and_reusable(self) -> None:
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            run_dir = Path(temp)
            with RunDirectoryLock(run_dir) as first:
                first.assert_held_for(run_dir)
                with self.assertRaisesRegex(RuntimeError, "locked by another writer"):
                    with RunDirectoryLock(run_dir):
                        pass
            with RunDirectoryLock(run_dir) as replacement:
                replacement.assert_held_for(run_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
