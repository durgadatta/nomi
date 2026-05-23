"""Regression tests for reducing demo.nomi through Core IR."""

from pathlib import Path

from prototype.parser.nomi.usage import generate_ast
from prototype.syntax.core import (
    core_to_python_ast,
    lower_python_ast_to_core,
    verify_core,
)


def test_demo_nomi_reduces_to_strict_core_ir_and_python_ast():
    source = Path("samples/demo.nomi")
    tree = generate_ast(filename=source)

    core = lower_python_ast_to_core(tree)
    verify_core(core, strict=True)

    lowered = core_to_python_ast(core)
    assert len(lowered.body) > 0
