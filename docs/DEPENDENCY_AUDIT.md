# Dependency audit

CI **`supply-chain`** runs `pip-audit --ignore-vuln CVE-2026-4539 --ignore-vuln CVE-2025-69872 --desc` after `pip install -e ".[dev]"`. PyPA **pip-audit** has no `--severity-high` flag; any reported vulnerability fails unless ignored here and in `.github/workflows/ci.yml`.

**Supported versions and CI alignment:** See **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** for the compatibility matrix, pin strategy, and how the **`test`** / **`supply-chain`** matrices relate to **`pyproject.toml`**. **OpenTelemetry** upper-bound vs float policy (why there is **no** **`<`** cap on runtime deps, how CI observes new releases, integrator pinning) is normative in **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**.

## Runtime: OpenTelemetry

| Package | Policy |
| ------- | ------ |
| **`opentelemetry-api`** | Lower bound **`>=1.0.0`** in **`pyproject.toml`** only — **no** PEP 440 **upper bound** on the **1.x** line under current policy. Keep in step with **`opentelemetry-sdk`** from the **same** upstream release line. |
| **`opentelemetry-sdk`** | Lower bound **`>=1.0.0`**; required for **`SpanExporter`**, **`TracerProvider`**, and **`ReadableSpan`** used by **`ReplaytSpanExporter`**. Bump both API and SDK together when adjusting pins. |

**CI observation:** After **`pip install -e ".[dev]"`**, **`pip`** resolves **API** and **SDK** to the **newest** versions satisfying these floors (and compatible with the **`dev`** graph). Default **`test`** CI therefore exercises the adapter against **floating** **1.x** OTel until floors are raised — see **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** §4 and **[docs/CI_SPEC.md](CI_SPEC.md)** §4.

## Test / integration: replayt

| Package | Policy |
| ------- | ------ |
| **`replayt`** | Lower bound **`>=0.4.25`** on the **`dev`** extra (not a runtime dependency of the library). Boundary tests in **`tests/integration/test_replayt_boundary.py`** use **`Runner`** / **`RunContext.set`** / **`Workflow`** / **`SQLiteStore`** / **`DryRunLLMClient`** / **`LogMode`** per **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7. **`packaging`** on **`dev`** supports the §4.6 installed-version check against that specifier. Bump the lower bound when replayt API used by those imports changes. |

## Accepted risk: CVE-2026-4539 (pygments)

Transitive **pygments** may appear in the dev/install graph and trigger **CVE-2026-4539** (ReDoS in **AdlLexer**). We do not use that lexer in this package; re-assess on dependency bumps. Remove the ignore from CI when the tree is clean.

## Accepted risk: CVE-2025-69872 (diskcache)

Transitive **diskcache** (pulled in with **`replayt`**) is flagged for default **pickle** serialization (**CVE-2025-69872**). This package does not operate untrusted cache directories in CI or tests; re-check when **diskcache** ships a fix or **replayt** changes dependencies. **`dev`** also pins **`requests>=2.33.0`** so **CVE-2026-25645** stays resolved for the install graph audited in CI.
