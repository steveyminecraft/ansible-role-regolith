"""Canonical GitHub Actions workflow display names for CI gating scripts."""

from __future__ import annotations

WORKFLOW_UNIT_TESTS = "CI — Regolith: lint & unit tests"
WORKFLOW_SECURITY_SCAN = "CI — Regolith: security (Trivy)"
WORKFLOW_INTEGRATION_TESTS = "CI — Regolith: container integration"
WORKFLOW_AWS_PR_REMOTE_TESTS = "CI — Regolith: AWS EC2 (PR gate)"
WORKFLOW_AWS_MANUAL_REMOTE_TESTS = "CI — Regolith: AWS EC2 (manual)"

PREREQUISITE_WORKFLOWS: tuple[tuple[str, str], ...] = (
    (WORKFLOW_UNIT_TESTS, "unit-tests.yml"),
    (WORKFLOW_SECURITY_SCAN, "trivy.yml"),
)
