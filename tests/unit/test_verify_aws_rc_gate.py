"""Tests for AWS RC gate before Galaxy publication."""

from __future__ import annotations

import unittest

from scripts.verify_aws_rc_gate import (
    parse_stable_release_tag,
    rc_tag_sort_key,
    verify_aws_jobs,
)


class VerifyAwsRcGateTests(unittest.TestCase):
    def test_parse_stable_release_tag(self) -> None:
        self.assertEqual(parse_stable_release_tag("v3.7.0"), "v3.7.0")
        self.assertIsNone(parse_stable_release_tag("v3.7.0-rc.1"))
        self.assertIsNone(parse_stable_release_tag("main"))

    def test_rc_tag_sort_key(self) -> None:
        self.assertLess(
            rc_tag_sort_key("v3.7.0-rc.1"),
            rc_tag_sort_key("v3.7.0-rc.2"),
        )
        self.assertLess(
            rc_tag_sort_key("v3.6.9-rc.9"),
            rc_tag_sort_key("v3.7.0-rc.1"),
        )

    def test_verify_aws_jobs_requires_platform_jobs(self) -> None:
        ok, message = verify_aws_jobs(
            [
                {
                    "name": "Prepare EC2 test matrix",
                    "conclusion": "success",
                }
            ]
        )
        self.assertFalse(ok)
        self.assertIn("no AWS remote test platform jobs", message)

    def test_verify_aws_jobs_fails_on_platform_failure(self) -> None:
        ok, message = verify_aws_jobs(
            [
                {
                    "name": "Prepare EC2 test matrix",
                    "conclusion": "success",
                },
                {"name": "Debian bookworm", "conclusion": "success"},
                {"name": "Ubuntu 24.04 (noble)", "conclusion": "failure"},
            ]
        )
        self.assertFalse(ok)
        self.assertIn("Ubuntu 24.04 (noble)", message)

    def test_verify_aws_jobs_passes_when_all_platform_jobs_succeed(self) -> None:
        ok, message = verify_aws_jobs(
            [
                {
                    "name": "Prepare EC2 test matrix",
                    "conclusion": "success",
                },
                {"name": "Debian bookworm", "conclusion": "success"},
                {"name": "Ubuntu 24.04 (noble)", "conclusion": "success"},
            ]
        )
        self.assertTrue(ok)
        self.assertIn("2 platform job(s)", message)


if __name__ == "__main__":
    unittest.main()
