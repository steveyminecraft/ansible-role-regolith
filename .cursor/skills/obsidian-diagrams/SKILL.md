---
name: obsidian-diagrams
description: >-
  Map ansible-role-regolith architecture in the local graphify Obsidian vault
  using draw.io. Use when the user asks to diagram, map, visualize, or sketch
  role flow, CI pipelines, molecule tests, or any system in Obsidian.
---

# Obsidian diagram maps (ansible-role-regolith)

Visual maps live in the **local** graphify Obsidian vault — never committed to git.

Follow **drawio-skill** for diagram generation and export. This skill adds vault paths, graphify context, and Obsidian note conventions.

## Prerequisites

1. **Knowledge vault bootstrapped:**
   ```bash
   ./scripts/setup-knowledge-vault.sh
   ```
   For role tasks, molecule, and CI coverage, run a full build: `./scripts/setup-knowledge-vault.sh --full` then `/graphify .` in Cursor.

2. **draw.io desktop CLI** on PATH (`drawio` or `draw.io`). Prefer the [jgraph `.deb`/`.rpm`](https://github.com/jgraph/drawio-desktop/releases) — **avoid snap** (AppArmor breaks headless export on Linux servers).

3. **Obsidian** opened on vault root: `graphify-out/obsidian/`

Optional: [Draw.io Integration](https://github.com/zapthedingbat/drawio-obsidian) community plugin for in-vault `.drawio` editing.

## Output locations (always use these)

| Artifact | Path |
|----------|------|
| Editable source | `graphify-out/obsidian/diagrams/<slug>.drawio` |
| Vault embed (PNG) | `graphify-out/obsidian/diagrams/<slug>.drawio.png` |
| Obsidian note | `graphify-out/obsidian/diagrams/<slug>.md` |
| Diagram index | `graphify-out/obsidian/diagrams/00 - Diagram Maps Index.md` |

`<slug>` = kebab-case, short (`ci-pipeline`, `role-task-flow`, `molecule-pyramid`).

Scaffold the folder if missing:
```bash
./scripts/scaffold-obsidian-diagrams.sh
```

## Workflow

### 1. Orient with graphify (before drawing)

```bash
graphify query "<what to map>"
graphify path "<A>" "<B>"    # when tracing a chain
graphify explain "<concept>"
```

Use query results for node labels, tiers, and wikilink targets in the companion note.

### 2. Generate diagram (drawio-skill)

- **Architecture / CI / flow** → Architecture or Flowchart preset in drawio-skill
- **Sequence** (e.g. apt install steps) → `scripts/seqlayout.py` or Sequence preset
- **Large graphs (>15 nodes)** → JSON + `scripts/autolayout.py`
- **CI/workflow YAML** → hand-write or Mermaid → CLI convert (draw.io ≥ v30)

**Default output directory:** `graphify-out/obsidian/diagrams/` (not repo root).

### 3. Export into the vault

After user approval (drawio-skill step 7):

```bash
./scripts/obsidian-diagram-export.sh graphify-out/obsidian/diagrams/<slug>.drawio
```

Or manually:
```bash
drawio -x -f png -e -s 2 -o graphify-out/obsidian/diagrams/<slug>.drawio.png \
  graphify-out/obsidian/diagrams/<slug>.drawio
python3 .cursor/skills/drawio-skill/scripts/repair_png.py \
  graphify-out/obsidian/diagrams/<slug>.drawio.png
```

### 4. Write companion Obsidian note

Create or update `graphify-out/obsidian/diagrams/<slug>.md`:

```markdown
---
tags: [diagram, map]
created: YYYY-MM-DD
source: graphify + draw.io
---

# <Title>

![[<slug>.drawio.png]]

## What this shows

<2-4 sentences>

## Related (graphify)

- [[tasks/main.yml]] — entry point
- [[Continuous integration (workflow reference)]] — CI detail

## Source files

- `tasks/main.yml`
- `.github/workflows/unit-tests.yml`
```

Use `[[Note Title]]` wikilinks that match existing vault note filenames (from `graphify query` or filename search in `graphify-out/obsidian/`). Prefer graphify hub notes over inventing new titles.

### 5. Update index

Add a row to `diagrams/00 - Diagram Maps Index.md`:

```markdown
| [[ci-pipeline]] | CI test pyramid and workflow gates | 2026-07-11 |
```

## Suggested maps for this repo

| Slug | Subject | graphify query hint |
|------|---------|---------------------|
| `role-task-flow` | facts → validate → repository → install | `"role deployment chain tasks main"` |
| `ci-pipeline` | lint → policy → unit → integration → AWS | `"CI workflow pipeline gating"` |
| `molecule-pyramid` | unit vs docker vs vagrant vs AWS | `"molecule scenarios test layers"` |
| `repository-lifecycle` | keyring, apt source, suite transitions | `"repository keyring lifecycle"` |
| `galaxy-release` | Release Please → tag → Galaxy import | `"Release Please Galaxy import flow"` |

## Agent rules

1. **Query graphify first** — diagrams should reflect the graph, not guesswork.
2. **All diagram artifacts go under `graphify-out/obsidian/diagrams/`** — never commit `.drawio` to the repo root.
3. **Always create the companion `.md` note** with wikilinks; PNG alone is not enough for Obsidian navigation.
4. **Re-run export** after diagram edits; keep `.drawio` and `.drawio.png` in sync.
5. After changing **source** that the diagram depicts, note "may be stale" in the companion note until redrawn.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Vault folder missing | `./scripts/setup-knowledge-vault.sh` then `./scripts/scaffold-obsidian-diagrams.sh` |
| Snap drawio crashes / no PNG | Install `.deb` from jgraph releases; verify `drawio --version` |
| Wikilink unresolved | Match exact vault filename (graphify export names can include punctuation) |
| Stale graph context | `/graphify .` full rebuild, then redraw |

See also: `docs/knowledge-vault.md` → **Draw.io maps in Obsidian**.
