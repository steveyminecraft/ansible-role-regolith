Ansible Role: regolith
=========

Requirements
------------

- **ansible-core 2.20** or newer (2.20 is the supported baseline; avoid EOL 2.15–2.19).
- Target host must be a [supported platform](#supported-platforms) (Debian family).
- Root privileges (`become: true`) for APT repository and package changes.

Supported platforms
-------------------

This role follows the [Regolith install documentation](https://regolith-desktop.com/docs/using-regolith/install/).

| Distribution | Release (codename) | Version |
|--------------|-------------------|---------|
| Ubuntu | jammy | 22.04 |
| Ubuntu | noble | 24.04 |
| Ubuntu | plucky | 25.04 |
| Ubuntu | questing | 25.10 |
| Debian | bookworm | 12 |
| Debian | trixie | 13 |

Unsupported distributions or releases fail during role validation with a clear error message.

Role Variables
--------------

Available variables and their defaults:

```yaml
regolith_repository_key_url: https://archive.regolith-desktop.com/regolith.key
regolith_repository_keyring: /usr/share/keyrings/regolith-archive-keyring.gpg
regolith_repository_base_url: https://archive.regolith-desktop.com
regolith_repository_suite: stable
regolith_repository_component: v3.4
# regolith_repository_architecture is auto-detected from ansible_facts in tasks/facts.yml

regolith_packages:
  - regolith-desktop
  - regolith-session-flashback
  - regolith-look-lascaille
  - xdg-desktop-portal-regolith

regolith_ubuntu_packages: "{{ regolith_packages }}"
regolith_debian_packages: "{{ regolith_packages }}"
```

The default `regolith_repository_component` value of `v3.4` matches the official install examples for a pinned Regolith release. Set it to `main` to follow the latest stable release in the archive.

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

### Continuous integration

GitHub Actions workflows:

| Workflow | Trigger | What it runs |
|----------|---------|----------------|
| [Unit tests](.github/workflows/unit-tests.yml) | PR, push to `main`, manual | pre-commit; `ansible-playbook` unit matrix; Galaxy metadata validation |
| [Integration tests](.github/workflows/integration-tests.yml) | PR, push to `main`, daily cron, manual | Native container jobs (Debian bookworm/trixie, Ubuntu noble/plucky/questing) |
| [Auto-tag on main](.github/workflows/auto-tag.yml) | Push to `main` | Bumps the latest `v*.*.*` tag (starts at `v3.4.0`) and pushes it |
| [Publish to Ansible Galaxy](.github/workflows/galaxy-publish.yml) | Push to `main`, manual | Imports `steveyminecraft.regolith` from the latest `main` commit |
| [Release](.github/workflows/release.yml) | Tag `v*`, manual | GitHub release plus Galaxy import (versioned by tag) |
| [Security scan](.github/workflows/trivy.yml) | PR, push to `main`, weekly, manual | Trivy filesystem, secret, and misconfig scan (CRITICAL/HIGH) |
| [Vagrant integration](.github/workflows/testing.yml) | Manual only | Full install on a self-hosted runner with VirtualBox or libvirt |

#### Dependency updates

[Dependabot](.github/dependabot.yml) opens weekly PRs for **GitHub Actions** and **pip** (`requirements.txt`, `requirements-ci.txt`), with a **7-day cooldown** after each upstream release (14 days for semver-major). Enable it under **Settings → Code security → Dependabot**.

#### Ansible Galaxy

1. Create a [Galaxy](https://galaxy.ansible.com) account and connect your GitHub account.
2. Add repository secret **`GALAXY_API_KEY`** (Galaxy → Preferences → API Key).
3. Merge to **`main`** — CI runs, [auto-tag.yml](.github/workflows/auto-tag.yml) creates the next `v*.*.*` tag, [galaxy-publish.yml](.github/workflows/galaxy-publish.yml) imports the role, and [release.yml](.github/workflows/release.yml) publishes a GitHub release for that tag.
4. To skip auto-tagging for a merge, include `[skip tag]` in the commit message.

Install after publish:

```bash
ansible-galaxy install steveyminecraft.regolith
```

The Vagrant scenario verifies package installation, apt dependency health, and registration of the Regolith desktop session under `/usr/share/xsessions`.

#### Further hardening (optional)

- **Branch protection** on `main`: require unit and integration checks (and Trivy) before merge.
- **pip-audit** in CI for Python requirement files (complements Trivy; no lockfile today).
- **OpenSSF Scorecard** workflow for supply-chain posture on the repo.
- **CodeQL** is low value here (mostly YAML/Ansible); ansible-lint and Trivy cover more of this role.

License
-------

MIT

Author Information
------------------

This role is maintained by [steveyminecraft](https://github.com/steveyminecraft).
