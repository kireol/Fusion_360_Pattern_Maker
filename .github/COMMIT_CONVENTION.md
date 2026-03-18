# Commit Convention

This project uses a lightweight conventional commit format suited to a solo-developer Fusion 360 add-in.

## Format

```
<type>: <short description>

[optional body]
```

## Types

| Type       | When to use                                        |
|------------|----------------------------------------------------|
| `feat`     | New feature or engine capability                   |
| `fix`      | Bug fix in pattern generation or UI logic          |
| `tweak`    | Small adjustment to defaults, spacing, tolerances  |
| `refactor` | Code restructuring without behavior change         |
| `ui`       | Changes to command dialogs, icons, or menu layout  |
| `docs`     | Documentation only                                 |
| `chore`    | Maintenance: config, manifest, build, dependencies |

## Examples

```
feat: add diamond shape to wall engine
fix: cylinder pattern offset when density is odd
tweak: increase default margin to 0.7mm
ui: add tooltip image for multi-face command
refactor: extract stagger offset calculation into helper
docs: document cylinder engine density formula
chore: bump manifest version to 1.2.0
```

## Guidelines

- Keep the subject line under 72 characters.
- Use imperative mood ("add", "fix", "change" -- not "added", "fixed", "changed").
- The body is optional. Use it when the "why" is not obvious from the subject.
- No need for scope tags (e.g., `feat(wall):`) -- the project is small enough that the description makes the scope clear.
