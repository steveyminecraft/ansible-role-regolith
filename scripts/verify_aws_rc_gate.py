#!/usr/bin/env python3
"""Block Galaxy publication unless AWS RC remote tests passed for the release."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.aws_integration_platforms import PLATFORMS_BY_JOB_NAME

AWS_WORKFLOW_FILE = "rc-aws-remote-tests.yml"
PREPARE_MATRIX_JOB = "Prepare AWS matrix from integration results"
STABLE_TAG_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")

def github_request(url: str, token: str) -> dict | list:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def parse_stable_release_tag(tag: str) -> str | None:
    if STABLE_TAG_RE.fullmatch(tag):
        return tag
    return None


def rc_tag_sort_key(tag_name: str) -> tuple[int, int, int, int]:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)-rc\.(\d+)", tag_name)
    if not match:
        return (0, 0, 0, 0)
    return tuple(int(group) for group in match.groups())


def latest_rc_tag_for_release(repo: str, stable_tag: str, token: str) -> tuple[str, str] | None:
    prefix = f"{stable_tag}-rc."
    tags = github_request(
        f"https://api.github.com/repos/{repo}/git/matching-refs/tags/{prefix}",
        token,
    )
    assert isinstance(tags, list)
    candidates: list[tuple[str, str]] = []
    for entry in tags:
        ref_name = entry.get("ref", "").removeprefix("refs/tags/")
        if not ref_name.startswith(prefix):
            continue
        sha = entry.get("object", {}).get("sha", "")
        if sha:
            candidates.append((ref_name, sha))
    if not candidates:
        return None
    candidates.sort(key=lambda item: rc_tag_sort_key(item[0]))
    return candidates[-1]


def list_workflow_jobs(repo: str, run_id: int, token: str) -> list[dict]:
    jobs: list[dict] = []
    page = 1
    while True:
        payload = github_request(
            f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100&page={page}",
            token,
        )
        assert isinstance(payload, dict)
        batch = payload.get("jobs", [])
        jobs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return jobs


def list_completed_aws_runs(repo: str, head_sha: str, token: str) -> list[dict]:
    payload = github_request(
        "https://api.github.com/repos/"
        f"{repo}/actions/workflows/{AWS_WORKFLOW_FILE}/runs"
        f"?head_sha={head_sha}&status=completed&per_page=20",
        token,
    )
    assert isinstance(payload, dict)
    return list(payload.get("workflow_runs", []))


def verify_aws_jobs(jobs: list[dict]) -> tuple[bool, str]:
    prepare_jobs = [job for job in jobs if job.get("name") == PREPARE_MATRIX_JOB]
    if not prepare_jobs:
        return False, f"missing {PREPARE_MATRIX_JOB} job"
    if prepare_jobs[0].get("conclusion") != "success":
        return False, f"{PREPARE_MATRIX_JOB} did not succeed"

    aws_jobs = [job for job in jobs if job.get("name") in PLATFORMS_BY_JOB_NAME]
    if not aws_jobs:
        return False, "no AWS remote test platform jobs ran"
    failed = [job["name"] for job in aws_jobs if job.get("conclusion") != "success"]
    if failed:
        return False, f"AWS remote test jobs failed: {', '.join(failed)}"
    return True, f"passed ({len(aws_jobs)} platform job(s))"


def verify_release_ready(
    repo: str,
    stable_tag: str,
    token: str,
) -> tuple[bool, str]:
    if parse_stable_release_tag(stable_tag) is None:
        return False, f"invalid stable release tag: {stable_tag}"

    rc = latest_rc_tag_for_release(repo, stable_tag, token)
    if rc is None:
        return False, f"no RC tag found for {stable_tag}; AWS RC tests are required before Galaxy publish"

    rc_tag, head_sha = rc
    runs = list_completed_aws_runs(repo, head_sha, token)
    if not runs:
        return False, f"no completed AWS RC workflow runs for {rc_tag} ({head_sha[:7]})"

    latest_run = runs[0]
    run_id = int(latest_run["id"])
    conclusion = latest_run.get("conclusion", "")
    jobs = list_workflow_jobs(repo, run_id, token)
    ok, detail = verify_aws_jobs(jobs)
    if not ok:
        return False, f"{rc_tag} AWS RC run {run_id} ({conclusion}): {detail}"
    if conclusion != "success":
        return False, f"{rc_tag} AWS RC workflow run {run_id} concluded {conclusion}"
    return True, f"{rc_tag} AWS RC run {run_id} {detail}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--skip", action="store_true", help="Skip gate (manual recovery only)")
    args = parser.parse_args()

    if args.skip:
        print("AWS RC gate skipped.")
        return 0

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    if not args.repo:
        print("--repo or GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    ok, message = verify_release_ready(args.repo, args.release_tag, token)
    if ok:
        print(f"AWS RC gate passed: {message}")
        return 0
    print(f"AWS RC gate blocked Galaxy publish: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise SystemExit(1) from exc
