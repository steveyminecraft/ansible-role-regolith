# Knowledge vault (local graphify)

This role can be mapped with [graphify](https://github.com/safishamsi/graphify) into a **local** knowledge graph. Outputs stay on your machine under `graphify-out/` (gitignored) so nothing is pushed to GitHub.

Agents and contributors use the graph for architecture questions; humans can browse the Obsidian vault or `graph.html`.

## Quick start

```bash
# From repo root — installs graphify if needed, builds code graph, exports HTML/Obsidian
./scripts/setup-knowledge-vault.sh

# Optional: rebuild code graph after every commit (local only)
./scripts/install-graphify-hook.sh
# Or: ./scripts/setup-knowledge-vault.sh --hook
```

Open the interactive map: `graphify-out/graph.html`  
Open Obsidian vault: `graphify-out/obsidian/`

## What gets generated (all local)

| Path | Purpose |
|------|---------|
| `graphify-out/graph.json` | Query target for agents (`graphify query`, MCP) |
| `graphify-out/graph.html` | Browser visualization |
| `graphify-out/GRAPH_REPORT.md` | God nodes, communities, surprising connections |
| `graphify-out/KNOWLEDGE_VAULT.md` | Local entry point (copied from this doc + build stats) |
| `graphify-out/obsidian/` | Wikilinked notes + `graph.canvas` |
| `graphify-out/obsidian/diagrams/` | Draw.io maps (`.drawio`, PNG embeds, companion notes) — see below |

## Bootstrap modes

### Fast (default) — no API key

`./scripts/setup-knowledge-vault.sh`

Runs `graphify update .`: AST extraction for Python/shell **code** only. Good for scripts and unit tests. Ansible YAML and markdown are not fully covered until a full build.

### Full — docs, role tasks, molecule, Obsidian

`./scripts/setup-knowledge-vault.sh --full`

Prints instructions to run **`/graphify .`** in Cursor (or any graphify-capable agent). That pipeline extracts the full corpus (role tasks, molecule scenarios, CI workflows, docs) and produces the rich Obsidian vault.

Optional: set `GEMINI_API_KEY` or `GOOGLE_API_KEY` for automated semantic extraction instead of agent subagents.

## Agent workflow

Cursor rule `.cursor/rules/graphify-knowledge-base.mdc` tells agents to:

1. Check for `graphify-out/graph.json`
2. Run `./scripts/setup-knowledge-vault.sh` if missing
3. Use `graphify query` before `Grep`/`Read` for architecture questions
4. Run `graphify update .` after code edits

Example queries:

```bash
graphify query "How does repository keyring lifecycle work?"
graphify path "tasks/main.yml" "molecule/default/verify.yml"
graphify explain "regolith_repository_component"
```

## Refresh after changes

| Change type | Command |
|-------------|---------|
| Python/shell | `graphify update .` (automatic with post-commit hook) |
| Role tasks, molecule, docs | `/graphify .` or full rebuild |
| After full rebuild | `python3 scripts/bridge-role-graph.py` then `python3 scripts/dedupe-graphify-graph.py --prune-isolated` |
| Re-export Obsidian | `graphify export obsidian` |
| Re-export HTML | `graphify export html` |

### Post-commit hook

```bash
./scripts/install-graphify-hook.sh
```

Installs graphify's post-commit hook locally. After each commit, changed Python/shell
files are re-extracted into `graphify-out/graph.json`. YAML and doc changes still
need a full `/graphify .` rebuild.

Check status: `graphify hook status`

### Reduce graph noise

Duplicate concepts (e.g. the same playbook referenced in docs vs molecule) can appear after a full corpus build. Run a dedupe pass:

```bash
python3 scripts/dedupe-graphify-graph.py --dry-run          # preview
python3 scripts/dedupe-graphify-graph.py                    # merge duplicates
python3 scripts/dedupe-graphify-graph.py --prune-isolated  # also drop isolated nodes
```

Prefer a periodic full rebuild (`/graphify .`) then dedupe, rather than incremental
AST-only updates when exploring role tasks and molecule scenarios.

## Cursor MCP (optional)

Agents can query the graph via MCP instead of shelling out to `graphify query`.

1. Bootstrap the vault: `./scripts/setup-knowledge-vault.sh`
2. Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` (gitignored)
3. Replace `GRAPHIFY_PYTHON` and `GRAPH_PATH` with values from your machine:

```bash
cat graphify-out/.graphify_python   # interpreter path
realpath graphify-out/graph.json    # absolute graph path
```

4. Reload Cursor MCP servers

Tools exposed: `query_graph`, `get_node`, `get_neighbors`, `get_community`,
`god_nodes`, `graph_stats`, `shortest_path`.

## Security

- `graphify-out/` is **not committed** — AWS inventory templates and local `.env` stay out of any graph artifact on GitHub.
- Graphify skips `.env`, keys, and `secrets/` paths during detection.
- Before sharing `graphify-out/` manually, scan for accidental secrets.

## Draw.io maps in Obsidian

Use the **drawio-skill** and **obsidian-diagrams** project skills in Cursor to create visual maps that live inside the vault (local only).

```bash
./scripts/setup-knowledge-vault.sh          # vault + graph
./scripts/scaffold-obsidian-diagrams.sh     # diagrams/ folder + index note
```

**Workflow:**

1. `graphify query "<topic>"` — gather nodes and relationships before drawing.
2. Agent generates `graphify-out/obsidian/diagrams/<slug>.drawio` (drawio-skill).
3. Export PNG for Obsidian embed:
   ```bash
   ./scripts/obsidian-diagram-export.sh graphify-out/obsidian/diagrams/<slug>.drawio
   ```
4. Companion note `<slug>.md` wikilinks graphify notes and embeds `![[<slug>.drawio.png]]`.
5. Index: `diagrams/00 - Diagram Maps Index.md`.

Open Obsidian on **`graphify-out/obsidian/`** (vault root). Optional: install the [Draw.io Integration](https://github.com/zapthedingbat/drawio-obsidian) plugin to edit `.drawio` files in-app.

**draw.io CLI:** install the [jgraph desktop release](https://github.com/jgraph/drawio-desktop/releases) (`.deb`/`.rpm`). Avoid snap on Linux — AppArmor can break headless export.

Example prompts in Cursor:

- "Map the CI pipeline in the Obsidian vault"
- "Diagram role task flow from facts to install with wikilinks"
- "Draw the molecule test pyramid in draw.io under graphify-out/obsidian/diagrams"

## Role deployment chain (reference)

```
facts → validate → repository_facts → repository → repository_keyring → install
```

Key surfaces: `tasks/main.yml`, `defaults/main.yml`, `molecule/default/verify.yml`, `tests/remote/playbooks/bootstrap-regolith.yml`.

**Test chain:** `molecule/default/converge.yml` applies the role via `tasks/main.yml`; `molecule/default/verify.yml` asserts the installed packages from `defaults/main.yml` (`regolith_packages`). Docker integration scenarios reuse the same converge/verify playbooks through `molecule/common/converge.yml`.

**Graph scope:** `.graphifyignore` excludes `.cursor/skills/drawio-skill/` so the vault emphasizes Ansible role, Molecule, and CI nodes. Rebuild with `/graphify .` then `python3 scripts/bridge-role-graph.py` and `python3 scripts/dedupe-graphify-graph.py --prune-isolated`.
