#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  AWS_REGION
  AWS_SUBNET_ID
  AWS_KEY_NAME
  AWS_INSTANCE_TYPE
  AWS_OS_FAMILY
  AWS_ARCH
  AWS_TEST_SCENARIO
  AWS_SSH_PRIVATE_KEY_PATH
  AWS_INVENTORY_FILE
  AWS_STATE_FILE
  AWS_METADATA_FILE
  AWS_INVENTORY_TEMPLATE
  AWS_ANSIBLE_USER
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    exit 2
  fi
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

write_state_file() {
  local instance_ids_json="[]"
  local state_dir state_tmp
  if [[ -n "${instance_id:-}" ]]; then
    instance_ids_json="[\"${instance_id}\"]"
  fi

  state_dir="$(dirname "${AWS_STATE_FILE}")"
  state_tmp="$(mktemp "${state_dir}/aws-state.XXXXXX")"
  cat > "${state_tmp}" <<EOF
{
  "region": "${AWS_REGION}",
  "instance_ids": ${instance_ids_json},
  "security_group_id": "${security_group_id:-}"
}
EOF
  mv "${state_tmp}" "${AWS_STATE_FILE}"
}

cleanup_on_failure() {
  local exit_code="$?"
  if [[ "${exit_code}" -eq 0 ]]; then
    return
  fi

  if [[ -f "${AWS_STATE_FILE}" ]]; then
    echo "Provisioning failed; attempting best-effort AWS cleanup." >&2
    if ! "${script_dir}/destroy-ephemeral-env.sh"; then
      echo "WARNING: best-effort cleanup failed; manual AWS cleanup may be required." >&2
    fi
  fi
}
trap cleanup_on_failure EXIT

if [[ ! -f "${AWS_INVENTORY_TEMPLATE}" ]]; then
  echo "Inventory template not found: ${AWS_INVENTORY_TEMPLATE}" >&2
  exit 2
fi

AWS_OS_VERSION="${AWS_OS_VERSION:-}"
AWS_PROJECT_TAG="${AWS_PROJECT_TAG:-ansible-role-regolith}"
arch_suffix="${AWS_ARCH}"
if [[ "${AWS_ARCH}" == "arm64" ]]; then
  arch_suffix="arm64"
fi

resolve_ubuntu_ami() {
  local version="${1:-24.04}"
  local arch="${2:-amd64}"
  aws ssm get-parameter \
    --region "${AWS_REGION}" \
    --name "/aws/service/canonical/ubuntu/server/${version}/stable/current/${arch}/hvm/ebs-gp3/ami-id" \
    --query 'Parameter.Value' \
    --output text
}

resolve_debian_ami() {
  local version="${1:-12}"
  local arch="${2:-amd64}"
  aws ssm get-parameter \
    --region "${AWS_REGION}" \
    --name "/aws/service/debian/release/${version}/latest/${arch}" \
    --query 'Parameter.Value' \
    --output text
}

case "${AWS_OS_FAMILY}" in
  ubuntu)
    ubuntu_version="${AWS_OS_VERSION:-24.04}"
    ami_id="$(resolve_ubuntu_ami "${ubuntu_version}" "${arch_suffix}")"
    ;;
  debian)
    debian_version="${AWS_OS_VERSION:-12}"
    ami_id="$(resolve_debian_ami "${debian_version}" "${arch_suffix}")"
    ;;
  *)
    echo "Unsupported AWS_OS_FAMILY: ${AWS_OS_FAMILY}" >&2
    exit 2
    ;;
esac

if [[ -z "${ami_id}" || "${ami_id}" == "None" ]]; then
  echo "Unable to resolve AMI for ${AWS_OS_FAMILY} ${AWS_OS_VERSION:-${AWS_OS_CODENAME:-default}} (${arch_suffix})." >&2
  exit 2
fi

echo "Selected AMI ${ami_id} for ${AWS_OS_FAMILY} ${AWS_OS_VERSION:-${AWS_OS_CODENAME:-default}} (${arch_suffix})"

name_suffix="$(date +%s)-${RANDOM}"
name_prefix="${AWS_TEST_PREFIX:-ansible-regolith-remote}"
security_group_name="${name_prefix}-sg-${name_suffix}"
resource_name="${name_prefix}-${AWS_OS_FAMILY}-${AWS_ARCH}-${name_suffix}"
instance_id=""
security_group_id=""

if [[ -s "${AWS_STATE_FILE}" ]]; then
  echo "State file already exists (${AWS_STATE_FILE}); refusing to overwrite." >&2
  exit 2
fi

if [[ -z "${AWS_SSH_CIDR:-}" ]]; then
  AWS_SSH_CIDR="0.0.0.0/0"
fi

vpc_id="$(aws ec2 describe-subnets \
  --region "${AWS_REGION}" \
  --subnet-ids "${AWS_SUBNET_ID}" \
  --query 'Subnets[0].VpcId' \
  --output text)"

if [[ -z "${vpc_id}" || "${vpc_id}" == "None" ]]; then
  echo "Unable to resolve VPC for subnet ${AWS_SUBNET_ID}" >&2
  exit 2
