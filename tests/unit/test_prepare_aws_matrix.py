"""Tests for AWS matrix gating against integration job results."""

from __future__ import annotations

import unittest

from scripts.aws_integration_platforms import PLATFORMS, matrix_from_jobs


class PrepareAwsMatrixTests(unittest.TestCase):
    def test_matrix_includes_only_successful_integration_jobs(self) -> None:
        jobs = [
            {"name": "Debian bookworm", "conclusion": "success"},
            {"name": "Debian trixie", "conclusion": "failure"},
            {"name": "Ubuntu 24.04 (noble)", "conclusion": "success"},
            {"name": "Lint", "conclusion": "success"},
        ]
        matrix = matrix_from_jobs(jobs)
        labels = [entry["label"] for entry in matrix]
        self.assertEqual(labels, ["Debian bookworm", "Ubuntu 24.04 (noble)"])

    def test_platform_catalog_matches_integration_matrix_size(self) -> None:
        self.assertEqual(len(PLATFORMS), 5)


if __name__ == "__main__":
    unittest.main()
