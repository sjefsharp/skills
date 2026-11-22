---
name: Skill PR
about: Add, update, or remove a Hermes Agent Skill
title: '<type>(<category>/<skill>): <description>'
labels: ['skill']
assignees: ''
---

## Type

- [ ] `feat` — New skill
- [ ] `fix` — Bug fix in existing skill
- [ ] `docs` — Documentation only
- [ ] `refactor` — Structure/code improvement
- [ ] `chore` — Maintenance (deps, metadata, CI)
- [ ] `remove` — Skill removal (rare — deprecate first)

## Skill Identity

- **Category:** `software-development` / `autonomous-ai-agents` / `creative` /
  `productivity` / `research` / `web` / `frontend` / `media` / `email` /
  `note-taking` / `devops`
- **Skill name:** `<skill-name>` (lowercase, hyphens)
- **Tier:** `bundled` (skills/) or `optional` (optional-skills/)
- **Path:** `skills/<category>/<skill-name>/` or `optional-skills/<category>/<skill-name>/`

## Description

**What does this skill do?** (One sentence, ≤60 chars — matches frontmatter `description`)

**Why is it needed?** (User problem, gap in existing skills)

**Tier rationale:** Why bundled vs optional? (Bundled bar: "user loads this in 5+ sessions/month")

## Changes

- [ ] New `SKILL.md` with valid frontmatter at byte 0
- [ ] Supporting files in `references/`, `templates/`, `scripts/`, `assets/` (if any)
- [ ] Tests in `tests/skills/test_<skill-name>_skill.py`
- [ ] Updated `AGENTS.md` / `CONTRIBUTING.md` / `SECURITY.md` (if cross-cutting)

## Validation Checklist (Local)

Run these before pushing:

```bash
# Frontmatter + structure
python3 scripts/validate-skills.py skills/<category>/<skill-name>/SKILL.md

# Tests (stdlib + pytest + mock only, no network)
pytest tests/skills/test_<skill-name>_skill.py -q

# No secrets
gitleaks detect --source .
```

- [ ] `validate-skills.py` exits 0
- [ ] Tests pass
- [ ] `gitleaks` clean
- [ ] Description ≤ 60 chars, one sentence, period, no marketing words
- [ ] Author: `Real Name (github-handle), Hermes Agent`
- [ ] `platforms:` audited against actual prose/scripts
- [ ] All `related_skills` resolve in-repo
- [ ] No machine-local paths (`/home/...`, `/Users/...`, etc.)
- [ ] Commands use Hermes tools (`terminal`, `read_file`, `write_file`,
      `patch`, `search_files`, `web_search`, `web_extract`, `browser_navigate`,
      `vision_analyze`, `delegate_task`, `cronjob`)
- [ ] Each procedure step has checkable completion criterion

## Testing

| Test                   | Command                                             | Exit Code |
| ---------------------- | --------------------------------------------------- | --------- |
| Frontmatter validation | `python3 scripts/validate-skills.py ...`            | 0         |
| Skill tests            | `pytest tests/skills/test_<skill-name>_skill.py -q` | 0         |
| Secret scan            | `gitleaks detect --source .`                        | 0         |

## Documentation (If Generator Exists)

```bash
python3 scripts/generate-docs.py
git checkout -- $(git diff --name-only | grep -v -E "(SKILL\.md|tests/skills/test_<skill-name>_skill\.py|docs/skills/<skill-name>\.md|website/sidebars\.ts)")
```

- [ ] Diff shows only: your `SKILL.md`, your docs page, 1 catalog row, 1 sidebar entry
- [ ] Sidebar has exactly one hit: `grep -n '<skill-name>' website/sidebars.ts`

## Review Requirements

Reviewers will enforce:

1. **Frontmatter valid at byte 0** — no leading whitespace/BOM
2. **Description HARDLINE** — ≤60 chars, sentence, period, no marketing, quotes if `:`
3. **Author credits human first** — not `Hermes Agent` alone
4. **Platforms audited** — not copied from sibling
5. **Related skills resolve** — in-repo, same tree state
6. **Body structure** — When to Use + actionable + Pitfalls + Verification minimum
7. **Hermes tools** — no raw shell utilities
8. **No local paths** — repo-relative only
9. **Checkable steps** — every numbered step has completion criterion
10. **Tests pass** — stdlib only, deterministic, no network
11. **Docs scope clean** — only your skill's artifacts
12. **No secrets** — gitleaks/trufflehog clean

## Related

- Closes #<issue-number> (if applicable)
- Depends on #<pr-number> (if stacked)

## Screenshots / Demo (Optional)

If the skill produces visible output (diagrams, reports, etc.), attach a screenshot or example output.

---

**By submitting this PR, I confirm:**

- I have read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md)
- This skill follows the [Hermes Agent Skill Authoring Standards](https://hermes-agent.nousresearch.com/docs/skills/authoring)
- No secrets, tokens, or private credentials are included
- All tests pass locally
