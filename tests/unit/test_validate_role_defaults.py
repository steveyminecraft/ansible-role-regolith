"""Smoke tests for scripts/validate-role-defaults.py."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate-role-defaults.py"


class ValidateRoleDefaultsTests(unittest.TestCase):
    def test_validate_role_defaults_passes_on_repository_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stderr or result.stdout,
        )
        self.assertIn("valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
