"""The hosted with reduction retains its protocol and portable boundary."""

import ast

import pytest

from prototype.interpreter.constants import CONTEXT_METHODS_HELPER
from prototype.parser.nomi.desugar.with_ import With
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import CoreVerificationError, lower_python_ast_to_core, verify_core


def _lower(source):
    return ast.fix_missing_locations(With().visit(ast.parse(source)))


def test_nested_scopes_reduce_recursively_to_guarded_finalizers():
    tree = _lower("with outer:\n    with inner as (first, second):\n        pass\n")
    assert not any(isinstance(node, ast.With) for node in ast.walk(tree))
    scopes = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
    assert len(scopes) == 2
    assert all(scope.finalbody and not scope.orelse for scope in scopes)
    assert all(scope.handlers[0].type._nomi_builtin_reference == "BaseException" for scope in scopes)


def test_generated_protocol_references_are_not_ordinary_source_loads():
    tree = _lower("with manager:\n    raise ValueError('body')\n")
    intrinsic = [
        node._nomi_builtin_reference for node in ast.walk(tree)
        if isinstance(node, ast.Name) and hasattr(node, "_nomi_builtin_reference")
    ]
    assert set(intrinsic) == {CONTEXT_METHODS_HELPER, "BaseException", "type"}
    assert all(
        node.id.startswith("__nomi_builtin_")
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and hasattr(node, "_nomi_builtin_reference")
    )


@pytest.mark.parametrize(
    "declaration",
    (
        "_with_manager_1 = 1\n",
        "def function(_with_manager_1):\n    pass\n",
        "global _with_manager_1\n",
        "match value:\n    case _with_manager_1:\n        pass\n",
        "match value:\n    case [*_with_manager_1]:\n        pass\n",
        "match value:\n    case {'key': _, **_with_manager_1}:\n        pass\n",
        "import os as _with_manager_1\n",
        "try:\n    pass\nexcept Exception as _with_manager_1:\n    pass\n",
    ),
)
def test_temporary_allocator_reserves_authored_and_declared_names(declaration):
    tree = _lower(declaration + "with manager:\n    pass\n")
    assert tree.body[-5].targets[0].id != "_with_manager_1"


def test_hosted_protocol_intrinsics_cannot_silently_enter_portable_core(capsys):
    tree = _lower("print('before')\nwith manager:\n    print('body')\n")
    core = lower_python_ast_to_core(tree)
    with pytest.raises(CoreVerificationError, match="unsupported"):
        verify_core(core, strict=True)
    with pytest.raises(CoreVerificationError, match="unsupported"):
        CoreRuntimeEvaluator().evaluate(core)
    assert capsys.readouterr().out == ""


def test_a_hosted_intrinsic_load_is_itself_rejected_by_core():
    intrinsic = ast.Name(id="__nomi_builtin_type__", ctx=ast.Load())
    intrinsic._nomi_builtin_reference = "type"
    tree = ast.Module(body=[ast.Expr(value=intrinsic)], type_ignores=[])
    core = lower_python_ast_to_core(tree)
    with pytest.raises(CoreVerificationError, match="hosted protocol intrinsic"):
        verify_core(core, strict=True)
