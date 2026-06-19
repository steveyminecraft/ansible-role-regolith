"""Tests for AWS PR pre-merge gate decisions."""

from __future__ import annotations

import unittest

from scripts.should_run_aws_pr_tests import should_run_aws_pr_tests


class ShouldRunAwsPrTests(unittest.TestCase):
    def test_runs_for_open_feature_pr(self) -> None:
        run, message = should_run_aws_pr_tests(
            event_name="pull_request",
            head_ref="feat/my-change",
            commit_on_main=False,
        )
        self.assertTrue(run)
        self.assertIn("pre-merge", message)

    def test_skips_workflow_run_on_main(self) -> None:
        run, message = should_run_aws_pr_tests(
            event_name="workflow_run",
            head_ref="main",
            commit_on_main=True,
        )
        self.assertFalse(run)
        self.assertIn("pull_request", message)

    def test_skips_release_please_pr(self) -> None:
        run, message = should_run_aws_pr_tests(
            event_name="pull_request",
            head_ref="release-please--branches--main",
            commit_on_main=False,
        )
        self.assertFalse(run)
        self.assertIn("Release Please", message)

    def test_skips_when_commit_already_on_main(self) -> None:
        run, message = should_run_aws_pr_tests(
            event_name="pull_request",
            head_ref="feat/my-change",
            commit_on_main=True,
        )
        self.assertFalse(run)
        self.assertIn("post-merge", message)

    def test_skips_when_head_branch_is_main(self) -> None:
        run, message = should_run_aws_pr_tests(
            event_name="pull_request",
            head_ref="main",
            commit_on_main=False,
        )
        self.assertFalse(run)
        self.assertIn("default branch", message)


if __name__ == "__main__":
    unittest.main()
