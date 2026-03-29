# OpenTelemetry runtime dependency policy (upper bound vs float)

This document is the **normative contract** for how **`replayt-otel-span-exporter`** declares **`opentelemetry-api`** and **`opentelemetry-sdk`** in **`[project].dependencies`**, how **default CI** observes new upstream releases, and what **integrators** should pin in their own graphs.

**Backlog traceability**

| Mission Control item | Role |
| -------------------- | ---- |
| **`9b94e677-914a-471a-8499-071c1cb92455`** (phase **2** spec lead) | **Clarify** upper-bound strategy, CI proof story, and integrator pins across **`pyproject.toml`**, **[COMPATIBILITY.md](COMPATIBILITY.md)**, **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** — this doc is the single normative policy. |
| Earlier doc-only backlog **“Document OpenTelemetry upper-bound or float policy in pyproject and COMPATIBILITY”** | Initial policy text, **`tests/test_compatibility_contract.py`** wiring, and cross-links. |

**Related docs:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (matrix and pin strategy), **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** (runtime table, **`pip-audit`** context), **[docs/CI_SPEC.md](CI_SPEC.md)** §4–§5 (install path and suite bar).

## 1. Decision summary

| Question | Project policy |
| -------- | -------------- |
| **Upper bounds on runtime OTel?** | **No.** Runtime dependencies use **PEP 440 lower bounds only** (for example **`>=1.0.0`**). Do **not** add **`<`** upper caps to **`opentelemetry-api`** / **`opentelemetry-sdk`** in **`[project].dependencies`** unless a **separate backlog** explicitly changes this policy and updates this spec, **COMPATIBILITY**, **DEPENDENCY_AUDIT**, and **CHANGELOG** in one maintenance pass. |
| **How do new OTel releases get exercised?** | **Floating resolution:** **`pip install -e ".[dev]"`** (no committed lockfile on the default CI path) installs the **latest** **`opentelemetry-api`** and **`opentelemetry-sdk`** versions that satisfy the declared lower bounds **and** remain compatible with the rest of the **`[dev]`** graph. PEP 440 specifiers here are **not** labeled “minor-only”; **any** upstream **1.x** release that satisfies **`>=1.0.0`** (and the resolver graph) may be chosen. Every **green** **`test`** job on **`master`** / integration branches therefore ran the full **`pytest`** suite against **whatever versions pip resolved that day** on each matrix Python (**[docs/CI_SPEC.md](CI_SPEC.md)** §4–§5). |
| **What should integrators pin?** | Treat this package’s OTel entries as **minimum supported** versions, not as an exact bill of materials. For **reproducible** deployments, pin **`opentelemetry-api`** and **`opentelemetry-sdk`** to the **same upstream OpenTelemetry Python release line** (matching versions from [PyPI](https://pypi.org/project/opentelemetry-api/) / [SDK](https://pypi.org/project/opentelemetry-sdk/)) alongside this package, or use an organization lockfile — see **§1.1**. |

### 1.1 Integrator pinning (normative)

- **Pair API + SDK:** Always pin **both** packages to **matching** release versions (same release train). Mixing arbitrary API/SDK versions is out of policy for interpreting support from this repo.
- **Floor vs lock:** This library declares a **floor** only. Integrator **`requirements.txt`** / **`uv.lock`** / Poetry / PDM should pin **exact** or **capped** OTel versions **for the application**, independent of this package’s lower bound.
- **Example shape (illustrative):** `opentelemetry-api==1.40.0` and `opentelemetry-sdk==1.40.0` — replace with versions you validate; do not copy from this doc as a live recommendation.

### 1.2 Forbidden patterns in **`[project].dependencies`** (runtime OTel)

Unless a **separate backlog** reverses policy and updates all linked docs + **CHANGELOG**:

- Do **not** use **`<`**, **`<=`** combined with an upper cap, **`, <2`**, **`~=1.0,<2`**, or any specifier that **excludes** newer **1.x** releases that would otherwise satisfy the documented intent (broad **1.x** compatibility).
- **`tests/test_compatibility_contract.py`** **`test_opentelemetry_runtime_deps_have_no_upper_bound_in_specifier`** asserts the stricter rule **no `<` substring** in the specifier string for runtime **`opentelemetry-api`** / **`opentelemetry-sdk`** (see **§6**).

## 2. Rationale (lower bounds only)

- **Library ergonomics:** Applications and platforms often **already** pin OTel. Adding **tight upper bounds** here can make **`pip`** fail to resolve a single environment when another dependency needs a **newer** OTel **1.x** release.
- **Signal without caps:** **CI** already reinstalls on every run; when upstream ships a **breaking** change in a version that still satisfies our lower bound, **tests go red** and maintainers **fix forward** (code or **raised minimum**), document the change in **CHANGELOG**, and refresh **COMPATIBILITY** / **CI_SPEC** reference text as needed.
- **API / SDK pairing:** **`opentelemetry-api`** and **`opentelemetry-sdk`** MUST stay on the **same OpenTelemetry Python release line** when maintainers bump pins (**[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime).

## 3. Major versions and semver expectations

- **OpenTelemetry Python 1.x:** This policy assumes **1.x** minors remain compatible with the **documented public usage** of this package (`ReadableSpan`, exporter hooks, trace API usage covered by tests). If an upstream **1.x** release breaks the suite, respond with a **fix** and/or a **higher lower bound** in **`pyproject.toml`**, not with a silent upper cap.
- **Hypothetical OpenTelemetry Python 2.x:** Supporting **2.x** is **out of scope** for this document until the project explicitly adopts it (likely a **semver major** or dedicated backlog). Do not imply **2.x** support from **`>=1.0.0`** alone.

## 4. Relationship to CI and supply-chain jobs

**What default CI proves when OpenTelemetry publishes a new release**

1. The next **`push`** / **`pull_request`** that runs **`.github/workflows/ci.yml`** executes **`pip install -e ".[dev]"`** on **each** matrix Python (**3.11** / **3.12** / **3.13** unless **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4.1.2 defers one).
2. **`pip`** resolves **`opentelemetry-api`** and **`opentelemetry-sdk`** to the **newest** versions compatible with **`[project].dependencies`** and the **`dev`** extra graph (no project lockfile on this path — **[docs/CI_SPEC.md](CI_SPEC.md)** §4).
3. A **green** **`test`** job means the **entire** default **`pytest`** command (**[docs/CI_SPEC.md](CI_SPEC.md)** §5) passed against **that** resolved pair on **that** cell — including integration smokes such as **`tests/integration/test_opentelemetry_api_usage.py`** and the rest of the suite mapped in **[docs/MISSION.md](MISSION.md)**.
4. **Not guaranteed by metadata alone:** **`pyproject.toml`** does **not** record the exact resolved OTel version; operators infer **what ran** from **CI logs** (resolver output) or by reproducing **`pip install -e ".[dev]"`** locally. The **contract** is **floating resolution + green tests**, not a pinned OTel version in source control.

**Jobs**

- **`test` job:** Proves **API / behavior** compatibility against the **resolved** OTel versions after **`pip install -e ".[dev]"`** on **each** CI Python (**[docs/CI_SPEC.md](CI_SPEC.md)** §4–§5, **Reference fingerprint**). This is the **primary** signal when upstream ships a new **1.x** release.
- **`supply-chain` job:** Runs **`pip-audit`** on the same install graph; it validates **documented CVE ignore / fix policy** (**[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**). It does **not** assert OTel API stability and does **not** replace **`pytest`** for adapter behavior.
- **Optional future hardening** (separate backlog): scheduled workflows, committed lockfiles, or explicit **`constraints.txt`** in CI **may** be added if documented in **CI_SPEC** and **COMPATIBILITY**.

## 5. Maintainer maintenance checklist

When changing OTel runtime bounds or reacting to upstream breakage:

1. Update **`pyproject.toml`** (keep **API** and **SDK** aligned per **DEPENDENCY_AUDIT**).
2. Update **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §2 / §3 and this file if policy narrative changes.
3. Update **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** § Runtime if the numeric bound or risk story changes.
4. Record user-visible dependency policy or bound changes under **CHANGELOG** **[Unreleased]**.
5. Ensure **green** default **`test`** job on **all** matrix Pythons after **`pip install -e ".[dev]"`**.

## 6. Verifiable acceptance criteria (backlog / gate)

A gate or Builder can mark the OpenTelemetry dependency-policy backlogs **done** when all of the following are true:

1. **COMPATIBILITY** — §2 (**OpenTelemetry** rows) and §3 (**Pin strategy**, especially **§3.1**) describe **lower bounds only**, **no** runtime **`<`** upper cap on the **1.x** line, **floating CI resolution**, integrator **API+SDK pairing**, and link to this spec (filename **`SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md`**).
2. **DEPENDENCY_AUDIT** — § Runtime documents the same policy, distinguishes **`pip-audit`** from **pytest** compatibility proof, and links this spec (same filename substring as in **(1)**).
3. **CI_SPEC** — §4 states default CI installs **without** a project lockfile so **OpenTelemetry** versions **float** to newest compatible releases unless **`pyproject.toml`** floors change; §5 states the **`pytest`** bar; cross-link this spec.
4. **pyproject.toml** — Runtime **`opentelemetry-api`** / **`opentelemetry-sdk`** lines carry comments pointing at **COMPATIBILITY** §3.1 and this spec (**both** are preferred; numeric truth stays in **`pyproject.toml`**).
5. **MISSION** — Compatibility matrix **OpenTelemetry** row points integrators at this spec and **DEPENDENCY_AUDIT**; Mission Control **`9b94e677-914a-471a-8499-071c1cb92455`** traceability (if present) remains aligned.
6. **CHANGELOG** — **Unreleased** notes documentation/policy updates when this work ships (documentation-only is sufficient).
7. **Automated contract** — **`tests/test_compatibility_contract.py`** passes: runtime OTel specifiers contain **no** **`<`**, and **COMPATIBILITY** + **DEPENDENCY_AUDIT** include **`SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md`** (see **`test_opentelemetry_runtime_deps_have_no_upper_bound_in_specifier`** and **`test_compatibility_and_dependency_audit_link_opentelemetry_policy_spec`**).

## 7. Acceptance criteria — Mission Control **`9b94e677-914a-471a-8499-071c1cb92455`** (clarify upper-bound strategy)

Phase **2** (spec lead) and phase **2b** (spec gate) treat the backlog **“Clarify OpenTelemetry upper-bound strategy in pyproject and COMPATIBILITY”** as satisfied when:

| # | Criterion |
| - | --------- |
| A | **Policy choice documented:** Runtime **`opentelemetry-api`** / **`opentelemetry-sdk`** use **lower bounds only** on the **1.x** line; **no** **`<`**-style upper caps in **`[project].dependencies`** unless a future backlog explicitly changes policy (**§1**, **§1.2**). |
| B | **CI proof documented:** **§4** (this doc) and **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §3.1 / §4 explain that **green `test`** after floating **`pip install -e ".[dev]"`** is how new upstream **1.x** releases are exercised; **`supply-chain`** / **`pip-audit`** is explicitly **not** the OTel API compatibility proof (**[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**). |
| C | **Integrator pins documented:** **§1.1** — pin **API** and **SDK** together; treat this package as a **floor**; use app-level pins or lockfiles for reproducibility. |
| D | **Surfaces updated:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)**, **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**, this spec, **[docs/CI_SPEC.md](CI_SPEC.md)** (traceability), **[docs/MISSION.md](MISSION.md)** (traceability + matrix), and **`pyproject.toml`** comments are mutually consistent with **§6**–**§7**. |
