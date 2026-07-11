---
name: readme-maintenance
description: >-
  Requires keeping README.md and docs accurate in steveyminecraft/ansible-role-regolith
  whenever code, config, CI, Molecule, setup, or behavior changes. Use on every
  implementation task in this repository, before finishing work or opening a PR.
---

# README maintenance (ansible-role-regolith)

**READMEs must stay up to date at all times.** Treat README updates as part of the same change—not a follow-up.

Also apply the **readme-change-log** user skill when editing this repo. This file adds repo-specific scope.

This is a **single-role** repository: role variables, tasks, and usage live in the root `README.md` (there is no `roles/regolith/README.md`).

## Files to maintain

| File | Update when |
|------|-------------|
| `README.md` (repo root) | Role variables (`defaults/main.yml`), tasks, Molecule scenarios, CI workflows, scripts, Galaxy/meta, supported OS releases, branch/workflow notes, local dev commands |
| `docs/aws-remote-tests-workflow.md` | AWS OIDC, EC2 test harness, repository variables/secrets, teardown behavior |
| `docs/knowledge-vault.md` | graphify setup, hooks, or agent workflow for the knowledge vault |
| `CONTRIBUTING.md` | PR conventions, Release Please / squash-merge guidance, local validation commands |

## When to edit (non-exhaustive)

Update README and/or docs in the **same commit/PR** as the functional change when you touch:

- `.github/workflows/` or Actions under `.github/actions/`
- `molecule/` (scenarios, boxes, providers, test sequence)
- `playbooks/`, `inventory/`, `tasks/`, `defaults/`, `handlers/`, `meta/`
- `scripts/` users or CI run (`validate-role-defaults.py`, `molecule-test-all`, `molecule-vagrant`, AWS matrix helpers, etc.)
- `meta/main.yml` or `meta/argument_specs.yml` (Galaxy platforms, versions)
- `requirements.txt`, `requirements-ci.txt`, or `.pre-commit-config.yaml`
- `tests/` (Python unit tests, workflow validation scripts)

Skip README edits only if the user explicitly says not to, or the change is purely internal with zero user-visible effect (rare—when in doubt, update).

## Where to put updates

Match existing root `README.md` sections:

- **Role Variables** — defaults in `defaults/main.yml`, supported platforms table
- **Development / Testing** — unit, integration, Vagrant, lint commands
- **Test pyramid** and **Unit tests workflow** — CI job names and ordering
- **Continuous integration (workflow reference)** — workflow table, triggers, AWS vs release path
- **Ansible Galaxy** — Release Please, tag-based import, `GALAXY_API_KEY`

Prefer **editing stale text in place** over duplicating. Remove wrong platform versions, workflow names, or branch names when replacing with new ones.

## Completion check (every task)

Before marking work done or suggesting a PR:

```
- [ ] Root README.md reflects the change (or consciously N/A)
- [ ] Relevant docs/*.md updated if specialized docs changed
- [ ] CONTRIBUTING.md updated if contributor workflow changed
- [ ] No contradictions (old platform versions, wrong branch names, removed scripts)
```

Include README changes in the topic-branch PR to `main`, not a separate doc-only PR unless the user requests that.
