# replayt (upstream)

No third-party verbatim excerpts in this file.

## Why this matters here

**replayt** is a **separate** PyPI distribution from **replayt-otel-span-exporter**. This adapter prepares span-shaped data for replayt-oriented consumers **without** listing **`replayt`** under **`[project].dependencies`**. CI and local **contributor** installs use **`pip install -e ".[dev]"`**, which pulls **`replayt`** only for boundary tests per **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](../SPEC_REPLAYT_INTEGRATION_TESTS.md)**. The exporter wheel itself does not require **replayt** at runtime.

## Release tracking

For supported **replayt** versions on the **`dev`** path and PyPI links, use **[docs/COMPATIBILITY.md](../COMPATIBILITY.md)** (section 5).

## Canonical links

- **replayt on PyPI:** [https://pypi.org/project/replayt/](https://pypi.org/project/replayt/)

PyPI metadata for **replayt** may not list a home page or source URL; when the project publishes official repository or changelog links on the project page, prefer those in maintenance passes to this stub.
