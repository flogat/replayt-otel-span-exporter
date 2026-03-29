# Specification: Beta and 1.0 promotion, semver, and public API stability

This document refines backlog items **“Define beta/1.0 promotion criteria and public API stability promises”** and Mission Control **`e9115fe4-6d8f-44b7-97e1-008a1a8cf478`** (**Post-alpha roadmap: beta or 1.0 criteria and deprecation policy**) into **testable maintainer and integrator expectations**. **Production code** and **automated CI gates** that enforce §2 checklists are **optional** follow-ons unless a backlog adds them (see §8). Default **`pytest`** includes **`tests/test_beta_stable_promotion_docs.py`**, which only checks that this file and **`docs/ROADMAP.md`** keep expected headings and cross-links (**[docs/CI_SPEC.md](CI_SPEC.md)** §5). This file remains the **normative policy** for promotion gates, **semantic versioning**, **changelog discipline**, **evolution of optional hooks**, and **deprecation** (§6).

**Human-readable roadmap:** **[docs/ROADMAP.md](ROADMAP.md)** — release phases and links for Mission Control alignment.

**Prerequisite:** A **first alpha** (or later prerelease) is **verified on an index** per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §5 before maintainers claim **beta** readiness against real integrator installs.

## Backlog traceability

| Backlog phrase | Satisfied by (this doc) |
| -------------- | ------------------------ |
| Criteria for promoting to **beta** or **1.0** after first alpha is verified | [§2 Promotion gates](#2-promotion-gates-normative) |
| **Semver** expectations for **`PreparedSpanRecord`** and **`ReplaytSpanExporter`** | [§3 Semantic versioning](#3-semantic-versioning-and-public-api-normative) |
| **Changelog** discipline | [§4 Changelog discipline](#4-changelog-discipline-normative) |
| How **optional hooks** evolve | [§5 Optional hooks evolution](#5-optional-hooks-and-extension-points-normative) |
| **Deprecation** policy (warnings, timeline, **`__all__` / IR / hooks**) | [§6 Deprecation policy](#6-deprecation-policy-normative) |
| **Mission Control** / integrator alignment | **[docs/ROADMAP.md](ROADMAP.md)** + cross-links from **[docs/MISSION.md](MISSION.md)** |

**Related contracts:** Public symbols and IR fields are defined in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (especially **§3** and **`__all__`**). Approval / audit hooks are specified in **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**. **OpenTelemetry** dependency policy remains **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**. **replayt** boundary tests remain **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**.

## 1. Goals

- Give **integrators** a clear statement of what **stability** means for **`PreparedSpanRecord`**, **`ReplaytSpanExporter`**, and documented **optional hooks** across **prerelease** and **stable** lines.
- Give **maintainers** explicit **checklists** for claiming **beta** vs **1.0** so backlog and release decisions stay consistent.
- Keep **CHANGELOG** practice aligned with **[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)** and **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)** once the distribution leaves **alpha-only** experimentation.

## 2. Promotion gates (normative)

### 2.1 Definitions

| Phase | Meaning in this repository |
| ----- | --------------------------- |
| **Alpha** | PEP 440 **`aN`** prerelease per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)**; API and IR may still tighten as specs and tests converge. |
| **Beta** | PEP 440 **`bN`** prerelease (for example **`0.3.0b1`**). Signals **feature-complete** intent for the targeted **minor** line: integrators should treat **IR field names**, **`ReplaytSpanExporter`** lifecycle methods, and symbols in **`replayt_otel_span_exporter.__all__`** as **frozen** except for fixes and documented additive MINOR changes (§3). |
| **1.0** | First **release** with **no** PEP 440 prerelease segment (for example **`1.0.0`**). Signals **SemVer-major** stability for **`__all__`** and the **normative** **`PreparedSpanRecord`** / **`ReplaytSpanExporter`** contracts in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**. |

**Note:** The project MAY ship multiple **`0.y.z`** lines before **1.0**; **beta** gates apply to the **version being promoted**, not to every historical alpha.

### 2.2 Beta promotion checklist

Maintainers MUST verify **all** of the following before publishing a **beta** tag for a given version line:

1. **Index proof:** At least one **alpha** (or prior prerelease) for this package has passed **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §5 on the **same** index family (PyPI or the same private index) integrators are expected to use.
2. **CI health:** Default branch workflows in **[docs/CI_SPEC.md](CI_SPEC.md)** §7 are **green** for the release revision (no waived failures on the merge path used for the tag).
3. **Spec alignment:** **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**, **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**, and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** describe the **shipped** behavior; any **known** deviations are listed under **`[Unreleased]`** or the release section in **[CHANGELOG.md](../CHANGELOG.md)** with integrator impact.
4. **Version shape:** **`[project].version`** uses a PEP 440 **beta** segment (**`bN`**), **`__version__`** (if present) matches **`[project].version`**, and **CHANGELOG** has a dated section for that beta when it is published (§4).
5. **Stability comms:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** or **[README.md](../README.md)** (as appropriate) states that **beta** prereleases follow §3 for **`__all__`** and **§3.1** field stability for **`PreparedSpanRecord`**.

### 2.3 1.0 promotion checklist

Maintainers MUST verify **all** of the following before publishing **1.0.0** (or the chosen first stable major):

1. **Beta discipline:** At least one **beta** prerelease has been published on the target index **or** maintainers document in **CHANGELOG** why the project skipped beta (exceptional; requires explicit rationale).
2. **No prerelease segment:** **`[project].version`** is **SemVer-shaped** (**`MAJOR.MINOR.PATCH`**) with **no** **`a` / `b` / `rc`** suffix on the **1.0.0** build.
3. **Integration proof:** **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** contract and **`tests/integration/test_replayt_boundary.py`** (when **`replayt`** is installed) pass on the release revision.
4. **Public API inventory:** **`replayt_otel_span_exporter.__all__`** lists **only** **`ReplaytSpanExporter`**, **`PreparedSpanRecord`**, and **`__version__`** unless a **prior** MINOR release already documented **additional** symbols in **CHANGELOG** and **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** reference naming; **1.0** MUST NOT silently expand **`__all__`** without that history.
5. **Stable story:** **README** and **[docs/MISSION.md](MISSION.md)** describe **1.0** as **SemVer-stable** for **`__all__`** per §3; **CHANGELOG** includes migration notes from the last **beta** / **0.x** line if integrators must change pins or behavior.

## 3. Semantic versioning and public API (normative)

This project **adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)** for **stable** releases (**no** prerelease segment). **PEP 440** prereleases (**`aN`**, **`bN`**, **`rcN`**) are ordered **before** the corresponding stable; they **do not** relax the obligation to document **breaking** changes in **CHANGELOG** when maintainers intentionally break early adopters.

**Scope of “public API” for SemVer:** symbols exported in **`replayt_otel_span_exporter.__all__`** and the **documented** fields and encodings of **`PreparedSpanRecord`** in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §3, plus **documented** constructor parameters and methods of **`ReplaytSpanExporter`** in that spec §2. **Underscore-prefixed** names, modules not listed for integrators, and helpers **omitted** from **`__all__`** are **not** SemVer-guaranteed unless documented otherwise.

### 3.1 `PreparedSpanRecord`

| Change class | SemVer bump (stable line) |
| ------------ | ------------------------- |
| Remove, rename, or **narrow** the type or meaning of a **documented** §3 field | **MAJOR** |
| Add a **new** field with a default such that **keyword** construction and **read** access remain backward compatible | **MINOR** |
| Fix bugs that bring behavior **into** spec (tests + docs updated) | **PATCH** (or **MINOR** if integrators relied on the bug in practice—call out in **CHANGELOG**) |
| Change **encoding** rules for **trace_id** / **span_id** / times / attribute serialization **contrary** to §3 | **MAJOR** |

### 3.2 `ReplaytSpanExporter`

| Change class | SemVer bump (stable line) |
| ------------ | ------------------------- |
| Remove or rename **`export`**, **`shutdown`**, or **`force_flush`**; change documented **no-raise** / return-code contract for the SDK | **MAJOR** |
| Add **optional** constructor parameters or **optional** behavior branches that default to prior semantics | **MINOR** |
| Tighten **thread-safety** or **shutdown** behavior in a way that breaks documented guarantees | **MAJOR** |
| Change **failure** vs **policy denial** semantics (**`SpanExportResult`**) | **MAJOR** (must align with **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** and failure spec) |

### 3.3 `__version__` and packaging

**`[project].version`**, shipped **`__version__`**, and **CHANGELOG** headings MUST match for each published build per **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §2–§3, extended to **beta** and **stable** lines.

## 4. Changelog discipline (normative)

- Every **published** version (alpha, beta, **rc**, stable) MUST have a **top-level** **`## [<version>] - YYYY-MM-DD`** section in **[CHANGELOG.md](../CHANGELOG.md)** when cut from **`[Unreleased]`**, per existing project practice.
- **`[Unreleased]`** MUST accumulate **user-visible** bullets for: **API** changes, **dependency** bound changes affecting integrators, **hook** or **IR** behavior changes, and **security**-relevant logging/redaction updates.
- **MAJOR** (including future **2.0.0**) MUST include **migration** guidance: what integrators must change (pins, imports, hook signatures, field expectations).
- **Deprecations** SHOULD appear in **CHANGELOG** at least **one MINOR** before removal when feasible; the **deprecated** release MUST be **published** (not only on `main`).

## 5. Optional hooks and extension points (normative)

Optional **`on_export_commit`** / **`on_export_audit`** (names per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**) are **public integrator contracts** once documented and shipped.

| Change class | SemVer bump (stable line) |
| ------------ | ------------------------- |
| Add a **new** optional hook parameter with **`None`** default (no behavior change when unset) | **MINOR** |
| Widen callback **inputs** in a backward-compatible way (e.g. add keyword-only parameters with defaults) | **MINOR** |
| Narrow or change **return** protocol, **required** parameters, or **ordering** guarantees of callbacks | **MAJOR** |
| Add a **new** optional **Protocol** / type alias **outside** **`__all__`** only | **PATCH** or **MINOR** per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** typing guidance; if added to **`__all__`**, treat as **MINOR** minimum |

New **optional** exporter parameters MUST **default** to current behavior. Integrators relying on **exact** exception types or log message strings rely on **undefined** behavior unless a spec explicitly freezes them; **CHANGELOG** should still mention **observable** log field changes when **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** requires.

## 6. Deprecation policy (normative)

This section defines how **documented public API** (§3) and **optional hooks** (§5) **sunset** before removal. It complements §4 (**CHANGELOG**) and §3 (**SemVer** when behavior is removed).

### 6.1 What requires a deprecation period

Any change that would be a **MAJOR** removal or **narrowing** under §3 or §5 **SHOULD** ship a **published deprecation** on a **stable** line (no PEP 440 prerelease segment) **or** on a **beta** line that integrators already treat as frozen (§2.2), **before** the breaking release.

Maintainers **MUST** run a deprecation period (§6.2) before removal or incompatible narrowing of:

- Symbols listed in **`replayt_otel_span_exporter.__all__`**
- **Documented** **`PreparedSpanRecord`** fields or encodings in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §3
- **Documented** **`ReplaytSpanExporter`** constructor parameters, methods, or **`SpanExporter`** return contracts in that spec §2
- **Documented** optional hook parameters, callback ordering guarantees, or audit allow-list keys per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**

Maintainers **MAY** omit a deprecation period when **any** of the following holds:

- The surface is **not** in **`__all__`**, **not** described in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** as integrator-facing stable IR / exporter API, and **not** already promised by a published **beta** or **stable** release under §2.
- The change is **security-critical** and delay is **explicitly** waived in **CHANGELOG** with maintainer rationale (exceptional).

### 6.2 Minimum process

1. **Announce:** Add a **`Deprecated`** bullet under **`[Unreleased]`** in **[CHANGELOG.md](../CHANGELOG.md)** naming the symbol or contract, the **first version** that emits the deprecation, and the **replacement** or migration path when one exists.
2. **Runtime signal (Python API):** For callable or importable **public** deprecations, emit **`warnings.warn(..., category=DeprecationWarning, stacklevel=...)`** at the point of use (constructor, method, or module access as appropriate). A one-**MINOR** **`PendingDeprecationWarning`** phase is allowed if **CHANGELOG** documents it.
3. **Docs:** Update **docstrings** and the relevant spec (**[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** and/or **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**) so integrators see a clear **deprecated since X.Y.Z** note aligned with **CHANGELOG**.
4. **Timeline:** Prefer **at least one published MINOR** on the same **MAJOR** line after the release that **introduces** the deprecation before **removal** (align with §4 fourth bullet). Shorter paths on **alpha**-only lines are allowed with explicit **CHANGELOG** notice that the line is experimental.
5. **Removal:** Ship removal in the **MAJOR** (or documented **MINOR** if the project commits to that rarer pattern) promised in **CHANGELOG**; use **`Removed`** / **migration** sections per §4.

### 6.3 Non-API surfaces

**Log message text**, **exception** types not documented as stable, and **private** helpers remain outside the SemVer scope of §3; they **SHOULD** still appear under **Changed** in **CHANGELOG** when observability shifts materially, per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**.

## 7. Verifiable acceptance checklist (Spec gate / maintainer review)

Use when closing **“Define beta/1.0 promotion criteria and public API stability promises”**, Mission Control **`e9115fe4-6d8f-44b7-97e1-008a1a8cf478`** (**Post-alpha roadmap: beta or 1.0 criteria and deprecation policy**), or when reviewing a release plan:

- [ ] **[docs/ROADMAP.md](ROADMAP.md)** exists and links this spec, **first alpha** spec, and **[docs/MISSION.md](MISSION.md)**.
- [ ] **[docs/MISSION.md](MISSION.md)** references promotion/stability and deprecation (scope, success criteria, traceability, or dedicated subsection).
- [ ] §2–§6 of **this document** are consistent with **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** and **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**.
- [ ] **CHANGELOG** practice for **beta** and **stable** matches §4, including deprecations per §6.
- [ ] **Beta** and **1.0** promotion claims on a version are backed by §2.2 / §2.3 checklists (recorded in PR, release issue, or **`handoff.md`**).

### 7.1 Mission Control `e9115fe4-6d8f-44b7-97e1-008a1a8cf478` — documentation closure criteria

The following are **documentation deliverables** for the **Post-alpha roadmap** backlog; they do **not** require shipping a beta/stable release in the same change set:

1. **Promotion** — §2.2 and §2.3 checklists are present and actionable.
2. **SemVer** — §3 tables cover **`PreparedSpanRecord`**, **`ReplaytSpanExporter`**, and optional hooks.
3. **Changelog** — §4 defines **Unreleased**, **migration**, and **deprecation** expectations.
4. **Hooks** — §5 ties hook contract changes to **MAJOR** / **MINOR** as appropriate.
5. **Deprecation** — §6 defines what **MUST** be deprecated before removal and the **minimum process**.
6. **Roadmap alignment** — **[docs/ROADMAP.md](ROADMAP.md)** orients Mission Control and integrators to phases; **[docs/MISSION.md](MISSION.md)** links **ROADMAP** and this spec.

## 8. Non-goals (this backlog)

- Mandating a **calendar** date or **download count** for promotion.
- Changing **replayt** runtime dependency policy (separate backlog).
- Adding **automated** release gates in CI (optional follow-on; document in **[docs/CI_SPEC.md](CI_SPEC.md)** if added).
