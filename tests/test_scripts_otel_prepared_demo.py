"""CI proof for scripts/otel_to_prepared_demo.py (docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md §6)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO_ROOT / "scripts" / "otel_to_prepared_demo.py"


def test_otel_to_prepared_demo_subprocess_exits_zero_and_prints_fields() -> None:
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "name: demo-prepared-span" in out
    assert re.search(r"trace_id: [0-9a-f]{32}\n", out)
    assert re.search(r"span_id: [0-9a-f]{16}\n", out)
    assert "kind: INTERNAL" in out
    assert "start_time_unix_nano:" in out
    assert "end_time_unix_nano:" in out
    assert "workflow_id: wf-demo-scripts" in out
    assert "step_id: step-demo-1" in out
    assert "attributes.app.demo: fiction" in out
