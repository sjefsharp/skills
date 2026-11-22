# skills

**Canonical source repository for portable Agent Skills** maintained by [sjefsharp](https://github.com/sjefsharp).

This repository follows portable Skill Authoring Standards and ships skills that work across compatible agent runtimes.

## Quick Start

```bash
# Clone locally
git clone https://github.com/sjefsharp/skills.git
cd skills

# Install a skill into your agent
# (Use your agent's skill installation mechanism)
```

## Repository Structure

```
skills/
├── skills/                    # Bundled skills (shipped by default)
│   ├── software-development/
│   ├── autonomous-ai-agents/
│   ├── creative/
│   ├── productivity/
│   ├── research/
│   ├── web/
│   ├── frontend/
│   ├── media/
│   ├── email/
│   ├── note-taking/
│   └── devops/
├── optional-skills/           # Optional skills (install on demand)
├── scripts/                   # Repository tooling (validation, docs gen, release)
├── references/                # Cross-cutting reference documentation
├── assets/                    # Shared assets (logos, schemas, etc.)
├── .github/                   # GitHub workflows, templates, CODEOWNERS
├── AGENTS.md                  # Repository instructions for AI agents
├── CONTRIBUTING.md            # Contribution guide
├── SECURITY.md                # Security policy
├── LICENSE                    # MIT License
├── CODEOWNERS                 # Code ownership map
└── .gitignore
```

## Skill Categories

| Category               | Description                                                     |
| ---------------------- | --------------------------------------------------------------- |
| `software-development` | Git, GitHub, code review, debugging, TDD, code inspection       |
| `autonomous-ai-agents` | Claude Code, Codex, OpenCode, computer-use                      |
| `creative`             | Architecture diagrams, infographics, design, video, music       |
| `productivity`         | Airtable, Notion, Google Workspace, docs, PDF, Office           |
| `research`             | arXiv, citations, LLM wiki, RSS, competitor monitoring          |
| `web`                  | Accessibility, core web vitals, performance, SEO, quality audit |
| `frontend`             | ADHD-friendly reading, modern web guidance                      |
| `media`                | GIF search, audio analysis, YouTube content                     |
| `email`                | Inbox triage, Himalaya CLI                                      |
| `note-taking`          | Obsidian                                                        |
| `devops`               | Diagnose crash, blocked page recovery                           |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Skill authoring standards (frontmatter, structure, validation)
- Tier decision: bundled vs optional
- Testing and documentation requirements
- PR workflow and review process

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and supply-chain policies.

## License

[MIT](LICENSE) — Copyright (c) 2026 Sjef Sharp (sjefsharp)
