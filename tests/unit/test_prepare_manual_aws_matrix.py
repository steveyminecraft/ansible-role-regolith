"""Tests for manual AWS remote test matrix builder."""

from __future__ import annotations

import unittest

from scripts.prepare_manual_aws_matrix import build_matrix


class PrepareManualAwsMatrixTests(unittest.TestCase):
    def test_single_ubuntu_platform_uses_catalog_metadata(self) -> None:
        matrix = build_matrix("ubuntu-noble", "one-arch", "amd64")
        self.assertEqual(len(matrix), 1)
        entry = matrix[0]
        self.assertEqual(entry["label"], "Ubuntu 24.04 (noble)")
        self.assertEqual(entry["platform_id"], "ubuntu-noble")
        self.assertEqual(entry["ansible_user"], "ubuntu")
        self.assertEqual(entry["os_family"], "ubuntu")
        self.assertEqual(entry["os_version"], "24.04")

    def test_all_platforms_returns_five_amd64_entries(self) -> None:
        matrix = build_matrix("all-platforms", "one-arch", "amd64")
        self.assertEqual(len(matrix), 5)
        labels = [entry["label"] for entry in matrix]
        self.assertIn("Debian bookworm", labels)
        self.assertIn("Ubuntu 25.10 (questing)", labels)

    def test_all_archs_duplicates_selected_platform(self) -> None:
        matrix = build_matrix("debian-bookworm", "all-archs", "amd64")
        self.assertEqual([entry["arch"] for entry in matrix], ["amd64", "arm64"])


if __name__ == "__main__":
    unittest.main()
