"""Release versioning checks per docs/SPEC_FIRST_ALPHA_RELEASE.md §2."""

from __future__ import annotations

import pathlib
import re
import tomllib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"

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
