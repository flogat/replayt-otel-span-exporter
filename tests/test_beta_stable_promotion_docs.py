"""Smoke checks for beta/1.0 promotion docs (docs/CI_SPEC.md §5)."""

from __future__ import annotations

import pathlib

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SPEC = _ROOT / "docs" / "SPEC_BETA_AND_STABLE_PROMOTION.md"
_ROADMAP = _ROOT / "docs" / "ROADMAP.md"
_MISSION = _ROOT / "docs" / "MISSION.md"
_CI_SPEC = _ROOT / "docs" / "CI_SPEC.md"


def test_promotion_spec_has_normative_sections_and_roadmap_pointer():
    text = _SPEC.read_text(encoding="utf-8")
    assert "## 2. Promotion gates (normative)" in text
    assert "## 3. Semantic versioning and public API (normative)" in text
    assert "## 4. Changelog discipline (normative)" in text
    assert "## 5. Optional hooks and extension points (normative)" in text
    assert "## 6. Deprecation policy (normative)" in text
    assert "### 3.1 `PreparedSpanRecord`" in text
    assert "### 3.2 `ReplaytSpanExporter`" in text
    assert "docs/ROADMAP.md" in text


def test_roadmap_links_normative_spec_first_alpha_and_mission():
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "SPEC_BETA_AND_STABLE_PROMOTION" in text
    assert "MISSION.md" in text
    assert "SPEC_FIRST_ALPHA_RELEASE" in text
    assert "## Release phases" in text


def test_mission_links_promotion_spec_and_roadmap():
    mission = _MISSION.read_text(encoding="utf-8")
    assert "SPEC_BETA_AND_STABLE_PROMOTION.md" in mission
    assert "ROADMAP.md" in mission


def test_ci_spec_mentions_promotion_doc_contract_test():
    ci_text = _CI_SPEC.read_text(encoding="utf-8")
    assert "tests/test_beta_stable_promotion_docs.py" in ci_text
