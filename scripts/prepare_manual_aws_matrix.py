#!/usr/bin/env python3
"""Build a workflow_dispatch matrix for manual AWS remote functional tests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.aws_integration_platforms import PLATFORMS, platform_to_matrix_entry

PLATFORMS_BY_ID = {platform.platform_id: platform for platform in PLATFORMS}


def resolve_platforms(platform_id: str) -> list:
    if platform_id == "all-platforms":
        return list(PLATFORMS)
    platform = PLATFORMS_BY_ID.get(platform_id)
    if platform is None:
        known = ", ".join(sorted(PLATFORMS_BY_ID))
        raise SystemExit(f"Unknown platform id '{platform_id}'. Expected one of: {known}, all-platforms")
    return [platform]


def build_matrix(platform_id: str, coverage: str, arch: str) -> list[dict[str, str]]:
    matrix: list[dict[str, str]] = []
    archs = ("amd64", "arm64") if coverage in {"all-archs", "full"} else (arch or "amd64",)

    for platform in resolve_platforms(platform_id):
        for selected_arch in archs:
            entry = platform_to_matrix_entry(platform)
            entry["arch"] = selected_arch
            matrix.append(entry)
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", default=os.environ.get("INPUT_PLATFORM", "ubuntu-noble"))
    parser.add_argument(
        "--platform-coverage",
        default=os.environ.get("INPUT_PLATFORM_COVERAGE", "one-arch"),
    )
    parser.add_argument("--arch", default=os.environ.get("INPUT_ARCH", "amd64"))
    parser.add_argument("--scenario", default=os.environ.get("INPUT_SCENARIO", "regolith-stable"))
    parser.add_argument(
        "--skip-transitions",
        default=os.environ.get("INPUT_SKIP_TRANSITIONS", "false"),
    )
    parser.add_argument("--aws-region", default=os.environ.get("INPUT_AWS_REGION", ""))
    parser.add_argument(
        "--default-aws-region",
        default=os.environ.get("DEFAULT_AWS_REGION", ""),
    )
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    matrix = build_matrix(args.platform.strip(), args.platform_coverage.strip(), args.arch.strip())
    region = args.aws_region.strip() or args.default_aws_region.strip()
    skip_transitions = args.skip_transitions.strip().lower()

    payload = {"include": matrix}
    if args.github_output:
        output_path = Path(args.github_output)
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(f"matrix={json.dumps(payload)}\n")
            handle.write(f"scenario={args.scenario.strip()}\n")
            handle.write(f"skip_transitions={skip_transitions}\n")
            handle.write(f"aws_region={region}\n")
    else:
        print(json.dumps({"matrix": payload, "scenario": args.scenario, "aws_region": region}, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
