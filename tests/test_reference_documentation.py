"""Reference documentation tree matches docs/SPEC_REFERENCE_DOCUMENTATION.md (folder, indexes, root README §7)."""

from __future__ import annotations

import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_REF = _ROOT / "docs" / "reference-documentation"
_README = _REF / "README.md"
_OTEL = _REF / "opentelemetry-python.md"
_REPLAYT = _REF / "replayt.md"
_ROOT_README = _ROOT / "README.md"
_SPEC = _ROOT / "docs" / "SPEC_REFERENCE_DOCUMENTATION.md"
_CI_SPEC = _ROOT / "docs" / "CI_SPEC.md"


def _https_urls(text: str) -> list[str]:
    return re.findall(r"https://[^\s)>\]]+", text)


def test_reference_documentation_folder_readme_covers_licensing_scope_refresh():
    text = _README.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "## licensing and attribution" in lowered
    assert "## scope (in / out)" in lowered
    assert "## refresh policy" in lowered
    assert "verbatim" in lowered
    assert "out of scope" in lowered


def test_stub_indexes_exist_with_maintainer_summary_and_https_links():
    for path in (_OTEL, _REPLAYT):
        body = path.read_text(encoding="utf-8")
        assert "No third-party verbatim excerpts in this file." in body
        urls = _https_urls(body)
        assert urls, f"{path.name} should include canonical https:// links"
        assert all(u.startswith("https://") for u in urls)

    otel = _OTEL.read_text(encoding="utf-8")
    assert "SpanExporter" in otel
    assert "opentelemetry-python.readthedocs.io" in otel
    assert "replayt.workflow_id" in otel or "SPEC_EXPORT_TRIAGE_METADATA" in otel

    replayt = _REPLAYT.read_text(encoding="utf-8")
    assert "https://pypi.org/project/replayt/" in replayt
    assert "SPEC_REPLAYT_INTEGRATION_TESTS" in replayt
    assert "dev" in replayt.lower()


def test_reference_documentation_total_size_under_spec_guidance():
    """SPEC_REFERENCE_DOCUMENTATION.md §4.2: whole tree SHOULD stay under ~300 KiB."""
    total = sum(p.read_bytes().__len__() for p in _REF.rglob("*.md"))
    assert total < 300 * 1024, f"reference-documentation tree is {total} bytes"


def test_ci_spec_mentions_reference_doc_contract_test():
    ci_text = _CI_SPEC.read_text(encoding="utf-8")
    assert "tests/test_reference_documentation.py" in ci_text

    spec_text = _SPEC.read_text(encoding="utf-8")
    assert "docs/reference-documentation/" in spec_text


def test_root_readme_documents_reference_documentation_tree():
    """SPEC_REFERENCE_DOCUMENTATION.md §7 — present folder, folder README, and Builder spec."""
    text = _ROOT_README.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "## reference documentation" in lowered
    assert "docs/reference-documentation/README.md" in text
    assert "docs/SPEC_REFERENCE_DOCUMENTATION.md" in text
    assert "| `docs/SPEC_REFERENCE_DOCUMENTATION.md` |" in text
    assert "| `docs/reference-documentation/` |" in text
