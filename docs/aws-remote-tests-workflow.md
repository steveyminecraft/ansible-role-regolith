# AWS remote tests workflow

Ephemeral EC2 tests validate the role on real cloud instances. They run on **feature PRs**
after integration passes, not on the Release Please PR or at Galaxy publish time.

## Pipeline

```text
Feature PR
  → CI — Regolith: lint & unit tests + CI — Regolith: security (Trivy)
  → CI — Regolith: container integration
  → CI — Regolith: AWS EC2 (PR gate) (workflow_call from integration-tests.yml)
```

Release Please PRs skip AWS — the code was already tested before merge to `main`.

When a release PR merges, [release-please.yml](../.github/workflows/release-please.yml) imports
to Galaxy from the release tag with no AWS gate.

## Workflow

[rc-aws-remote-tests.yml](../.github/workflows/rc-aws-remote-tests.yml) (**CI — Regolith: AWS EC2 (PR gate)**):

- **Trigger:** `workflow_call` from integration tests, or `workflow_dispatch` for manual runs
- **Matrix:** built by [`scripts/prepare-aws-matrix-from-integration.py`](../scripts/prepare-aws-matrix-from-integration.py) from successful integration job names

Manual recovery:

```bash
gh workflow run "CI — Regolith: AWS EC2 (PR gate)" --ref main \
  -f git_ref=<sha> \
  -f integration_workflow_run_id=<integration-run-id>
```

On-demand platform testing: [aws-remote-tests.yml](../.github/workflows/aws-remote-tests.yml)
(**CI — Regolith: AWS EC2 (manual)**; `workflow_dispatch`, all supported integration platforms).

## Prerequisites

Repository variables and secrets (`AWS_TEST_*`) must be configured. The build-ci IAM role
needs `ssm:GetParameter` for AWS-managed AMI paths used by `tests/remote/aws/create-ephemeral-env.sh`.
