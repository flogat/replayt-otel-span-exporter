# Specification: `docs/reference-documentation/` (replayt and OpenTelemetry context)

This document refines reference-documentation backlogs into testable requirements, including **“Seed `docs/reference-documentation/` with replayt + OTel snapshot markdown”** (Mission Control item **`dda05c31-9820-45d0-9e56-e58625f1686f`**) and the earlier wording **“Populate `docs/reference-documentation/` for offline replayt and OTel context.”** **Creating or changing directory contents** (except incidental README/spec cross-links) belongs in phase **3** (Builder); this file is the contract for what “done” means.

## Backlog traceability

| Original backlog wording | Satisfied by (this doc) |
| ------------------------ | ------------------------ |
| **Seed** folder with **bounded**, **license-appropriate** markdown (**snapshots** and/or **deep links + local stubs**) | [§4 Content strategies](#4-content-strategies-normative), [§6 Licensing and attribution](#6-licensing-and-attribution-normative), [§9.0](#90-backlog-seed-reference-documentation-normative) |
| **replayt** + **OpenTelemetry Python** integration context **from the tree** | [§5 Topical coverage](#5-topical-coverage-normative), §4.1 |
| Short **README** in the folder: **licensing**, **scope (in/out)**, **refresh policy** | [§3 Folder README](#3-folder-readme-normative) |
| Optional folder (root README may still describe absence until Builder lands content) | [§2 Directory and presence](#2-directory-and-presence-normative), [§7 Cross-links from root `README`](#7-cross-links-from-root-readme-normative) |
| Stub vs verbatim layout and **CI test** coupling | [§4.3](#43-index-files-vs-verbatim-snapshot-files-normative), [§8](#8-ci-and-automated-tests-normative) |

**Related contracts:** Material MUST stay consistent with **[docs/MISSION.md](MISSION.md)** (this repo prepares spans for replayt-oriented workflows; **`replayt`** is not a runtime library dependency), **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (import boundary and dev pin), **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (**`ReadableSpan`** → **`PreparedSpanRecord`**), **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (where to track **replayt** and OpenTelemetry releases), and **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Not a lever on core”).

## 1. Goals

- Give **contributors** and **automation** (for example LLM-assisted reviews) enough **in-repo** context to reason about the **OpenTelemetry Python SDK → exporter → replayt-prep** story **without** assuming network access to upstream sites.
- Keep the tree **small** and **legally clear**: prefer **curated** excerpts and **canonical** deep links over full-site mirrors.
- Make **maintenance** explicit so snapshots do not silently rot or violate upstream license expectations.

## 2. Directory and presence (normative)

- All material for this backlog lives under **`docs/reference-documentation/`** at the repository root (same path the root **`README.md`** already names in the project layout table).
- After the Builder completes this backlog, the directory **MUST** exist and **MUST NOT** be empty: it contains **`README.md`** per §3 and at least **two** additional **`.md`** files that satisfy §4.1 (**OpenTelemetry** index + **replayt** index), unless a future spec revision explicitly merges those roles into fewer files with the same topical coverage.
- The folder remains **documentation-only**: no **`import`** hooks, no runtime code paths, no changes to **`[project].dependencies`** solely to satisfy this spec.

## 3. Folder README (normative)

**`docs/reference-documentation/README.md`** MUST exist and MUST include clearly labeled sections (headings or equivalent) that cover:

### 3.1 Licensing and attribution

- State that files in the folder may **quote** or **summarize** upstream documentation and that **this repository’s** license (see root **`LICENSE`** if present) applies to **original** prose written here, **not** necessarily to **verbatim** third-party text.
- For **each** upstream **verbatim** excerpt (see §4.2), either:
  - point to the **specific** file in this folder that carries the mandatory **attribution block** per §6, **or**
  - if the tree uses **stub-only** pages (§4.1), state clearly that there are **no** verbatim upstream copies and that readers should rely on the linked sources for license terms.
- **MUST NOT** present the README as legal advice; **MAY** point to upstream **LICENSE** URLs or PyPI **classifiers** for OpenTelemetry and **replayt**.

### 3.2 Scope (in / out)

- **In scope:** Integration-oriented context for this package: OpenTelemetry **trace** / **export** concepts used by **`ReplaytSpanExporter`**, and **replayt** positioning sufficient to understand why **`replayt`** stays off runtime deps and how **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** fits.
- **Out of scope:** Full mirrors of **opentelemetry.io**, the entire **opentelemetry-python** repository, or **replayt**’s full product documentation; vendoring generated API docs for every symbol; replacing **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** or **[docs/MISSION.md](MISSION.md)** as the canonical policy source.

### 3.3 Refresh policy

- **When to refresh:** When **`pyproject.toml`** bumps **OpenTelemetry** lower bounds, the **`replayt`** **`dev`** lower bound, or when maintainers observe that linked upstream URLs or quoted behavior are **materially** wrong for this repo’s contract.
- **Who:** Maintainers (or contributors via PR) following the same change-set discipline as **`COMPATIBILITY.md`** (update references in the **same** maintenance pass as pin changes when integration behavior is affected).
- **How:** Prefer **updating stub links** and **short** excerpt refreshes over growing the folder; if a snapshot is dropped in favor of links-only, **remove** stale verbatim text rather than leaving contradictory copies.

## 4. Content strategies (normative)

The Builder **MAY** mix both strategies below; the combination MUST satisfy §5.

### 4.1 Stub index pages (link-first)

- At least **one** markdown file (for example **`opentelemetry-python.md`** or **`index-opentelemetry.md`**) MUST act as an **index**: **canonical `https://` links** (no bare paths) to **official** OpenTelemetry Python documentation or repositories, focused on:
  - **Tracing** / **`TracerProvider`** / **processors** / **exporters** concepts relevant to **`SpanExporter`** and span lifecycle.
  - The **`opentelemetry-python`** distribution surface this repo depends on (**`opentelemetry-api`**, **`opentelemetry-sdk`**) — link to **readthedocs** or **`opentelemetry.io`** sections that describe those packages, not unofficial wikis.
- At least **one** markdown file (for example **`replayt.md`** or **`index-replayt.md`**) MUST act as an **index** for **replayt**: **PyPI** project URL **[https://pypi.org/project/replayt/](https://pypi.org/project/replayt/)**, plus any **official** project links shown on PyPI (source, changelog) when available. The page SHOULD cross-link **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §5 for release tracking.
- Each stub index MUST include **one short** (roughly 5–15 lines) **maintainer-written** summary in **this repo’s words** explaining why the link matters for **`replayt-otel-span-exporter`** (so the file is not **only** a list of URLs).

### 4.2 Bounded markdown snapshots (optional excerpts)

- If the Builder includes **verbatim** upstream text (quotes, copied tutorial paragraphs, CLI help, docstrings copied as documentation), each file that contains such text MUST start with an **attribution block** per §6.
- **Bounds:** Per-file **verbatim** third-party text SHOULD stay under **~800 lines** and **~60 KiB** (UTF-8) unless maintainers explicitly justify a larger excerpt in the folder README §3.3 refresh notes for that revision. The **entire** **`docs/reference-documentation/`** tree SHOULD stay under **~300 KiB** total unless a maintainer documents why a one-time larger drop was needed (for example a single upstream LICENSE copy).
- Snapshots MUST be **trimmed** to passages that help this integration (for example **`SpanExporter`** interface description, export result semantics) — not whole upstream guides.

### 4.3 Index files vs verbatim snapshot files (normative)

The backlog title mentions **snapshot** markdown; **§4.1 stub indexes** (deep links + maintainer summaries, no verbatim upstream copy) **fully satisfy** the backlog when combined with §3 and §5 — **snapshots** (§4.2) are **optional** unless a separate backlog makes them mandatory.

**Coupling to `tests/test_reference_documentation.py`:** As of the normative contract, that module requires the sentences **`## Licensing and attribution`**, **`## Scope (in / out)`**, and **`## Refresh policy`** (case-insensitive) in the folder **README**, and requires **`opentelemetry-python.md`** and **`replayt.md`** each to contain the exact line **`No third-party verbatim excerpts in this file.`** plus canonical **`https://`** links and §5 keywords. Therefore:

- **Preferred (no test edits):** Keep **`opentelemetry-python.md`** and **`replayt.md`** **stub-only**. Place any **verbatim** upstream excerpts in **additional** **`.md`** files (same directory or a subdirectory such as **`snapshots/`**), each with a §6 attribution block. The existing total-size assertion applies to **all** **`*.md`** under **`docs/reference-documentation/`**.
- **Alternative:** Embed verbatim text in **`opentelemetry-python.md`** and/or **`replayt.md`**. The Builder **MUST** update **`tests/test_reference_documentation.py`** in the **same** change set: drop or replace the stub-only line assertion for affected paths and add checks that §6 **attribution** fields (**`Source:`**, **`License:`**, snapshot date) appear in every file that contains verbatim upstream text.

## 5. Topical coverage (normative)

Collectively, the markdown files in **`docs/reference-documentation/`** MUST make the following discoverable **from the tree** (by in-file text or by links opened from the index pages):

| Topic | Minimum bar |
| ----- | ------------- |
| **OpenTelemetry Python exporter pattern** | How a **`SpanExporter`** participates in export (batch vs simple processor is optional detail; link or excerpt MUST mention **export** and **SDK** relationship). |
| **Span / trace data model at the boundary** | That spans carry **attributes** and **identifiers** relevant to **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** (**`replayt.workflow_id`**, **`replayt.step_id`**) — by link to OpenTelemetry **attributes** / **semantic conventions** docs or by maintainer summary with links. |
| **replayt as upstream** | That **replayt** is a **separate** PyPI distribution consumed in **this** repo **only** on the **`dev`** / CI path for boundary tests per **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** — not implied as a runtime dep of the exporter wheel. |

## 6. Licensing and attribution (normative)

For any file containing **verbatim** third-party documentation:

- **Attribution block** at the **top** of the file (after an optional single-line title), including:
  - **Source:** stable URL to the page or section (versioned URL **preferred** when upstream provides it).
  - **Retrieved / snapshot date:** ISO **YYYY-MM-DD** and optional upstream **commit** or **release tag** if the text came from GitHub.
  - **License:** name or “see upstream” pointer (for example Apache-2.0 for OpenTelemetry projects, or the license **replayt** declares on PyPI / its repository).
- **MUST NOT** strip license headers that upstream requires to accompany the excerpt.

For **stub-only** files with no verbatim third-party text, a short note **“No third-party verbatim excerpts in this file.”** under the title is enough.

## 7. Cross-links from root `README` (normative)

When this backlog is satisfied, the root **`README.md`** MUST:

- In the **Reference documentation** section, state that the folder is **present** and point readers to **`docs/reference-documentation/README.md`** for licensing, scope, and refresh policy, and to **`docs/SPEC_REFERENCE_DOCUMENTATION.md`** (this file) as the **Builder contract**.
- Add rows to the **Project layout** table (or equivalent inventory) for **`docs/reference-documentation/`** and **`docs/SPEC_REFERENCE_DOCUMENTATION.md`** so the folder and its normative spec both appear in the root index.

Until the Builder lands the folder, the README **MAY** keep wording that the checkout does not yet include the tree; the Builder MUST replace that with the above in the same change set that adds **`docs/reference-documentation/`**.

## 8. CI and automated tests (normative)

- **Default CI** (see **[docs/CI_SPEC.md](CI_SPEC.md)** §5) runs **`tests/test_reference_documentation.py`** with the full suite. That module performs **local** checks (no outbound HTTP): folder **README** sections for licensing, scope, and refresh policy; stub index disclaimers, canonical **`https://`** links, and keywords tied to §5; total tree size vs §4.2 guidance; root **README** §7 (**Reference documentation** section + project layout rows); and that **CI_SPEC** still names the test module. Behavior is aligned with **§4.3** (stub-only index files vs verbatim in separate files vs test updates).
- **Optional follow-up:** A later backlog **MAY** add non-network or allow-listed **link liveness** checks; if so, update **[docs/CI_SPEC.md](CI_SPEC.md)** §5 in the **same** change set.

## 9. Verifiable acceptance checklist

### 9.0 Backlog: seed `docs/reference-documentation/` (normative)

These criteria restate the Mission Control backlog **“Seed `docs/reference-documentation/` with replayt + OTel snapshot markdown”** (**dda05c31-9820-45d0-9e56-e58625f1686f**) body into **testable** requirements. **Conformance** is demonstrated by **`tests/test_reference_documentation.py`** (no outbound HTTP), manual inspection of **`docs/reference-documentation/`**, and root **`README.md`** §7 when the folder is first landed.

1. **`docs/reference-documentation/README.md`** satisfies **§3** (licensing and attribution; scope **in / out**; refresh policy), including explicit **out of scope** language so this folder does not replace **COMPATIBILITY** or **MISSION**.
2. **OpenTelemetry Python** and **replayt** each have a dedicated index **`.md`** under the folder satisfying **§4.1** and **§5** (canonical **`https://`** links, maintainer-written “why this matters” prose, and discoverability of exporter / triage / dev-only **replayt** story).
3. **License-appropriate content:** Any **verbatim** upstream text satisfies **§4.2** and **§6**; **stub-only** trees state the no-verbatim posture per **§3.1** and the index disclaimer per **§6** (last paragraph).
4. **Bounded size:** The tree respects **§4.2** size guidance (enforced in CI by total **`*.md`** size under **`docs/reference-documentation/`**).
5. Root **`README.md`** satisfies **§7** once the folder is present (reference section + project layout rows for **`docs/reference-documentation/`** and **`docs/SPEC_REFERENCE_DOCUMENTATION.md`**).

**Note:** If the checkout **already** satisfies §9.2 before this backlog starts, the Builder’s remaining work may be **verification only**, optional **§4.2** excerpts in **additional** files, or **README** tweaks — still subject to **§4.3** and CI.

### 9.1 Spec lead (reference-documentation backlog — contract landed)

1. This **`SPEC_REFERENCE_DOCUMENTATION.md`** file exists and matches **[docs/MISSION.md](MISSION.md)** / **[docs/CI_SPEC.md](CI_SPEC.md)** pointers.
2. Root **`README.md`** lists **`docs/SPEC_REFERENCE_DOCUMENTATION.md`** in the **Project layout** table and points to it from the **Reference documentation** section.

### 9.2 Builder (folder populated — full backlog “done”)

1. **`docs/reference-documentation/`** exists with **`README.md`** covering §3.1–§3.3.
2. At least **two** additional **`.md`** files (or one index split into clear parts) satisfy §4.1 (**replayt** index + **OpenTelemetry** index).
3. §5 topics are **findable** without leaving the repository for readers who accept following **in-repo** `https://` links from those pages.
4. Any **verbatim** upstream excerpts include §6 attribution blocks and respect §4.2 size guidance.
5. Root **`README.md`** satisfies §7 (replaces “not yet included” wording for the folder).
