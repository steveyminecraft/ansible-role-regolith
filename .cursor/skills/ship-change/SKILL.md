---
name: ship-change
description: >-
  Branch, commit, GitHub issue (ticket), and PR for steveyminecraft/ansible-role-regolith.
  Use when the user asks to ship, commit, open a ticket, create a PR, or
  "branch commit pr ticket".
---

# Ship a change (branch → ticket → commit → PR)

Follow **git-branch-workflow** and **readme-maintenance** project skills.

## When the user asks to ship

Run only when explicitly requested (commit/push/PR). Never force-push `main`.

### 1. Refresh `main`

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
```

If fast-forward fails, stop and ask the user.

### 2. Topic branch

```bash
git checkout -b <type>/<short-kebab-description>
```

Types: `feature/`, `fix/`, `bugfix/`, `chore/`, `docs/`.

### 3. GitHub issue (ticket)

Create before or with the PR so the PR can link it:

```bash
gh issue create \
  --title "<concise title>" \
  --body "$(cat <<'EOF'
## Problem / goal

<why this change exists>

## Proposed solution

- <bullet>

## Acceptance criteria

- [ ] <checkable item>

EOF
)"
```

Note the issue number (e.g. `#42`).

### 4. Commit

```bash
git status
git diff
git log -3 --oneline
```

Stage only relevant files. Never commit secrets (`.env`, vault blobs, `graphify-out/`).

Conventional commit subject (`feat:`, `fix:`, `docs:`, `chore:`, etc.). Body explains **why**. PR titles must follow Conventional Commits—Release Please reads merged squash commits for version bumps and `CHANGELOG.md`.

```bash
git add <paths>
git commit -m "$(cat <<'EOF'
<type>: <summary>

<optional body — user-visible impact, not file list>

Fixes #<issue>
EOF
)"
```

Use `Fixes #N` or `Closes #N` when the issue should close on merge.

### 5. Push and PR

```bash
git push -u origin HEAD
```

```bash
gh pr create \
  --base main \
  --title "<type>: <summary>" \
  --body "$(cat <<'EOF'
Fixes #<issue>

## Summary

- <1-3 bullets — user-visible or explicit internal-only>

## Release notes

- Proposed release note sentence:
  - `<one sentence or N/A for internal-only>`
- Changelog type:
  - [ ] `feat`
  - [ ] `fix`
  - [ ] `perf`
  - [ ] `refactor`
  - [x] non-user-facing (`docs` / `ci` / `chore` / `test` / `build`)

## Validation

- [ ] pre-commit / ansible-lint / yamllint (or N/A)
- [ ] `python scripts/validate-role-defaults.py` (or N/A)
- [ ] `python -m unittest discover -s tests/unit -p 'test_*.py'` (or N/A)
- [ ] Molecule unit/integration when behavior changes (or N/A)
- [ ] README / docs updated when needed

## Scope and risk

- Risk level: [x] low  [ ] medium  [ ] high
- Rollback plan: revert PR merge commit

EOF
)"
```

Return the **issue URL** and **PR URL** to the user.

### 6. After merge (later)

Per git-branch-workflow: delete merged topic branch locally and on origin.

Prefer **squash merge** into `main` so Release Please gets one clean Conventional Commit (see `CONTRIBUTING.md`).

## Checklist

```
- [ ] main fast-forwarded from origin
- [ ] topic branch from main
- [ ] GitHub issue created
- [ ] conventional commit; no secrets in diff
- [ ] README / docs updated if setup/behavior docs changed
- [ ] PR targets main; links issue
- [ ] PR body includes test plan and release-note intent (see CONTRIBUTING.md)
```

## Repo-specific notes

- PRs merge to **`main`** only.
- Release Please opens release PRs from `release-please--branches--main`; Galaxy import runs on the semver tag after that PR merges—not on ordinary feature PRs.
- PR title must match Conventional Commit format (used for release notes).
- `graphify-out/` is gitignored — never add it.
- No `.github/pull_request_template.md`; follow `CONTRIBUTING.md` and the PR body structure above.
