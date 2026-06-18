"""Integration test labels and matching AWS ephemeral host profiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AwsIntegrationPlatform:
    platform_id: str
    integration_job_name: str
    os_family: str
    os_version: str
    os_codename: str
    arch: str
    ansible_user: str


# Keep integration job names in sync with .github/workflows/integration-tests.yml matrix labels.
PLATFORMS: tuple[AwsIntegrationPlatform, ...] = (
    AwsIntegrationPlatform(
        platform_id="debian-bookworm",
        integration_job_name="Debian bookworm",
        os_family="debian",
        os_version="12",
        os_codename="bookworm",
        arch="amd64",
        ansible_user="admin",
    ),
    AwsIntegrationPlatform(
        platform_id="debian-trixie",
        integration_job_name="Debian trixie",
        os_family="debian",
        os_version="13",
        os_codename="trixie",
        arch="amd64",
        ansible_user="admin",
    ),
    AwsIntegrationPlatform(
        platform_id="ubuntu-jammy",
        integration_job_name="Ubuntu 22.04 (jammy)",
        os_family="ubuntu",
        os_version="22.04",
        os_codename="jammy",
        arch="amd64",
        ansible_user="ubuntu",
    ),
    AwsIntegrationPlatform(
        platform_id="ubuntu-noble",
        integration_job_name="Ubuntu 24.04 (noble)",
        os_family="ubuntu",
        os_version="24.04",
        os_codename="noble",
        arch="amd64",
        ansible_user="ubuntu",
    ),
    AwsIntegrationPlatform(
        platform_id="ubuntu-plucky",
        integration_job_name="Ubuntu 25.04 (plucky)",
        os_family="ubuntu",
        os_version="25.04",
        os_codename="plucky",
        arch="amd64",
        ansible_user="ubuntu",
    ),
    AwsIntegrationPlatform(
        platform_id="ubuntu-questing",
        integration_job_name="Ubuntu 25.10 (questing)",
        os_family="ubuntu",
        os_version="25.10",
        os_codename="questing",
        arch="amd64",
        ansible_user="ubuntu",
    ),
)

PLATFORMS_BY_JOB_NAME = {platform.integration_job_name: platform for platform in PLATFORMS}


def matrix_from_jobs(jobs: list[dict]) -> list[dict[str, str]]:
    matrix: list[dict[str, str]] = []
    for job in jobs:
        if job.get("conclusion") != "success":
            continue
        platform = PLATFORMS_BY_JOB_NAME.get(job.get("name", ""))
        if platform is None:
            continue
        matrix.append(platform_to_matrix_entry(platform))
    return matrix


def platform_to_matrix_entry(platform: AwsIntegrationPlatform) -> dict[str, str]:
    return {
        "platform_id": platform.platform_id,
        "label": platform.integration_job_name,
        "os_family": platform.os_family,
        "os_version": platform.os_version,
        "os_codename": platform.os_codename,
        "arch": platform.arch,
        "ansible_user": platform.ansible_user,
    }
