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

Fast unit tests (repository line generation, no VM):

```bash
molecule test -s unit
molecule test -s unit-ubuntu-plucky   # Ubuntu 25.04 only
molecule test -s unit-ubuntu-questing # Ubuntu 25.10 only
```

Debian integration tests (Docker; one scenario per release):

```bash
molecule test -s debian-bookworm # 12
molecule test -s debian-trixie   # 13
```

Ubuntu integration tests (Docker; one scenario per release):

```bash
molecule test -s ubuntu-noble    # 24.04
molecule test -s ubuntu-plucky   # 25.04
molecule test -s ubuntu-questing # 25.10
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
| [Unit tests](.github/workflows/unit-tests.yml) | PR, push to `main`, manual | pre-commit; unit matrix (all, Ubuntu 25.04, Ubuntu 25.10); Galaxy import; syntax-check |
| [Integration tests](.github/workflows/integration-tests.yml) | PR, push to `main`, daily cron, manual | Docker Molecule scenarios (Debian bookworm/trixie, Ubuntu noble/plucky/questing) |
| [Vagrant integration](.github/workflows/testing.yml) | Manual only | Full install on a self-hosted runner with VirtualBox or libvirt |

The Vagrant scenario verifies package installation, apt dependency health, and registration of the Regolith desktop session under `/usr/share/xsessions`.

License
-------

MIT

Author Information
------------------

This role was created in 2026 by [Richard Laing](mail@rlaing.net).
