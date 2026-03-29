# Specification: Runnable `scripts/` OpenTelemetry → prepared-record demo

This document refines the backlog item **“Ship a runnable scripts/ demo beyond the README snippet test harness”** into testable requirements. **The script under `scripts/`** and **any new tests** that prove it belong in phase **3** (Builder); this file is the contract for what “done” means.

## Backlog traceability

| Original theme | Satisfied by (this doc) |
| ---------------- | ------------------------ |
| Runnable script under **`scripts/`** (beyond **`tests/readme_usage_example_snippet.py`**) | [§2 Script deliverable](#2-script-deliverable-normative), [§6 Checklist](#6-verifiable-acceptance-checklist) |
| Configures **`TracerProvider`**, emits spans with **`replayt.workflow_id`** / **`replayt.step_id`** | [§3 Required behavior](#3-required-behavior-normative) |
| Prints key **`PreparedSpanRecord`** fields | [§3.3 Printed fields](#33-printed-fields-normative) |
| Aligns with **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**; no **`replayt`** runtime dependency | [§4 Constraints](#4-constraints-normative), [§5 Documentation and demos](#5-documentation-and-demos-normative) |
| Documented invocation (README and/or **`scripts/`** README) | [§5 Documentation and demos](#5-documentation-and-demos-normative) |

**Related contracts:** The demo MUST use the public API and tracing pipeline patterns defined in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (§2, §3). Triage attributes **`replayt.workflow_id`** / **`replayt.step_id`** MUST follow **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**. The README quick-start example remains governed by **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)**; this script is an **additional** operator-facing entry point, not a replacement for **`tests/readme_usage_example_snippet.py`** or **`tests/test_readme_usage_example.py`**.

## 1. Goals

- Give **contributors and integrators** a **copy-paste runnable** path (shell + **`python …`**) that shows the full **SDK → exporter → `PreparedSpanRecord`** pipeline **without** importing **`replayt`**.
- Complement the **CI-proven** README snippet (**`tests/readme_usage_example_snippet.py`**) with a **script-shaped** demo: obvious **`scripts/`** location, **stdout** oriented for terminal use, and **clear exit codes** per **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Observable automation”).
- Keep the demo **small** and **maintainable**: one primary script file, no new runtime dependencies beyond what the package and **`SPEC_OTEL_EXPORTER_SKELETON.md`** already require.

## 2. Script deliverable (normative)

- The repository MUST include **exactly one** primary demo module at **`scripts/otel_to_prepared_demo.py`** (path relative to repository root). **MAY** add thin wrappers or shell helpers only if documented in the same change set and kept trivial.
- The file MUST be **executable as a module or script** from the repository root after a normal contributor install (**`pip install -e ".[dev]"`** per **[docs/CI_SPEC.md](CI_SPEC.md)** §4), for example:  
  **`python scripts/otel_to_prepared_demo.py`**  
  Document the **canonical** invocation in **[§5](#5-documentation-and-demos-normative)** surfaces; alternative forms (**`python -m …`**) are optional if the package layout supports them without contortion.
- The script MUST **not** be packaged as importable library API under **`src/`**; it is **contributor / operator** tooling only (no requirement to add it to **`[project].scripts`** console entry points unless a later backlog asks for it).

## 3. Required behavior (normative)

### 3.1 OpenTelemetry setup

- Configure a **`TracerProvider`** and register **`ReplaytSpanExporter`** via **`SimpleSpanProcessor`** or **`BatchSpanProcessor`** (pick **one** and stay consistent with tests).
- Use a **shared** **`list`** (or equivalent) passed into **`ReplaytSpanExporter(records=...)`** per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §2.2 so the script can inspect **`PreparedSpanRecord`** instances after export.
- Set the global tracer provider (**`trace.set_tracer_provider`**) for the duration of the demo and **restore** the previous provider in a **`finally`** block (same isolation pattern as **`tests/readme_usage_example_snippet.py`**) so repeated runs or test subprocesses do not leak global state.

### 3.2 Spans and triage metadata

- Start and end **at least one** non-root span with a **non-empty** name.
- On that span, set **at least one** arbitrary non-sensitive string attribute (for example **`app.demo`** or **`demo.operation`**) so **`PreparedSpanRecord.attributes`** is visibly non-empty.
- Set **`replayt.workflow_id`** and **`replayt.step_id`** on the span with **stable, fictional** string values (no secrets, no real LLM prompts; see §5). After export, the corresponding **`PreparedSpanRecord.workflow_id`** and **`PreparedSpanRecord.step_id`** MUST be non-**`None`** and match those attribute values per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**.

### 3.3 Printed fields (normative)

After **`provider.shutdown()`** (or equivalent flush), the script MUST print **human-readable** lines to **stdout** that allow a reader to verify the **intermediate representation** without reading Python objects. **At minimum**, stdout MUST include the **labels or unambiguous prefixes** for these **`PreparedSpanRecord`** fields (names per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §3):

| Field | Requirement |
| ----- | ------------- |
| **`name`** | Visible |
| **`trace_id`** | Visible, encoding consistent with §3 of the skeleton spec (lowercase hex, 32 chars for real spans) |
| **`span_id`** | Visible, encoding consistent with §3 of the skeleton spec (16 chars for real spans) |
| **`kind`** | Visible (enum **member name**, e.g. **`INTERNAL`**) |
| **`start_time_unix_nano`** | Visible |
| **`end_time_unix_nano`** | Visible |
| **`workflow_id`** | Visible (first-class triage field) |
| **`step_id`** | Visible (first-class triage field) |
| **`attributes`** | At least **one** key–value pair from the mapping shown (the non-triage demo attribute is enough) |

Pretty-printing (JSON, YAML, aligned columns) is allowed; **cryptic** one-line dumps are discouraged unless labels stay unambiguous.

### 3.4 Exit codes

- Exit **`0`** when the pipeline completes and printing succeeds.
- Exit **non-zero** when setup fails, no records are produced, or required fields are missing. **MAY** print a short error message to **stderr**.

## 4. Constraints (normative)

- **No `import replayt`** (or submodule thereof) anywhere in **`scripts/otel_to_prepared_demo.py`** or in tests that exist solely to prove this spec. Library-user parity matches **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §4.
- Imports from **`replayt_otel_span_exporter`** MUST use the **public** surface only (**`ReplaytSpanExporter`**, **`PreparedSpanRecord`**, **`__version__`** as needed) — same rule as the README example (**`SPEC_README_QUICK_START.md`** §3.1).
- **Do not** add **`replayt`** to **`[project].dependencies`**. Optional **`replayt`** for **`dev`** / integration tests remains governed by **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** only.
- The script MUST **not** send data to the network or write outside the process except **stdout** / **stderr**.

## 5. Documentation and demos (normative)

- **Invocation** MUST be documented in **at least one** of:
  - the repository root **`README.md`** (short subsection or bullet under **Quick start**, **Usage**, or **See also**), **or**
  - **`scripts/README.md`** (preferred if the root README is already crowded — then root README MUST still link to **`scripts/README.md`** with one line).
- Documentation MUST state:
  - prerequisite: contributor install **`pip install -e ".[dev]"`** (or equivalent **editable** install that pulls **`opentelemetry-*`** per **`pyproject.toml`**);
  - canonical command **`python scripts/otel_to_prepared_demo.py`** from the repository root;
  - that the demo does **not** require **`replayt`**.
- Any prose or sample values MUST follow **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** **LLM / demos**: no live secrets, no realistic API keys, no production workflow IDs.

## 6. Test contract (script MUST be proven in CI)

The backlog is **not** satisfied by manual runs alone.

- The Builder MUST add **at least one** automated test module collected by default **`pytest`** (recommended name **`tests/test_scripts_otel_prepared_demo.py`**). If the filename differs, update **[docs/CI_SPEC.md](CI_SPEC.md)** §5 in the same maintenance pass.
- The test MUST exercise the **same** end state as a human running the script:
  - **Preferred:** run **`python scripts/otel_to_prepared_demo.py`** as a **subprocess** from the repository root with the **same** interpreter / environment as **`pytest`**, assert **exit code 0**, and assert **stdout** contains **unambiguous** substrings or patterns for every field listed in [§3.3](#33-printed-fields-normative) (labels or values).
  - **Alternative:** import a **`main()`** (or equivalent) defined in the script module **only if** the script’s **`if __name__ == "__main__"`** block calls that entry point without extra side effects; the test MUST still validate the **printed** output (or captured print buffer) so formatting regressions are caught.
- The test MUST **not** `import replayt`.
- The test MUST run under **`pip install -e ".[dev]"`** like other unit tests.

**CI mapping:** **[docs/CI_SPEC.md](CI_SPEC.md)** §5 records the test module name (**`tests/test_scripts_otel_prepared_demo.py`** unless renamed in the same maintenance pass as that sentence).

## 7. Non-goals (this backlog)

- Shipping **`replayt`** payload conversion in the script (that remains **`tests/integration/test_replayt_boundary.py`** and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**).
- New **`SpanExporter`** features, approval hooks, or failure-injection scenarios — unless needed only to satisfy §3–§4 of this spec (keep the demo **happy-path**).
- Packaging the demo as a **`console_scripts`** entry point on PyPI (optional future backlog).

## 8. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for **“Ship a runnable scripts/ demo beyond the README snippet test harness”**.

1. **`scripts/otel_to_prepared_demo.py`** exists and runs per §2–§3 with exit codes per §3.4.
2. **No `replayt` import** in the script or its dedicated test module (§4).
3. **Documentation** satisfies §5 (README and/or **`scripts/README.md`** + root pointer if needed).
4. **`tests/test_scripts_otel_prepared_demo.py`** (or the name recorded in **`CI_SPEC.md`** §5) exists and passes under default **`pytest`** per §6.
5. **CHANGELOG** under **Unreleased** notes the new script and docs when the Builder delivers them (see root **`CHANGELOG.md`** policy).
