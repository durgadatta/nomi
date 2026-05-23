"""Cross-backend acceptance fixtures for the current Core IR ladder."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from prototype.runtime import create_session


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = ROOT / "prototype/tests/backend_fixtures"
NODE = shutil.which("node")

FIXTURES = {
    "01_literals_ops.nomi": ("x", "truth", "choice"),
    "02_functions_recursion.nomi": ("answer",),
    "03_collections_data.nomi": ("px", "items", "fallback"),
    "04_flow_for_each.nomi": ("total",),
    "05_patterns_errors_blocks.nomi": ("matched", "try_val", "collected"),
}

BACKENDS = ("core-runtime", "js-core-runtime")


def _run_fixture(filename: str, backend: str | None):
    session = create_session(mode="nomi", eval_backend=backend)
    return session.run(
        filename=FIXTURE_DIR / filename,
        capture_output=True,
    )


@pytest.mark.parametrize("filename", sorted(FIXTURES))
@pytest.mark.parametrize("backend", BACKENDS)
def test_backend_fixture_matches_python_ast_oracle(filename, backend):
    if backend == "js-core-runtime" and NODE is None:
        pytest.skip("node is not installed")

    oracle = _run_fixture(filename, "python-ast")
    candidate = _run_fixture(filename, backend)

    assert candidate.ok
    assert candidate.stdout == oracle.stdout
    for name in FIXTURES[filename]:
        assert candidate.bindings[name] == oracle.bindings[name]
