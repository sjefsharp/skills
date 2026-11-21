#!/usr/bin/env python3
"""
Skill Frontmatter & Structure Validator

Validates a SKILL.md file against the Hermes Agent Skill Authoring Standards.
Run from repo root: python3 scripts/validate-skills.py skills/<category>/<skill>/SKILL.md
"""

import sys
import re
import yaml
from pathlib import Path
from typing import List, Tuple

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 60
MAX_CONTENT_CHARS = 100_000

VALID_PLATFORMS = {"linux", "macos", "windows"}
REQUIRED_FIELDS = {"name", "description", "version", "author", "license", "platforms"}
REQUIRED_METADATA = {"hermes.tags", "hermes.related_skills"}


def validate_frontmatter(content: str, path: Path) -> Tuple[bool, List[str]]:
    """Validate frontmatter structure and required fields."""
    errors = []

    # Must start with --- at byte 0
    if not content.startswith("---"):
        errors.append("Frontmatter must start with '---' at byte 0 (no leading whitespace/BOM)")
        return False, errors

    # Find closing ---
    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        errors.append("Frontmatter must close with '\\n---\\n' before body")
        return False, errors

    fm_end = match.start() + 3
    fm_text = content[3:fm_end]

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        errors.append(f"Frontmatter YAML parse error: {e}")
        return False, errors

    if not isinstance(fm, dict):
        errors.append("Frontmatter must be a YAML mapping")
        return False, errors

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required frontmatter field: {field}")

    # Name validation
    if "name" in fm:
        name = fm["name"]
        if not isinstance(name, str):
            errors.append("name must be a string")
        elif len(name) > MAX_NAME_LENGTH:
            errors.append(f"name exceeds {MAX_NAME_LENGTH} chars: {len(name)}")
        elif not re.match(r"^[a-z][a-z0-9-]*$", name):
            errors.append("name must be lowercase, hyphens only, start with letter")

    # Description validation (HARDLINE)
    if "description" in fm:
        desc = fm["description"]
        if not isinstance(desc, str):
            errors.append("description must be a string")
        elif len(desc) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"description exceeds {MAX_DESCRIPTION_LENGTH} chars (HARDLINE): {len(desc)}")
        elif not desc.endswith("."):
            errors.append("description must end with a period")
        elif ":" in desc and not (desc.startswith('"') and desc.endswith('"')):
            errors.append("description contains ':' — wrap in double quotes to avoid YAML mapping parse")

    # Version validation (semver-ish)
    if "version" in fm:
        ver = fm["version"]
        if not isinstance(ver, str) or not re.match(r"^\d+\.\d+\.\d+", ver):
            errors.append("version must be semver (e.g., 0.1.0)")

    # Author validation
    if "author" in fm:
        author = fm["author"]
        if not isinstance(author, str):
            errors.append("author must be a string")
        elif "Hermes Agent" not in author:
            errors.append("author must include 'Hermes Agent' as secondary collaborator")
        elif author.strip() == "Hermes Agent":
            errors.append("author must credit human first, then 'Hermes Agent'")

    # License
    if "license" in fm and fm["license"] != "MIT":
        errors.append("license must be MIT (or compatible — discuss in PR)")

    # Platforms validation
    if "platforms" in fm:
        platforms = fm["platforms"]
        if not isinstance(platforms, list):
            errors.append("platforms must be a list")
        else:
            for p in platforms:
                if p not in VALID_PLATFORMS:
                    errors.append(f"invalid platform: {p} (valid: {', '.join(sorted(VALID_PLATFORMS))})")

    # Metadata validation
    if "metadata" in fm:
        meta = fm["metadata"]
        if isinstance(meta, dict):
            hermes = meta.get("hermes", {})
            if not isinstance(hermes, dict):
                errors.append("metadata.hermes must be a mapping")
            else:
                if "tags" not in hermes:
                    errors.append("metadata.hermes.tags required")
                elif not isinstance(hermes["tags"], list):
                    errors.append("metadata.hermes.tags must be a list")

                if "related_skills" not in hermes:
                    errors.append("metadata.hermes.related_skills required")
                elif not isinstance(hermes["related_skills"], list):
                    errors.append("metadata.hermes.related_skills must be a list")

    return len(errors) == 0, errors


