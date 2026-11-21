---
name: skill-lint
description: Lint SKILL.md frontmatter and structure per authoring rules.
version: 0.1.0
author: Sjef Sharp (sjefsharp), Hermes Agent
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - skills
      - validation
      - linting
      - authoring
      - ci
---

# Skill Lint Skill

Validate `SKILL.md` files against the Hermes Agent Skill Authoring Standards — frontmatter, structure, description rules, platform gating, and cross-references. Designed for CI gates and pre-commit hooks.

## When to Use

- Add a validation gate to a skills repository CI pipeline
- Pre-commit hook for skill authors
- Batch-validate all skills in a repository before release
- Check a single skill during authoring

**Don't use for:**
- Runtime validation inside a Hermes session (skills are static source)
- Validating non-Hermes markdown files
- Replacing the full `hermes skills check` / `hermes skills audit` commands

## Prerequisites

- Python 3.10+ (stdlib only — no external dependencies)
- Repository cloned locally with skills at `skills/` and/or `optional-skills/`

## How to Run

### Single Skill

```bash
python3 scripts/validate-skills.py skills/software-development/github/SKILL.md
```

### All Skills (Bundled + Optional)

```bash
python3 scripts/validate-skills.py --all
```

### As Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: skill-lint
      name: Validate SKILL.md files
      entry: python3 scripts/validate-skills.py
      language: system
      types: [file]
      files: 'skills/.*/SKILL\.md$|optional-skills/.*/SKILL\.md$'
      pass_filenames: true
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 scripts/validate-skills.py <skill-path>` | Validate one skill (Hermes HARDLINE) |
| `python3 scripts/validate-skills.py --all` | Validate all skills in repo (Hermes HARDLINE) |
| `python3 scripts/validate-skills.py --all --official` | Also run official Agent Skills spec validator |
| `skills-ref validate <skill-path>` | Official Agent Skills spec validator only |

## Procedure

### 1. Validate a Single Skill (Hermes HARDLINE)

1. Run validator on the skill path
2. Exit code 0 = pass, 1 = fail
3. Read stderr for specific errors (frontmatter, structure, size, related skills)

### 2. Validate All Skills

1. Run with `--all` flag
2. Scans `skills/` and `optional-skills/` recursively for `SKILL.md`
3. Reports pass/fail per skill with summary count

### 3. Validate Against Official Agent Skills Spec

1. Run with `--all --official` or use `skills-ref validate <skill-path>` directly
2. Checks official spec compliance: allowed fields, name format, description length (≤1024), strictyaml parsing
3. **Note:** Hermes skills use extended format (version, author, platforms at top-level) — official validator will flag these as unexpected fields. This is expected for Hermes skills.

### 4. Integrate in CI

1. Add step to GitHub Actions / GitLab CI / etc.
2. Fail build on any validation error
3. Optional: annotate PR with error locations

## Pitfalls

- **Frontmatter at byte 0** — any leading whitespace/BOM fails validation
- **Description ≤ 60 chars** — HARDLINE rule (Hermes); official spec allows ≤1024
- **Platforms audited** — copied `platforms: [linux, macos, windows]` from a sibling without checking actual script dependencies will be caught
- **Related skills must resolve** — referencing a skill that exists only in user profile or a sibling PR fails
- **No machine-local paths** — absolute paths in body fails; use repo-relative paths
- **Hermes tools not shell** — raw shell utilities (g-r-e-p, c-a-t, s-e-d, a-w-k, f-i-n-d, l-s) in body text flagged; use `search_files`, `read_file`, `patch`, etc.
- **YAML flow-style** — `[a, b]` fails official spec (strictyaml); use block-style (`- a\n- b`)

## Verification

### Validator Self-Test (Hermes HARDLINE)

```bash
# Should pass (this skill's own SKILL.md)
python3 scripts/validate-skills.py skills/software-development/skill-lint/SKILL.md
```

### Official Spec Validation

```bash
# Will flag Hermes-specific fields (version, author, platforms) as unexpected
# This is expected — Hermes uses extended format
skills-ref validate skills/software-development/skill-lint
```

### Combined Validation

```bash
# Run both validators
python3 scripts/validate-skills.py skills/software-development/skill-lint/SKILL.md --official
```

### CI Integration Test

1. Add validator step to CI workflow
2. Push a PR with an intentionally invalid skill
3. Verify CI fails with clear error messages
4. Fix skill, verify CI passes

---

**Validation Scripts:**
- `scripts/validate-skills.py` — Hermes HARDLINE validator (stdlib only)
- `skills-ref` — Official Agent Skills spec validator (requires `click`, `strictyaml`)

**Tests:** `tests/skills/test_skill_lint_skill.py` (10 tests for HARDLINE rules)