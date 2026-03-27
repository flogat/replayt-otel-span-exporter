# CI pipeline specification

This document refines the backlog item **“Set up CI pipeline for automated testing”** into testable requirements. Implementation belongs in **`.github/workflows/`** and supporting config; this file is the contract for what “done” means.

## Goals

- Run automated tests on every relevant **push** and **pull_request** so regressions are caught before merge.
- Use the same **Python compatibility window** and **dependency installation path** as local development (`pyproject.toml`), so CI failures are reproducible locally.

## Acceptance criteria

1. **Workflow present**  
   At least one workflow file under **`.github/workflows/`** (for example **`ci.yml`**) defines a job that runs the test suite.

2. **Triggers**  
   The workflow runs on **`push`** and **`pull_request`** for the branches this repository integrates on. As of this writing that includes **`master`** and the Mission Control integration pattern **`mc/**`** (adjust if the default branch or naming changes—update this doc in the same change).

3. **Python versions match the package**  
   CI uses only Python versions that satisfy **`[project].requires-python`** in **`pyproject.toml`** (currently **`>=3.11`**). The job matrix (or single version) must not include interpreters the project metadata excludes, or CI will fail at install time in a confusing way.

4. **Dependencies from the project**  
   Before tests, install the package in editable mode with dev extras, matching contributor quick start:

   ```bash
   python -m pip install --upgrade pip
   pip install -e ".[dev]"
   ```

   Do not rely on a hand-maintained `requirements-ci.txt` unless the project later adds one and documents it here.

5. **Tests executed**  
   **`pytest`** is run from the repository root so all collected tests run. Today tests live under **`tests/`**; if **`tests/integration/`** or similar is added later, it remains part of default discovery unless explicitly excluded.

6. **“Unit” and “integration” in this repo**  
   The backlog asks for both. Until the tree is split, **all pytest-collected tests** under **`tests/`** satisfy the requirement. If the suite grows, prefer either:

   - directories such as **`tests/unit/`** and **`tests/integration/`**, or  
   - markers (`pytest.mark.unit` / `pytest.mark.integration`) with documented invocations,

   and ensure CI runs the full suite (or document a deliberate subset in this file).

7. **Green mainline**  
   The workflow is **required to pass** on the current **`master`** (or default branch) tip once implementation matches this spec—no failing steps for the canonical install-and-test path.

## Optional jobs (recommended, not part of the minimal three backlog bullets)

These align with **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Observable automation”) and existing docs:

- **Lint:** `ruff check` on **`src/`** and **`tests/`** using the version pinned in **`[project.optional-dependencies].dev`**.
- **Supply chain:** `pip-audit` with ignore rules documented in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**.

## Coverage and third-party upload steps

If the workflow runs **`pytest --cov=...`** or uploads coverage (e.g. Codecov), then **`pytest-cov`** (or an equivalent documented tool) MUST be listed in **`[project.optional-dependencies].dev`** so local runs and CI use the same stack. If the project chooses not to track coverage in CI, drop the coverage flags and upload steps instead of implying a dependency that is not declared.

## Non-goals (this backlog)

- Release publishing, deployment, or secret-dependent integration tests against live services.
- Defining replayt upstream release policy (see mission and design docs).

## Implementation notes for Builder / Maintainer

When **`pyproject.toml`** changes **`requires-python`** or dev dependencies, update the workflow and this document in the same maintenance pass so they stay aligned.

### Known drift (as of spec authoring)

The checked-in **`.github/workflows/ci.yml`** should be reconciled with this spec:

- The **test** job matrix may list Python versions **below** **`requires-python`**; those rows will fail `pip install -e .` until the matrix is aligned (e.g. **3.11** and **3.12** only).
- The **test** job may invoke **`pytest --cov=...`** without **`pytest-cov`** in **`dev`** dependencies; add the dependency or remove coverage from the command.

The **Spec gate** and **Builder** phases should treat the bullets in **Acceptance criteria** as authoritative and fix or justify any deviation.
