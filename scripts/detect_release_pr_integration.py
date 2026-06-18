#!/usr/bin/env python3
"""Detect whether an Integration tests workflow run is for a Release Please PR."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

RELEASE_PLEASE_BRANCH_PREFIX = "release-please--branches--"


def github_request(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    assert isinstance(payload, dict)
    return payload


def is_release_please_integration_run(run: dict) -> bool:
    if run.get("name") != "Integration tests":
        return False
    if run.get("conclusion") != "success":
        return False

    head_branch = str(run.get("head_branch", ""))
    if head_branch.startswith(RELEASE_PLEASE_BRANCH_PREFIX):
        return True

    pull_requests = run.get("pull_requests") or []
    for pull_request in pull_requests:
        head = pull_request.get("head", {})
        if str(head.get("ref", "")).startswith(RELEASE_PLEASE_BRANCH_PREFIX):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--workflow-run-id", type=int, required=True)
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    if not args.repo:
        print("--repo or GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    run = github_request(
        f"https://api.github.com/repos/{args.repo}/actions/runs/{args.workflow_run_id}",
        token,
    )
    is_release_pr = is_release_please_integration_run(run)
    value = "true" if is_release_pr else "false"

    print(
        "Integration run "
        f"{args.workflow_run_id}: head_branch={run.get('head_branch')}, "
        f"release_pr={value}"
    )

    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write(f"is_release_pr={value}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise SystemExit(1) from exc
