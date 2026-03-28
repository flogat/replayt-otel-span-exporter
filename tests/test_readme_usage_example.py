"""README usage example is CI-proven (docs/SPEC_README_QUICK_START.md §4)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_readme_usage_example_snippet_matches_readme_contract() -> None:
    snippet_path = Path(__file__).resolve().parent / "readme_usage_example_snippet.py"
    spec = spec_from_file_location("readme_usage_example_snippet", snippet_path)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.run_readme_usage_example()
