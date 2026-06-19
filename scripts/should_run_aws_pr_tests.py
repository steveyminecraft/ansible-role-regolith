#!/usr/bin/env python3
"""Decide whether ephemeral AWS tests should run for the current CI event."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

RELEASE_PLEASE_BRANCH_PREFIX = "release-please--branches--"
DEFAULT_BASE_BRANCHES = ("main", "master")


def should_run_aws_pr_tests(
    *,
    event_name: str,
    head_ref: str,
    commit_on_main: bool,
) -> tuple[bool, str]:
    if event_name != "pull_request":
        return False, "AWS remote tests run only on pull_request events (pre-merge)."
    if head_ref.startswith(RELEASE_PLEASE_BRANCH_PREFIX):
        return (
            False,
            "Release Please PRs skip AWS; feature commits were already tested before merge.",
        )
    if head_ref in DEFAULT_BASE_BRANCHES:
        return False, f"Head branch {head_ref} is the default branch."
    if commit_on_main:
        return False, "Commit is already on main (post-merge); skipping duplicate AWS run."
    return True, "Feature PR pre-merge gate passed."


def commit_is_on_branch(head_sha: str, base_ref: str, repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", head_sha, base_ref],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def resolve_remote_base(base_branch: str, repo_root: Path) -> str:
    for candidate in (f"origin/{base_branch}", base_branch):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", candidate],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return candidate.strip()
    raise RuntimeError(f"Could not resolve base branch ref for {base_branch}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", default="")
    parser.add_argument("--head-ref", default="")
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--commit-on-main",
        choices=("true", "false", "auto"),
        default="auto",
        help="Override ancestor check (for tests) or auto-detect via git",
    )
    args = parser.parse_args()

    if not args.event_name:
        print("--event-name is required", file=sys.stderr)
        return 2
    if not args.head_ref:
        print("--head-ref is required", file=sys.stderr)
        return 2

    if args.commit_on_main == "auto":
        if not args.head_sha:
            print("--head-sha is required when --commit-on-main=auto", file=sys.stderr)
            return 2
        base_ref = resolve_remote_base(args.base_branch, args.repo_root)
        on_main = commit_is_on_branch(args.head_sha, base_ref, args.repo_root)
    else:
        on_main = args.commit_on_main == "true"

    run_aws, message = should_run_aws_pr_tests(
        event_name=args.event_name,
        head_ref=args.head_ref,
        commit_on_main=on_main,
    )
    print(message)
    return 0 if run_aws else 3


if __name__ == "__main__":
    raise SystemExit(main())
