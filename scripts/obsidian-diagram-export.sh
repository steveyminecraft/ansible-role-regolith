#!/usr/bin/env bash
# Export a .drawio file to PNG in the Obsidian diagrams folder (with IEND repair).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPAIR="$ROOT/.cursor/skills/drawio-skill/scripts/repair_png.py"
VAULT_DIAGRAMS="$ROOT/graphify-out/obsidian/diagrams"

usage() {
  cat <<'EOF'
Usage: ./scripts/obsidian-diagram-export.sh <file.drawio> [--scale N]

Exports an embedded PNG next to the source file (or into graphify-out/obsidian/diagrams/
if the input path is outside the vault). Runs repair_png.py after -e export.

Requires draw.io desktop CLI (drawio or draw.io on PATH).
EOF
}

resolve_drawio() {
  if command -v drawio >/dev/null 2>&1; then
    echo drawio
  elif command -v draw.io >/dev/null 2>&1; then
    echo draw.io
  else
    echo "draw.io CLI not found — install from https://github.com/jgraph/drawio-desktop/releases" >&2
    exit 1
  fi
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

INPUT="$1"
shift
SCALE=2

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scale) SCALE="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$INPUT" ]]; then
  echo "Not a file: $INPUT" >&2
  exit 1
fi

INPUT="$(realpath "$INPUT")"
BASE="$(basename "$INPUT" .drawio)"
DIR="$(dirname "$INPUT")"

if [[ "$DIR" != *"/graphify-out/obsidian/diagrams"* ]]; then
  mkdir -p "$VAULT_DIAGRAMS"
  TARGET="$VAULT_DIAGRAMS/$BASE.drawio"
  if [[ "$INPUT" != "$TARGET" ]]; then
    cp "$INPUT" "$TARGET"
    echo "Copied source to $TARGET"
  fi
  INPUT="$TARGET"
  DIR="$VAULT_DIAGRAMS"
fi

OUT="$DIR/$BASE.drawio.png"
DRAWIO="$(resolve_drawio)"

echo "Exporting $OUT (${DRAWIO}, scale=${SCALE})..."
"$DRAWIO" -x -f png -e -s "$SCALE" -o "$OUT" "$INPUT"

if [[ -f "$REPAIR" ]]; then
  python3 "$REPAIR" "$OUT"
fi

echo "Done: $OUT"
echo "Embed in Obsidian: ![[${BASE}.drawio.png]]"
