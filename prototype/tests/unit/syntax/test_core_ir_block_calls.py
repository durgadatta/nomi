"""Tests for preserving block calls in Core IR."""

import ast as py_ast

from prototype.parser.nomi.usage import generate_ast
from prototype.parser.nomi.desugar.pipeline import desugar_module_for_nomi_interpreter
from prototype.syntax.core import Call, Function, lower_python_ast_to_core, verify_core


def test_lower_python_ast_to_core_preserves_block_call_body():
    source = (
        "func twice():\n"
        "    yield\n"
        "count = 0\n"
        "twice():\n"
        "    count = count + 1\n"
    )
    tree = desugar_module_for_nomi_interpreter(generate_ast(code=source))

    core = lower_python_ast_to_core(tree)
    call = core.body[2]

    assert isinstance(call, Call)
    assert isinstance(call.block, Function)
    assert call.block.params == ()
    assert len(call.block.body.body) == 1
    verify_core(core, strict=True)


def test_core_to_python_ast_roundtrips_block_call_keyword():
    source = (
        "func each(sequence):\n"
        "    yield 1\n"
        "each([1]) -> n:\n"
        "    seen = n\n"
    )
    tree = desugar_module_for_nomi_interpreter(generate_ast(code=source))
    core = lower_python_ast_to_core(tree)

    from prototype.syntax.core import core_to_python_ast

    lowered = core_to_python_ast(core)
    dumped = py_ast.dump(lowered, include_attributes=False)

    assert "__block__" in dumped
