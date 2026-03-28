# Specification: Publish first alpha release

This document refines the backlog item **“Publish first alpha release”** into testable requirements for maintainers and the Builder phase. **Production code, workflow YAML, and release automation** belong in later phases unless this file only adjusts contracts; this spec is the contract for what “done” means.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Version bumped to alpha | [§2 Versioning](#2-versioning-normative) |
| Changelog updated | [§3 Changelog](#3-changelog-normative) |
| Package published and installable | [§4 Publishing target](#4-publishing-target-normative), [§5 Verification](#5-verification-normative), [§7 Acceptance checklist](#7-acceptance-checklist) |

**Related contracts:** Distribution metadata MUST stay consistent with **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (Python / OpenTelemetry policy) and **`[project].name`** in **`pyproject.toml`** (**`replayt-otel-span-exporter`**). README integrator install prose MUST follow **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §2.1 once the package is available on an index. Default CI behavior and “green” definition remain **[docs/CI_SPEC.md](CI_SPEC.md)**; this backlog does **not** require a new CI job unless maintainers choose to add one in the same change set and document it there.

## 0. Testable acceptance criteria (expanded backlog wording)

The three backlog bullets are satisfied **only** when all of the following are true (cross-check [§7](#7-acceptance-checklist)):

| Backlog phrase | Testable “pass” condition |
| ---------------- | ------------------------- |
| **Version bumped to alpha** | **`[project].version`** in **`pyproject.toml`** matches PEP 440 with an **`aN`** prerelease segment (see [§2](#2-versioning-normative)). If the package exposes **`__version__`** in **`src/`**, it MUST equal **`[project].version`** byte-for-byte on the revision that is built and uploaded. |
| **Changelog updated** | **[CHANGELOG.md](../CHANGELOG.md)** contains a top-level **`## [<version>] - YYYY-MM-DD`** section whose version label (for example **`[0.2.0a1]`**) matches **`[project].version`**, with material copied out of **`[Unreleased]`** for that release per [§3](#3-changelog-normative). An empty **`[Unreleased]`** section MUST exist after the cut. |
| **Package published and installable** | The **sdist** and **wheel** for that **`[project].version`** appear on the **chosen index** (PyPI project files or private registry listing), and [§5 Verification](#5-verification-normative) completes successfully from a clean environment. **Repository-only** state (version already edited locally but **no** upload) does **not** satisfy this bullet. |

**Provenance (recommended):** Maintain a **git tag** (for example **`v0.2.0a1`**) on the exact commit used for the release build, or record the **commit SHA** next to the publish handoff. This spec does not mandate tag format; it mandates traceability between **source revision**, **metadata**, and **uploaded artifacts**.

## 1. Goals

- Ship a **PEP 440** **alpha** prerelease of **`replayt-otel-span-exporter`** to **PyPI** or a **private package index** so integrators can `pip install` without cloning the repository.
- Keep **version**, **changelog**, and **published artifacts** aligned so support and audits can trace what left the repository.
- Preserve project policy: **`replayt`** remains **out** of **`[project].dependencies`**; runtime dependencies stay as declared today unless a separate backlog changes **`pyproject.toml`**.

## 2. Versioning (normative)

- **`[project].version`** in **`pyproject.toml`** MUST be a **PEP 440** version that includes an **alpha** prerelease segment (for example **`0.2.0a1`**, **`0.3.0a1`**). A plain **`0.1.0`**-style release with **no** `a` / `b` / `rc` segment does **not** satisfy “version bumped to alpha” for this backlog.
- If **`replayt_otel_span_exporter.__version__`** (or any other public **`__version__`** in the distribution) is shipped, it MUST equal **`[project].version`** on the release revision. **`importlib.metadata.version("replayt-otel-span-exporter")`** MUST return the same string after install ([§5](#5-verification-normative)).
- The **same** version string MUST appear in:
  - the **sdist** and **wheel** built from that revision, and
  - the **CHANGELOG** release heading for that publish ([§3](#3-changelog-normative)).
- **Post-publish fixes** (documentation-only or packaging metadata) use a **new** prerelease index (**`a2`**, **`a3`**, …) or a later policy decided by maintainers; this spec does not require semantic versioning beyond PEP 440 compatibility and project changelog practice.

## 3. Changelog (normative)

- Before or as part of the release commit, **[CHANGELOG.md](../CHANGELOG.md)** MUST move content from **`[Unreleased]`** into a **new** dated section titled with the **exact** version being published (for example **`## [0.2.0a1] - 2026-03-28`**), following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) structure already used in this repository.
- That section MUST summarize **user-visible** changes in this release (API, dependencies, notable fixes, documentation that affects integrators). Purely internal refactors with no observable effect MAY be omitted or grouped under **Changed** at maintainer discretion.
- After the release, **`[Unreleased]`** MUST exist again (possibly empty) for ongoing work.

## 4. Publishing target (normative)

- **Primary target:** **PyPI** (`https://pypi.org/project/replayt-otel-span-exporter/`) **or** a **private** index (DevPI, Artifactory, etc.) explicitly named in maintainer runbooks or **`handoff.md`** for Mission Control.
- Artifacts MUST be built from the **tagged** or **merged** revision that matches **`pyproject.toml`** and **CHANGELOG** for that version (no “dirty” tree in the release commit).
- **Recommended** build/upload steps (Builder or maintainer implements or runs):
  - Create a clean environment; install **`build`** and **`twine`** (or use project-pinned tooling if added later).
  - Run **`python -m build`** from the repository root so **sdist** and **wheel** are produced under **`dist/`**.
  - Run **`twine check dist/*`** before upload to catch metadata or filename issues early.
  - Upload with **`twine upload dist/*`** (or host-specific upload) using **credentials stored outside the repo** (environment variables, OIDC / trusted publishing, or secret store). Clear **`dist/`** between releases so stale wheels are not uploaded accidentally.
- **Not required** by this spec: GitHub Actions workflow for release, GPG signing of tags, or automated promotion from CI. If automation is added later, **[docs/CI_SPEC.md](CI_SPEC.md)** MUST be updated to describe any new job and how it relates to §7 here.

## 5. Verification (normative)

After upload, a verifier (human or scripted) MUST confirm from a **clean** environment (fresh venv, no editable install of this repo):

1. **Interpreter:** Use Python **≥** the package’s **`[project].requires-python`** minimum (today **3.11+**) so verification matches integrator expectations.
2. **Install:**  
   `python -m pip install --upgrade pip` then  
   `pip install replayt-otel-span-exporter==<published-version>`  
   using **`--index-url`** / **`--extra-index-url`** if the target is **not** public PyPI.  
   **Note:** Always pin **`==<published-version>`** for verification. For **private** indexes, a concrete pattern is:  
   `pip install --index-url https://<private-index>/simple/ replayt-otel-span-exporter==<published-version>`  
   (adjust URL and add **`--trusted-host`** only if your index requires it). For **PyPI**, the default index is sufficient with the same **`==`** pin.
3. **Prerelease discovery (informative):** Integrators who run **`pip install replayt-otel-span-exporter`** without a version pin may not receive a prerelease unless they pass **`--pre`** (pip behavior). Documentation and README examples SHOULD prefer an **explicit version** or **`--pre`** when steering users to alphas.
4. **Import and version:** Running Python code equivalent to:
   - `import replayt_otel_span_exporter`
   - `import importlib.metadata as m; assert m.version("replayt-otel-span-exporter") == "<published-version>"`  
   MUST succeed without installing **`[dev]`** extras. If **`__version__`** is defined on the package, it SHOULD match **`<published-version>`** (required at source per [§2](#2-versioning-normative)).
5. **Runtime deps:** The install MUST **not** pull **`replayt`** into the environment as a dependency of **`replayt-otel-span-exporter`** (consistent with **`[project].dependencies`** in **`pyproject.toml`**). A quick check is: **`pip show replayt-otel-span-exporter`** lists only the declared runtime requirements, and **`pip list`** does not show **`replayt`** as **Required-by** that package unless the user installed it separately.

Record **where** the package was verified (PyPI project URL or private index name), **the verifier’s Python version**, and **the install command** (redact secrets) in release notes or the merge handoff so the next phase knows the source of truth.

## 5.1 CI and suite health (informative)

This backlog’s **§5** verification uses a **minimal** install path and does **not** replace full **`pytest`** coverage. **[docs/CI_SPEC.md](CI_SPEC.md)** still defines whether the default branch is “green.” **Unrelated** test failures (for example **`tests/integration/test_replayt_boundary.py`** collection errors under **`pip install -e ".[dev]"`**) are owned by the **Tester** phase and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**; they SHOULD be resolved **before** merging a release branch so maintainers do not ship from a known-red mainline. Packaging defects that block **§5** (broken **`pyproject.toml`**, wrong files in the wheel) **are** in scope for the **Builder** on this backlog.

## 6. Documentation updates (normative for Builder)

When the package is **actually** available on the chosen index:

- **`README.md`** library-user quick start MUST be updated per **[docs/SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §2.1 (state that PyPI—or the named private index—install works; keep **`pip install replayt-otel-span-exporter`** as the primary example for public PyPI).
- **`docs/COMPATIBILITY.md`** SHOULD mention that published wheels/sdists track **`[project].requires-python`** and OpenTelemetry lower bounds as on PyPI for that version (adjust wording if the matrix is unchanged—still point integrators at the published package name).

## 7. Acceptance checklist

- [ ] **`[project].version`** includes a PEP 440 **alpha** prerelease segment and matches built artifacts.
- [ ] Any shipped **`__version__`** in **`src/replayt_otel_span_exporter/`** equals **`[project].version`** on the release revision.
- [ ] **`CHANGELOG.md`** has a **dated** section for that version; **`[Unreleased]`** is ready for follow-up work.
- [ ] **Sdist and wheel** for that version are uploaded to the chosen index (artifacts visible in the index UI or API, not only local **`dist/`** files).
- [ ] **§5 Verification** install + import + version + no-**`replayt`**-runtime-dep checks pass from a **clean** venv on a supported Python version.
- [ ] **README** / **COMPATIBILITY** updated per [§6](#6-documentation-updates-normative-for-builder) when the index is live.
- [ ] **Optional:** Git tag or recorded **SHA** links the published version to source ([§0](#0-testable-acceptance-criteria-expanded-backlog-wording)).

## 8. Non-goals (this backlog)

- Declaring API stability or **1.0** semantics.
- Changing OpenTelemetry or **replayt** pin policy beyond what **`pyproject.toml`** already states (separate maintenance items).
- Fixing unrelated test failures (for example integration collection issues); the **Tester** phase owns the suite. If **§5** verification is blocked by a packaging bug, fix that in the **Builder** scope for this item.
