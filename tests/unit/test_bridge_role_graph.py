"""Unit tests for scripts/bridge-role-graph.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bridge-role-graph.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bridge_role_graph", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BridgeRoleGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def test_bridge_graph_adds_role_to_verify_edge(self) -> None:
        graph = {
            "nodes": [
                {"id": "tasks_main", "label": "tasks/main.yml"},
                {"id": "molecule_default_verify", "label": "molecule/default/verify.yml"},
            ],
            "links": [],
        }
        result, added = self.mod.bridge_graph(graph)
        self.assertGreaterEqual(added, 1)
        links = result["links"]
        self.assertTrue(
            any(
                link["source"] == "molecule_default_verify"
                and link["target"] == "tasks_main"
                for link in links
            )
        )

    def test_bridge_graph_skips_missing_nodes(self) -> None:
        graph = {
            "nodes": [{"id": "tasks_main", "label": "tasks/main.yml"}],
            "links": [],
        }
        _, added = self.mod.bridge_graph(graph)
        self.assertEqual(added, 0)


if __name__ == "__main__":
    unittest.main()
