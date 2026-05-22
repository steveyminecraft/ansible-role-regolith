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
| Ubuntu | jammy | 22.04 |
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

For local autoenv/direnv-style setup, copy the tracked example file to a private local `.env` file and edit any machine-specific values. The `.env` path is listed in `.gitignore` and must not be committed; only [`.env.example`](.env.example) belongs in git.

```bash
cp .env.example .env
```

Unit tests (repository line generation, no VM):

```bash
ansible-playbook molecule/unit/converge.yml
ansible-playbook molecule/unit-ubuntu-plucky/converge.yml
ansible-playbook molecule/unit-ubuntu-questing/converge.yml
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

Optional Molecule wrappers (local development):

```bash
pip install -r requirements.txt
molecule test -s unit
molecule test -s debian-bookworm
molecule test -s ubuntu-noble
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

Linting and validation:

```bash
pre-commit run --all-files
ansible-lint
yamllint .
```

Ansible-lint uses the production profile in offline mode, excluding local caches, virtual environments, GitHub workflow files, and Molecule-generated state so local and CI runs stay deterministic.
Yamllint follows `.yamllint`, warning on lines longer than 150 characters while ignoring local caches, virtual environments, collections, and generated Molecule Vagrant state.

### Continuous integration

GitHub Actions workflows:

| Workflow | Trigger | What it runs |
|----------|---------|----------------|
| [Unit tests](.github/workflows/unit-tests.yml) | PR, push to `main`, manual | pre-commit; `ansible-playbook` unit matrix; Galaxy metadata validation |
| [Integration tests](.github/workflows/integration-tests.yml) | PR, push to `main`, daily cron, manual | Native container jobs (Debian bookworm/trixie, Ubuntu jammy/noble/plucky/questing) |
| [Check Regolith stable pin (docs)](.github/workflows/check-regolith-stable.yml) | Daily cron, manual | Compares `defaults/main.yml` pinned component with the latest stable release listed on Regolith docs and fails on mismatch |
| [Release Please](.github/workflows/release-please.yml) | Push to `main`, manual | Creates or updates the release PR; imports the released tag into Ansible Galaxy when a release is created |
| [Release](.github/workflows/release.yml) | Manual only | Recovery import of an existing semantic-version tag into Ansible Galaxy |
| [Security scan](.github/workflows/trivy.yml) | PR, push to `main`, weekly, manual | Trivy filesystem, secret, and misconfig scan (CRITICAL/HIGH) |

#### Dependency updates

[Dependabot](.github/dependabot.yml) opens weekly PRs for **GitHub Actions** and **pip** (`requirements.txt`, `requirements-ci.txt`), with a **7-day cooldown** after each upstream release (14 days for semver-major). Enable it under **Settings → Code security → Dependabot**.

#### Ansible Galaxy

This repository does **not** auto-tag `main` or publish the default branch to Galaxy. Every import must target an existing semantic-version tag via `ansible-galaxy role import --branch <tag>`.

1. Create a [Galaxy](https://galaxy.ansible.com) account and connect your GitHub account.
2. Add repository secret **`GALAXY_API_KEY`** (Galaxy → Preferences → API Key). Publication jobs fail if this secret is missing.
3. Use Conventional Commits in merged PR titles/commits. `fix:` creates patch releases, `feat:` creates minor releases, and breaking changes create major releases. See [CONTRIBUTING.md](CONTRIBUTING.md) for squash-merge guidance that keeps release notes deduplicated.
4. Merge the Release Please PR to create the version tag and GitHub release.
5. **Normal publish path:** when Release Please creates a release, [release-please.yml](.github/workflows/release-please.yml) checks out that tag and imports it into Ansible Galaxy with `ansible-galaxy role import --branch <tag>`.
6. **Recovery publish path:** run [release.yml](.github/workflows/release.yml) manually, supply an existing semantic-version tag (for example `v1.2.3`) as `release-tag`, and the workflow passes the same tag to Galaxy as `git-reference`. The workflow cannot publish `main` or another branch.

PR validation and ordinary `main` CI runs do not import the role into Galaxy.

Install after publish:

```bash
ansible-galaxy install steveyminecraft.regolith
```

The Vagrant scenario verifies package installation, apt dependency health, and registration of the Regolith desktop session under `/usr/share/xsessions`.

Repository key fingerprint enforcement is not enabled because this role does not currently have an authoritative published fingerprint to validate against. The role follows the official Regolith key-install method and removes temporary key material after dearmoring.

#### Further hardening (optional)

- **Repository signing-key rotation:** the role refreshes the installed keyring when downloaded key material changes, but automatic rotation after upstream key changes should still be verified on real hosts when Regolith publishes a new signing key.
- **Branch protection** on `main`: PR merges require unit tests (Lint, all Unit matrix jobs, Role validation), integration tests (Debian bookworm/trixie, Ubuntu jammy/noble/plucky/questing), and Trivy.
- **pip-audit** in CI for Python requirement files (complements Trivy; no lockfile today).
- **OpenSSF Scorecard** workflow for supply-chain posture on the repo.
- **CodeQL** is low value here (mostly YAML/Ansible); ansible-lint and Trivy cover more of this role.

License
-------

MIT

Author Information
------------------

This role is maintained by [steveyminecraft](https://github.com/steveyminecraft).
