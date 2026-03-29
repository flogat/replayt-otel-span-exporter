# OpenTelemetry runtime dependency policy (upper bound vs float)

This document is the **normative contract** for how **`replayt-otel-span-exporter`** declares **`opentelemetry-api`** and **`opentelemetry-sdk`** in **`[project].dependencies`**, how **default CI** observes new upstream releases, and what **integrators** should pin in their own graphs. It refines backlog **“Document OpenTelemetry upper-bound or float policy in pyproject and COMPATIBILITY”**.

**Related docs:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (matrix and pin strategy), **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** (runtime table and audit context), **[docs/CI_SPEC.md](CI_SPEC.md)** §4 (install path).

## 1. Decision summary

| Question | Project policy |
| -------- | -------------- |
| **Upper bounds on runtime OTel?** | **No.** Runtime dependencies use **PEP 440 lower bounds only** (for example **`>=1.0.0`**). Do **not** add **`<`** upper caps to **`opentelemetry-api`** / **`opentelemetry-sdk`** in **`[project].dependencies`** unless a **separate backlog** explicitly changes this policy and updates this spec, **COMPATIBILITY**, **DEPENDENCY_AUDIT**, and **CHANGELOG** in one maintenance pass. |
| **How do new OTel minors get exercised?** | **Floating resolution:** **`pip install -e ".[dev]"`** (no committed lockfile on the default CI path) installs the **latest** **`opentelemetry-api`** and **`opentelemetry-sdk`** versions that satisfy the declared lower bounds **and** remain compatible with the rest of the **`[dev]`** graph. Every **green** **`test`** job on **`master`** / integration branches therefore ran the full **`pytest`** suite against **whatever versions pip resolved that day** on each matrix Python. |
| **What should integrators pin?** | Treat this package’s OTel entries as **minimum supported** versions, not as an exact bill of materials. For **reproducible** deployments, pin **`opentelemetry-api`** and **`opentelemetry-sdk`** to the **same upstream OpenTelemetry Python release line** (matching versions from [PyPI](https://pypi.org/project/opentelemetry-api/) / [SDK](https://pypi.org/project/opentelemetry-sdk/)) alongside this package, or use an organization lockfile. |

## 2. Rationale (lower bounds only)

- **Library ergonomics:** Applications and platforms often **already** pin OTel. Adding **tight upper bounds** here can make **`pip`** fail to resolve a single environment when another dependency needs a **newer** OTel **1.x** release.
- **Signal without caps:** **CI** already reinstalls on every run; when upstream ships a **breaking** change in a version that still satisfies our lower bound, **tests go red** and maintainers **fix forward** (code or **raised minimum**), document the change in **CHANGELOG**, and refresh **COMPATIBILITY** / **CI_SPEC** reference text as needed.
- **API / SDK pairing:** **`opentelemetry-api`** and **`opentelemetry-sdk`** MUST stay on the **same OpenTelemetry Python release line** when maintainers bump pins (**[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime).

## 3. Major versions and semver expectations

- **OpenTelemetry Python 1.x:** This policy assumes **1.x** minors remain compatible with the **documented public usage** of this package (`ReadableSpan`, exporter hooks, trace API usage covered by tests). If an upstream **1.x** release breaks the suite, respond with a **fix** and/or a **higher lower bound** in **`pyproject.toml`**, not with a silent upper cap.
- **Hypothetical OpenTelemetry Python 2.x:** Supporting **2.x** is **out of scope** for this document until the project explicitly adopts it (likely a **semver major** or dedicated backlog). Do not imply **2.x** support from **`>=1.0.0`** alone.

## 4. Relationship to CI and supply-chain jobs

- **`test` job:** Proves the code against the **resolved** OTel versions after **`pip install -e ".[dev]"`** on **each** CI Python (**[docs/CI_SPEC.md](CI_SPEC.md)** §4–§5, **Reference fingerprint**). That is the **primary** mechanism for catching breakage from **new OTel releases**.
- **`supply-chain` job:** Runs **`pip-audit`** on the same install graph; it validates **known CVE policy** for declared and transitive packages (**[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**). It does **not** replace **pytest** for **API / behavior** compatibility.
- **Optional future hardening** (not required by this backlog): scheduled workflows, lockfiles, or **`pip install`** with **`--resolution`** / constraints **may** be added later if documented in **CI_SPEC** and **COMPATIBILITY**.

## 5. Maintainer maintenance checklist

When changing OTel runtime bounds or reacting to upstream breakage:

1. Update **`pyproject.toml`** (keep **API** and **SDK** aligned per **DEPENDENCY_AUDIT**).
2. Update **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §2 / §3 and this file if policy narrative changes.
3. Update **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime if the numeric bound or risk story changes.
4. Record user-visible dependency policy or bound changes under **CHANGELOG** **[Unreleased]**.
5. Ensure **green** default **`test`** job on **all** matrix Pythons after **`pip install -e ".[dev]"`**.

## 6. Verifiable acceptance criteria (backlog / gate)

A gate or Builder can mark the backlog **done** when all of the following are true:

1. **COMPATIBILITY** — §2 (**OpenTelemetry** rows) and §3 (**Pin strategy**) describe **lower bounds only**, **no runtime upper cap**, **floating CI resolution**, and link to this spec.
2. **DEPENDENCY_AUDIT** — § Runtime documents the same policy and links here (numeric bounds remain consistent with **`pyproject.toml`**).
3. **CI_SPEC** — §4 (or equivalent) states that default CI installs **without** a project lockfile so **OpenTelemetry** versions **float** to newest compatible releases unless **`pyproject.toml`** pins change; cross-link this spec.
4. **pyproject.toml** — Runtime **`opentelemetry-api`** / **`opentelemetry-sdk`** lines either carry brief comments pointing at **COMPATIBILITY** / this spec **or** the policy is solely in those docs with **COMPATIBILITY** explicitly naming **`pyproject.toml`** as the numeric source of truth (at least one of: comments in **`pyproject.toml`** OR an unambiguous matrix row is required; **both** is preferred).
5. **MISSION** (or **COMPATIBILITY** if MISSION is trimmed) — Compatibility summary for OpenTelemetry points integrators at this spec in addition to **DEPENDENCY_AUDIT**.
6. **CHANGELOG** — **Unreleased** notes the documented policy when this backlog ships (documentation-only is sufficient).
