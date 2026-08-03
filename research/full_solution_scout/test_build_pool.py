from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research.full_solution_scout.build_pool import (
    OPEN_STATES,
    eligible_status,
    parse_problems_yaml,
)


class BuildPoolStatusTests(unittest.TestCase):
    def test_all_open_state_refinements_are_eligible(self) -> None:
        self.assertEqual(
            OPEN_STATES,
            frozenset({"open", "falsifiable", "decidable", "verifiable"}),
        )
        for status in OPEN_STATES:
            with self.subTest(status=status):
                self.assertTrue(eligible_status(status))

    def test_resolved_and_unknown_states_are_ineligible(self) -> None:
        for status in (None, "", "proved", "disproved", "solved", "independent"):
            with self.subTest(status=status):
                self.assertFalse(eligible_status(status))

    def test_yaml_parser_preserves_refined_status(self) -> None:
        sample = """- number: \"583\"
  status:
    state: \"falsifiable\"
    last_update: \"2026-04-01\"
  formalized:
    state: \"no\"
  tags: [\"graph theory\"]
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "problems.yaml"
            path.write_text(sample, encoding="utf-8")
            parsed = parse_problems_yaml(path)

        self.assertEqual(parsed[583]["status"], "falsifiable")
        self.assertEqual(parsed[583]["status_updated"], "2026-04-01")
        self.assertTrue(eligible_status(parsed[583]["status"]))


if __name__ == "__main__":
    unittest.main()
