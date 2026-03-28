# CI pipeline specification

This document refines the backlog item **“Set up CI pipeline for automated testing”** into testable requirements. Implementation belongs in **`.github/workflows/`** and supporting config; this file is the contract for what “done” means.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| CI workflow file exists | [§1 Workflow present](#1-workflow-present) |
| Tests run on PR and push | [§2 Triggers](#2-triggers) |
| CI passes with current code | [§7 Green mainline and workflow success](#7-green-mainline-and-workflow-success) |

The rows below expand those three bullets into checks a human or gate phase can verify without guessing.

**Replayt integration tests:** The **`test`** job satisfies §5 here and meets **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (install path includes **`replayt`** for default **`pytest`**).

## Goals

- Run automated tests on every relevant **push** and **pull_request** so regressions are caught before merge.
- Use the same **Python compatibility window** and **dependency installation path** as local development (`pyproject.toml`), so CI failures are reproducible locally.
- Keep **documented supported versions** (Python, OpenTelemetry, **replayt** on the **`dev`** path) consistent with **[docs/COMPATIBILITY.md](COMPATIBILITY.md)**; update that file when the matrix or pins change.

## Acceptance criteria

### 1. Workflow present

At least one workflow file under **`.github/workflows/`** (for example **`ci.yml`**) defines a job that runs the test suite.

**Verify:** The file is committed on the default branch and appears under **Actions** (or the host’s equivalent) as a workflow.

### 2. Triggers

The workflow runs on **`push`** and **`pull_request`** for the branches this repository integrates on. As of this writing that includes **`master`** and the Mission Control integration pattern **`mc/**`** (adjust if the default branch or naming changes—update this doc in the same change).

**Branch filters:** **`pull_request`** events must target **`master`** or **`mc/**`** so PRs into those integration lines run CI. **`push`** events must include **`master`** and **`mc/**`** so direct pushes run CI.

**Supplementary:** **`workflow_dispatch`** is allowed for manual reruns; it does not replace the push/PR requirement above.

### 3. Python versions match the package

CI uses only Python versions that satisfy **`[project].requires-python`** in **`pyproject.toml`** (currently **`>=3.11`**). The job matrix (or single version) must not include interpreters the project metadata excludes, or CI will fail at install time in a confusing way.

**Tomllib validation:** Any step that parses **`pyproject.toml`** with **`tomllib`** requires **Python ≥ 3.11**, which matches the minimum in **`requires-python`**.

### 4. Dependencies from the project

Before tests, install the package in editable mode with dev extras, matching contributor quick start:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Do not rely on a hand-maintained `requirements-ci.txt` unless the project later adds one and documents it here.

**Verify:** The workflow does not install ad hoc package lists that bypass **`pyproject.toml`** for the main test path.

### 5. Tests executed

**`pytest`** is run from the repository root so all collected tests run. Today tests live under **`tests/`**; if **`tests/integration/`** or similar is added later, it remains part of default discovery unless explicitly excluded.

**Current layout (informative):** The suite includes module smoke, dependency checks (e.g. **`tests/test_init.py`**, **`tests/test_dependencies.py`**, **`tests/test_compatibility_contract.py`** for **`pyproject.toml`** / **`docs/COMPATIBILITY.md`** / **`ci.yml`** alignment, **`tests/test_release_metadata.py`** for PEP 440 **alpha** **`[project].version`**, changelog headings, and **`tests/test_release_packaging.py`** for **`python -m build`**, **`twine check`**, and clean-venv wheel install smoke per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §2–§5), exporter skeleton coverage (**`tests/test_exporter.py`**, **`tests/test_records.py`**, **`tests/test_redaction.py`**) per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §4 and the **§6 verifiable acceptance checklist**, export failure behavior and tests per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** **§6** and **§7**, triage metadata and attribute redaction tests per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §5, optional **approval / audit hook** tests per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** §8 in **`tests/test_exporter.py`**, and **`tests/integration/`** for API-boundary checks. **`tests/integration/test_opentelemetry_api_usage.py`** covers the OpenTelemetry trace API only. **`tests/integration/test_replayt_boundary.py`** imports **`replayt`** per **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**; other integration files that call **`replayt`** MUST follow the same spec. **README usage example:** **`tests/test_readme_usage_example.py`** loads **`tests/readme_usage_example_snippet.py`** per **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §4; if either filename changes, update this sentence in the same maintenance pass. CI runs the full **`pytest`** command in §5 with an install that includes **`replayt`** via the **`dev`** extra (see that spec). New tests stay in default **`pytest`** discovery unless this doc is updated. Treat this as the minimal “unit + integration” bar (see §6).

**CI command (must stay equivalent unless this doc is updated):** after install,

```bash
pytest --cov=replayt_otel_span_exporter --cov-report=xml
```

### 6. “Unit” and “integration” in this repo

The backlog asks for both. Until the tree is split, **all pytest-collected tests** under **`tests/`** satisfy the requirement. If the suite grows, prefer either:

- directories such as **`tests/unit/`** and **`tests/integration/`**, or  
- markers (`pytest.mark.unit` / `pytest.mark.integration`) with documented invocations,

and ensure CI runs the full suite (or document a deliberate subset in this file).

### 7. Green mainline and workflow success

**Definition — “CI passes”:** A push or PR that triggers the workflow must produce a **successful** workflow run: **every job** in **`.github/workflows/ci.yml`** completes without failure (no job-level failure and no failed required step). Today that includes at least **`test`** and **`supply-chain`**; if jobs are added or marked advisory, update this section in the same change.

**Default branch:** The same workflow must be **green** on the current **`master`** (or default branch) tip for the canonical paths above.

**Codecov:** Upload uses **`fail_ci_if_error: false`** so missing tokens or fork PRs do not fail the workflow; coverage still uploads when Codecov accepts the report.

## Optional jobs (recommended, not part of the minimal three backlog bullets)

These align with **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Observable automation”) and existing docs:

- **Lint:** `ruff check` on **`src/`** and **`tests/`** using the version pinned in **`[project.optional-dependencies].dev`** — **not** present as a separate job in **`ci.yml`** today; add when the team wants lint gating in CI.
- **Supply chain:** Implemented as job **`supply-chain`**: **`pip-audit`** with ignore rules documented in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**. This job counts toward [§7](#7-green-mainline-and-workflow-success).

## Coverage and third-party upload steps

If the workflow runs **`pytest --cov=...`** or uploads coverage (e.g. Codecov), then **`pytest-cov`** (or an equivalent documented tool) MUST be listed in **`[project.optional-dependencies].dev`** so local runs and CI use the same stack. If the project chooses not to track coverage in CI, drop the coverage flags and upload steps instead of implying a dependency that is not declared.

## Non-goals (this backlog)

- **Release publishing automation** in this workflow file (the **“Set up CI pipeline”** backlog does not require upload jobs or PyPI secrets). Requirements for the **“Publish first alpha release”** backlog live in **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**; if maintainers add a **`release`** or **`publish`** job later, update this document’s **Reference fingerprint** and §7 in the same change.
- Deployment or secret-dependent integration tests against live services beyond **`pip-audit`** / install steps already described.
- Defining replayt upstream release policy (see mission and design docs).

## Implementation notes for Builder / Maintainer

When **`pyproject.toml`** changes **`requires-python`** or dev dependencies, update the workflow and this document in the same maintenance pass so they stay aligned.

### Reference fingerprint (reconcile when editing CI)

**Current** **`.github/workflows/ci.yml`** includes:

- **Default `GITHUB_TOKEN` permissions:** workflow-level **`permissions: contents: read`** (least privilege).
- **`test`**: **`actions/checkout@v3`**, **`actions/setup-python@v4`**, matrix **`python-version: ["3.11", "3.12"]`**, **`tomllib`** parse of **`pyproject.toml`**, **`pip install -e ".[dev]"`**, **`pytest --cov=replayt_otel_span_exporter --cov-report=xml`**, **`codecov/codecov-action@v3`** with **`./coverage.xml`** and **`fail_ci_if_error: false`**.
- **`supply-chain`**: same Python matrix, checkout/setup/validate/install, then **`pip-audit --ignore-vuln CVE-2026-4539 --ignore-vuln CVE-2025-69872 --desc`**.
- **`[project.optional-dependencies].dev`** includes **`build`** and **`twine`** so **`tests/test_release_packaging.py`** can run **`python -m build`** and **`twine check`** in CI.

Update this subsection when jobs, pins, or commands diverge.

### Known drift

- **Lint job:** Recommended in [Optional jobs](#optional-jobs-recommended-not-part-of-the-minimal-three-backlog-bullets) but **not** implemented as its own job; **`ruff`** remains available via **`[dev]`** for local use.
- **Otherwise:** The **test** matrix matches **`requires-python`** (**3.11** and **3.12**), **`pytest-cov`** is in **`[project.optional-dependencies].dev`**, and **`pytest --cov`** matches §5. Update this subsection whenever **`pyproject.toml`** or **`.github/workflows/ci.yml`** diverges from the acceptance criteria above.
