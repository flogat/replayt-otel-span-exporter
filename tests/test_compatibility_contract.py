"""Contract tests: compatibility docs and CI stay aligned with pyproject.toml.

See docs/COMPATIBILITY.md §6 (checklist) and docs/CI_SPEC.md §5.
"""

from __future__ import annotations

import pathlib
import re
import tomllib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"
_COMPAT = _ROOT / "docs" / "COMPATIBILITY.md"
_SPEC_REPLAYT = _ROOT / "docs" / "SPEC_REPLAYT_INTEGRATION_TESTS.md"
_CI = _ROOT / ".github" / "workflows" / "ci.yml"
_EXPECTED_CI_PYTHON_VERSIONS = frozenset({"3.11", "3.12", "3.13"})


def _load_pyproject() -> dict:
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))


def _replayt_dev_line(dev: list[str]) -> str:
    for dep in dev:
        stripped = dep.strip()
        if stripped.startswith("replayt"):
            return stripped.replace(" ", "")
    raise AssertionError("replayt must be declared under [project.optional-dependencies].dev")


def _replayt_minimum_version(replayt_line: str) -> str:
    m = re.match(r"replayt>=([\d.]+)", replayt_line)
    if m:
        return m.group(1)
    raise AssertionError(
        f"expected dev replayt dependency like replayt>=0.4.25, got {replayt_line!r}"
    )


def test_runtime_dependencies_exclude_replayt():
    data = _load_pyproject()
    deps = data["project"]["dependencies"]
    assert not any(str(d).strip().startswith("replayt") for d in deps)


def test_replayt_dev_pin_matches_compatibility_and_replayt_spec():
    data = _load_pyproject()
    dev = data["project"]["optional-dependencies"]["dev"]
    replayt_line = _replayt_dev_line(dev)
    minimum = _replayt_minimum_version(replayt_line)

    compat = _COMPAT.read_text(encoding="utf-8")
    assert minimum in compat
    assert f">={minimum}" in compat.replace(" ", "")

    spec_text = _SPEC_REPLAYT.read_text(encoding="utf-8")
    assert minimum in spec_text
    assert f">={minimum}" in spec_text.replace(" ", "")


def test_ci_default_path_installs_dev_extra_and_python_matrix():
    workflow = _CI.read_text(encoding="utf-8")
    assert 'pip install -e ".[dev]"' in workflow
    blocks = re.findall(r"python-version:\s*\[([^\]]+)\]", workflow)
    assert blocks, "ci.yml should declare python-version matrix entries"
    for block in blocks:
        versions = set(re.findall(r'"([0-9]+\.[0-9]+)"', block))
        assert versions == _EXPECTED_CI_PYTHON_VERSIONS, (
            "expected matrix "
            f"{sorted(_EXPECTED_CI_PYTHON_VERSIONS)} per docs/COMPATIBILITY.md §4, "
            f"got {sorted(versions)}"
        )


def test_requires_python_named_in_compatibility_doc():
    data = _load_pyproject()
    req = data["project"]["requires-python"].strip()
    compat = _COMPAT.read_text(encoding="utf-8")
    normalized_doc = compat.replace(" ", "")
    assert req.replace(" ", "") in normalized_doc