def validate_body(content: str, path: Path) -> Tuple[bool, List[str]]:
    """Validate skill body structure."""
    errors = []

    # Find body start (after closing ---)
    match = re.search(r"\n---\s*\n", content[3:])
    if not match:
        return False, ["No valid frontmatter closing found"]

    body = content[match.end() + 3:].strip()

    if not body:
        errors.append("Body must not be empty after frontmatter")

    # Check for required sections (minimum)
    required_sections = ["## When to Use", "## Pitfalls", "## Verification"]
    for section in required_sections:
        if section not in body:
            errors.append(f"Missing required section: {section}")

    # Check for machine-local paths
    local_path_patterns = [
        r"/home/[^/]+/",
        r"/Users/[^/]+/",
        r"~/",
        r"C:\\Users\\",
    ]
    for pattern in local_path_patterns:
        if re.search(pattern, body):
            errors.append(f"Machine-local path detected (pattern: {pattern}) — use repo-relative paths")

    # Check for raw shell utilities that should be Hermes tools
    shell_utils = [
        (r"\bgrep\b", "search_files"),
        (r"\bcat\b", "read_file"),
        (r"\bsed\b", "patch"),
        (r"\bawk\b", "patch"),
        (r"\bfind\b", "search_files target='files'"),
        (r"\bls\b", "search_files target='files'"),
    ]
    for pattern, replacement in shell_utils:
        if re.search(pattern, body):
            errors.append(f"Raw shell utility '{pattern}' found — use Hermes tool `{replacement}` instead")

    return len(errors) == 0, errors


def validate_content_size(content: str, path: Path) -> Tuple[bool, List[str]]:
    """Validate content size limit."""
    if len(content) > MAX_CONTENT_CHARS:
        return False, [f"Skill content exceeds {MAX_CONTENT_CHARS} chars: {len(content)}"]
    return True, []


def validate_related_skills(fm: dict, repo_root: Path) -> Tuple[bool, List[str]]:
    """Validate that all related_skills exist in-repo."""
    errors = []
    related = fm.get("metadata", {}).get("hermes", {}).get("related_skills", [])

    for skill in related:
        # Check skills/ and optional-skills/
        found = False
        for base in ["skills", "optional-skills"]:
            skill_dir = repo_root / base
            if skill_dir.exists():
                for cat_dir in skill_dir.iterdir():
                    if cat_dir.is_dir() and (cat_dir / skill).exists():
                        found = True
                        break
        if not found:
            errors.append(f"related_skills entry '{skill}' does not exist in-repo (checked skills/ and optional-skills/)")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate-skills.py <path-to-SKILL.md>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    repo_root = path.parent.parent.parent  # skills/<cat>/<skill>/SKILL.md -> repo_root

    all_errors = []

    # Validate frontmatter
    ok, errors = validate_frontmatter(content, path)
    all_errors.extend(errors)

    if ok:
        # Parse frontmatter for related_skills check
        match = re.search(r"\n---\s*\n", content[3:])
        if match:
            fm_text = content[3:match.start() + 3]
            fm = yaml.safe_load(fm_text)
            ok2, errors2 = validate_related_skills(fm, repo_root)
            all_errors.extend(errors2)

    # Validate body
    ok, errors = validate_body(content, path)
    all_errors.extend(errors)

    # Validate content size
    ok, errors = validate_content_size(content, path)
    all_errors.extend(errors)

    if all_errors:
        print(f"❌ Validation FAILED for {path}")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"✅ Validation PASSED for {path}")
        sys.exit(0)


if __name__ == "__main__":
    main()