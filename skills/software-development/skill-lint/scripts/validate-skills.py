#!/usr/bin/env python3
"""
Skill Frontmatter & Structure Validator

Validates a SKILL.md file against the Skill Authoring Standards.
Run from repo root: python3 skills/software-development/skill-lint/scripts/validate-skills.py skills/<category>/<skill>/SKILL.md

Also supports official Agent Skills spec validation via skills-ref (if installed).
"""

import sys
import re
import yaml
import subprocess
from pathlib import Path
from typing import List, Tuple

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 60
MAX_CONTENT_CHARS = 100_000

VALID_PLATFORMS = {"linux", "macos", "windows"}
REQUIRED_FIELDS = {"name", "description", "version", "author", "license", "platforms"}
REQUIRED_METADATA = {"tags"}

OFFICIAL_ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def validate_frontmatter(content: str, path: Path) -> Tuple[bool, List[str]]:
    """Validate frontmatter structure and required fields (HARDLINE)."""
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

    # Required fields (HARDLINE)
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

    # Description validation (HARDLINE: ≤60 chars)
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
        # Credit human first (no "Agent" suffix requirement for this repo)

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
            if "tags" not in meta:
                errors.append("metadata.tags required")
            elif not isinstance(meta["tags"], list):
                errors.append("metadata.tags must be a list")

            # related_skills is optional; if present, must be a list
            if "related_skills" in meta and not isinstance(meta["related_skills"], list):
                errors.append("metadata.related_skills must be a list")

    return len(errors) == 0, errors


def validate_official_spec(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Validate using official Agent Skills spec validator (skills-ref)."""
    errors = []

    # Find skills-ref executable (prefer venv, then PATH)
    skills_ref_cmd = None
    for candidate in [
        "skills-ref",
    ]:
        if Path(candidate).exists() or candidate == "skills-ref":
            skills_ref_cmd = candidate
            break

    if not skills_ref_cmd:
        errors.append("Official validator 'skills-ref' not found. Install with: pip install -e /path/to/skills-ref")
        return False, errors

    try:
        result = subprocess.run(
            [skills_ref_cmd, "validate", str(skill_dir)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        errors.append("Official validator timed out")
        return False, errors
    except FileNotFoundError:
        errors.append(f"Official validator not found at {skills_ref_cmd}")
        return False, errors

    if result.returncode != 0:
        # Parse output for structured errors
        output = result.stdout + result.stderr
        for line in output.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("Validation failed"):
                errors.append(f"Official spec: {line}")

    return result.returncode == 0, errors


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

    # Check for raw shell utilities that should be agent tools
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
            errors.append(f"Raw shell utility '{pattern}' found — use agent tool `{replacement}` instead")

    return len(errors) == 0, errors


def validate_content_size(content: str, path: Path) -> Tuple[bool, List[str]]:
    """Validate content size limit."""
    if len(content) > MAX_CONTENT_CHARS:
        return False, [f"Skill content exceeds {MAX_CONTENT_CHARS} chars: {len(content)}"]
    return True, []


def validate_related_skills(fm: dict, repo_root: Path) -> Tuple[bool, List[str]]:
    """Validate that all related_skills exist in-repo."""
    errors = []
    related = fm.get("metadata", {}).get("related_skills", [])

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


def find_skill_dirs(repo_root: Path) -> List[Path]:
    """Find all skill directories in the repository."""
    skill_dirs = []
    for base in ["skills", "optional-skills"]:
        base_dir = repo_root / base
        if base_dir.exists():
            for cat_dir in base_dir.iterdir():
                if cat_dir.is_dir():
                    for skill_dir in cat_dir.iterdir():
                        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                            skill_dirs.append(skill_dir)
    return sorted(skill_dirs)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate SKILL.md files")
    parser.add_argument("path", nargs="?", help="Path to SKILL.md file or skill directory")
    parser.add_argument("--all", action="store_true", help="Validate all skills in repository")
    parser.add_argument("--official", action="store_true", help="Also run official Agent Skills spec validator (skills-ref)")
    parser.add_argument("--changed", action="store_true", help="Validate only git-changed skills (not implemented)")
    args = parser.parse_args()

    repo_root = Path.cwd()

    if args.all:
        skill_dirs = find_skill_dirs(repo_root)
        if not skill_dirs:
            print("No skills found in repository")
            sys.exit(0)

        all_passed = True
        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            print(f"\n=== Validating {skill_dir.relative_to(repo_root)} ===")

            # HARDLINE validation
            content = skill_md.read_text(encoding="utf-8")
            ok, errors = validate_frontmatter(content, skill_md)
            if ok:
                match = re.search(r"\n---\s*\n", content[3:])
                if match:
                    fm_text = content[3:match.start() + 3]
                    fm = yaml.safe_load(fm_text)
                    ok2, errors2 = validate_related_skills(fm, repo_root)
                    errors.extend(errors2)

            ok, errors = validate_body(content, skill_md)
            ok2, errors2 = validate_content_size(content, skill_md)
            errors.extend(errors2)

            if errors:
                all_passed = False
                print(f"❌ HARDLINE FAILED for {skill_dir.relative_to(repo_root)}")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ HARDLINE PASSED for {skill_dir.relative_to(repo_root)}")

            # Official spec validation
            if args.official:
                ok_official, errors_official = validate_official_spec(skill_dir)
                if errors_official:
                    all_passed = False
                    print(f"❌ Official spec FAILED for {skill_dir.relative_to(repo_root)}")
                    for err in errors_official:
                        print(f"  - {err}")
                else:
                    print(f"✅ Official spec PASSED for {skill_dir.relative_to(repo_root)}")

        if all_passed:
            print("\n✅ All validations PASSED")
            sys.exit(0)
        else:
            print("\n❌ Some validations FAILED")
            sys.exit(1)

    if not args.path:
        print("Usage: python3 scripts/validate-skills.py <path-to-SKILL.md> [--all] [--official]")
        sys.exit(1)

    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    # If path is a directory, look for SKILL.md inside
    if path.is_dir():
        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            print(f"Error: SKILL.md not found in {path}")
            sys.exit(1)
        path = skill_md

    content = path.read_text(encoding="utf-8")
    repo_root = path.parent.parent.parent.parent  # skills/<cat>/<skill>/SKILL.md -> repo_root

    all_errors = []

    # HARDLINE validation
    ok, errors = validate_frontmatter(content, path)
    all_errors.extend(errors)

    if ok:
        match = re.search(r"\n---\s*\n", content[3:])
        if match:
            fm_text = content[3:match.start() + 3]
            fm = yaml.safe_load(fm_text)
            ok2, errors2 = validate_related_skills(fm, repo_root)
            all_errors.extend(errors2)

    ok, errors = validate_body(content, path)
    all_errors.extend(errors)

    ok, errors = validate_content_size(content, path)
    all_errors.extend(errors)

    # Official spec validation
    if args.official:
        skill_dir = path.parent
        ok_official, errors_official = validate_official_spec(skill_dir)
        if errors_official:
            all_errors.extend([f"Official spec: {e}" for e in errors_official])

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