Ansible Role: regolith
=========

Requirements
------------

None.

Role Variables
--------------

Available variables and their defaults:

```yaml
regolith_repository_key_url: https://archive.regolith-desktop.com/regolith.key
regolith_repository_keyring: /usr/share/keyrings/regolith-archive-keyring.gpg
regolith_repository_base_url: https://archive.regolith-desktop.com
regolith_repository_suite: stable
regolith_repository_component: main
regolith_repository_architecture: "{{ 'arm64' if ansible_architecture in ['aarch64', 'arm64'] else 'amd64' }}"

regolith_packages:
  - regolith-desktop
  - regolith-session-flashback
  - regolith-look-lascaille
  - xdg-desktop-portal-regolith

regolith_ubuntu_packages: "{{ regolith_packages }}"
regolith_debian_packages: "{{ regolith_packages }}"
```

The default `regolith_repository_component` value of `main` follows the latest
stable Regolith release. Set it to a fixed release component such as `v3.4` to
hold the role to a specific Regolith release.

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

Testing
-------

Run the Vagrant-backed Molecule scenario:

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

The scenario uses `bento/ubuntu-24.04` and verifies package installation,
apt dependency health, and
registration of the Regolith desktop session under `/usr/share/xsessions`.

License
-------

MIT

Author Information
------------------

This role was created in 2026 by [Richard Laing](mail@rlaing.net).
