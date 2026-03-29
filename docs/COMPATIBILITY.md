# Compatibility and supported versions

This document refines the backlog item **“Document supported replayt versions and compatibility”** into a single place maintainers and integrators can verify. **Authoritative numeric pins** live in **`pyproject.toml`** and **`.github/workflows/ci.yml`**; this file explains **policy**, the **matrix**, and **where to track upstream releases**. If those files drift, update them and this doc in the same maintenance pass.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Compatibility matrix documented | [§2 Compatibility matrix](#2-compatibility-matrix) |
| Pin strategy and CI matrix described | [§3 Pin strategy](#3-pin-strategy), [§4 CI matrix](#4-ci-matrix-and-proven-contract) |
| Links to replayt release tracking | [§5 Tracking replayt releases](#5-tracking-replayt-releases) |
| **OpenTelemetry** upper-bound vs float policy, CI observation, integrator pins | [§2](#2-compatibility-matrix) (**OpenTelemetry** rows), [§3.1](#31-opentelemetry-runtime-float-policy) — normative detail in **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** |

**Expand CI matrix to Python 3.13 with documented policy** (Mission Control **`4a00b7f7-af4e-4200-9d28-38e3827fa2e5`**):

| Backlog acceptance theme | Satisfied by (this doc) |
| ------------------------ | ------------------------ |
| Documented **Python × CI** fingerprint including **3.13** | [§2](#2-compatibility-matrix), [§4](#4-ci-matrix-and-proven-contract), [§4.1](#41-python-313-matrix-expansion-operator-notes) |
| Caveats for **pip-audit**, **`replayt`** dev pin, **OpenTelemetry** resolution on **3.13** | [§4.1.1](#411-when-313-is-in-ci) |
| Deferring or rolling back a matrix Python | [§4.1.2](#412-deferring-or-removing-a-matrix-python) |

Related specs: **[docs/CI_SPEC.md](CI_SPEC.md)** (workflow contract), **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** (audit and transitive risk), **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** (runtime OTel float / no upper cap), **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (boundary API and minimum **`replayt`** for tests).

## 1. Roles of each dependency class

| Class | Declared in | Consumed by |
| ----- | ----------- | ------------ |
| **Runtime** | **`[project].dependencies`** in **`pyproject.toml`** | Library users at install time (**OpenTelemetry** only today). |
| **Dev / integration** | **`[project.optional-dependencies].dev`** | Contributors, default CI, **`pip-audit`** supply-chain job — includes **`replayt`** for boundary tests. |

**replayt** is intentionally **not** a runtime dependency of **`replayt-otel-span-exporter`** unless a future backlog promotes it; see **[docs/MISSION.md](MISSION.md)** scope and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §5.

## 2. Compatibility matrix

Values below match the repository **at the time this section was last revised**; re-read **`pyproject.toml`** and **[docs/CI_SPEC.md](CI_SPEC.md)** (reference fingerprint) if pins or CI change.

| Component | Supported policy (this package) | Where enforced |
| --------- | ------------------------------- | -------------- |
| **Python** | **`>=3.11`** per **`[project].requires-python`** | **`pyproject.toml`**; default CI exercises **3.11**, **3.12**, and **3.13** (see §4). |
| **opentelemetry-api** | **Lower bound only** **`>=1.0.0`**; **no** **`<`** upper bound on runtime deps. New **1.x** releases are picked by the resolver until maintainers raise the floor or fix breakages. | **`pyproject.toml`** **`[project].dependencies`** (comments + spec); **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime; **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**. |
| **opentelemetry-sdk** | **Lower bound only** **`>=1.0.0`**, kept on the **same OTel Python release line** as **API** | Same as API. |
| **replayt** | **Test/dev only:** lower bound **`>=0.4.25`** on **`dev`** extra | **`pyproject.toml`** **`[project.optional-dependencies].dev`**; boundary contract in **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7. |

**Interpretation for integrators:** Any **Python** and **OpenTelemetry** versions satisfying the table are in policy for **using this exporter as a library**. The declared OTel bounds are **minimums**; for **reproducible** installs, pin **`opentelemetry-api`** and **`opentelemetry-sdk`** to **matching** versions (same upstream release line) in **your** application or lockfile — see **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** §1. Compatibility with **replayt** at runtime is **not** claimed by this matrix unless you align your environment with the **dev** pin or validate **`PreparedSpanRecord`** → replayt yourself; CI proves a **minimum** replayt API against the declared lower bound.

**Published wheels and sdists:** The first alpha line in **[CHANGELOG.md](../CHANGELOG.md)** is **`0.2.0a1`**. When that build is on [PyPI](https://pypi.org/project/replayt-otel-span-exporter/) (or another index), the **`[project]`** metadata for each uploaded version — **`requires-python`**, runtime **`Requires-Dist`** entries — comes from **`pyproject.toml`** at the release revision. Confirm the live project page for the version you install; it should match this matrix for that tag. Until the index lists the release, treat the source tree and local **`python -m build`** artifacts as the source of truth.

## 3. Pin strategy

### 3.1 OpenTelemetry runtime (float policy)

- **No upper bounds:** **`[project].dependencies`** MUST **not** add **`<`** caps on **`opentelemetry-api`** / **`opentelemetry-sdk`** under this policy (avoids resolver conflicts with applications that need newer **1.x** OTel). A deliberate change requires a backlog, spec update, and **CHANGELOG** entry.
- **How CI sees new minors:** Default CI uses **`pip install -e ".[dev]"`** **without** a committed lockfile, so pip selects the **newest** OTel **1.x** releases compatible with the declared **lower bounds** and the **`dev`** graph. A **green `test`** job means the suite passed against **that resolved pair** on each matrix Python. Upstream releases that break tests surface as **CI failures** until the code or **minimum** bounds are updated — see **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** §2–§4 and **[docs/CI_SPEC.md](CI_SPEC.md)** §4.
- **Integrators:** Pin **API** + **SDK** together at versions you validate; treat this package as declaring **floor** versions only (**[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** §1).

- **OpenTelemetry version bumps:** When raising (or reconciling) floors in **`pyproject.toml`**, move **`opentelemetry-api`** and **`opentelemetry-sdk`** together on the **same** OpenTelemetry Python release line, per **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime.
- **replayt (dev extra):** Use a **lower bound** that matches the **minimum version** documented in **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7 (**Implemented boundary**). Raising the bound is appropriate when replayt’s public API used by **`tests/integration/test_replayt_boundary.py`** changes; do that in the same change set as spec §7 and **`DEPENDENCY_AUDIT.md`** updates.
- **No duplicate source of truth:** Do not maintain a shadow pin file (for example **`requirements.txt`**) for the default CI path unless the project adds one and documents it in **[docs/CI_SPEC.md](CI_SPEC.md)** §4.
- **Resolver behavior:** **`pip install -e ".[dev]"`** resolves **replayt** and transitives to current releases compatible with the lower bound; CI therefore proves **≥ minimum**, not an exact single version. If the team needs a **fully locked** integration environment, document an optional lockfile workflow separately (not required by this backlog).

## 4. CI matrix and proven contract

Default CI is specified in **[docs/CI_SPEC.md](CI_SPEC.md)**. Summary:

| Dimension | Value |
| --------- | ----- |
| **Workflow** | **`.github/workflows/ci.yml`** |
| **Python versions** | **3.11**, **3.12**, and **3.13** (same matrix on **`test`** and **`supply-chain`**) |
| **Install** | `python -m pip install --upgrade pip` then **`pip install -e ".[dev]"`** |
| **Tests** | **`pytest --cov=replayt_otel_span_exporter --cov-report=xml`** from repo root (full collection, including **`tests/integration/test_replayt_boundary.py`** when **`replayt`** is installed) |
| **Supply chain** | **`pip-audit`** with ignores documented in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** |

Every matrix cell runs the **same** install and **pytest** command unless **[docs/CI_SPEC.md](CI_SPEC.md)** is explicitly revised. That is how **supported Python × declared dev dependencies** stay aligned.

## 4.1 Python 3.13 matrix expansion (operator notes)

**Normative requirements** (matrices, pytest, **`pip-audit`**, contract tests) live in **[docs/CI_SPEC.md](CI_SPEC.md)** §3.1. This section is the **compatibility-facing** place for **3.13** notes so integrators and operators see **OpenTelemetry** / **`replayt`** / audit context next to the matrix.

### 4.1.1 When 3.13 is in CI

Keep this short; CVE policy and ignore rationale stay in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**.

- **OpenTelemetry resolution:** **`pip install -e ".[dev]"`** on **3.13** pulls **opentelemetry-api** and **opentelemetry-sdk** satisfying the same **`>=1.0.0`** bounds as on **3.11** / **3.12** (resolver output can differ by minor release day; integrators rely on **`requires-python`** and published **`Requires-Dist`**).
- **`replayt` (dev extra):** CI still proves **≥** the minimum in **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7; **`tests/integration/test_replayt_boundary.py`** is part of default **`pytest`** collection on **3.13** like the other matrix cells.
- **`pip-audit`:** The **`supply-chain`** job uses the same **`--ignore-vuln CVE-2026-4539`** and **`CVE-2025-69872`** flags on **3.13** as on **3.11** / **3.12**; any **3.13-only** extra ignores MUST be documented in **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** in the same change set as **`ci.yml`** (see **[docs/CI_SPEC.md](CI_SPEC.md)** §3.1 item **4**).

### 4.1.2 Deferring or removing a matrix Python

If **3.13** (or any matrix entry) cannot stay green—install failure, **`pytest`** / collection failure, or **`pip-audit`** policy block—do **not** leave **MISSION**, **CI_SPEC** fingerprint, **`COMPATIBILITY.md`** §4, and **`tests/test_compatibility_contract.py`** claiming that interpreter while **`ci.yml`** omits it (or the reverse). In one maintenance pass: document the **blocker** in §4.1 (short operator note), align **`.github/workflows/ci.yml`**, update **[docs/CI_SPEC.md](CI_SPEC.md)** **Reference fingerprint** and §3.1 **Blocked** guidance, bump **`_EXPECTED_CI_PYTHON_VERSIONS`**, and refresh §2 / §4 tables. Removing **3.13** from CI is allowed only under that documented deferral story; widening **`requires-python`** upward without a backlog is out of scope here.

## 5. Tracking replayt releases

Use these when bumping **`replayt`** or assessing breakage:

| Resource | URL / action |
| -------- | ------------- |
| **PyPI project (releases and metadata)** | [https://pypi.org/project/replayt/](https://pypi.org/project/replayt/) |
| **Release history on PyPI** | From the project page, open **Release history** to see published versions and upload dates. |
| **Installable version set** | `pip index versions replayt` (or inspect **PyPI** JSON API **`https://pypi.org/pypi/replayt/json`**) for available versions in your environment. |

Upstream **source** or **changelog** URLs may appear on the PyPI sidebar as **Project links** when the publisher provides them; prefer those over third-party mirrors. Feature and compatibility requests for **replayt** itself follow normal upstream channels (**[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — “Not a lever on core”).

## 6. Verifiable checklist (Spec / Build / review)

1. **Matrix** — §2 table matches **`pyproject.toml`** and the Python matrix in **`.github/workflows/ci.yml`**. When the matrix or **3.13** notes change, update §4.1.1 (and §4.1.2 if deferring) in the same pass.
2. **Pins** — Any change to **`replayt`**, OpenTelemetry, or **`requires-python`** updates §2–§4 here (including §3.1 float policy if policy shifts), **`docs/DEPENDENCY_AUDIT.md`**, **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** when normative OTel policy changes, and **[docs/CI_SPEC.md](CI_SPEC.md)** reference fingerprint when applicable.
3. **Boundary** — **`SPEC_REPLAYT_INTEGRATION_TESTS.md`** §7 **minimum replayt** stays in sync with the **`dev`** extra lower bound.
4. **Pin bump proof** — A **`replayt`** lower-bound change is supported by **green** default CI (**`test`** job): **`pip install -e ".[dev]"`** then full **`pytest`** collects and passes **`tests/integration/test_replayt_boundary.py`** on **each** matrix Python. See **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §5.1 and **[docs/CI_SPEC.md](CI_SPEC.md)** §5.
5. **Links** — §5 URLs remain valid; adjust if PyPI layout changes.
6. **Published distribution** — When **[docs/SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §5–§6 are satisfied for a version on PyPI or a named private index, confirm §2 **Published wheels and sdists** still matches integrator expectations (metadata on the live project page; index URL named in maintainer handoff if not public PyPI).

## Non-goals

- Declaring **replayt** as a **runtime** dependency of this library (unless mission scope changes elsewhere).
- Multi-version **replayt** CI matrices (optional future backlog).
- Adding **runtime** **`<`** upper bounds on **OpenTelemetry** under the current policy (**[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** §1); optional lockfiles or pinned CI constraints are a **separate** documented change, not silent drift.
