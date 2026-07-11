#!/usr/bin/env python3
"""Add canonical Ansible role bridge edges missing from AST-only graphify extraction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LINK_KEYS = ("links", "edges")

# (source_id, target_id, relation, confidence, confidence_score, source_file)
BRIDGES: list[tuple[str, str, str, str, float, str]] = [
    (
        "molecule_default_converge",
        "tasks_main",
        "conceptually_related_to",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "molecule_default_verify",
        "tasks_main",
        "conceptually_related_to",
        "INFERRED",
        0.85,
        "docs/knowledge-vault.md",
    ),
    (
        "molecule_default_verify",
        "molecule_default_converge",
        "conceptually_related_to",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "molecule_default_verify",
        "defaults_main_regolith_packages",
        "references",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "defaults_main_regolith_packages",
        "defaults_main",
        "references",
        "EXTRACTED",
        1.0,
        "defaults/main.yml",
    ),
    (
        "docs_knowledge_vault_test_chain",
        "molecule_default_converge",
        "references",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "docs_knowledge_vault_test_chain",
        "molecule_default_verify",
        "references",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "docs_knowledge_vault_role_deployment_chain",
        "tasks_main",
        "references",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "docs_knowledge_vault_role_deployment_chain",
        "molecule_default_verify",
        "references",
        "EXTRACTED",
        1.0,
        "docs/knowledge-vault.md",
    ),
    (
        "molecule_common_converge",
        "molecule_default_converge",
        "conceptually_related_to",
        "INFERRED",
        0.85,
        "docs/knowledge-vault.md",
    ),
]


def link_list(graph: dict[str, Any]) -> list[dict[str, Any]]:
    for key in LINK_KEYS:
        links = graph.get(key)
        if isinstance(links, list):
            return links
    return []


def set_link_list(graph: dict[str, Any], links: list[dict[str, Any]]) -> None:
    primary = "links" if "links" in graph else "edges" if "edges" in graph else "links"
    graph[primary] = links
    for key in LINK_KEYS:
        if key != primary and key in graph:
            graph[key] = []


def bridge_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], int]:
    node_ids = {str(node["id"]) for node in graph.get("nodes", [])}
    links = link_list(graph)
    seen = {
        (str(link["source"]), str(link["target"]), str(link.get("relation", "")))
        for link in links
    }
    added = 0

    for source, target, relation, confidence, score, source_file in BRIDGES:
        if source not in node_ids or target not in node_ids:
            continue
        key = (source, target, relation)
        if key in seen:
            continue
        links.append(
            {
                "source": source,
                "target": target,
                "relation": relation,
                "confidence": confidence,
                "confidence_score": score,
                "source_file": source_file,
                "source_location": None,
                "weight": 1.0,
            }
        )
        seen.add(key)
        added += 1

    result = dict(graph)
    set_link_list(result, links)
    return result, added


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add canonical role→molecule bridge edges to graphify-out/graph.json."
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path("graphify-out/graph.json"),
        help="Path to graph.json (default: graphify-out/graph.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print how many edges would be added without writing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.graph.is_file():
        print(f"Graph not found: {args.graph}", file=sys.stderr)
        return 1

    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    result, added = bridge_graph(graph)
    print(f"bridge edges added: {added}")

    if args.dry_run:
        return 0

    args.graph.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
