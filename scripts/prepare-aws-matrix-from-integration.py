#!/usr/bin/env python3
"""Build an AWS remote test matrix from successful Integration tests jobs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.aws_integration_platforms import matrix_from_jobs


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


def list_workflow_jobs(repo: str, run_id: int, token: str) -> list[dict]:
    jobs: list[dict] = []
    page = 1
    while True:
        payload = github_request(
            f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100&page={page}",
            token,
        )
        assert isinstance(payload, dict)
        jobs.extend(payload.get("jobs", []))
        if len(payload.get("jobs", [])) < 100:
            break
        page += 1
    return jobs


def find_integration_run_for_sha(repo: str, head_sha: str, token: str) -> dict | None:
    payload = github_request(
        "https://api.github.com/repos/"
        f"{repo}/actions/workflows/integration-tests.yml/runs"
        f"?head_sha={head_sha}&event=pull_request&status=completed&per_page=20",
        token,
    )
    assert isinstance(payload, dict)
    runs = payload.get("workflow_runs", [])
    if not runs:
        payload = github_request(
            "https://api.github.com/repos/"
            f"{repo}/actions/workflows/integration-tests.yml/runs"
            f"?head_sha={head_sha}&status=completed&per_page=20",
            token,
        )
        assert isinstance(payload, dict)
        runs = payload.get("workflow_runs", [])
    return runs[0] if runs else None


def resolve_git_sha(repo: str, git_ref: str, token: str) -> str:
    ref = git_ref.strip()
    if not ref:
        return ""
    if ref.startswith("refs/"):
        api_ref = ref.removeprefix("refs/")
    elif ref.startswith("v"):
        api_ref = f"tags/{ref}"
    else:
        api_ref = f"heads/{ref}"
    payload = github_request(
        f"https://api.github.com/repos/{repo}/git/ref/{api_ref}",
        token,
    )
    assert isinstance(payload, dict)
    return payload["object"]["sha"]


def commit_has_rc_tag(repo: str, head_sha: str, token: str) -> bool:
    tags = github_request(
        f"https://api.github.com/repos/{repo}/git/matching-refs/tags/v",
        token,
    )
    assert isinstance(tags, list)
    for entry in tags:
        ref_name = entry.get("ref", "").removeprefix("refs/tags/")
        if "-rc." not in ref_name:
            continue
        if entry.get("object", {}).get("sha") == head_sha:
            return True
    return False


def write_github_output(path: Path, key: str, value: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        if "\n" in value or len(value) > 256:
            delimiter = f"{key}_DELIM"
            handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
        else:
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--workflow-run-id", type=int, default=0)
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--git-ref", default="")
    parser.add_argument("--require-rc-tag", action="store_true")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    parser.add_argument(
        "--matrix-file",
        default="",
        help="Write matrix JSON payload to this file for the workflow step to publish",
    )
    parser.add_argument(
        "--meta-file",
        default="",
        help="Write git_ref/head_sha metadata JSON when using --matrix-file",
    )
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    if not args.repo:
        print("--repo or GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    head_sha = args.head_sha.strip()
    workflow_run_id = args.workflow_run_id

    if workflow_run_id:
        run = github_request(
            f"https://api.github.com/repos/{args.repo}/actions/runs/{workflow_run_id}",
            token,
        )
        assert isinstance(run, dict)
        head_sha = run.get("head_sha", head_sha)
        jobs = list_workflow_jobs(args.repo, workflow_run_id, token)
    else:
        if not head_sha and args.git_ref:
            head_sha = resolve_git_sha(args.repo, args.git_ref, token)
        if not head_sha:
            print("workflow run id or head sha is required", file=sys.stderr)
            return 2
        run = find_integration_run_for_sha(args.repo, head_sha, token)
        if run is None:
            print(f"No completed Integration tests run found for {head_sha}", file=sys.stderr)
            return 1
        workflow_run_id = int(run["id"])
        jobs = list_workflow_jobs(args.repo, workflow_run_id, token)

    if args.require_rc_tag and head_sha and not commit_has_rc_tag(args.repo, head_sha, token):
        print(f"No RC tag points at {head_sha}; skipping AWS remote tests.")
        matrix: list[dict[str, str]] = []
    else:
        matrix = matrix_from_jobs(jobs)

    git_ref = args.git_ref.strip() or head_sha
    payload = {"include": matrix}
    has_matrix = "true" if matrix else "false"

    print(f"Integration workflow run: {workflow_run_id}")
    print(f"Head SHA: {head_sha}")
    print(f"AWS matrix entries: {len(matrix)}")
    for entry in matrix:
        print(f"  - {entry['label']}")

    matrix_json = json.dumps(payload)
    if args.matrix_file:
        Path(args.matrix_file).write_text(matrix_json, encoding="utf-8")
        if args.meta_file:
            Path(args.meta_file).write_text(
                json.dumps(
                    {
                        "git_ref": git_ref,
                        "head_sha": head_sha,
                        "has_matrix": has_matrix,
                        "integration_run_id": str(workflow_run_id),
                    }
                ),
                encoding="utf-8",
            )
    elif args.github_output:
        output_path = Path(args.github_output)
        write_github_output(output_path, "has_matrix", has_matrix)
        write_github_output(output_path, "git_ref", git_ref)
        write_github_output(output_path, "head_sha", head_sha)
        write_github_output(output_path, "integration_run_id", str(workflow_run_id))
        write_github_output(output_path, "matrix", matrix_json)
    else:
        print(json.dumps({"matrix": payload, "git_ref": git_ref, "has_matrix": has_matrix}, indent=2))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise SystemExit(1) from exc
