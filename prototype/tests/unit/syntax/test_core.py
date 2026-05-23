import pytest
import ast

from prototype.syntax.core import (
    Bind,
    Branch,
    CoreVerificationError,
    Diagnostic,
    Literal,
    Load,
    Module,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)
from prototype.syntax.surface import SurfaceNode


def test_verify_core_accepts_passive_core_tree():
    tree = Module(body=(Bind(name="x", value=Literal(value=1)),))

    verify_core(tree)


def test_verify_core_rejects_surface_nodes():
    class DummySurface(SurfaceNode):
        def lower(self):
            raise NotImplementedError

    tree = Module(body=(Bind(name="x", value=DummySurface()),))

    with pytest.raises(CoreVerificationError, match="surface node"):
        verify_core(tree)


def test_verify_core_rejects_non_core_values():
    tree = Module(body=(Bind(name="x", value=object()),))

    with pytest.raises(CoreVerificationError, match="non-core value"):
        verify_core(tree)


def test_dump_core_is_stable_and_readable():
    tree = Module(
        body=(
            Bind(name="x", value=Literal(value=1)),
            Branch(
                test=Load(name="x"),
                then_body=Module(body=(Diagnostic(message="ok"),)),
            ),
        )
    )

    assert dump_core(tree) == "\n".join(
        [
            "Module",
            "  Bind('x')",
            "    Literal(1)",
            "  Branch",
            "    Load('x')",
            "    Module",
            "      Diagnostic('ok')",
        ]
    )


def test_lower_python_ast_to_core_supports_tiny_inspection_subset():
    python_tree = ast.parse("x = 1\nfunc_result = f(x)\n")
    core = lower_python_ast_to_core(python_tree)

    assert dump_core(core) == "\n".join(
        [
            "Module",
            "  Bind('x')",
            "    Literal(1)",
            "  Bind('func_result')",
            "    Call",
            "      Load('f')",
            "      Load('x')",
        ]
    )


def test_lower_python_ast_to_core_marks_unsupported_shapes_as_diagnostics():
    python_tree = ast.parse("x = [n for n in xs]\n")

    assert "Diagnostic('unsupported Python AST: ListComp')" in dump_core(
        lower_python_ast_to_core(python_tree)
    )
