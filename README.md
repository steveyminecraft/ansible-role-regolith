Ansible Role: regolith
=========

Requirements
------------

- **ansible-core 2.20.x** (CI validates `ansible-core>=2.20,<2.21`; newer versions are not yet in the tested matrix; avoid EOL 2.15–2.19).
- Target host must be a [supported platform](#supported-platforms) (Ubuntu or Debian).
- Root privileges (`become: true`) for APT repository and package changes.

Supported platforms
-------------------

This role follows the [Regolith install documentation](https://regolith-desktop.com/docs/using-regolith/install/).
Only the Ubuntu and Debian distributions listed below are supported; Debian-family derivatives are rejected during validation.

| Distribution | Release (codename) | Version |
|--------------|-------------------|---------|
| Ubuntu | noble | 24.04 |
| Ubuntu | plucky | 25.04 |
| Ubuntu | questing | 25.10 |
| Debian | bookworm | 12 |
| Debian | trixie | 13 |

Unsupported operating systems, Debian-family derivatives, distributions, releases, or architectures fail during role validation with a clear error message.

Role Variables
--------------

Available variables and their defaults:

```yaml
regolith_repository_key_url: https://archive.regolith-desktop.com/regolith.key
regolith_repository_keyring: /usr/share/keyrings/regolith-archive-keyring.gpg
regolith_repository_base_url: https://archive.regolith-desktop.com
regolith_repository_suite: stable
regolith_repository_component: v3.4
# regolith_repository_architecture is auto-detected from host facts when omitted.
# Set it only when it matches the host (amd64 or arm64); cross-arch/multiarch is not supported.

regolith_repository_prerequisite_packages:
  - ca-certificates
  - gnupg

regolith_base_packages:
  - regolith-desktop
  - xdg-desktop-portal-regolith

regolith_session_packages:
  - regolith-session-flashback

regolith_look_packages:
  - regolith-look-lascaille

regolith_extra_packages: []

regolith_packages: >-
  {{
    regolith_base_packages
    + regolith_session_packages
    + regolith_look_packages
    + regolith_extra_packages
  }}

regolith_ubuntu_packages: "{{ regolith_packages }}"
regolith_debian_packages: "{{ regolith_packages }}"
```

The default `regolith_repository_component` value of `v3.4` matches the official install examples for a pinned Regolith release. Set it to `main` to follow the latest stable release in the archive.
Flashback is the default Regolith session. To choose a different session or look, override the package group you want to change:

```yaml
regolith_session_packages:
  - regolith-session-sway
regolith_look_packages:
  - regolith-look-nord
regolith_extra_packages:
  - regolith-compositor-picom-glx
```

You can still override `regolith_packages` directly to replace the complete install list.

Dependencies
------------

None.

Example Playbook
----------------

Install regolith:
```yaml
    - hosts: servers
      roles:
         - { role: regolith }
```

Development / Testing
---------------------

CI uses native GitHub Actions (`ansible-playbook` and container jobs). Locally you can run the same playbooks or use Molecule.

### Local Python environment (`.venv`)

Use a virtual environment at **`.venv/`** in the repo root (gitignored). Do not use `env/` or other ad-hoc venv paths.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyyaml   # script unit tests and policy checks
```

CI Actions use a separate `.ci-venv/` under the workspace; locally, stick to `.venv`.

For autoenv/direnv-style activation, copy the tracked example to a private local `.env` file (it sources `.venv/bin/activate`). The `.env` path is listed in `.gitignore` and must not be committed; only [`.env.example`](.env.example) belongs in git.

```bash
cp .env.example .env
```

With [direnv](https://direnv.net/), `.envrc` loads `.env` when present.

Unit tests (repository line generation, no VM; activate `.venv` first):

```bash
ansible-playbook molecule/unit/converge.yml
ansible-playbook molecule/unit-ubuntu-plucky/converge.yml
ansible-playbook molecule/unit-ubuntu-questing/converge.yml
```

Python policy and script unit tests (with `.venv` activated; see [Unit tests workflow](#unit-tests-workflow) for CI job detail):

```bash
python -m pip install pyyaml
python -m unittest discover -s tests/unit -p 'test_*.py'
python scripts/validate-role-defaults.py
python scripts/check-ansible-version-policy.py
ansible-playbook -i inventory/ci/ci.yml playbooks/ci-check-mode.yml --check
```

Integration tests (Docker container, same steps as CI):

```bash
docker run --rm -it -v "$PWD:/work" -w /work python:3.13-bookworm bash -lc '
  apt-get update && apt-get install -y python3-pip python3-apt gnupg ca-certificates
  python3.13 -m pip install --break-system-packages -r requirements-ci.txt
  export PATH="$HOME/.local/bin:$PATH"
  ansible-playbook -i localhost, -c local molecule/common/docker_prepare.yml
  ansible-playbook -i localhost, -c local molecule/common/converge.yml
  ansible-playbook -i localhost, -c local molecule/default/verify.yml
'
```

Optional Molecule wrappers (with `.venv` activated):

```bash
pip install -r requirements.txt
./scripts/molecule-test-all --list
./scripts/molecule-test-all debian-bookworm ubuntu-noble
molecule test -s unit
```

Optional Vagrant integration (Ubuntu 24.04 noble):

```bash
molecule test
```

VirtualBox is used by default. You can also use the helper script:

```bash
./scripts/molecule-vagrant test
```

Run the Vagrant scenario with libvirt/KVM:

```bash
VAGRANT_DEFAULT_PROVIDER=libvirt ./scripts/molecule-vagrant test
```

Linting and validation (with `.venv` activated):

```bash
pre-commit run --all-files
ansible-lint
yamllint .
```

Ansible-lint uses the production profile in offline mode, excluding local caches, virtual environments, GitHub workflow files, and Molecule-generated state so local and CI runs stay deterministic.
Yamllint follows `.yamllint`, warning on lines longer than 150 characters while ignoring local caches, virtual environments, collections, and generated Molecule Vagrant state.

### Test pyramid

Tests run in layers from fast/cheap to slow/realistic. Feature-branch PRs exercise every layer including AWS after integration passes. Release Please PRs skip AWS; Galaxy publish has no AWS gate.

| Layer | What it validates | CI workflow |
|-------|-------------------|-------------|
| Lint & static | Style, syntax, check-mode, workflow contracts | [Unit tests](.github/workflows/unit-tests.yml) → `lint` |
| Python policy | Defaults, Ansible version policy, docs parser, AWS platform map | [Unit tests](.github/workflows/unit-tests.yml) → `policy` |
| Ansible unit | Role logic with synthetic facts (no apt/VM) | [Unit tests](.github/workflows/unit-tests.yml) → `unit` matrix |
| Galaxy import | Legacy role metadata for publication | [Unit tests](.github/workflows/unit-tests.yml) → `validate` |
| Security scan | Vulnerabilities and secrets in repo tree | [trivy.yml](.github/workflows/trivy.yml) |
| Docker integration | Real apt install in containers | [integration-tests.yml](.github/workflows/integration-tests.yml) (after lint/unit + Trivy) |
| AWS remote | Full apply on ephemeral EC2 | [RC AWS](.github/workflows/rc-aws-remote-tests.yml), [manual AWS](.github/workflows/aws-remote-tests.yml) |

See also [docs/aws-remote-tests-workflow.md](docs/aws-remote-tests-workflow.md) for OIDC, repository variables, and teardown guarantees.

### Unit tests workflow

[`.github/workflows/unit-tests.yml`](.github/workflows/unit-tests.yml) runs on every PR, push to `main`, and `workflow_dispatch`. Jobs run in sequence:

```text
lint → policy → unit (matrix) → validate
```

#### `lint` job

| Step | Purpose |
|------|---------|
| `pre-commit run --all-files` | ansible-lint, yamllint, whitespace, EOF fixes |
| `ansible-playbook --syntax-check tests/test.yml` | Role example playbook syntax |
| `playbooks/ci-check-mode.yml --check` | Synthetic Ubuntu noble host: facts, validation, repository line generation without apt changes |
| `tests/validate-release-workflows.sh` | Release/Galaxy workflow contracts (semantic-version tags only) |
| `tests/validate-gitignore.sh` | No tracked files violate `.gitignore` |

#### `policy` job

| Step | Purpose |
|------|---------|
| `python -m unittest discover -s tests/unit` | Python unit tests (see below) |
| `scripts/validate-role-defaults.py` | `defaults/main.yml`, `meta/argument_specs.yml`, and `meta/main.yml` stay aligned with the unit-test platform matrix |
| `scripts/check-ansible-version-policy.py` | `ansible-core>=2.20,<2.21` documented consistently in README, requirements, Galaxy metadata |
| Molecule schema check | Every `molecule/*/molecule.yml` has required keys (Vagrant scenarios omit `dependency`) |
| AWS platform catalog | Five integration platforms defined in `scripts/aws_integration_platforms.py` |

#### `unit` matrix

Three parallel jobs run `ansible-playbook` against synthetic facts (no containers, no network apt):

| Job | Playbook | Coverage |
|-----|----------|----------|
| Unit (all platforms) | `molecule/unit/converge.yml` | All supported distros/releases in one matrix: noble, plucky, questing, bookworm, trixie; amd64 and arm64 |
| Unit (Ubuntu 25.04) | `molecule/unit-ubuntu-plucky/converge.yml` | Plucky-specific regression path |
| Unit (Ubuntu 25.10) | `molecule/unit-ubuntu-questing/converge.yml` | Questing-specific regression path |

Ansible unit tasks under `molecule/common/unit/tasks/` cover:

- Repository fact generation (`test_repository_facts.yml`)
- Package list composition per distribution (`test_distribution_packages.yml`, `test_package_selection.yml`)
- Platform validation failures (`test_validation_failure.yml`)
- Architecture detection and override rules (`test_architecture_validation.yml`)
- Apt keyring install and rotation with local fixtures (`test_keyring_lifecycle.yml`)

#### `validate` job

Runs `galaxy_importer` in **legacy role** mode to ensure the role would pass Ansible Galaxy import checks before a tagged release.

### Python unit tests (`tests/unit/`)

| Test module | What it checks |
|-------------|----------------|
| `test_parse_regolith_docs_stable.py` | `scripts/parse-regolith-docs-stable.py` extracts stable version pins from Regolith docs HTML |
| `test_validate_role_defaults.py` | `validate-role-defaults.py` accepts the current repository tree |
| `test_prepare_aws_matrix.py` | AWS matrix builder includes only integration jobs with `conclusion: success`; platform catalog matches the five integration containers |
| `test_verify_aws_rc_gate.py` | Legacy Galaxy/AWS RC gate helper (unused by publish workflows) |
| `test_verify_ci_prerequisites.py` | Integration gate requires successful lint/unit and Trivy workflows |

Run locally (with `.venv` activated):

```bash
python -m pip install pyyaml
python -m unittest discover -s tests/unit -p 'test_*.py' -v
```

### Integration tests workflow

[`.github/workflows/integration-tests.yml`](.github/workflows/integration-tests.yml) (**CI — Regolith: container integration**) starts after **CI — Regolith: lint & unit tests** and **CI — Regolith: security (Trivy)** pass on PRs
and `main` pushes. On pull requests it waits for both workflows on the PR head commit; after merge to
`main`, the same gate runs via `workflow_run` when the unit workflow completes. Scheduled and manual runs skip
that gate.

Five parallel container jobs (same platforms as the supported-platforms table):

| Container image | Job name |
|-----------------|----------|
| `python:3.13-bookworm` | Debian bookworm |
| `python:3.13-trixie` | Debian trixie |
| `ubuntu:24.04` | Ubuntu 24.04 (noble) |
| `ubuntu:25.04` | Ubuntu 25.04 (plucky) |
| `ubuntu:25.10` | Ubuntu 25.10 (questing) |

Each job uses [`.github/actions/run-integration-test`](.github/actions/run-integration-test/action.yml):

1. **Prepare** — `molecule/common/docker_prepare.yml` (apt, python)
2. **Apply** — `molecule/common/converge.yml` (full role install from the real Regolith archive)
3. **Verify** — `molecule/default/verify.yml` (packages, apt health, X session registration)
4. **Idempotence** — second converge; fails if `PLAY RECAP` shows `changed > 0`
5. **Repository transitions** — `repository_transition.yml`, `repository_suite_transition.yml`

Triggers: PR, push to `main`, daily cron, `workflow_dispatch`.

### PR CI and AWS remote tests

**Feature PRs** run the full pyramid before merge:

```text
PR (feature branch)
  → CI — Regolith: lint & unit tests  ─┐
  → CI — Regolith: security (Trivy)   ─┤ both must pass
  → CI — Regolith: container integration ─┘
  → CI — Regolith: AWS EC2 (PR gate) (after integration; per successful platform)
```

Release Please PRs (`release-please--branches--main`) run lint/unit/integration only — AWS already ran on the merged commits.

**After merge to `main` (release path):**

```text
push to main
  → Release Please opens/updates release PR
  → Merge release PR → vX.Y.Z tag, GitHub release
  → Galaxy import on the release tag (no AWS gate)
```

| Stage | Trigger | AWS? |
|-------|---------|------|
| Feature PR | `pull_request` | Yes, after integration (per platform) |
| Release PR | `pull_request` from `release-please--branches--main` | No |
| Final release | Merge release PR | Galaxy publish only |

[`.github/workflows/rc-aws-remote-tests.yml`](.github/workflows/rc-aws-remote-tests.yml) (**CI — Regolith: AWS EC2 (PR gate)**) builds its matrix with [`scripts/prepare-aws-matrix-from-integration.py`](scripts/prepare-aws-matrix-from-integration.py), which reads successful jobs from the container integration workflow run. Failed integration platforms are skipped automatically.

Manual platform testing: [`.github/workflows/aws-remote-tests.yml`](.github/workflows/aws-remote-tests.yml) (**CI — Regolith: AWS EC2 (manual)**; `workflow_dispatch`, all supported platforms).

### Continuous integration (workflow reference)

| Workflow | Display name | Trigger | What it runs |
|----------|--------------|---------|----------------|
| [unit-tests.yml](.github/workflows/unit-tests.yml) | CI — Regolith: lint & unit tests | PR, push to `main`, manual | `lint` → `policy` → Ansible unit matrix → Galaxy `validate` (see above) |
| [trivy.yml](.github/workflows/trivy.yml) | CI — Regolith: security (Trivy) | PR, push to `main`, weekly, manual | Trivy filesystem scan (CRITICAL/HIGH); must pass before integration |
| [integration-tests.yml](.github/workflows/integration-tests.yml) | CI — Regolith: container integration | After unit workflow on PR/`main`, daily cron, manual | Five container jobs: full install, verify, idempotence, repo transitions |
| [rc-aws-remote-tests.yml](.github/workflows/rc-aws-remote-tests.yml) | CI — Regolith: AWS EC2 (PR gate) | After integration on feature PRs, manual | Ephemeral EC2 per **successful** integration platform |
| [aws-remote-tests.yml](.github/workflows/aws-remote-tests.yml) | CI — Regolith: AWS EC2 (manual) | Manual | On-demand EC2: pick platform, arch coverage, scenario |
| [auto-run-release-please-checks.yml](.github/workflows/auto-run-release-please-checks.yml) | Release — Regolith: unblock release PR CI | Release PR opened/synced | Re-runs CI blocked by first-time contributor approval on release PRs |
| [check-regolith-stable.yml](.github/workflows/check-regolith-stable.yml) | Maintenance — Regolith: stable pin drift | Daily cron, manual | Compares `defaults/main.yml` pin with Regolith docs; opens drift issue |
| [release-please.yml](.github/workflows/release-please.yml) | Release — Regolith: version bump | Push to `main`, manual | Release PR, Galaxy import on final release |
| [release.yml](.github/workflows/release.yml) | Release — Regolith: Galaxy import (manual) | Manual only | Recovery Galaxy import for an existing semver tag |

#### Dependency updates

[Dependabot](.github/dependabot.yml) opens weekly PRs for **GitHub Actions** and **pip** (`requirements.txt`, `requirements-ci.txt`), with a **7-day cooldown** after each upstream release (14 days for semver-major). Enable it under **Settings → Code security → Dependabot**.

#### Ansible Galaxy

This repository does **not** auto-tag `main` or publish the default branch to Galaxy. Every import must target an existing semantic-version tag via `ansible-galaxy role import --branch <tag>`.

1. Create a [Galaxy](https://galaxy.ansible.com) account and connect your GitHub account.
2. Add repository secret **`GALAXY_API_KEY`** (Galaxy → Preferences → API Key). Publication jobs fail if this secret is missing.
3. Use Conventional Commits in merged PR titles/commits. `fix:` creates patch releases, `feat:` creates minor releases, and breaking changes create major releases. See [CONTRIBUTING.md](CONTRIBUTING.md) for squash-merge guidance that keeps release notes deduplicated.
4. Merge the Release Please PR to create the version tag and GitHub release.
5. **Normal publish path:** when Release Please creates a release, [release-please.yml](.github/workflows/release-please.yml) checks out that tag and imports into Ansible Galaxy with `ansible-galaxy role import --branch <tag>`.
6. **Recovery publish path:** run [release.yml](.github/workflows/release.yml) manually and supply an existing semantic-version tag (for example `v1.2.3`) as `release-tag`.

PR validation and ordinary `main` CI runs do not import the role into Galaxy.

Install after publish:

```bash
ansible-galaxy install steveyminecraft.regolith
```

The Vagrant scenario verifies package installation, apt dependency health, and registration of the Regolith desktop session under `/usr/share/xsessions`.

Repository key fingerprint enforcement is not enabled because this role does not currently have an authoritative published fingerprint to validate against. The role follows the official Regolith key-install method and removes temporary key material after dearmoring.

#### Further hardening (optional)

- **Repository signing-key rotation:** the role refreshes the installed keyring when downloaded key material changes, but automatic rotation after upstream key changes should still be verified on real hosts when Regolith publishes a new signing key.
- **Branch protection** on `main`: PR merges require lint & unit jobs (Lint & static analysis, all Unit tests matrix jobs, Galaxy import validation), container integration (Debian bookworm/trixie, Ubuntu noble/plucky/questing), and Trivy.
- **pip-audit** in CI for Python requirement files (complements Trivy; no lockfile today).
- **OpenSSF Scorecard** workflow for supply-chain posture on the repo.
- **CodeQL** is low value here (mostly YAML/Ansible); ansible-lint and Trivy cover more of this role.

Further reading
---------------

- [Knowledge vault (local graphify)](docs/knowledge-vault.md) — optional agent architecture map; `graphify-out/` stays local

License
-------

MIT

Author Information
------------------

This role is maintained by [steveyminecraft](https://github.com/steveyminecraft).
