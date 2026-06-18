# Remote functional tests

This harness applies the Regolith Ansible role and reusable verification playbooks
against externally provisioned AWS instances or lab VMs.

Optional lifecycle hooks:

```bash
export REMOTE_CREATE_COMMAND='tests/remote/aws/create-ephemeral-env.sh'
export REMOTE_RESET_COMMAND='tests/remote/aws/destroy-ephemeral-env.sh'
```

Run a scenario from the repository root:

```bash
tests/remote/run.sh \
  --inventory tests/remote/inventories/example-ubuntu-noble.yml \
  --scenario regolith-stable
```

| Scenario | Role variables |
|----------|----------------|
| `regolith-stable` | defaults (`v3.4`, `stable`) |
| `regolith-main` | `regolith_repository_component: main` |
| `regolith-preview` | `regolith_repository_suite: preview` |

Copy an example inventory outside the repository and replace placeholder addresses
and credentials. Never commit production credentials.

## GitHub Actions AWS workflows

- `.github/workflows/rc-aws-remote-tests.yml` — **CI — Regolith: AWS EC2 (PR gate)** (`workflow_call` / manual recovery)
- `.github/workflows/aws-remote-tests.yml` — **CI — Regolith: AWS EC2 (manual)** (`workflow_dispatch` for any supported platform)

See [docs/aws-remote-tests-workflow.md](../docs/aws-remote-tests-workflow.md) for
required repository variables, OIDC setup, and teardown guarantees.

Ephemeral EC2 resources must be tagged `Project=ansible-role-regolith`.
