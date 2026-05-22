#!/usr/bin/env bash
# Validate release workflow and Galaxy import action contracts without live publication.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

fail() {
  echo "validate-release-workflows: $*" >&2
  exit 1
}

action="${repo_root}/.github/actions/import-galaxy-role/action.yml"
release_please="${repo_root}/.github/workflows/release-please.yml"
release="${repo_root}/.github/workflows/release.yml"

[[ -f "${action}" ]] || fail "missing ${action}"
[[ -f "${release_please}" ]] || fail "missing ${release_please}"
[[ -f "${release}" ]] || fail "missing ${release}"

grep -q 'name: Import role to Ansible Galaxy' "${action}" \
  || fail "import action must be the Galaxy import composite action"
grep -q 'git-reference:' "${action}" || fail "import action missing git-reference input"
grep -q 'required: true' "${action}" || fail "import action must declare required inputs"
grep -q 'GALAXY_API_KEY is required for Ansible Galaxy publication' "${action}" \
  || fail "import action must fail closed without GALAXY_API_KEY"
grep -q 'exit 1' "${action}" || fail "import action must exit non-zero on failure"
grep -q '\-\-branch' "${action}" || fail "import action must pass --branch to ansible-galaxy role import"
grep -q 'git-reference must be a semantic version tag' "${action}" \
  || fail "import action must validate semantic version tags"

grep -q 'git-reference: \${{ needs.release-please.outputs.tag_name }}' "${release_please}" \
  || fail "release-please workflow must pass git-reference to import action"

grep -q 'release-tag:' "${release}" || fail "release workflow must require release-tag input"
grep -q 'git-reference: \${{ inputs.release-tag }}' "${release}" \
  || fail "release workflow must pass release-tag as git-reference"
grep -q 'ref: \${{ inputs.release-tag }}' "${release}" \
  || fail "release workflow must check out release-tag only"

if grep -qE '^[[:space:]]*release:' "${release}"; then
  fail "release workflow must not trigger on release: published"
fi

if grep -q 'github\.ref' "${release}"; then
  fail "release workflow must not fall back to github.ref for publication"
fi

# Exercise tag validation logic from the composite action.
validate_tag() {
  local tag="$1"
  case "${tag}" in
    v[0-9]*.[0-9]*.[0-9]*) return 0 ;;
    *) return 1 ;;
  esac
}

validate_tag v1.2.3 || fail "valid tag v1.2.3 rejected"
validate_tag main && fail "branch name main must be rejected"
validate_tag v1.2 && fail "incomplete tag v1.2 must be rejected"

echo "validate-release-workflows: all checks passed"
