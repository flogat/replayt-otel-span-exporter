"""Sdist/wheel build and twine check per docs/SPEC_FIRST_ALPHA_RELEASE.md §4."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tomllib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"


def _project_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


@pytest.fixture(scope="module")
def built_dist_dir(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    dist = tmp_path_factory.mktemp("dist")
    proc = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist)],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.fail(
            "python -m build failed:\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
    return dist


def test_build_produces_one_wheel_and_one_sdist_named_with_version(built_dist_dir: pathlib.Path) -> None:
    v = _project_version()
    wheels = sorted(built_dist_dir.glob("*.whl"))
    sdists = sorted(built_dist_dir.glob("*.tar.gz"))
    assert len(wheels) == 1, f"expected one wheel, got {[p.name for p in wheels]}"
    assert len(sdists) == 1, f"expected one sdist, got {[p.name for p in sdists]}"
    assert v in wheels[0].name, f"wheel name should contain {v!r}, got {wheels[0].name!r}"
    assert v in sdists[0].name, f"sdist name should contain {v!r}, got {sdists[0].name!r}"


def test_twine_check_passes_on_built_artifacts(built_dist_dir: pathlib.Path) -> None:
    paths = sorted(built_dist_dir.iterdir())
    assert paths, "dist directory should contain build outputs"
    proc = subprocess.run(
        [sys.executable, "-m", "twine", "check", *[str(p) for p in paths]],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.fail(
            "twine check failed:\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
