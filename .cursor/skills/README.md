# Project skills (Cursor)

Skills in this folder guide agents for **ansible-role-regolith**.

| Skill | Use when |
|-------|----------|
| [git-branch-workflow](git-branch-workflow/SKILL.md) | Branching, PRs, merge flow (`main`) |
| [readme-maintenance](readme-maintenance/SKILL.md) | Code/CI changes that need README or docs updates |
| [ship-change](ship-change/SKILL.md) | User asks to commit, push, open issue/PR |
| [drawio-skill](drawio-skill/SKILL.md) | Any draw.io diagram generation or export |
| [obsidian-diagrams](obsidian-diagrams/SKILL.md) | Map role/CI architecture into the graphify Obsidian vault |

**Obsidian vault:** `graphify-out/obsidian/` (local, gitignored). Bootstrap with `./scripts/setup-knowledge-vault.sh`.

**draw.io CLI:** [jgraph desktop releases](https://github.com/jgraph/drawio-desktop/releases) — prefer `.deb`/`.rpm` over snap on Linux.
