#!/usr/bin/env python3
"""Parse ansible.builtin.json playbook output and fail when changed > 0."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_playbook_stats(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"No output in {path}")

    try:
        payload = json.loads(text)
        if isinstance(payload, dict) and "stats" in payload:
            return payload["stats"]
    except json.JSONDecodeError:
        pass

    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "stats" in payload:
            return payload["stats"]

    raise ValueError(f"Could not find playbook stats JSON in {path}")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PLAYBOOK_JSON_OUTPUT", file=sys.stderr)
        return 2

    stats = load_playbook_stats(Path(sys.argv[1]))
    offenders = {
        host: host_stats.get("changed", 0)
        for host, host_stats in stats.items()
        if host_stats.get("changed", 0) > 0
    }
    if offenders:
        for host, changed in offenders.items():
            print(f"Non-idempotent tasks on {host}: changed={changed}", file=sys.stderr)
        return 1

    print("Playbook run is idempotent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
