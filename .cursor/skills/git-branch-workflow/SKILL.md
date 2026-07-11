---
name: git-branch-workflow
description: >-
  Defines steveyminecraft/ansible-role-regolith Git branch flow:
  topic branch → main. Use when creating branches, merging, opening
  PRs, or any git workflow in this repository.
---

# ansible-role-regolith Git branch workflow

## Branch flow

```
<topic-branch>  →  main
```

- **Topic branches** (`feature/*`, `fix/*`, `bugfix/*`, `chore/*`, etc.): all implementation work happens here.
- **`main`**: integration + release branch (Release Please opens release PRs from here).

Do **not** do long-lived development directly on `main` when the change is non-trivial.

## Agent rules

1. **Start new work only after refreshing local `main` from remote `main`**:
   ```bash
   git fetch origin
   git checkout main
   git pull --ff-only origin main
   git checkout -b feature/short-description   # or fix/, bugfix/, chore/, docs/
   ```

2. **Merge direction** (one way):
   - Topic branch → `main` (PR preferred)
   - Never merge `main` into a topic branch for “latest code” unless resolving a specific conflict—prefer rebasing the topic branch onto `main`.

3. **Before starting work**, always verify local `main` is current:
   ```bash
   git fetch origin
   git checkout main
   git pull --ff-only origin main
   git status -sb
   ```
   If fast-forward is not possible, stop and ask the user how to reconcile (do not force-push).

4. **After `main` moves** (release merge, hotfix), rebase active topic branches onto `main` as needed.

5. **PR targets**:
   - Topic branch → **`main`**
   - Release Please PRs (`release-please--branches--main`) → **`main`** (do not retarget)

6. **After a topic branch is merged**, delete it locally and remotely to keep repo hygiene:
   ```bash
   git fetch origin --prune
   git checkout main
   git pull --ff-only origin main
   git branch -d feature/short-description
   git push origin --delete feature/short-description
   git fetch origin --prune
   ```
   Use `git branch -d` for merged branches. Use `git branch -D` only after confirming the branch is merged or intentionally abandoned.

7. **Commits**: only when the user asks. Do not push unless asked.

8. **README / docs**: keep root `README.md` and relevant `docs/` files current in the same change set. See **readme-maintenance** project skill.

## CI context

GitHub Actions run on **every pull request** and on **push to `main`**. Key workflows:

| Workflow | Purpose |
|----------|---------|
| `.github/workflows/unit-tests.yml` | Lint, policy, Ansible unit matrix, Galaxy validate |
| `.github/workflows/trivy.yml` | Security scan (gates integration) |
| `.github/workflows/integration-tests.yml` | Container integration (after unit + Trivy) |
| `.github/workflows/rc-aws-remote-tests.yml` | AWS EC2 gate on feature PRs (after integration) |

Release Please PRs skip AWS; Galaxy import runs on the semver tag after the release PR merges. See root `README.md` → Continuous integration.

## Quick checklist

```
- [ ] local main is fast-forwarded to origin/main
- [ ] branch created from main
- [ ] changes merged to main via PR
- [ ] merged topic branch deleted locally
- [ ] merged topic branch deleted from origin
- [ ] README / docs updated (see readme-maintenance skill)
```
