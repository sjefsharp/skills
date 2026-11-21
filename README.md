# hermes-skills

**Canonical source repository for portable Agent Skills and compatible Agent Plugins** maintained by [sjefsharp](https://github.com/sjefsharp).

This repository follows the [Hermes Agent Skill Authoring Standards](https://hermes-agent.nousresearch.com/docs/skills/authoring) and ships skills that work across Hermes Agent surfaces (CLI, TUI, Desktop, Web, ACP) and compatible runtimes.

## Quick Start

```bash
# Clone locally
git clone https://github.com/sjefsharp/hermes-skills.git
cd hermes-skills

# Install a skill into your Hermes profile
hermes skills install official/software-development/github

# Or install from local source (development)
hermes skills install local ./skills/software-development/github
```

## Repository Structure

```
hermes-skills/
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

| Category | Description |
|----------|-------------|
| `software-development` | Git, GitHub, code review, debugging, TDD, code inspection |
| `autonomous-ai-agents` | Hermes, Claude Code, Codex, OpenCode, computer-use |
| `creative` | Architecture diagrams, infographics, design, video, music |
| `productivity` | Airtable, Notion, Google Workspace, docs, PDF, Office |
| `research` | arXiv, citations, LLM wiki, RSS, competitor monitoring |
| `web` | Accessibility, core web vitals, performance, SEO, quality audit |
| `frontend` | ADHD-friendly reading, modern web guidance |
| `media` | GIF search, audio analysis, YouTube content |
| `email` | Inbox triage, Himalaya CLI |
| `note-taking` | Obsidian |
| `devops` | Diagnose crash, blocked page recovery |

## Installing Skills

### From Official Registry (recommended)

```bash
# List available official skills
hermes skills browse

# Install a bundled skill
hermes skills install official/software-development/github

# Install an optional skill
hermes skills install official/creative/architecture-diagram
```

### From Local Source (development)

```bash
# Install from cloned repo
hermes skills install local ./skills/software-development/github

# Or add the repo as a skill source
hermes skills tap add local-hermes-skills /path/to/hermes-skills
hermes skills install local-hermes-skills/software-development/github
```

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

## Related

- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- [Hermes Agent Skill Authoring Guide](https://hermes-agent.nousresearch.com/docs/skills/authoring)
- [Hermes Agent Repository](https://github.com/NousResearch/hermes-agent)