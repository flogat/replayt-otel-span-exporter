"""Release checks per docs/SPEC_FIRST_ALPHA_RELEASE.md §2–§3."""

from __future__ import annotations

import pathlib
import re
import tomllib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"
_CHANGELOG = _ROOT / "CHANGELOG.md"

# Spec example: 0.2.0a1 — final segment is PEP 440 "a" prerelease + serial.
_ALPHA_LIKE = re.compile(r"^\d+\.\d+\.\d+a\d+$")


def _project_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_pyproject_version_is_pep440_alpha_prerelease():
    v = _project_version()
    assert _ALPHA_LIKE.match(v), (
        f"expected PEP 440 alpha like 0.2.0a1 per SPEC_FIRST_ALPHA_RELEASE §2, got {v!r}"
    )


def test_changelog_has_release_heading_matching_project_version():
    v = _project_version()
    text = _CHANGELOG.read_text(encoding="utf-8")
    assert f"## [{v}]" in text, (
        f"CHANGELOG must contain '## [{v}]' per SPEC_FIRST_ALPHA_RELEASE §3, got headings in file"
    )


def test_changelog_has_dated_release_line_for_project_version():
    v = _project_version()
    text = _CHANGELOG.read_text(encoding="utf-8")
    # Keep a Changelog: dated section, e.g. "## [0.2.0a1] - 2026-03-28"
    assert re.search(rf"^## \[{re.escape(v)}\]\s+-\s+\d{{4}}-\d{{2}}-\d{{2}}\s*$", text, re.M), (
        f"CHANGELOG must have dated '## [{v}] - YYYY-MM-DD' line per SPEC_FIRST_ALPHA_RELEASE §3"
    )


def test_changelog_has_unreleased_section():
    text = _CHANGELOG.read_text(encoding="utf-8")
    assert "## [Unreleased]" in text, "CHANGELOG must keep a ## [Unreleased] section after a release cut"
