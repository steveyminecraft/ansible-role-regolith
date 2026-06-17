#!/usr/bin/env python3
"""Parse ansible.builtin.json playbook output and fail when changed > 0."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PLAYBOOK_JSON_OUTPUT", file=sys.stderr)
        return 2

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    stats = payload.get("stats", {})
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
