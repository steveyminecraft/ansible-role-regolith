"""Tests for CI prerequisite gating before integration tests."""

from __future__ import annotations

import unittest

from scripts.verify_ci_prerequisites import WorkflowRunStatus, evaluate_prerequisites


class VerifyCiPrerequisitesTests(unittest.TestCase):
    def test_evaluate_prerequisites_passes_when_all_succeeded(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus("Unit tests", 1, "completed", "success"),
                WorkflowRunStatus("Security scan", 2, "completed", "success"),
            ]
        )
        self.assertTrue(ok)
        self.assertEqual(message, "all prerequisite workflows passed")

    def test_evaluate_prerequisites_waits_when_one_workflow_pending(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus("Unit tests", 1, "completed", "success"),
                WorkflowRunStatus("Security scan", None, "in_progress", None),
            ]
        )
        self.assertFalse(ok)
        self.assertIn("not finished", message)
        self.assertIn("Security scan", message)

    def test_evaluate_prerequisites_fails_when_workflow_failed(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus("Unit tests", 1, "completed", "failure"),
                WorkflowRunStatus("Security scan", 2, "completed", "success"),
            ]
        )
        self.assertFalse(ok)
        self.assertIn("failed", message)
        self.assertIn("Unit tests", message)


if __name__ == "__main__":
    unittest.main()
