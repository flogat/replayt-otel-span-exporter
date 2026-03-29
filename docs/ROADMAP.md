# Roadmap: releases, stability, and Mission Control alignment

This document orients **maintainers**, **integrators**, and **Mission Control** backlog work to the same **release phases** and **stability** expectations. **Normative detail** (semver rules, checklists, hook evolution) lives in **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)**.

## Release phases

| Phase | Version example | Integrator expectation (summary) |
| ----- | ----------------- | ---------------------------------- |
| **Alpha** | `0.2.0a1` | Early index verification; contract may still tighten per specs and **CHANGELOG**. See **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**. |
| **Beta** | `0.3.0b1` | **Feature-complete** intent for the target line; **`__all__`** and **`PreparedSpanRecord`** §3 fields treated as **frozen** except documented additive **MINOR**-style changes and fixes. See **SPEC_BETA_AND_STABLE_PROMOTION** §2.2. |
| **Release candidate** | `1.0.0rc1` | Optional; use when maintainers want a **last** prerelease before **1.0**. Same changelog and semver rules as other prereleases. |
| **Stable** | `1.0.0` | **SemVer** applies to **`__all__`**, **`PreparedSpanRecord`**, and **`ReplaytSpanExporter`** per **SPEC_BETA_AND_STABLE_PROMOTION** §3. |

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
| **Publish first alpha release** / **Close first alpha** | **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** |
