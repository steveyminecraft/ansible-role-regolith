#!/usr/bin/env bash
# Create graphify-out/obsidian/diagrams/ for draw.io maps (local, gitignored).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIAGRAMS="$ROOT/graphify-out/obsidian/diagrams"
TEMPLATE="$ROOT/docs/obsidian-diagram-templates/00-diagram-maps-index.md"

if [[ ! -f "$ROOT/graphify-out/graph.json" ]]; then
  echo "graphify-out/graph.json missing — run ./scripts/setup-knowledge-vault.sh first" >&2
  exit 1
fi

mkdir -p "$DIAGRAMS"

if [[ ! -f "$DIAGRAMS/00 - Diagram Maps Index.md" ]]; then
  cp "$TEMPLATE" "$DIAGRAMS/00 - Diagram Maps Index.md"
  echo "Created $DIAGRAMS/00 - Diagram Maps Index.md"
else
  echo "Index already exists: $DIAGRAMS/00 - Diagram Maps Index.md"
fi

echo "Obsidian diagram folder ready: $DIAGRAMS"
echo "Open vault: graphify-out/obsidian/"
