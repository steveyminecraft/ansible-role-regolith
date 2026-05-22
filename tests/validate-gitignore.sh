#!/usr/bin/env bash
# Fail if any tracked file matches .gitignore patterns.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

fail() {
  echo "validate-gitignore: $*" >&2
  exit 1
}

[[ -f .gitignore ]] || fail "missing .gitignore"

tracked_ignored="$(git ls-files -ci --exclude-standard || true)"
if [[ -n "${tracked_ignored}" ]]; then
  echo "validate-gitignore: tracked files must not match .gitignore:" >&2
  printf '%s\n' "${tracked_ignored}" >&2
  exit 1
fi

echo "validate-gitignore: all checks passed"
