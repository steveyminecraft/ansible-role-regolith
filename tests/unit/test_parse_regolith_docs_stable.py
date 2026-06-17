"""Unit tests for scripts/parse-regolith-docs-stable.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "parse-regolith-docs-stable.py"
FIXTURE = ROOT / "tests" / "fixtures" / "regolith-docs-releases.html"


def load_helper():
    spec = importlib.util.spec_from_file_location("parse_regolith_docs_stable", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ParseRegolithDocsStableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.helper = load_helper()
        cls.fixture_html = FIXTURE.read_text(encoding="utf-8")

    def test_parse_stable_versions_from_fixture(self) -> None:
        versions = self.helper.parse_stable_versions(self.fixture_html)
        self.assertEqual(sorted(versions), ["3.10", "3.3", "3.4"])

    def test_latest_stable_prefers_higher_semver(self) -> None:
        self.assertEqual(self.helper.latest_stable(["3.4", "3.10", "3.3"]), "v3.10")

    def test_latest_stable_raises_on_empty_html(self) -> None:
        with self.assertRaises(ValueError):
            self.helper.latest_stable([])

    def test_fixture_latest_is_v3_10(self) -> None:
        versions = self.helper.parse_stable_versions(self.fixture_html)
        self.assertEqual(self.helper.latest_stable(versions), "v3.10")


if __name__ == "__main__":
    unittest.main()
