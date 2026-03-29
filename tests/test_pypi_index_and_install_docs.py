"""Public PyPI JSON vs README / COMPATIBILITY for first-alpha publish truth (SPEC_FIRST_ALPHA_RELEASE §0.2, §6)."""

from __future__ import annotations

import json
import pathlib
import tomllib
import urllib.error
import urllib.request

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_README = _ROOT / "README.md"
_COMPAT = _ROOT / "docs" / "COMPATIBILITY.md"
_PYPROJECT = _ROOT / "pyproject.toml"
_PYPI_JSON = "https://pypi.org/pypi/replayt-otel-span-exporter/json"
_PRE_INDEX_SENTENCE = "Until the index lists the release"
_USER_AGENT = "replayt-otel-span-exporter-tests (https://pypi.org/project/replayt-otel-span-exporter/)"


def _project_version() -> str:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _fetch_pypi_project() -> tuple[int, dict | None]:
    req = urllib.request.Request(_PYPI_JSON, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 404, None
        raise


def _release_has_sdist_and_wheel(files: list[dict]) -> bool:
    types = {f.get("packagetype") for f in files}
    return "sdist" in types and "bdist_wheel" in types


def test_public_pypi_json_matches_readme_and_compatibility_docs() -> None:
    """Pre-index: README warns integrators; COMPATIBILITY keeps §2 pre-upload sentence.

    Post-upload (both artifacts on PyPI for [project].version): drop the pre-index sentence from §2.
    """
    version = _project_version()
    status, payload = _fetch_pypi_project()
    readme = _README.read_text(encoding="utf-8")
    compat = _COMPAT.read_text(encoding="utf-8")

    if status == 404:
        assert "not listed" in readme.lower(), (
            "README integrator quick start must warn when the PyPI project is absent "
            "(SPEC_README_QUICK_START §2.1)."
        )
        assert _PRE_INDEX_SENTENCE in compat, (
            "docs/COMPATIBILITY.md §2 must keep pre-index wording until public PyPI lists the release."
        )
        return

    assert status == 200 and payload is not None
    files = payload.get("releases", {}).get(version, [])
    if not files or not _release_has_sdist_and_wheel(files):
        assert "not listed" in readme.lower()
        assert _PRE_INDEX_SENTENCE in compat
        return

    assert _PRE_INDEX_SENTENCE not in compat, (
        "Remove the pre-index sentence from docs/COMPATIBILITY.md §2 now that sdist and wheel "
        f"for {version!r} are on public PyPI (SPEC_FIRST_ALPHA_RELEASE §6)."
    )


def test_verify_published_release_script_uses_unix_line_endings() -> None:
    raw = (_ROOT / "scripts" / "verify_published_release.sh").read_bytes()
    assert b"\r\n" not in raw, (
        "scripts/verify_published_release.sh must use LF newlines so the shebang runs on Unix."
    )
