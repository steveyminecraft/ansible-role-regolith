#!/usr/bin/env python3
"""Verify lint/unit and Trivy workflows passed before integration tests run."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

PREREQUISITE_WORKFLOWS: tuple[tuple[str, str], ...] = (
    ("Unit tests", "unit-tests.yml"),
    ("Security scan", "trivy.yml"),
)


@dataclass(frozen=True)
class WorkflowRunStatus:
    workflow_name: str
    run_id: int | None
    status: str
    conclusion: str | None

    @property
    def succeeded(self) -> bool:
        return self.status == "completed" and self.conclusion == "success"


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


def latest_run_for_sha(
    repo: str,
    workflow_file: str,
    head_sha: str,
    token: str,
) -> WorkflowRunStatus:
    payload = github_request(
        "https://api.github.com/repos/"
        f"{repo}/actions/workflows/{workflow_file}/runs"
        f"?head_sha={head_sha}&per_page=10",
        token,
    )
    assert isinstance(payload, dict)
    runs = payload.get("workflow_runs", [])
    if not runs:
        return WorkflowRunStatus("", None, "missing", None)
    latest = runs[0]
    return WorkflowRunStatus(
        workflow_name=str(latest.get("name", "")),
        run_id=int(latest["id"]) if latest.get("id") else None,
        status=str(latest.get("status", "")),
        conclusion=latest.get("conclusion"),
    )


def evaluate_prerequisites(
    statuses: list[WorkflowRunStatus],
) -> tuple[bool, str]:
    pending: list[str] = []
    failed: list[str] = []
    for status in statuses:
        if status.succeeded:
            continue
        if status.status in {"queued", "in_progress", "waiting", "requested", "pending"}:
            pending.append(status.workflow_name)
            continue
        if status.status == "missing":
            pending.append(f"{status.workflow_name} (no run yet)")
            continue
        failed.append(
            f"{status.workflow_name} ({status.status}/{status.conclusion or 'unknown'})"
        )
    if failed:
        return False, f"prerequisite workflows failed: {', '.join(failed)}"
    if pending:
        return False, f"prerequisite workflows not finished: {', '.join(pending)}"
    return True, "all prerequisite workflows passed"


def verify_prerequisites(
    repo: str,
    head_sha: str,
    token: str,
    *,
    wait: bool = False,
    timeout_seconds: int = 5400,
    poll_seconds: int = 30,
) -> tuple[bool, str]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        statuses: list[WorkflowRunStatus] = []
        for workflow_name, workflow_file in PREREQUISITE_WORKFLOWS:
            latest = latest_run_for_sha(repo, workflow_file, head_sha, token)
            statuses.append(
                WorkflowRunStatus(
                    workflow_name=workflow_name,
                    run_id=latest.run_id,
                    status=latest.status,
                    conclusion=latest.conclusion,
                )
            )

        ok, message = evaluate_prerequisites(statuses)
        if ok:
            details = ", ".join(
                f"{status.workflow_name} run {status.run_id}"
                for status in statuses
                if status.run_id is not None
            )
            return True, details
        if not wait or "failed" in message:
            return False, message
        if time.monotonic() >= deadline:
            return False, f"timed out waiting for prerequisites: {message}"
        time.sleep(poll_seconds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--head-sha", default=os.environ.get("HEAD_SHA", ""))
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--timeout-minutes", type=int, default=90)
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    if not args.repo:
        print("--repo or GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2
    if not args.head_sha:
        print("--head-sha or HEAD_SHA is required", file=sys.stderr)
        return 2

    ok, message = verify_prerequisites(
        args.repo,
        args.head_sha,
        token,
        wait=args.wait,
        timeout_seconds=max(args.timeout_minutes, 1) * 60,
        poll_seconds=max(args.poll_seconds, 5),
    )
    if ok:
        print(f"CI prerequisites passed: {message}")
        return 0
    print(f"CI prerequisites blocked integration tests: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise SystemExit(1) from exc
