# Mission: OpenTelemetry Span Exporter for Replayt Workflows

## Users and problem

**Integrators** running Python services with OpenTelemetry tracing want a **narrow, well-tested bridge** from the OTel SDK to **replayt-oriented** workflow data. Today that path is underspecified; this package provides an explicit **exporter skeleton** and **documented intermediate representation** so replayt consumers can adopt it without forking replayt core.

## Replayt’s role

- **This repo** owns the OTel → replayt-prep adapter surface, **version pins**, and **CI** that prove the contract against declared OpenTelemetry versions.
- **Replayt core** stays upstream: compatibility and feature requests flow through normal channels (**[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — “Not a lever on core”).

## Primary positioning

- **Primary pattern:** **Framework bridge** (see **[REPLAYT_ECOSYSTEM_IDEA.md](REPLAYT_ECOSYSTEM_IDEA.md)**): OpenTelemetry Python SDK → documented prepared records for replayt workflows.

## Scope

| In scope | Out of scope (unless a later item says otherwise) |
| -------- | --------------------------------------------------- |
| **`SpanExporter`** implementation and **prepared span records** per **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** | Runtime dependency on **`replayt`** for the skeleton milestone |
| **`opentelemetry-api`** + **`opentelemetry-sdk`** as declared dependencies | Full replayt workflow execution, storage backends, or network export |
| Unit/integration tests described in the spec | Performance SLAs and advanced batching semantics |

## Success

- **Automated tests** (see **[CI_SPEC.md](CI_SPEC.md)**) cover span ingestion and transformation as specified in **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**.
- **Public API** remains small and listed explicitly (**`__all__`**); extension points are documented in the spec and design principles.
- **Changelog** records user-visible API and dependency changes under **Unreleased** until release.

## Compatibility matrix (initial)

| Component | Policy |
| --------- | ------ |
| **Python** | **`requires-python`** in **`pyproject.toml`** (currently **≥ 3.11**); CI matrix is the source of truth. |
| **OpenTelemetry** | **`opentelemetry-api`** and **`opentelemetry-sdk`** pinned with compatible lower bounds; audit trail in **`DEPENDENCY_AUDIT.md`**. |

Update this table when pins or CI versions change.
