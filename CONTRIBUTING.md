# Contributing

Thank you for improving this Ansible role.

## Pull requests

1. Open a focused PR against `main` with a clear description and test plan.
2. Ensure CI passes (unit tests, integration tests, and security scans as applicable).
3. Use a **Conventional Commit** PR title (`fix:`, `feat:`, `docs:`, etc.). Release Please reads merged commits to build version bumps and `CHANGELOG.md`.

## Release notes and merge strategy

This repository uses [Release Please](https://github.com/googleapis/release-please) to open release PRs and maintain `CHANGELOG.md`.

To keep release notes readable and avoid duplicate entries:

- **Prefer squash merges** when merging PRs into `main`.
- Write the **squash commit message** (or PR title, when GitHub uses it) as a single Conventional Commit that summarizes the whole change.
- Avoid merge commits whose message repeats work already captured on the feature branch; Release Please may list both the squash commit and intermediate branch commits, which duplicates changelog lines (see `CHANGELOG.md` v3.5.1 for an example).

Examples of good squash titles:

- `fix: reject mismatched repository architecture overrides`
- `feat: add repository suite transition integration test`

Breaking changes must include `BREAKING CHANGE:` in the commit body or use the `!` suffix in the type (for example `feat!:`) so Release Please can bump the major version.

## Local setup

Create and activate **`.venv/`** at the repo root (see [README.md](README.md#local-python-environment-venv)):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyyaml
```

Optional: `cp .env.example .env` for direnv/autoenv to activate `.venv` when you `cd` into the repo.

## Local validation

```bash
pre-commit run --all-files
bash tests/validate-release-workflows.sh
python -m unittest discover -s tests/unit -p 'test_*.py'
python scripts/validate-role-defaults.py
ansible-playbook molecule/unit/converge.yml
```

See [README.md](README.md) for Galaxy publication, integration test matrices, and role variable documentation.

## Local knowledge vault (graphify)

Architecture maps and agent context live under `graphify-out/` on your machine only (gitignored).

```bash
./scripts/setup-knowledge-vault.sh          # fast code graph + HTML/Obsidian export
./scripts/setup-knowledge-vault.sh --full   # how to run full /graphify . build
./scripts/install-graphify-hook.sh          # post-commit code graph refresh
```

See [docs/knowledge-vault.md](docs/knowledge-vault.md).
