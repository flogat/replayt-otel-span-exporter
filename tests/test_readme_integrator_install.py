"""README integrator install lines track [project].version (docs/SPEC_README_QUICK_START.md §2.1)."""

from __future__ import annotations

import pathlib
import re
import tomllib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_README = _ROOT / "README.md"
_PYPROJECT = _ROOT / "pyproject.toml"


def _project_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_readme_shows_version_pinned_pip_install_matching_pyproject() -> None:
    v = _project_version()
    text = _README.read_text(encoding="utf-8")
    assert f"replayt-otel-span-exporter=={v}" in text, (
        "README must include a copy-paste pip pin matching [project].version "
        f"(expected substring replayt-otel-span-exporter=={v!r})"
    )


def test_readme_documents_pre_flag_for_prerelease_pip() -> None:
    text = _README.read_text(encoding="utf-8")
    assert re.search(r"pip\s+install\s+--pre\s+replayt-otel-span-exporter", text), (
        "README should show pip install --pre for latest prerelease per SPEC_README_QUICK_START §2.1"
    )


def test_pyproject_declares_readme_for_packaging_metadata() -> None:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    assert data["project"].get("readme") == "README.md"
