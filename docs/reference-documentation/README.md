# Reference documentation (replayt and OpenTelemetry)

This folder holds **link-first** index pages for upstream context. It does **not** replace **[docs/COMPATIBILITY.md](../COMPATIBILITY.md)** or **[docs/MISSION.md](../MISSION.md)**.

## Licensing and attribution

Files here may **quote** or **summarize** upstream documentation in **this repository’s** words. The license at the repository root applies to **original** prose written for this tree, **not** to text copied verbatim from third-party sites.

There are **no** verbatim upstream copies in this revision. **[opentelemetry-python.md](opentelemetry-python.md)** and **[replayt.md](replayt.md)** are stub indexes only; each file states that under its title. Readers should rely on the linked sources for upstream license terms. This section is **not** legal advice. Upstream licensing for OpenTelemetry projects is commonly **Apache-2.0** (see upstream repositories and [opentelemetry-sdk on PyPI](https://pypi.org/project/opentelemetry-sdk/) classifiers). For **replayt**, see [replayt on PyPI](https://pypi.org/project/replayt/) and any source repository the project publishes.

## Scope (in / out)

**In scope:** Integration-oriented context for **replayt-otel-span-exporter**: OpenTelemetry **trace** and **export** concepts used by **`ReplaytSpanExporter`**, and **replayt** positioning so it is clear why **`replayt`** is not a runtime dependency of the wheel and how **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](../SPEC_REPLAYT_INTEGRATION_TESTS.md)** exercises the import boundary on the **`dev`** install path.

**Out of scope:** Full mirrors of **opentelemetry.io**, the entire **opentelemetry-python** repository, or **replayt** product documentation end-to-end; generated API dumps for every symbol; using this folder instead of **COMPATIBILITY** or **MISSION** for policy.

## Refresh policy

**When to refresh:** After **`pyproject.toml`** bumps OpenTelemetry lower bounds, the **`replayt`** **`dev`** lower bound, or when linked upstream pages or short summaries here are **materially** wrong for this repo’s contracts.

**Who:** Maintainers or contributors in the same PR as pin or contract changes when integration behavior is affected (same discipline as **COMPATIBILITY**).

**How:** Prefer updating stub links and short summaries over growing the tree. If a snapshot were removed in favor of links-only, delete stale quoted text rather than leaving contradictions.
