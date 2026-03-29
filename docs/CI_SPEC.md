# CI pipeline specification

This document refines the backlog item **“Set up CI pipeline for automated testing”** into testable requirements. Implementation belongs in **`.github/workflows/`** and supporting config; this file is the contract for what “done” means.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| CI workflow file exists | [§1 Workflow present](#1-workflow-present) |
| Tests run on PR and push | [§2 Triggers](#2-triggers) |
| CI passes with current code | [§7 Green mainline and workflow success](#7-green-mainline-and-workflow-success) |

The rows below expand those three bullets into checks a human or gate phase can verify without guessing.

**Expand CI matrix to Python 3.13** (separate backlog):

| Backlog acceptance theme | Satisfied by (this doc) |
| ------------------------- | ------------------------ |
| Add **3.13** to **`test`** and **`supply-chain`** when dependencies allow | [§3.1 Python 3.13 matrix expansion](#31-python-313-matrix-expansion-normative-backlog) |
| Update reference fingerprint + **COMPATIBILITY** caveats (**pip-audit**, **`replayt`**, OTel resolution) | §3.1 items 5–6, **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4.1 |

**Replayt integration tests:** The **`test`** job satisfies §5 here and meets **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (install path includes **`replayt`** for default **`pytest`**). **Pin bumps:** Validating a higher (or lower) **`replayt`** lower bound on the **`dev`** extra is **merging a green `test` job** on every Python matrix cell after **`pip install -e ".[dev]"`**: full **`pytest`** MUST collect and pass **`tests/integration/test_replayt_boundary.py`**. Normative steps and the maintainer doc pass live in that spec **[§5.1](SPEC_REPLAYT_INTEGRATION_TESTS.md#51-how-replayt-pin-bumps-are-validated-in-ci-normative)**.

**Python 3.13 matrix expansion:** Backlog **“Expand CI matrix to Python 3.13 with documented compatibility fingerprint”** is normative in [§3.1](#31-python-313-matrix-expansion-normative-backlog); it extends **`test`** / **`supply-chain`** matrices, **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4 / §4.1, and the **Reference fingerprint** below.

**OpenTelemetry runtime pins:** Backlog **“Document OpenTelemetry upper-bound or float policy in pyproject and COMPATIBILITY”** — default install has **no** committed lockfile; **`opentelemetry-api`** / **`opentelemetry-sdk`** **float** to newest compatible **1.x** releases satisfying **`pyproject.toml`** lower bounds on each CI run. Normative policy and integrator guidance: **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**; compatibility matrix context: **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §3.1.

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

### 3.1 Python 3.13 matrix expansion (normative backlog)

**Backlog:** Expand CI matrix to Python 3.13 with documented compatibility fingerprint.

**Objective:** When the **`dev`** stack (**`replayt`**, OpenTelemetry transitives, **`pip-audit`**, **`pytest`**, etc.) supports **Python 3.13** on **`ubuntu-latest`** in GitHub Actions, default CI MUST exercise **3.13** alongside **3.11** and **3.12** on every matrix cell that today runs **3.11** and **3.12**, so the proven contract in **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4 matches **`.github/workflows/ci.yml`**.

**Acceptance criteria** (one focused change set unless Mission Control splits work):

1. **Workflow matrices (`test` and `supply-chain`):** **`.github/workflows/ci.yml`** includes **`"3.13"`** in each **`python-version:`** list that today lists **3.11** and **3.12**, and **`test`** / **`supply-chain`** matrices stay aligned (same Python set).
2. **`requires-python`:** **3.13** MUST remain within **`[project].requires-python`** (today **`>=3.11`**). Do not narrow **`requires-python`** in a way that drops **3.11** or **3.12** unless a separate backlog approves it.
3. **Install + pytest bar:** On **3.13**, **`pip install -e ".[dev]"`** (§4) then **`pytest --cov=replayt_otel_span_exporter --cov-report=xml`** (§5) succeed end-to-end, including default collection of **`tests/integration/test_replayt_boundary.py`** when **`replayt`** is installed via **`[dev]`**.
4. **`supply-chain` + `pip-audit`:** The **3.13** cell runs the same **`pip-audit`** invocation documented in the **Reference fingerprint** (including **`--ignore-vuln`** flags). Any **new** ignores for **3.13-only** transitives MUST be recorded in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** with rationale in the same change set.
5. **Compatibility doc:** Update **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §2 (**Python** row), §4 (matrix table), and §4.1 so integrators see **3.13** in the exercised set and any **3.13**-specific notes for **OpenTelemetry resolution**, **`replayt` / dev pins**, and **`pip-audit`** (cross-link **DEPENDENCY_AUDIT** for CVE policy).
6. **Reference fingerprint (this doc):** Update the **Reference fingerprint** subsection under **Implementation notes for Builder / Maintainer** so matrix lines list **`3.11`**, **`3.12`**, and **`3.13`**, and refresh **Known drift** / **Otherwise** bullets if needed.
7. **Contract test:** Update **`tests/test_compatibility_contract.py`** so the expected Python set matches **COMPATIBILITY.md** §4 and **`ci.yml`** (once **`ci.yml`** lists all three, that means extending the assertion to **`{"3.11", "3.12", "3.13"}`**). Do not leave docs and contract tests out of sync.

**Blocked / “when dependencies allow”:** If **`pip install -e ".[dev]"`**, **`pytest`**, or **`pip-audit`** cannot succeed on a new interpreter without policy changes this repo will not take in the same item, document the **blocker** (step, package, error class) under **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4.1 and **do not** widen **`ci.yml`** until a follow-up unblocks it.

### 4. Dependencies from the project

Before tests, install the package in editable mode with dev extras, matching contributor quick start:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Do not rely on a hand-maintained `requirements-ci.txt` unless the project later adds one and documents it here.

**OpenTelemetry resolution (informative):** This path does **not** pin **`opentelemetry-api`** / **`opentelemetry-sdk`** to exact versions. **`pip`** selects the **latest** releases that satisfy **`[project].dependencies`** lower bounds and remain compatible with **`[dev]`** transitives, so **new OTel minors** are picked up on routine CI installs until maintainers change floors or constraints. See **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**.

**Verify:** The workflow does not install ad hoc package lists that bypass **`pyproject.toml`** for the main test path.

### 5. Tests executed

**`pytest`** is run from the repository root so all collected tests run. Today tests live under **`tests/`**; if **`tests/integration/`** or similar is added later, it remains part of default discovery unless explicitly excluded.

**Current layout (informative):** The suite includes module smoke, dependency checks (e.g. **`tests/test_init.py`**, **`tests/test_dependencies.py`**, **`tests/test_compatibility_contract.py`** for **`pyproject.toml`** / **`docs/COMPATIBILITY.md`** / **`ci.yml`** alignment (including OpenTelemetry runtime **no upper `<` cap** per **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**), **`tests/test_reference_documentation.py`** for **`docs/reference-documentation/`** per **[docs/SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**, **`tests/test_release_workflow_contract.py`** for **`release.yml`** / §8 optional OIDC release workflow, **`tests/test_release_metadata.py`** for PEP 440 **alpha** **`[project].version`**, changelog headings, and **`tests/test_release_packaging.py`** for **`python -m build`**, **`twine check`**, and clean-venv wheel install smoke per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §2–§5), exporter skeleton coverage (**`tests/test_exporter.py`**, **`tests/test_records.py`**, **`tests/test_redaction.py`**) per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §4 and the **§6 verifiable acceptance checklist**, export failure behavior and tests per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** **§6** and **§7** (including **§5.4** bounds / control stripping and **§6** items **4–6** once the **“Audit exporter logging for injection and oversized fields on failure paths”** backlog is implemented), triage metadata and attribute redaction tests per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §5, optional **approval / audit hook** tests per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** §8 in **`tests/test_exporter.py`** (informative production patterns for those hooks live in **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** and are **not** CI-tested), and **`tests/integration/`** for API-boundary checks. **`tests/integration/test_opentelemetry_api_usage.py`** covers the OpenTelemetry trace API only. **`tests/integration/test_replayt_boundary.py`** imports **`replayt`** per **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (including **import / IR contract** and **collection reliability** in that spec §3–§5 and §5.1); other integration files that call **`replayt`** MUST follow the same spec. **README usage example:** **`tests/test_readme_usage_example.py`** loads **`tests/readme_usage_example_snippet.py`** per **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §4; if either filename changes, update this sentence in the same maintenance pass. **`scripts/`** OTel → prepared-record demo: **`tests/test_scripts_otel_prepared_demo.py`** proves **`scripts/otel_to_prepared_demo.py`** per **[docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** §6 once the Builder adds both files; if the test module name changes, update this sentence in the same maintenance pass. **`tests/test_readme_integrator_install.py`** guards integrator **`pip install`** lines and **`[project].readme`** for release metadata (**[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §2.1). CI runs the full **`pytest`** command in §5 with an install that includes **`replayt`** via the **`dev`** extra (see that spec). New tests stay in default **`pytest`** discovery unless this doc is updated. Treat this as the minimal “unit + integration” bar (see §6).

**Reference docs tree:** **`docs/reference-documentation/`** is specified in **[docs/SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**. **`tests/test_reference_documentation.py`** checks that the folder **README** covers licensing, scope, and refresh policy, that stub index pages include canonical **`https://`** links and maintainer summaries, and that the tree stays within the spec’s size guidance. That module is part of default **`pytest`** discovery like other contract tests under **`tests/`**.

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

## 8. Optional release workflow (OIDC trusted publishing)

This section is the normative contract for **`.github/workflows/release.yml`**. The workflow is **optional**: it does **not** count toward [§7](#7-green-mainline-and-workflow-success) unless the organization adds the **`Release`** workflow (or a job from it) as a **required** check. Default merge health remains **`.github/workflows/ci.yml`**.

Implementation file: **`.github/workflows/release.yml`**. Contract tests: **`tests/test_release_workflow_contract.py`**.

### 8.1 Triggers and guards

- **`workflow_dispatch`:** Maintainers start a run from the Actions UI and choose the ref (tag or branch) to build and upload.
- **`push` of tags `v*`:** Pushing a version tag (for example **`v0.2.0a1`** for **`[project].version` `0.2.0a1`**) triggers a publish run for that ref.
- Ordinary branch pushes (without a matching tag event) do **not** publish.
- **`concurrency`:** Group **`release-${{ github.workflow }}-${{ github.ref }}`** with **`cancel-in-progress: false`** so two runs for the same ref are not interleaved; a newer run may queue instead of canceling an in-flight publish.

### 8.2 Build, check, and upload steps

- **Install (publish job only):** **`python -m pip install --upgrade pip`**, then **`pip install "build>=1.2.0" "twine>=5.0"`**. Do **not** run **`pip install -e ".[dev]"`** on the publish job: the release runner must not pull **`replayt`** or other **`[dev]`** pins ([§8.6](#86-runtime-deps-and-replayt)).
- **Build:** **`rm -rf dist`**, then **`python -m build`** from the repository root (sdist + wheel).
- **Check:** **`twine check dist/*`** MUST succeed before upload.
- **Upload:** **`pypa/gh-action-pypi-publish@ed0c53931b1dc9bd32cbe73a98c7f6766f8a527e`** (pinned commit; corresponds to **`release/v1`** at pin time) uploads **`dist/*`** to **PyPI** using OIDC (see [§8.3](#83-oidc-and-secrets-policy)).

This sequence matches the pre-upload bar in **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §4 for teams that use this automation path.

### 8.3 OIDC and secrets policy

- **Workflow permissions:** **`contents: read`** and **`id-token: write`** on the publish job so GitHub can mint an OIDC token for trusted publishing. Do **not** store a long-lived **PyPI API token** in repository **Secrets** for the default PyPI path documented here.
- **PyPI trusted publishing** exchanges that OIDC identity for a short-lived upload credential; configuration details live on PyPI’s trusted-publisher docs.
- **Private indexes** (DevPI, Artifactory, etc.) often still need **long-lived credentials** or host-specific auth maintained outside this contract. OIDC as described here targets the **PyPI**-style flow.

### 8.4 GitHub Environment `pypi` and PyPI trusted publisher alignment

- **GitHub Environment name:** **`pypi`** (exact spelling). The publish job sets **`environment: name: pypi`**.
- **Repository settings:** Create an environment named **`pypi`**. Add **protection rules** if the org wants a human gate (required reviewers, wait timer, deployment branches) before the job runs and OIDC is minted.
- **On PyPI:** Register a **trusted publisher** for this repository that references:
  - the **GitHub repository** (owner/name),
  - workflow file **`release.yml`**,
  - the **GitHub Environment** **`pypi`**.  
  Names MUST match the workflow and settings above or uploads will fail at the registry.

### 8.5 Optional TestPyPI lane

This repository does **not** define a second job for **TestPyPI** in **`release.yml`**. If maintainers want a dry-run index, add a parallel trusted publisher + GitHub Environment (for example **`testpypi`**) and either a separate workflow file or an additional job, and extend **`tests/test_release_workflow_contract.py`** in the same change.

### 8.6 Runtime deps and replayt

**`replayt`** MUST remain only under **`[project.optional-dependencies]`** (for example the **`dev`** extra), not under **`[project].dependencies`**. The publish job’s minimal install ([§8.2](#82-build-check-and-upload-steps)) keeps **`replayt`** off the release runner and keeps the uploaded distributions aligned with runtime metadata.

### 8.7 Rollback and recovery expectations

| Situation | Recommended response |
| --------- | -------------------- |
| **Wrong files uploaded** | **Yank** the affected files on PyPI (or unpublish per index policy); cut a **new** version (bump **`[project].version`** and **CHANGELOG**) and publish from a **new tag** after fixing the tree. Do not reuse the same version for different artifacts. |
| **Bad release tag points at broken commit** | Move maintenance forward: fix on **`master`**, tag a **new** patch/prerelease version, and publish that tag. Optionally delete the erroneous tag locally and on the remote only if the team agrees (deleting tags does not remove published wheels). |
| **Run triggered by mistake** | **Disable** or **restrict** the **`pypi`** environment (remove approval, lock deployments), cancel the workflow if still running, and avoid pushing tags until the workflow is corrected. |
| **OIDC / trusted-publisher mismatch** | Fix **PyPI** trusted-publisher settings or **GitHub** environment/workflow file name so they match [§8.4](#84-github-environment-pypi-and-pypi-trusted-publisher-alignment); no repo secret is required for the PyPI OIDC path. |

These steps are operator guidance; registry and org policy may impose extra requirements.

## Optional jobs (recommended, not part of the minimal three backlog bullets)

These align with **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Observable automation”) and existing docs:

- **Lint:** `ruff check` on **`src/`** and **`tests/`** using the version pinned in **`[project.optional-dependencies].dev`** — **not** present as a separate job in **`ci.yml`** today; add when the team wants lint gating in CI.
- **Supply chain:** Implemented as job **`supply-chain`**: **`pip-audit`** with ignore rules documented in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**. This job counts toward [§7](#7-green-mainline-and-workflow-success).

## Coverage and third-party upload steps

If the workflow runs **`pytest --cov=...`** or uploads coverage (e.g. Codecov), then **`pytest-cov`** (or an equivalent documented tool) MUST be listed in **`[project.optional-dependencies].dev`** so local runs and CI use the same stack. If the project chooses not to track coverage in CI, drop the coverage flags and upload steps instead of implying a dependency that is not declared.

## Non-goals (this backlog)

- **Release publishing automation inside `ci.yml`:** The **“Set up CI pipeline”** backlog does not require upload jobs in the default PR workflow. Optional PyPI automation lives in **`release.yml`** and [§8](#8-optional-release-workflow-oidc-trusted-publishing). Release content requirements stay in **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**.
- Deployment or secret-dependent integration tests against live services beyond **`pip-audit`** / install steps already described.
- Defining replayt upstream release policy (see mission and design docs).

## Implementation notes for Builder / Maintainer

When **`pyproject.toml`** changes **`requires-python`** or dev dependencies, update the workflow and this document in the same maintenance pass so they stay aligned.

### Reference fingerprint (reconcile when editing CI)

**Current** **`.github/workflows/ci.yml`** includes:

- **Default `GITHUB_TOKEN` permissions:** workflow-level **`permissions: contents: read`** (least privilege).
- **`test`**: **`actions/checkout@v3`**, **`actions/setup-python@v4`**, matrix **`python-version: ["3.11", "3.12", "3.13"]`**, **`tomllib`** parse of **`pyproject.toml`**, **`pip install -e ".[dev]"`**, **`pytest --cov=replayt_otel_span_exporter --cov-report=xml`**, **`codecov/codecov-action@v3`** with **`./coverage.xml`** and **`fail_ci_if_error: false`**.
- **`supply-chain`**: same Python matrix as **`test`**, checkout/setup/validate/install, then **`pip-audit --ignore-vuln CVE-2026-4539 --ignore-vuln CVE-2025-69872 --desc`**.
- **`[project.optional-dependencies].dev`** includes **`build`** and **`twine`** so **`tests/test_release_packaging.py`** can run **`python -m build`** and **`twine check`** in CI.
- **§8 release / OIDC:** **`.github/workflows/release.yml`** — **`workflow_dispatch`** and **`push`** of tags **`v*`**; **`concurrency`** group **`release-${{ github.workflow }}-${{ github.ref }}`** with **`cancel-in-progress: false`**; job **`publish`** uses GitHub Environment **`pypi`**, **`permissions: contents: read`** and **`id-token: write`**, **`actions/checkout@v3`**, **`actions/setup-python@v4`** with **`python-version: "3.12"`**, **`pip install "build>=1.2.0" "twine>=5.0"`** (no **`pip install -e ".[dev]"`**), **`rm -rf dist`**, **`python -m build`**, **`twine check dist/*`**, then **`pypa/gh-action-pypi-publish@ed0c53931b1dc9bd32cbe73a98c7f6766f8a527e`** to **PyPI** (no TestPyPI job in-repo; maintainers may add a parallel trusted publisher + environment if needed per §8.4).

Update this subsection when jobs, pins, or commands diverge.

### Known drift

- **Lint job:** Recommended in [Optional jobs](#optional-jobs-recommended-not-part-of-the-minimal-three-backlog-bullets) but **not** implemented as its own job; **`ruff`** remains available via **`[dev]`** for local use.
- **Release workflow:** [§8](#8-optional-release-workflow-oidc-trusted-publishing) is implemented as **`release.yml`** (optional; not part of §7 merge gate unless required checks are added).
- **Otherwise:** The **test** / **`supply-chain`** matrix uses **3.11**, **3.12**, and **3.13** (all within **`requires-python`**), **`pytest-cov`** is in **`[project.optional-dependencies].dev`**, and **`pytest --cov`** matches §5. Update this subsection whenever **`pyproject.toml`** or **`.github/workflows/ci.yml`** diverges from the acceptance criteria above.
