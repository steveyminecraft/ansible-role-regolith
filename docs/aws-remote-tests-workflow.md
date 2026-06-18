# AWS remote tests — workflow guide

Regolith AWS remote tests follow the same pattern as [ansible-pihole](https://github.com/steveyminecraft/ansible-pihole):
assume AWS role → launch ephemeral EC2 → apply role → verify → destroy.

## Workflows

| Workflow | Trigger | Default target |
|----------|---------|----------------|
| `rc-aws-remote-tests.yml` | `v*-rc*` tags, **after integration passes (per platform)**, manual | One AWS job per successful integration platform |
| `aws-remote-tests.yml` | Manual dispatch | Configurable OS/arch/scenario |

## Required GitHub configuration

Repository variables (from `terraform output -json ansible_regolith_remote_test_configuration`
in AWS-Cloud `build-account-isolation/build`):

- `AWS_TEST_ROLE_ARN`
- `AWS_TEST_REGION`
- `AWS_TEST_SUBNET_ID`
- `AWS_TEST_KEY_NAME`
- `AWS_TEST_INSTANCE_TYPE_AMD64` (`t3.medium` recommended)
- optional `AWS_TEST_INSTANCE_TYPE_ARM64`
- optional `AWS_TEST_SSH_CIDR`

Repository secrets:

- `AWS_TEST_SSH_PRIVATE_KEY` (shared with ansible-pihole remote tests)
- `RELEASE_PLEASE_TOKEN` (optional; unblocks release-PR CI approval and PAT-pushed RC tags)
- `GALAXY_API_KEY` (for Galaxy publish on release)

## Automatic RC test flow

On every PR and `main` push:

1. **Unit tests** (`lint` → `policy` → `unit` → `validate`) and **Trivy** run in parallel.
2. When Unit tests complete, **Integration tests** start and wait until Trivy has also passed.
3. On the Release Please PR only: when integration completes, `rc-aws-remote-tests.yml` starts
   via a `workflow_call` from the integration workflow (`workflow_run` alone is unreliable for
   `pull_request` triggers).

When Release Please opens or updates a release PR on `main`:

1. `tag-release-candidate` pushes `vX.Y.Z-rc.N` on the release PR branch.
2. Integration tests run on the release PR (six container platforms).
3. When integration completes on the release PR branch, `rc-aws-remote-tests.yml` starts via `workflow_run`.
4. Only platforms whose integration job **passed** receive a matching AWS ephemeral EC2 test.
   Failed integration platforms are skipped automatically.

`v*-rc*` tag pushes still trigger the same workflow (with RC-tag gating) when using a PAT.

**Note:** `workflow_run` payloads often report `head_branch: main` even when integration
ran on `release-please--branches--main`. The AWS workflow resolves the real branch via
[`scripts/detect_release_pr_integration.py`](../scripts/detect_release_pr_integration.py)
before starting EC2 jobs.

## Galaxy publish gate

When Release Please creates stable tag `vX.Y.Z`, [release-please.yml](../.github/workflows/release-please.yml)
runs [`scripts/verify_aws_rc_gate.py`](../scripts/verify_aws_rc_gate.py) before importing to Galaxy. Publication
is blocked unless:

1. An RC tag exists for that version (`vX.Y.Z-rc.N`).
2. The latest completed **AWS RC remote tests** workflow run for that RC commit succeeded.
3. At least one AWS platform job ran and every AWS platform job succeeded.

If AWS tests fail on the release PR, merge still creates the GitHub release and tag, but Galaxy import
is skipped until AWS passes and you re-run the manual [release.yml](../.github/workflows/release.yml)
recovery workflow (or fix and cut a new release).

## OIDC trust

Terraform must include:

```hcl
"github_subject_claims = [
  \"repo:steveyminecraft/ansible-role-regolith:ref:refs/tags/v*-rc*\",
]"
```

Manual `workflow_dispatch` runs additionally require a `refs/heads/main` claim unless
you only use RC tag triggers.

## Local dry run

Without AWS, run the Ansible unit and integration layers:

```bash
ansible-playbook molecule/unit/converge.yml
python -m unittest discover -s tests/unit -p 'test_*.py'
```

## Teardown

Both workflows always run `destroy-ephemeral-env.sh` and `verify-cleanup.sh` in
`if: always()` steps so failed tests do not leave hosts running.
