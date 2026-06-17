#!/usr/bin/env python3
"""Parse the latest stable Regolith release version from docs HTML."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://regolith-desktop.com/docs/reference/releases/"
VERSION_PATTERN = re.compile(r"(?<![\d.])(\d+\.\d+)\s+Release Notes")


def parse_stable_versions(html: str) -> list[str]:
    return VERSION_PATTERN.findall(html)


def latest_stable(versions: list[str]) -> str:
    if not versions:
        raise ValueError("Could not parse stable version from docs page")
    latest = max(versions, key=lambda value: tuple(int(part) for part in value.split(".")))
    return f"v{latest}"


def fetch_latest_stable(url: str = DEFAULT_URL, timeout: int = 20) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        html = response.read().decode("utf-8", "ignore")
    return latest_stable(parse_stable_versions(html))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Read HTML from a local fixture instead of fetching live docs.",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Docs URL to fetch when --fixture is not set (default: {DEFAULT_URL}).",
    )
    args = parser.parse_args()

    if args.fixture is not None:
        html = args.fixture.read_text(encoding="utf-8")
        print(latest_stable(parse_stable_versions(html)))
        return 0

    print(fetch_latest_stable(args.url))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - CLI entrypoint
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
