"""Tests for Release Please integration run detection."""

from __future__ import annotations

import unittest

from scripts.ci_workflow_names import WORKFLOW_INTEGRATION_TESTS
from scripts.detect_release_pr_integration import is_release_please_integration_run


class DetectReleasePrIntegrationTests(unittest.TestCase):
    def test_accepts_successful_release_please_branch_run(self) -> None:
        self.assertTrue(
            is_release_please_integration_run(
                {
                    "name": WORKFLOW_INTEGRATION_TESTS,
                    "conclusion": "success",
                    "head_branch": "release-please--branches--main",
                    "pull_requests": [],
                }
            )
        )

    def test_accepts_successful_pr_head_from_pull_requests(self) -> None:
        self.assertTrue(
            is_release_please_integration_run(
                {
                    "name": WORKFLOW_INTEGRATION_TESTS,
                    "conclusion": "success",
                    "head_branch": "main",
                    "pull_requests": [
                        {"head": {"ref": "release-please--branches--main"}},
                    ],
                }
            )
        )

    def test_rejects_main_integration_run(self) -> None:
        self.assertFalse(
            is_release_please_integration_run(
                {
                    "name": WORKFLOW_INTEGRATION_TESTS,
                    "conclusion": "success",
                    "head_branch": "main",
                    "pull_requests": [],
                }
            )
        )

    def test_rejects_failed_release_please_run(self) -> None:
        self.assertFalse(
            is_release_please_integration_run(
                {
                    "name": WORKFLOW_INTEGRATION_TESTS,
                    "conclusion": "failure",
                    "head_branch": "release-please--branches--main",
                    "pull_requests": [],
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
