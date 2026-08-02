from __future__ import annotations

import unittest

import triage_pipeline as pipeline


def valid_row() -> dict:
    return {
        "number": 42,
        "ask": "Can one finite object settle the question?",
        "leverage": 3,
        "uncertainty": 2,
        "reachability": 1,
        "collision": 1,
        "verification": 3,
        "total": 10,
        "verdict": "probe",
        "probe_sketch": "enumerate the smallest admissible objects",
        "stale_suspicion": False,
        "stale_why": "",
        "status_flag": "open_no_collision_found",
        "checked_utc": "2026-08-02T12:00:00Z",
        "source_urls": ["https://www.erdosproblems.com/42"],
        "recognition_path": True,
    }


class TriagePipelineTests(unittest.TestCase):
    def test_valid_live_row(self) -> None:
        self.assertEqual(
            pipeline.validate_row(valid_row(), pipeline.Path("test.json"), True),
            [],
        )

    def test_total_mismatch_is_rejected(self) -> None:
        row = valid_row()
        row["total"] = 9
        errors = pipeline.validate_row(row, pipeline.Path("test.json"), True)
        self.assertTrue(any("total 9 != 10" in error for error in errors))

    def test_stale_row_requires_reason(self) -> None:
        row = valid_row()
        row["stale_suspicion"] = True
        errors = pipeline.validate_row(row, pipeline.Path("test.json"), True)
        self.assertTrue(any("stale_why required" in error for error in errors))

    def test_scope_partition(self) -> None:
        rows = [
            {"number": 1, "research_open": True},
            {"number": 2, "research_open": False},
        ]
        self.assertEqual(pipeline.expected_numbers(rows, "formalized-open"), {1})
        self.assertEqual(pipeline.expected_numbers(rows, "non-formalized-open"), {2})

    def test_balanced_chunks_are_complete(self) -> None:
        rows = [{"number": number} for number in range(10)]
        chunks = pipeline.balanced_chunks(rows, 4)
        self.assertEqual([len(chunk) for chunk in chunks], [3, 3, 2, 2])
        self.assertEqual([row for chunk in chunks for row in chunk], rows)

    def test_probe_grade_requires_uncertainty_and_reachability(self) -> None:
        row = valid_row()
        self.assertTrue(pipeline.is_probe_grade(row))
        row["uncertainty"] = 1
        row["collision"] = 2
        self.assertEqual(row["total"], sum(row[field] for field in pipeline.SCORE_FIELDS))
        self.assertFalse(pipeline.is_probe_grade(row))
        row = valid_row()
        row["reachability"] = 0
        row["collision"] = 2
        self.assertEqual(row["total"], sum(row[field] for field in pipeline.SCORE_FIELDS))
        self.assertFalse(pipeline.is_probe_grade(row))


if __name__ == "__main__":
    unittest.main()
