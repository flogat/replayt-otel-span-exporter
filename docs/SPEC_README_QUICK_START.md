# Specification: README quick start and usage example

This document refines the backlog item **“Create README quick start and usage example”** into testable requirements. **README text at the repository root** and **any new tests** that prove the documented example belong in phase **3** (Builder) unless this file only adjusts contracts; this spec is the contract for what “done” means.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| README includes quick start steps | [§2 Quick start](#2-quick-start-normative-for-readme) |
| Usage example provided and tested | [§3 Usage example](#3-usage-example-normative-for-readme), [§4 Test contract](#4-test-contract-readme-example-must-be-proven-in-ci) |
| Links to mission and design principles | [§5 Required links](#5-required-links-normative-for-readme) |

**Related contracts:** The example MUST use the public API and tracing pipeline patterns defined in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (§2, §4). It MUST stay consistent with **[docs/MISSION.md](MISSION.md)** scope: **`replayt`** is **not** a runtime dependency for library installs (see **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** for the dev/CI boundary). Triage attributes **`replayt.workflow_id`** / **`replayt.step_id`** on spans are **recommended** in prose and in the example where they illustrate **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**.

## 1. Goals

- Give **integrators** copy-paste **install** and **minimal Python** steps to attach **`ReplaytSpanExporter`** to the OpenTelemetry SDK and observe **`PreparedSpanRecord`** instances **without** importing **`replayt`**.
- Give **contributors** the same **venv + editable dev install** path documented in **[docs/CI_SPEC.md](CI_SPEC.md)** §4 so local setup matches CI.
- Make the **“replayt workflow”** story explicit in **documentation only** for the minimal example: this package **prepares** span-shaped data for downstream replayt-oriented consumers; the **full** boundary with **`replayt`** imports remains documented in **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** and **`tests/integration/test_replayt_boundary.py`** (Builder fixes any collection or runtime failures there under that spec — not a substitute for this README contract).

## 2. Quick start (normative for README)

The root **`README.md`** MUST include a **Quick start** section (heading text MAY be **`## Quick start`** or equivalent) that covers **both** paths below in **separate** subsections or clearly labeled bullet groups.

### 2.1 Library users (integrators)

- State **`requires-python`** from **`pyproject.toml`** (today **≥ 3.11**).
- Show installing the **distribution** from PyPI when published, using the **`[project].name`** hyphenated form readers expect on the command line: **`replayt-otel-span-exporter`** (for example **`pip install replayt-otel-span-exporter`**). If the package is not yet published, the README MUST say so briefly and point contributors to §2.2 instead of implying a broken install command. When an **alpha** or later release is published per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**, the README MUST be updated in the same maintenance pass so §2.1 reflects the live index (public PyPI or documented **`--index-url`** pattern for a private registry).
- When **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §5 verification has been run for a published version, the integrator subsection MUST include a **copy-paste** install line that **pins** that version — **`pip install replayt-otel-span-exporter==<published-version>`** — matching the **§5** install command (including index flags for private registries). For **PEP 440** prereleases on public PyPI, MAY also show **`pip install --pre replayt-otel-span-exporter`** as a secondary example when maintainers want “latest alpha” without a pin; unpinned **`pip install replayt-otel-span-exporter`** alone is **misleading** for alphas unless paired with **`--pre`** (pip does not select prereleases by default).
- MUST **not** instruct library users to add **`replayt`** solely to run the minimal exporter example.

### 2.2 Contributors and CI parity

- Document **venv creation** and activation (one line each for Unix-style shells; **one** Windows note is enough).
- Document **`python -m pip install --upgrade pip`** then **`pip install -e ".[dev]"`** from the repository root so it matches **[docs/CI_SPEC.md](CI_SPEC.md)** §4 verbatim in intent.

The existing one-line quick start in **`README.md`** today is **insufficient**: it MUST be expanded per §2.1–§2.2 and MUST sit **before** or **alongside** the usage example so first-time readers see install context immediately.

## 3. Usage example (normative for README)

### 3.1 Placement and format

- The root **`README.md`** MUST include a dedicated subsection (for example **`## Usage`** or **`### Usage example`**) containing a **fenced Python code block** that is **complete** for a reader who already performed §2 (imports, tracer setup, span lifecycle, buffer inspection).
- The block MUST be **minimal** (roughly one tracer, one span, one export) but **real**: it MUST use the **OpenTelemetry SDK** types that **`SPEC_OTEL_EXPORTER_SKELETON.md`** §4.1 relies on (for example **`TracerProvider`**, **`trace.set_tracer_provider`**, **`SimpleSpanProcessor`**, **`BatchSpanProcessor`** is optional — pick **one** processor and stay consistent with the test in §4).
- The block MUST **`import`** from the public package surface only: **`from replayt_otel_span_exporter import ReplaytSpanExporter, PreparedSpanRecord`** (or equivalent imports that **do not** bypass **`__all__`** without a documented reason).

### 3.2 Required behavior shown

- Construct **`ReplaytSpanExporter`** with a **shared** **`list`** passed as the records/buffer argument (name per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §2.2 — today **`records=`** on **`ReplaytSpanExporter`**).
- Register the exporter with a **`SimpleSpanProcessor`** (or the chosen processor) on the **`TracerProvider`**.
- Start and end **one** span with a **non-empty** name; set **at least one** string attribute. **SHOULD** set **`replayt.workflow_id`** and **`replayt.step_id`** on the span to demonstrate triage metadata (see **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**).
- Call **`trace.get_tracer(...)`**, **`with` / `start_as_current_span`**, end the span, then **`provider.shutdown()`** (or equivalent ordering that **flushes** the span to the exporter on the supported SDK path used in tests).
- After shutdown, assert or print **at least one** property from the first **`PreparedSpanRecord`** (for example **`name`** or **`trace_id`**) so readers see the IR shape.

### 3.3 Replayt workflow wording

- Within a short prose paragraph (inside or immediately after the usage section), explain that **`PreparedSpanRecord`** values are the **hand-off** for replayt-oriented workflows and that importing **`replayt`** is **not** required for the package’s **runtime** install — point to **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7 and **`tests/integration/test_replayt_boundary.py`** for the **concrete** boundary exercised in CI when **`replayt`** is installed via **`[dev]`**.

### 3.4 Documentation hygiene

- Examples MUST **not** embed live secrets, API keys, or real LLM prompts. If an example mentions models or agents, it MUST stay within **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** LLM / demos expectations.

## 4. Test contract (README example MUST be proven in CI)

The backlog phrase **“usage example provided and tested”** is **not** satisfied by manual review alone.

- The Builder MUST add **at least one** automated test module (recommended name **`tests/test_readme_usage_example.py`**) collected by **default** **`pytest`** from the repository root.
- That test MUST **programmatically** exercise the **same** tracer-provider + processor + **`ReplaytSpanExporter`** + span lifecycle + buffer inspection pattern as the README Python block (shared **helper function** in **`tests/`** or **`src`** is allowed if the README duplicates the calls — duplication MUST stay **in sync**; prefer a single **`tests/readme_usage_example_snippet.py`** or **`tests/_readme_example.py`** imported by the test **and** copied from / kept identical to README via maintainer discipline, **or** a helper function with a comment in README: “mirrors **`tests/test_readme_usage_example.py`**”).
- Assertions MUST fail if **`PreparedSpanRecord`** entries are missing after **`shutdown`**, if **name** / **trace_id** / **span_id** / **kind** / ordered timestamps violate **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §3–§4 expectations for a normal SDK span, or if **`replayt.workflow_id`** / **`replayt.step_id`** on the span are not reflected on the record when the example sets them.
- The test MUST **not** `import replayt` (library-user parity). It MUST run under **`pip install -e ".[dev]"`** like other unit tests.

**CI mapping:** **[docs/CI_SPEC.md](CI_SPEC.md)** §5 lists this module once it exists.

## 5. Required links (normative for README)

The root **`README.md`** MUST include **working relative** links from the repository root to:

| Link target | Purpose |
| ----------- | ------- |
| **`docs/MISSION.md`** | North-star scope, replayt role, CI summary pointers |
| **`docs/DESIGN_PRINCIPLES.md`** | Integration principles, “not a lever on core,” LLM/demo boundaries |

These MAY live in **Overview**, **Quick start**, or a short **See also** list; they MUST be **visible** without hunting only in the project layout table. (The README **already** links both in **Overview** — keep or strengthen so Spec gate / review can tick this criterion quickly.)

**Recommended (non-blocking):** Link **`docs/COMPATIBILITY.md`** near install instructions for version matrix context.

## 6. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for **“Create README quick start and usage example”**.

1. **Quick start** satisfies §2.1 and §2.2 (library vs contributor paths explicit).
2. **Usage** Python block satisfies §3 (public imports, shared buffer, real SDK pipeline, triage attributes **recommended**, **`replayt`** not required in the snippet).
3. **Links** to **`docs/MISSION.md`** and **`docs/DESIGN_PRINCIPLES.md`** satisfy §5.
4. **`tests/test_readme_usage_example.py`** (or the name recorded in **`CI_SPEC.md`** §5) exists and passes under default **`pytest`** per §4.
5. **CHANGELOG** under **Unreleased** notes user-visible README improvements when the Builder delivers them (see project **`CHANGELOG.md`** policy).

## 7. Non-goals (this backlog)

- Replacing **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** or **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** with README-only prose.
- Adding **`replayt`** to **`[project].dependencies`**.
- Full replayt workflow tutorials, storage backends, or deployment guides.
