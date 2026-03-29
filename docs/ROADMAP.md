# Roadmap: releases, stability, and Mission Control alignment

This document orients **maintainers**, **integrators**, and **Mission Control** backlog work to the same **release phases** and **stability** expectations. **Normative detail** (semver rules, checklists, hook evolution) lives in **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)**.

## Release phases

| Phase | Version example | Integrator expectation (summary) |
| ----- | ----------------- | ---------------------------------- |
| **Alpha** | `0.2.0a1` | Early index verification; contract may still tighten per specs and **CHANGELOG**. See **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**. |
| **Beta** | `0.3.0b1` | **Feature-complete** intent for the target line; **`__all__`** and **`PreparedSpanRecord`** §3 fields treated as **frozen** except documented additive **MINOR**-style changes and fixes. See **SPEC_BETA_AND_STABLE_PROMOTION** §2.2. |
| **Release candidate** | `1.0.0rc1` | Optional; use when maintainers want a **last** prerelease before **1.0**. Same changelog and semver rules as other prereleases. |
| **Stable** | `1.0.0` | **SemVer** applies to **`__all__`**, **`PreparedSpanRecord`**, and **`ReplaytSpanExporter`** per **SPEC_BETA_AND_STABLE_PROMOTION** §3. **Removal** of promised API follows **§6** (deprecation period, **CHANGELOG**, **`DeprecationWarning`** where applicable). |

## Where to read next

| Audience | Document |
| -------- | -------- |
| **Integrators** | **[docs/MISSION.md](MISSION.md)** (scope), **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (pins), **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (IR + exporter) |
| **Maintainers** | **SPEC_BETA_AND_STABLE_PROMOTION**, **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**, **[CHANGELOG.md](../CHANGELOG.md)**, **[docs/CI_SPEC.md](CI_SPEC.md)** |
| **Hooks / governance** | **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**, **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** |

## Backlog traceability

| Backlog item | Roadmap anchor |
| ------------ | -------------- |
| **Define beta/1.0 promotion criteria and public API stability promises** | This file + **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** |
| **Post-alpha roadmap: beta or 1.0 criteria and deprecation policy** (MC **`e9115fe4-6d8f-44b7-97e1-008a1a8cf478`**) | **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §2–§7.1, this file, **[docs/MISSION.md](MISSION.md)** traceability |
| **Publish first alpha release** / **Close first alpha** | **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** |
| **Add optional GitHub Actions trusted publishing for PyPI** | **[docs/CI_SPEC.md](CI_SPEC.md)** §8 (**`release.yml`**, OIDC, **`tests/test_release_workflow_contract.py`**) |
| **Ship a minimal runnable example package or scripts/ recipe** (MC **`21487c24-8d58-4085-896c-4a6bad8d0af4`**) | **[docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** |
