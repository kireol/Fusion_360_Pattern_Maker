# Git Workflow

## Strategy: Trunk-Based Development (Solo)

PM2 is a single-developer Fusion 360 add-in. The recommended workflow is **trunk-based development** -- the simplest effective strategy for a solo project.

### How it works

1. **`main` is the primary branch.** It should always contain working code that can be loaded into Fusion 360.
2. **Commit directly to `main`** for everyday changes (bug fixes, tweaks, small features).
3. **Use short-lived feature branches** only when experimenting with something risky or large:
   ```
   git checkout -b feat/diamond-shape
   # ... work, commit, test in Fusion ...
   git checkout main
   git merge feat/diamond-shape
   git branch -d feat/diamond-shape
   ```
4. **Tag releases** when you distribute a version or hit a milestone:
   ```
   git tag -a v1.0.0 -m "First public release"
   ```

### Why not something more complex?

- **No Gitflow** -- there is no release pipeline, CI/CD, or team coordination that would benefit from develop/release/hotfix branches.
- **No PR workflow required** -- with a single developer, PRs add ceremony without value. A PR template is included below in case the project moves to GitHub for collaboration or open-source distribution later.
- **No protected branches** -- you are the only committer; self-discipline replaces branch protection.

### When to branch

Create a branch when:
- You are prototyping a new engine (e.g., a "sphere" surface type) and want to preserve a working `main`.
- You are refactoring something fundamental (e.g., splitting `PatternMaker.py` into modules) and want an easy rollback point.

### Tagging convention

Use semantic versioning: `vMAJOR.MINOR.PATCH`

| Bump  | When                                                      |
|-------|-----------------------------------------------------------|
| MAJOR | Breaking change to saved patterns or removed functionality|
| MINOR | New engine, new shape type, or significant new feature    |
| PATCH | Bug fix, UI tweak, spacing adjustment                     |

### Daily workflow

```bash
# 1. Check status
git status

# 2. Stage and commit (see COMMIT_CONVENTION.md)
git add PatternMaker.py
git commit -m "fix: correct stagger offset for odd row counts"

# 3. Occasionally review history
git log --oneline -20

# 4. Tag when distributing
git tag -a v1.1.0 -m "Add slot interlocking support"
```
