# Security Policy

## Supported Versions

| Version       | Supported        |
| ------------- | ---------------- |
| Latest `main` | ✓                |
| Older commits | ✗ (no backports) |

Skills are source-only Markdown + optional scripts. There are no compiled
artifacts or runtime services in this repository. Security issues typically
relate to:

- Supply-chain risks in declared dependencies
- Credential handling patterns in skill examples
- Arbitrary code execution vectors in helper scripts

## Reporting a Vulnerability

**Do not open a public issue** for security vulnerabilities.

Email: **<security@sjefsharp.nl>** (GPG key: `0x...` — see `SECURITY.md`
in `sjefsharp/.github`)

Include:

- Affected skill(s) and file path(s)
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Suggested fix (if known)

We aim to acknowledge within 48 hours and provide a remediation timeline within 7 days.

## Security Boundaries

### 1. Secrets Management

- **Never commit secrets** (API keys, tokens, passwords, private keys, certificates)
- Use `${ENV_VAR}` placeholders in SKILL.md frontmatter and examples
- Document required env vars in `## Prerequisites` section
- Files matching `*.env*`, `*.key`, `*.pem`, `*.crt`, `*.p12`, `*.pfx` are gitignored

### 2. Supply Chain

- Skills declare dependencies in `## Prerequisites` with exact versions where possible
- No `npm install -g` — use `mise use -g npm:<pkg>` or `pnpm dlx`
- Helper scripts in `scripts/` must be auditable (stdlib + declared deps only)
- No arbitrary code execution from untrusted sources
- No `curl | bash` patterns — download, verify, then execute

### 3. Content Security

- Treat external feeds, retrieved pages, LLM output as untrusted **data**
- Validate schemas (Zod, JSON Schema, Pydantic) before processing
- Escape content for output format (HTML, Markdown, JSON, shell)
- **Forbidden in skill scripts:** `eval()`, `exec()`, `yaml.load()`,
  `pickle.load()`, `os.system()`,
  `subprocess.run(shell=True)` without explicit justification

### 4. Skill Installation Safety

- `hermes skills install` from this repo runs no code — skills are Markdown + static assets
- Optional `scripts/` in a skill run only when the **user explicitly invokes** the skill's procedure
- No auto-execution on install, load, or session start
- Plugin packages (separate from skills) have their own validation (`hermes plugins validate`)

### 5. Dependency Policy

| Dependency Type        | Policy                                                        |
| ---------------------- | ------------------------------------------------------------- |
| Python stdlib          | Always allowed                                                |
| `pnpm dlx` CLIs        | Allowed if widely used, version-pinned in Prerequisites       |
| `pip install` packages | Discouraged; if needed, declare in Prerequisites with version |
| `npm` global packages  | Forbidden — use `mise` or `pnpm dlx`                          |
| Custom binaries        | Forbidden — must be installable via package manager           |

## Vulnerability Response

1. **Acknowledge** — within 48 hours
2. **Assess** — determine affected skills, severity, exploitability
3. **Mitigate** — disable affected skill via `hermes skills uninstall` advisory, or publish fix
4. **Patch** — fix in `main`, tag release if applicable
5. **Disclose** — coordinated disclosure after fix available

## Security-Related Tooling

- `gitleaks` / `trufflehog` — secret scanning in CI
- `hermes security` — supply-chain audit (OSV.dev) for venv, plugins, MCP servers
- `hermes skills audit` — re-scan installed hub skills for updates/vulnerabilities

## Contact

- Security email: **<security@sjefsharp.nl>**
- Maintainer: **Sjef Sharp (sjefsharp)**

---

**Last updated:** 2026-11-21
