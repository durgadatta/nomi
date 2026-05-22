from pathlib import Path

import pytest

from prototype.interpreter.nomi.usage import run_eval_loop
from prototype.parser.nomi.frontend import get_parser_frontend
from prototype.runtime import execute


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_rust_fast_ast_core_demo_ast_executes_downstream(capsys):
    rust = get_parser_frontend("rust-fast-ast")
    path = REPO_ROOT / "scripts" / "demo.nomi"

    try:
        tree = rust.generate_python_ast(filename=path)
    except RuntimeError as exc:
        if "cargo is required" in str(exc):
            pytest.skip(str(exc))
        raise

    bindings = run_eval_loop(tree=tree)
    output = capsys.readouterr().out

    assert bindings["filtered"] == [30, 60, 84, 16]
    assert "Demo completed" in output


def test_rust_fast_ast_executes_through_runtime_frontend_selector():
    path = REPO_ROOT / "scripts" / "demo.nomi"

    try:
        result = execute(filename=path, mode="nomi", parser_frontend="rust-fast-ast")
    except RuntimeError as exc:
        if "cargo is required" in str(exc):
            pytest.skip(str(exc))
        raise

    assert result.ok
    assert result.bindings["filtered"] == [30, 60, 84, 16]
    assert "Demo completed" in result.stdout
