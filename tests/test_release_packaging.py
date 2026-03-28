"""Sdist/wheel build, twine check, and clean-venv install smoke per docs/SPEC_FIRST_ALPHA_RELEASE.md §4–§5."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tomllib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"


def _project_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _venv_bin(venv_root: pathlib.Path, name: str) -> pathlib.Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / f"{name}.exe"
    return venv_root / "bin" / name


def _requires_distribution_names(pip_show_stdout: str) -> list[str]:
    m = re.search(r"^Requires:\s*(.+)$", pip_show_stdout, re.MULTILINE)
    if not m:
        return []
    blob = m.group(1).strip()
    if not blob or blob.lower() == "none":
        return []
    names: list[str] = []
    _pep508_name = re.compile(r"^([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)")
    for part in blob.split(","):
        head = part.strip().split("[", maxsplit=1)[0].split(";", maxsplit=1)[0].strip()
        mm = _pep508_name.match(head)
        if mm:
            names.append(mm.group(1).lower())
    return names


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


def test_built_wheel_installs_in_clean_venv_with_matching_metadata(
    built_dist_dir: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    """Analog to SPEC_FIRST_ALPHA_RELEASE §5: install artifact only (file URL), no editable checkout."""
    wheels = sorted(built_dist_dir.glob("*.whl"))
    assert len(wheels) == 1, f"expected one wheel, got {[p.name for p in wheels]}"
    v = _project_version()
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True)
    pip = _venv_bin(venv, "pip")
    py = _venv_bin(venv, "python")
    up = subprocess.run(
        [str(pip), "install", "--upgrade", "pip"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert up.returncode == 0, up.stderr
    inst = subprocess.run(
        [str(pip), "install", str(wheels[0])],
        check=False,
        capture_output=True,
        text=True,
    )
    assert inst.returncode == 0, f"{inst.stdout}\n{inst.stderr}"
    verify = f"""
import importlib.metadata as m
import replayt_otel_span_exporter as pkg
want = {v!r}
assert m.version("replayt-otel-span-exporter") == want, (m.version("replayt-otel-span-exporter"), want)
assert pkg.__version__ == want, (pkg.__version__, want)
"""
    run = subprocess.run(
        [str(py), "-c", verify],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr


def test_built_wheel_runtime_install_does_not_require_replayt(
    built_dist_dir: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    wheels = sorted(built_dist_dir.glob("*.whl"))
    assert len(wheels) == 1
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True)
    pip = _venv_bin(venv, "pip")
    py = _venv_bin(venv, "python")
    subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True, capture_output=True)
    subprocess.run([str(pip), "install", str(wheels[0])], check=True, capture_output=True)
    show = subprocess.run(
        [str(pip), "show", "replayt-otel-span-exporter"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert show.returncode == 0, show.stderr
    req_names = _requires_distribution_names(show.stdout)
    assert "replayt" not in req_names, (
        "runtime install must not depend on replayt; Requires parsed as "
        f"{req_names!r}:\n{show.stdout}"
    )
    miss = subprocess.run(
        [str(py), "-c", "import importlib.util; import sys; "
        "sys.exit(0 if importlib.util.find_spec('replayt') is None else 1)"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert miss.returncode == 0, "replayt must not be importable after wheel-only install"
