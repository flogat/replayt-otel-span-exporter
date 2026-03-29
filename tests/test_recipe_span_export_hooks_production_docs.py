"""Doc contract for docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md §10.1 (integrator cookbook backlog `29efde6c`)."""

from __future__ import annotations

import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_RECIPE = _ROOT / "docs" / "RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md"
_MISSION = _ROOT / "docs" / "MISSION.md"
_README = _ROOT / "README.md"
_CI_SPEC = _ROOT / "docs" / "CI_SPEC.md"
_MC_ID = "29efde6c-c106-43ca-a17a-1623d53145f5"


def _h2_sections(md: str) -> dict[str, str]:
    """Split markdown on `## ` headings (exclude `###`)."""
    lines = md.splitlines()
    sections: dict[str, str] = {}
    title: str | None = None
    buf: list[str] = []
    for line in lines:
        if line.startswith("## ") and not line.startswith("###"):
            if title is not None:
                sections[title] = "\n".join(buf).strip()
            title = line[3:].strip()
            buf = []
        elif title is not None:
            buf.append(line)
    if title is not None:
        sections[title] = "\n".join(buf).strip()
    return sections


def _subsection(body: str, h3_heading: str) -> str:
    start = body.find(h3_heading)
    assert start >= 0, f"missing subsection {h3_heading!r}"
    rest = body[start:]
    m = re.search(r"\n### [^#]", rest[len(h3_heading) :])
    if m is None:
        return rest.strip()
    return rest[: len(h3_heading) + m.start()].strip()


def test_recipe_section_1_5_minimal_pattern():
    sections = _h2_sections(_RECIPE.read_text(encoding="utf-8"))
    body = next(v for t, v in sections.items() if t.startswith("1.5 "))
    lowered = body.lower()
    assert "on_export_commit" in body
    assert "on_export_audit" in body
    assert "synchronous" in lowered
    assert "prepared" in lowered and "attributes" in lowered


def test_recipe_section_2_async_safe_and_deferral():
    sections = _h2_sections(_RECIPE.read_text(encoding="utf-8"))
    body = next(v for t, v in sections.items() if t.startswith("2. "))
    assert "**`await`**" in body or "`await`" in body
    assert "SimpleQueue" in body
    assert "call_soon_threadsafe" in body
    assert "logging" in body.lower()


def test_recipe_section_4_idempotency():
    sections = _h2_sections(_RECIPE.read_text(encoding="utf-8"))
    body = next(v for t, v in sections.items() if t.startswith("4. "))
    assert "more than once" in body or "multiple times" in body.lower()
    assert "allow-listed" in body.lower() or "allow listed" in body.lower()
    assert "hashing attribute payloads" in body or "attribute payloads" in body


def test_recipe_section_5_1_logging_example():
    sections = _h2_sections(_RECIPE.read_text(encoding="utf-8"))
    sink = sections["5. Sink examples"]
    s51 = _subsection(sink, "### 5.1 Stdlib logging (integrator logger)")
    assert "logging" in s51.lower()
    assert "repr(prepared)" in s51
    assert "PreparedSpanRecord.attributes" in s51


def test_recipe_sections_3_and_5_forbid_persisting_prepared_or_attributes():
    sections = _h2_sections(_RECIPE.read_text(encoding="utf-8"))
    s3 = sections["3. Allow-listed audit fields only"]
    assert "prepared" in s3
    assert "PreparedSpanRecord" in s3
    assert "attributes" in s3
    assert "persistent storage" in s3.lower() or "external systems" in s3.lower()

    s5 = sections["5. Sink examples"]
    assert "prepared" in s5.lower()
    assert "attribute" in s5.lower()


def test_mission_links_recipe_scope_row_and_traceability_subsection():
    text = _MISSION.read_text(encoding="utf-8")
    assert "RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md" in text
    assert _MC_ID in text
    assert "Document integrator cookbook: approval hook + audit in production services" in text
    assert "approval / audit hooks" in text.lower() or "approval" in text.lower()


def test_readme_optional_approval_hook_links_spec_and_recipe():
    text = _README.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "### optional approval hook" in lowered
    assert "docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md" in text
    assert "docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md" in text


def test_ci_spec_mentions_recipe_span_export_hooks_doc_contract():
    assert "tests/test_recipe_span_export_hooks_production_docs.py" in _CI_SPEC.read_text(encoding="utf-8")
