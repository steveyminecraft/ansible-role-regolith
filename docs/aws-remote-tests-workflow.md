# AWS remote tests — workflow guide

Regolith AWS remote tests follow the same pattern as [ansible-pihole](https://github.com/steveyminecraft/ansible-pihole):
assume AWS role → launch ephemeral EC2 → apply role → verify → destroy.

## Workflows

| Workflow | Trigger | Default target |
|----------|---------|----------------|
| `rc-aws-remote-tests.yml` | `v*-rc*` tags (auto from Release Please) | Ubuntu 24.04 amd64, `regolith-stable` |
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
- `RELEASE_PLEASE_TOKEN` (for auto RC tags in Release Please)
- `GALAXY_API_KEY` (for Galaxy publish on release)

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
