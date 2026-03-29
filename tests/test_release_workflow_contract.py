"""Contract tests: optional OIDC release workflow matches docs/CI_SPEC.md §8."""

from __future__ import annotations

import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"
_CI_SPEC = _ROOT / "docs" / "CI_SPEC.md"


def test_release_workflow_file_exists():
    assert _RELEASE_WORKFLOW.is_file(), "docs/CI_SPEC.md §8 expects .github/workflows/release.yml"


def test_release_workflow_avoids_dev_install_and_runs_build_twine_check():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert 'pip install -e ".[dev]"' not in yml
    assert "python -m build" in yml
    assert re.search(r"twine\s+check\s+dist", yml)


def test_release_workflow_triggers_dispatch_and_version_tags():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"^\s*workflow_dispatch:\s*$", yml, re.MULTILINE)
    assert re.search(r"^\s*push:\s*$", yml, re.MULTILINE)
    assert re.search(r"tags:\s*\n\s*-\s*[\"']v", yml)


def test_release_workflow_permissions_oidc_and_pypa_publish():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"id-token:\s*write", yml)
    assert re.search(r"contents:\s*read", yml)
    assert "pypa/gh-action-pypi-publish@release/v1" in yml


def test_release_workflow_environment_pypi():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"environment:\s*\n\s*name:\s*pypi", yml)


def test_release_workflow_python_312_for_publish_job():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert 'python-version: "3.12"' in yml


def test_release_workflow_build_pins_match_pyproject_dev_floor():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert 'pip install "build>=1.2.0" "twine>=5.0"' in yml


def test_release_workflow_declares_concurrency_no_cancel():
    yml = _RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert "concurrency:" in yml
    assert "cancel-in-progress: false" in yml


def test_ci_spec_documents_section_8_release_workflow():
    md = _CI_SPEC.read_text(encoding="utf-8")
    assert "## 8. Optional release workflow (OIDC trusted publishing)" in md
    for heading in (
        "### 8.1 Triggers and guards",
        "### 8.2 Build, check, and upload steps",
        "### 8.3 OIDC and secrets policy",
        "### 8.4 GitHub Environment `pypi` and PyPI trusted publisher alignment",
        "### 8.7 Rollback and recovery expectations",
    ):
        assert heading in md, f"docs/CI_SPEC.md missing {heading!r}"
    assert "id-token: write" in md
    assert "trusted publisher" in md.lower()
    assert "yank" in md.lower()
