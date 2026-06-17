#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo_root"

inventory=""
scenario=""
skip_converge=false
skip_transitions=false

usage() {
  cat <<'EOF'
Usage: tests/remote/run.sh --inventory PATH --scenario SCENARIO [options]

Deployment scenarios:
  regolith-stable   Default stable/v3.4 component install
  regolith-main     Install with regolith_repository_component=main
  regolith-preview  Install with regolith_repository_suite=preview

Options:
  --skip-converge      Verify an existing deployment without applying the role.
  --skip-transitions   Do not exercise repository transition playbooks.
  -h, --help           Show this help.

Optional lifecycle hooks:
  REMOTE_CREATE_COMMAND        Provision hosts before converge.
  REMOTE_IDEMPOTENCE_COMMAND   Run an environment-specific idempotence check.
  REMOTE_RESET_COMMAND         Reset or destroy hosts after verification.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --inventory)
      inventory="${2:-}"
      shift 2
      ;;
    --scenario)
      scenario="${2:-}"
      shift 2
      ;;
    --skip-converge)
      skip_converge=true
      shift
      ;;
    --skip-transitions)
      skip_transitions=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$inventory" || -z "$scenario" ]]; then
  usage >&2
  exit 2
fi

case "$scenario" in
  regolith-stable|regolith-main|regolith-preview)
    verify_playbooks=(regolith.yml apt-repository.yml)
    ;;
  *)
    echo "Unknown scenario: $scenario" >&2
    usage >&2
    exit 2
    ;;
esac

run_hook() {
  local name="$1"
  local command="$2"

  if [[ -z "$command" ]]; then
    echo "Skipping optional $name hook."
    return
  fi

  echo "Running $name hook."
  /bin/bash -lc "$command"
}

run_verification() {
  local playbook

  for playbook in "${verify_playbooks[@]}"; do
    echo "Running remote verification: $playbook"
    ansible-playbook -i "$inventory" "tests/remote/verify/$playbook"
  done
}

cleanup() {
  run_hook reset "${REMOTE_RESET_COMMAND:-}"
}
trap cleanup EXIT

run_hook create "${REMOTE_CREATE_COMMAND:-}"

if [[ ! -f "$inventory" ]]; then
  echo "Inventory not found after create hook: $inventory" >&2
  exit 2
fi

echo "Validating inventory: $inventory"
ansible-inventory -i "$inventory" --graph

if ! $skip_converge; then
  echo "Converging remote Regolith deployment."
  ansible-playbook -i "$inventory" tests/remote/playbooks/bootstrap-regolith.yml
  run_verification
fi

run_hook idempotence "${REMOTE_IDEMPOTENCE_COMMAND:-}"

if ! $skip_converge; then
  echo "Re-applying role to verify idempotence."
  json_output="${RUNNER_TEMP:-/tmp}/regolith-remote-idempotence.json"
  ansible-playbook -i "$inventory" tests/remote/playbooks/bootstrap-regolith.yml \
    -e ansible_stdout_callback=ansible.builtin.json \
    > "${json_output}"
  python3 scripts/check-playbook-idempotence.py "${json_output}"
fi

if ! $skip_transitions; then
  echo "Exercising repository component transitions."
  ansible-playbook -i "$inventory" tests/remote/playbooks/repository-transition.yml
  run_verification
fi

echo "Remote scenario passed: $scenario"
