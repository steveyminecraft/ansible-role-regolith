#!/usr/bin/env python3
"""Validate Regolith role defaults and metadata stay aligned."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
UNIT_MATRIX_PATH = ROOT / "molecule/unit/converge.yml"


def load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8")) or {}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def unit_matrix_releases() -> set[str]:
    content = UNIT_MATRIX_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"release:\s+(\w+)", content))


def galaxy_platform_releases() -> set[str]:
    meta = load_yaml("meta/main.yml")
    releases: set[str] = set()
    for platform in meta.get("galaxy_info", {}).get("platforms", []):
        releases.update(platform.get("versions", []))
    return releases


def main() -> None:
    defaults = load_yaml("defaults/main.yml")
    specs = load_yaml("meta/argument_specs.yml")
    component_choices = (
        specs.get("argument_specs", {})
        .get("main", {})
        .get("options", {})
        .get("regolith_repository_component", {})
        .get("choices", [])
    )

    pinned_component = defaults.get("regolith_repository_component")
    require(
        pinned_component in component_choices,
        f"defaults regolith_repository_component {pinned_component!r} must be listed in argument_specs choices",
    )

    matrix_releases = unit_matrix_releases()
    galaxy_releases = galaxy_platform_releases()
    require(
        galaxy_releases <= matrix_releases,
        f"meta/main.yml platform versions {sorted(galaxy_releases)} must be covered by molecule/unit matrix {sorted(matrix_releases)}",
    )

    for key in (
        "regolith_repository_key_url",
        "regolith_repository_base_url",
    ):
        value = defaults.get(key, "")
        require(
            isinstance(value, str) and value.startswith("https://"),
            f"{key} must default to an https:// URL",
        )

    packages_expr = defaults.get("regolith_packages", "")
    require(
        isinstance(packages_expr, str),
        "regolith_packages must be defined as a Jinja expression in defaults/main.yml",
    )
    for var_name in (
        "regolith_base_packages",
        "regolith_session_packages",
        "regolith_look_packages",
        "regolith_extra_packages",
    ):
        require(var_name in packages_expr, f"regolith_packages must reference {var_name}")

    meta = load_yaml("meta/main.yml")
    min_version = str(meta.get("galaxy_info", {}).get("min_ansible_version", ""))
    require(min_version.startswith("2.20"), "meta/main.yml min_ansible_version must be 2.20.x")

    requirements = (ROOT / "requirements-ci.txt").read_text(encoding="utf-8")
    require("ansible-core>=2.20" in requirements, "requirements-ci.txt must pin ansible-core>=2.20")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("ansible-core 2.20" in readme, "README.md must document ansible-core 2.20 support")

    print("Regolith role defaults and metadata are valid.")


if __name__ == "__main__":
    main()