fi

security_group_id="$(aws ec2 create-security-group \
  --region "${AWS_REGION}" \
  --vpc-id "${vpc_id}" \
  --group-name "${security_group_name}" \
  --description "Ephemeral ansible-role-regolith remote test SG (${name_suffix})" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${security_group_name}},{Key=Project,Value=${AWS_PROJECT_TAG}},{Key=Ephemeral,Value=true}]" \
  --query 'GroupId' \
  --output text)"

mkdir -p "$(dirname "${AWS_STATE_FILE}")" "$(dirname "${AWS_INVENTORY_FILE}")" "$(dirname "${AWS_METADATA_FILE}")"
write_state_file

aws ec2 authorize-security-group-ingress \
  --region "${AWS_REGION}" \
  --group-id "${security_group_id}" \
  --ip-permissions "[
    {\"IpProtocol\":\"tcp\",\"FromPort\":22,\"ToPort\":22,\"IpRanges\":[{\"CidrIp\":\"${AWS_SSH_CIDR}\"}]}
  ]"

instance_id="$(aws ec2 run-instances \
  --region "${AWS_REGION}" \
  --image-id "${ami_id}" \
  --instance-type "${AWS_INSTANCE_TYPE}" \
  --key-name "${AWS_KEY_NAME}" \
  --subnet-id "${AWS_SUBNET_ID}" \
  --security-group-ids "${security_group_id}" \
  --associate-public-ip-address \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${resource_name}},{Key=Project,Value=${AWS_PROJECT_TAG}},{Key=Ephemeral,Value=true}]" \
  --count 1 \
  --query 'Instances[0].InstanceId' \
  --output text)"
write_state_file

aws ec2 wait instance-running --region "${AWS_REGION}" --instance-ids "${instance_id}"
aws ec2 wait instance-status-ok --region "${AWS_REGION}" --instance-ids "${instance_id}"

public_ip="$(aws ec2 describe-instances \
  --region "${AWS_REGION}" \
  --instance-ids "${instance_id}" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)"

private_ip="$(aws ec2 describe-instances \
  --region "${AWS_REGION}" \
  --instance-ids "${instance_id}" \
  --query 'Reservations[0].Instances[0].PrivateIpAddress' \
  --output text)"

if [[ -z "${public_ip}" || "${public_ip}" == "None" ]]; then
  echo "Instance ${instance_id} has no public IP for SSH." >&2
  exit 2
fi

inventory_host="${AWS_HOST_NAME:-${AWS_OS_FAMILY}-${AWS_OS_VERSION:-unknown}}"

write_state_file

cat > "${AWS_METADATA_FILE}" <<EOF
{
  "scenario": "${AWS_TEST_SCENARIO}",
  "region": "${AWS_REGION}",
  "os_family": "${AWS_OS_FAMILY}",
  "os_version": "${AWS_OS_VERSION:-}",
  "os_codename": "${AWS_OS_CODENAME:-}",
  "ansible_user": "${AWS_ANSIBLE_USER}",
  "arch": "${AWS_ARCH}",
  "inventory_host": "${inventory_host}",
  "instance_ids": ["${instance_id}"],
  "public_ips": ["${public_ip}"],
  "private_ips": ["${private_ip}"],
  "security_group_id": "${security_group_id}",
  "project_tag": "${AWS_PROJECT_TAG}"
}
EOF

cp "${AWS_INVENTORY_TEMPLATE}" "${AWS_INVENTORY_FILE}"

PUBLIC_IP="${public_ip}" \
AWS_TEST_SCENARIO="${AWS_TEST_SCENARIO}" \
INVENTORY_HOST="${inventory_host}" \
python3 - <<'PY'
import os
from pathlib import Path

inventory_path = Path(os.environ["AWS_INVENTORY_FILE"])
content = inventory_path.read_text(encoding="utf-8")
replacements = {
    "REPLACE_HOST_NAME": os.environ["INVENTORY_HOST"],
    "REPLACE_PUBLIC_IP": os.environ["PUBLIC_IP"],
    "REPLACE_SSH_KEY_PATH": os.environ["AWS_SSH_PRIVATE_KEY_PATH"],
    "REPLACE_ANSIBLE_USER": os.environ["AWS_ANSIBLE_USER"],
}
for old, new in replacements.items():
    content = content.replace(old, new)

scenario = os.environ.get("AWS_TEST_SCENARIO", "regolith-stable")
if scenario == "regolith-main":
    content = content.replace("regolith_repository_component: v3.4", "regolith_repository_component: main")
elif scenario == "regolith-preview":
    content = content.replace("regolith_repository_suite: stable", "regolith_repository_suite: preview")

inventory_path.write_text(content, encoding="utf-8")
PY

echo "Created ephemeral AWS test environment:"
echo "  region: ${AWS_REGION}"
echo "  inventory_host: ${inventory_host}"
echo "  instance_id: ${instance_id}"
echo "  public_ip: ${public_ip}"
echo "  inventory: ${AWS_INVENTORY_FILE}"
echo "  project_tag: ${AWS_PROJECT_TAG}"
