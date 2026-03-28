#!/usr/bin/env bash
# Post-upload checks per docs/SPEC_FIRST_ALPHA_RELEASE.md §5.
# Usage:
#   ./scripts/verify_published_release.sh [VERSION]
# Optional env:
#   INDEX_URL   — if set, passed as pip --index-url (private index)
#   TRUSTED_HOST — if set, passed as pip --trusted-host
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-}"
if [[ -z "${VERSION}" ]]; then
  VERSION="$(python3 -c "import tomllib, pathlib; print(tomllib.loads(pathlib.Path('${ROOT}/pyproject.toml').read_text())['project']['version'])")"
fi

TMP="${TMPDIR:-/tmp}/replayt-otel-verify-$$"
cleanup() { rm -rf "${TMP}"; }
trap cleanup EXIT

python3 -m venv "${TMP}/venv"
# shellcheck source=/dev/null
source "${TMP}/venv/bin/activate"
python -m pip install --upgrade pip >/dev/null

EXTRA=()
if [[ -n "${INDEX_URL:-}" ]]; then
  EXTRA+=(--index-url "${INDEX_URL}")
fi
if [[ -n "${TRUSTED_HOST:-}" ]]; then
  EXTRA+=(--trusted-host "${TRUSTED_HOST}")
fi
python -m pip install "${EXTRA[@]}" "replayt-otel-span-exporter==${VERSION}"

python - <<PY
import importlib.metadata as m
import replayt_otel_span_exporter as pkg
want = "${VERSION}"
got = m.version("replayt-otel-span-exporter")
assert got == want, (got, want)
assert pkg.__version__ == want, (pkg.__version__, want)
PY

python - <<'PY'
import importlib.util
import sys
if importlib.util.find_spec("replayt") is not None:
    sys.exit("replayt must not be installed for a minimal library install")
PY

echo "OK: replayt-otel-span-exporter==${VERSION} import and metadata checks passed."
