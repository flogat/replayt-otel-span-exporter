# Dependency audit

CI **`supply-chain`** runs `pip-audit --ignore-vuln CVE-2026-4539 --desc` after `pip install -e ".[dev]"`. PyPA **pip-audit** has no `--severity-high` flag; any reported vulnerability fails unless ignored here and in `.github/workflows/ci.yml`.

## Runtime: OpenTelemetry

| Package | Policy |
| ------- | ------ |
| **`opentelemetry-api`** | Lower bound **`>=1.0.0`** in **`pyproject.toml`**; keep in step with **`opentelemetry-sdk`** from the same release line. |
| **`opentelemetry-sdk`** | Lower bound **`>=1.0.0`**; required for **`SpanExporter`**, **`TracerProvider`**, and **`ReadableSpan`** used by **`ReplaytSpanExporter`**. Bump both API and SDK together when adjusting pins. |

## Accepted risk: CVE-2026-4539 (pygments)

Transitive **pygments** may appear in the dev/install graph and trigger **CVE-2026-4539** (ReDoS in **AdlLexer**). We do not use that lexer in this package; re-assess on dependency bumps. Remove the ignore from CI when the tree is clean.
