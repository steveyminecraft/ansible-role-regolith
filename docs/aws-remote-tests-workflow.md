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

When Release Please opens or updates a release PR on `main`:

1. `tag-release-candidate` pushes `vX.Y.Z-rc.N` on the release PR branch.
2. Integration tests run on the release PR (six container platforms).
3. When integration completes on the release PR branch, `rc-aws-remote-tests.yml` starts via `workflow_run`.
4. Only platforms whose integration job **passed** receive a matching AWS ephemeral EC2 test.
   Failed integration platforms are skipped automatically.

`v*-rc*` tag pushes still trigger the same workflow (with RC-tag gating) when using a PAT.

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
