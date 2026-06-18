#!/usr/bin/env python3
"""Fail when documented and tested ansible-core support policy drifts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = "ansible-core>=2.20,<2.21"


def require(path: str, text: str) -> None:
    content = (ROOT / path).read_text(encoding="utf-8")
    if text not in content:
        raise SystemExit(f"{path} must contain {text!r}")


def main() -> None:
    require("requirements.txt", POLICY)
    require("requirements-ci.txt", POLICY)
    require("README.md", "ansible-core 2.20")
    require(".github/actions/setup-ansible-test/action.yml", "ansible-core 2.20")
    require(".github/actions/import-galaxy-role/action.yml", POLICY)
    require(".github/workflows/unit-tests.yml", "setup-ansible-test")
    require("meta/main.yml", 'min_ansible_version: "2.20"')
    print("Ansible Core support policy is aligned.")


if __name__ == "__main__":
    main()
