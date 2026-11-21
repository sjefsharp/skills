#!/usr/bin/env python3
"""
Tests for skill-lint skill validation script.

Run: pytest tests/skills/test_skill_lint_skill.py -q
"""

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def get_venv_python() -> str:
    """Get the venv python path."""
    repo_root = Path(__file__).parent.parent.parent
    venv_python = repo_root / ".venv" / "bin" / "python3"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_validator(skill_path: Path) -> subprocess.CompletedProcess:
    """Run the validator on a skill file."""
    repo_root = Path(__file__).parent.parent.parent
    validator = repo_root / "scripts" / "validate-skills.py"
    return subprocess.run(
        [get_venv_python(), str(validator), str(skill_path)],
        capture_output=True,
        text=True,
    )


def check_output(result: subprocess.CompletedProcess, expected: str) -> bool:
    """Check if expected string is in stdout or stderr."""
    return expected in result.stdout or expected in result.stderr


def test_valid_skill_passes():
    """A valid skill should pass validation."""
    skill_path = Path(__file__).parent.parent.parent / "skills" / "software-development" / "skill-lint" / "SKILL.md"
    result = run_validator(skill_path)
    assert result.returncode == 0, f"Valid skill failed: {result.stdout} {result.stderr}"
    assert check_output(result, "PASSED")


def test_missing_frontmatter_fails():
    """Skill without frontmatter should fail."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# No Frontmatter\n\nBody only.\n")
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "Frontmatter must start with '---' at byte 0")
    finally:
        path.unlink()


def test_description_too_long_fails():
    """Description > 60 chars should fail (HARDLINE)."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: This description is way too long and contains marketing words like powerful and comprehensive which violates the hardline rules.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill
        Valid body with required sections.

        ## When to Use
        - Test

        ## Pitfalls
        - None

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "description exceeds 60 chars")
    finally:
        path.unlink()


def test_author_hermes_agent_alone_fails():
    """Author = 'Hermes Agent' alone should fail."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill

        ## When to Use
        - Test

        ## Pitfalls
        - None

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "author must credit human first")
    finally:
        path.unlink()


def test_related_skill_missing_fails():
    """Non-existent related_skills should fail."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [this-skill-does-not-exist]
        ---
        # Test Skill

        ## When to Use
        - Test

        ## Pitfalls
        - None

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "related_skills entry 'this-skill-does-not-exist' does not exist in-repo")
    finally:
        path.unlink()


def test_machine_local_path_fails():
    """Machine-local path in body should fail."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill

        ## When to Use
        - Test

        ## Pitfalls
        - Uses /home/user/local/path

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "Machine-local path detected")
    finally:
        path.unlink()


def test_shell_utility_flagged():
    """Raw shell utilities in body should be flagged."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill

        ## When to Use
        - Test

        ## Pitfalls
        - Uses grep and cat commands

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        # Validator outputs regex patterns with escaped backslashes
        assert check_output(result, "grep")
        assert check_output(result, "cat")
    finally:
        path.unlink()


def test_missing_required_sections_fails():
    """Missing required sections (When to Use, Pitfalls, Verification) should fail."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill
        Body without required sections.
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "Missing required section: ## When to Use")
        assert check_output(result, "Missing required section: ## Pitfalls")
        assert check_output(result, "Missing required section: ## Verification")
    finally:
        path.unlink()


def test_invalid_platform_fails():
    """Invalid platform value should fail."""
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows, bsd]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill

        ## When to Use
        - Test

        ## Pitfalls
        - None

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "invalid platform: bsd")
    finally:
        path.unlink()


def test_content_size_limit():
    """Content exceeding 100k chars should fail."""
    large_body = "x" * 100_001
    content = textwrap.dedent(f"""\
        ---
        name: test-skill
        description: Valid description under sixty chars.
        version: 0.1.0
        author: Test User (testuser), Hermes Agent
        license: MIT
        platforms: [linux, macos, windows]
        metadata:
          hermes:
            tags: [test]
            related_skills: [hermes-agent-skill-authoring]
        ---
        # Test Skill

        {large_body}

        ## When to Use
        - Test

        ## Pitfalls
        - None

        ## Verification
        - Run test
        """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = Path(f.name)

    try:
        result = run_validator(path)
        assert result.returncode == 1
        assert check_output(result, "exceeds 100000 chars")
    finally:
        path.unlink()


if __name__ == "__main__":
    sys.exit(subprocess.run([get_venv_python(), "-m", "pytest", __file__, "-q"]).returncode)