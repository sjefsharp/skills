# Contributing to hermes-skills

Thank you for contributing! This guide covers the skill authoring workflow, standards, and review process.

## Table of Contents

- [Quick Start](#quick-start)
- [Skill Authoring Standards](#skill-authoring-standards)
- [Tier Decision: Bundled vs Optional](#tier-decision-bundled-vs-optional)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/sjefsharp/hermes-skills.git
cd hermes-skills

# 2. Create a feature branch
git checkout -b feat/software-development/my-new-skill

# 3. Draft your skill
mkdir -p skills/software-development/my-new-skill
# Edit skills/software-development/my-new-skill/SKILL.md

# 4. Validate locally
python3 scripts/validate-skills.py skills/software-development/my-new-skill/SKILL.md

# 5. Add tests
mkdir -p tests/skills
# Edit tests/skills/test_my_new_skill_skill.py

# 6. Run tests
pytest tests/skills/test_my_new_skill_skill.py -q

# 7. Commit and push
git add skills/software-development/my-new-skill/ tests/skills/test_my_new_skill_skill.py
git commit -m "feat(software-development/my-new-skill): Add my new skill"
git push origin feat/software-development/my-new-skill

# 8. Open PR
gh pr create --title "feat(software-development/my-new-skill): Add my new skill" --body "..."

```

## Skill Authoring Standards

### Frontmatter (Required)

Every `SKILL.md` must start with valid YAML frontmatter at **byte 0**:

```yaml
---
name: my-skill-name              # lowercase, hyphens, ≤64 chars
description: Concise capability statement, under sixty chars.
version: 0.1.0                   # semver; new skills start at 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]  # audit from actual prose/scripts
metadata:
  hermes:
    tags: [Short, Descriptive, Tags]
    related_skills: [existing-in-repo-skill]
---
```

### Description Rules (HARDLINE)

- **≤ 60 characters** (enforced in review)
- One sentence, ends with period
- Capability, not implementation
- No marketing words ("powerful", "comprehensive", "seamless", "advanced")
- If contains `:`, wrap in double quotes

### Author Rules

- Credit **human first**: `Real Name (github-handle), Hermes Agent`
- Never `author: Hermes Agent` alone

### Platform Gating

Set `platforms:` from what the skill's prose/scripts **actually invoke**:

| Uses… | `platforms:` |
|-------|--------------|
| Hermes tools + stdlib Python + cross-platform CLIs | `[linux, macos, windows]` |
| bash pipelines, `grep`/`awk`/`sed`, heredocs | `[linux, macos]` |
| `osascript`, `defaults`, `pmset` | `[macos]` |
| `apt`/`systemctl`/`/proc` | `[linux]` |

Default: fix cross-platform first; gate narrower only when genuinely platform-bound.

### Body Structure

```
# <Skill> Skill
2-3 sentence intro: what it does, what it doesn't, dependency stance.

## When to Use          — bulleted triggers + "Don't use for:" counter-triggers
## Prerequisites        — exact env vars, installs, API key sourcing
## How to Run           — canonical invocation through Hermes tools
## Quick Reference      — flat command list, no narration
## Procedure            — numbered steps, each with checkable completion criterion
## Pitfalls             — known limits, things that look broken but aren't
## Verification         — how to prove the skill worked
```

Minimum: When to Use + actionable body + Pitfalls + Verification.

### Reference Hermes Tools

Use backticks for Hermes tools: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `web_search`, `web_extract`, `browser_navigate`, `vision_analyze`, `delegate_task`, `cronjob`. Do NOT name shell utilities the agent already wraps.

### No Machine-Local Paths

Repo-relative only: `skills/...`, `scripts/...`, `references/...`. No `/home/user/...`.

## Tier Decision: Bundled vs Optional

| Tier | Criteria | Location |
|------|----------|----------|
| **Bundled** | Daily-driver, broadly useful, low footprint. "User loads this in 5+ sessions/month." | `skills/<category>/<skill>/` |
| **Optional** | Niche, vertical-specific, heavy, or recurring-job skills | `optional-skills/<category>/<skill>/` |

**When in doubt: optional.** Promoting later is easy; demoting is churn.

## Development Workflow

### 1. Survey Peers

```bash
ls skills/<category>/
```

Read 2-3 peer `SKILL.md` files to match tone and structure. **Extend rather than create narrow siblings.**

### 2. Decide Tier & Category

Pick category by what the tool **IS**, not what it feels like. Confirm existing categories:

```bash
find skills -maxdepth 1 -mindepth 1 -type d | sort
find optional-skills -maxdepth 1 -mindepth 1 -type d | sort
```

### 3. Draft the Skill

Create directory and `SKILL.md`:

```bash
mkdir -p skills/<category>/<skill-name>
# Edit SKILL.md following the standards above
```

Supporting files go in subdirectories:
- `references/*.md` — detailed docs
- `templates/*.md` — template files
- `scripts/*.py` — helper scripts (pnpm dlx compatible)
- `assets/` — images, schemas, data

### 4. Validate Locally

```bash
python3 scripts/validate-skills.py skills/<category>/<skill-name>/SKILL.md
```

Checks: frontmatter at byte 0, name/description present, description ≤60 chars + period, platforms present, related_skills resolve in-repo, content ≤100k chars.

### 5. Add Tests

```bash
mkdir -p tests/skills
# Create tests/skills/test_<skill-name>_skill.py
```

Requirements:
- stdlib + pytest + unittest.mock only
- No live network calls
- Test frontmatter parsing, structure, key behaviors
- Run via: `pytest tests/skills/test_<skill-name>_skill.py -q`

### 6. Documentation (if generator exists)

```bash
python3 scripts/generate-docs.py
```

**Scope discipline:** Final diff must show only:
- Your `SKILL.md`
- Your one per-skill docs page
- One-line catalog row
- One-line `website/sidebars.ts` insertion (verify: exactly one hit for your slug)

## Testing

### Local Test Run

```bash
# Single skill
pytest tests/skills/test_<skill>_skill.py -q

# All skills
pytest tests/skills/ -q

# With coverage (optional)
pytest tests/skills/ --cov=skills --cov-report=term-missing
```

### Test Requirements

- No network dependencies (mock everything)
- Deterministic — same result every run
- Fast — < 5 seconds per skill test file
- Test the skill's contract, not implementation details

## Documentation

If the repo has a docs generator:
1. Run `python3 scripts/generate-docs.py`
2. `git checkout --` everything that isn't yours
3. Final diff = your SKILL.md + your docs page + 1 catalog row + 1 sidebar entry
4. Verify sidebar: `grep -n '<your-slug>' website/sidebars.ts` → exactly one hit

## Pull Request Process

### Before Opening PR

- [ ] Skill validates locally (`scripts/validate-skills.py`)
- [ ] Tests pass (`pytest tests/skills/test_<skill>_skill.py -q`)
- [ ] No secrets in any file (`gitleaks detect` clean)
- [ ] Description ≤ 60 chars, ends with period
- [ ] All `related_skills` entries resolve in-repo
- [ ] `platforms:` audited against actual prose/scripts
- [ ] No machine-local paths anywhere

### PR Requirements

- **Title:** `feat(<category>/<skill>): <description>` or `fix(<category>/<skill>): <description>`
- **Branch:** `feat/<category>/<skill-name>` or `fix/<category>/<skill-name>`
- **Base:** `main`
- **Description:** What the skill does, why it's needed, tier decision rationale
- **Labels:** `skill`, `bundled` or `optional`, `<category>`

### Review Checklist (Reviewers Enforce)

- [ ] Frontmatter valid at byte 0
- [ ] Description ≤ 60 chars, one sentence, period, no marketing words
- [ ] Author credits human first
- [ ] `platforms:` audited (not copied from sibling)
- [ ] Every `related_skills` resolves in-repo
- [ ] Body follows modern section order
- [ ] Commands framed through Hermes tools
- [ ] No machine-local paths
- [ ] Each step has checkable completion criterion
- [ ] Tests pass (stdlib only, no network)
- [ ] Docs scope clean (only your skill's artifacts)
- [ ] No secrets
- [ ] License MIT (or compatible)

### After Approval

- Squash merge (enforced by GitHub ruleset)
- Branch deleted automatically
- Skill available in next Hermes release / `hermes skills check` + `update`

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code.

## Questions?

- Check existing skills for patterns
- Read [Hermes Agent Skill Authoring Docs](https://hermes-agent.nousresearch.com/docs/skills/authoring)
- Open a discussion or issue for clarification