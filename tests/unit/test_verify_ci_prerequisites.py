"""Tests for CI prerequisite gating before integration tests."""

from __future__ import annotations

import unittest

from scripts.ci_workflow_names import WORKFLOW_SECURITY_SCAN, WORKFLOW_UNIT_TESTS
from scripts.verify_ci_prerequisites import WorkflowRunStatus, evaluate_prerequisites


class VerifyCiPrerequisitesTests(unittest.TestCase):
    def test_evaluate_prerequisites_passes_when_all_succeeded(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus(WORKFLOW_UNIT_TESTS, 1, "completed", "success"),
                WorkflowRunStatus(WORKFLOW_SECURITY_SCAN, 2, "completed", "success"),
            ]
        )
        self.assertTrue(ok)
        self.assertEqual(message, "all prerequisite workflows passed")

    def test_evaluate_prerequisites_waits_when_one_workflow_pending(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus(WORKFLOW_UNIT_TESTS, 1, "completed", "success"),
                WorkflowRunStatus(WORKFLOW_SECURITY_SCAN, None, "in_progress", None),
            ]
        )
        self.assertFalse(ok)
        self.assertIn("not finished", message)
        self.assertIn(WORKFLOW_SECURITY_SCAN, message)

    def test_evaluate_prerequisites_fails_when_workflow_failed(self) -> None:
        ok, message = evaluate_prerequisites(
            [
                WorkflowRunStatus(WORKFLOW_UNIT_TESTS, 1, "completed", "failure"),
                WorkflowRunStatus(WORKFLOW_SECURITY_SCAN, 2, "completed", "success"),
            ]
        )
        self.assertFalse(ok)
        self.assertIn("failed", message)
        self.assertIn(WORKFLOW_UNIT_TESTS, message)


if __name__ == "__main__":
    unittest.main()
