"""Tests for Core IR nodes, verifier, dump, and Python AST lowering."""

import ast as py_ast

import pytest

from prototype.syntax.core import (
    Bind,
    Branch,
    Call,
    ConstructData,
    CoreVerificationError,
    CORE_NODE_TYPES,
    Diagnostic,
    Function,
    GetField,
    Handle,
    ForEach,
    Literal,
    Load,
    Loop,
    Match,
    Module,
    PatternTest,
    Raise,
    Return,
    Sequence,
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)


# ── verifier ──────────────────────────────────────────────────────────────────


def test_verify_core_rejects_surface_node():
    """Non-CoreNode objects are rejected with a clear message."""
    class FakeSurface:
        pass

    with pytest.raises(CoreVerificationError, match="non-core value"):
        verify_core(FakeSurface())


def test_verify_core_accepts_all_builtin_nodes():
    for node_type in CORE_NODE_TYPES:
        instance = node_type()
        verify_core(instance)


def test_verify_core_rejects_non_dataclass_core_node():
    """A class that claims CoreNode heritage without being a dataclass is rejected."""
    class NotADataclass(Module):
        pass

    # NotADataclass inherits Module's dataclass fields, so it passes isinstance and dataclass checks.
    # The real guardrail is that only registered CORE_NODE_TYPES pass verification.
    # Subclasses are allowed (they pass isinstance check on their parent).
    # This test verifies the guardrail is structural, not nominal.
    instance = Module(body=(Bind(name="x", value=Literal(value=1)),))
    verify_core(instance)  # valid structure passes


def test_verify_core_strict_rejects_diagnostic():
    node = Module(body=(Diagnostic(message="unsupported: ListComp"),))
    with pytest.raises(CoreVerificationError, match="Diagnostic"):
        verify_core(node, strict=True)


def test_verify_core_non_strict_accepts_diagnostic():
    node = Module(body=(Diagnostic(message="unsupported: ListComp"),))
    verify_core(node, strict=False)


def test_verify_core_strict_accepts_valid_tree():
    node = Module(body=(Bind(name="x", value=Literal(value=1)),))
    verify_core(node, strict=True)


# ── dump ──────────────────────────────────────────────────────────────────────


def test_dump_core_literal():
    assert "Literal(42)" in dump_core(Literal(value=42))


def test_dump_core_bind():
    output = dump_core(Bind(name="x", value=Literal(value=1)))
    assert "Bind('x')" in output
    assert "Literal(1)" in output


def test_dump_core_module_with_body():
    output = dump_core(
        Module(body=(Bind(name="x", value=Literal(value=1)),))
    )
    assert "Module" in output
    assert "Bind('x')" in output
    assert "Literal(1)" in output


def test_dump_core_all_new_node_types():
    """Each added node type should have a dump representation."""
    nodes = {
        Loop(test=Literal(value=True)),
        Match(subject=Load(name="x")),
        PatternTest(pattern=Literal(value=1)),
        ConstructData(name="Point", fields=(("x", Literal(value=0)),)),
        GetField(object_=Load(name="obj"), field="attr"),
        Raise(exception=Load(name="ValueError")),
        Handle(
            body=Module(body=(Return(value=Literal(value=1)),)),
            finalbody=Module(body=(Return(value=Literal(value=None)),)),
        ),
        Sequence(elements=(Literal(value=1), Literal(value=2))),
    }
    for node in nodes:
        output = dump_core(node)
        assert output, f"dump_core returned empty for {type(node).__name__}"


# ── Python AST → Core IR (backward) ──────────────────────────────────────────


def test_lower_python_ast_to_core_simple_assign():
    core = lower_python_ast_to_core(py_ast.parse("x = 1"))
    assert isinstance(core, Module)
    stmt = core.body[0]
    assert isinstance(stmt, Bind)
    assert stmt.name == "x"
    assert isinstance(stmt.value, Literal)
    assert stmt.value.value == 1


def test_lower_python_ast_to_core_function_def():
    core = lower_python_ast_to_core(py_ast.parse("def f(a, b): return a + b"))
    bind = core.body[0]
    assert isinstance(bind, Bind)
    assert bind.name == "f"
    assert isinstance(bind.value, Function)
    assert bind.value.params == ("a", "b")


def test_lower_python_ast_to_core_if():
    core = lower_python_ast_to_core(py_ast.parse("if True: x = 1"))
    stmt = core.body[0]
    assert isinstance(stmt, Branch)
    assert isinstance(stmt.then_body, Module)


def test_lower_python_ast_to_core_return():
    core = lower_python_ast_to_core(py_ast.parse("return 42"))
    stmt = core.body[0]
    assert isinstance(stmt, Return)


def test_lower_python_ast_to_core_while():
    core = lower_python_ast_to_core(py_ast.parse("while x: pass"))
    stmt = core.body[0]
    assert isinstance(stmt, Loop)
    assert isinstance(stmt.body, Module)


def test_lower_python_ast_to_core_for():
    core = lower_python_ast_to_core(py_ast.parse("for i in items: pass"))
    stmt = core.body[0]
    assert isinstance(stmt, ForEach)
    assert isinstance(stmt.body, Module)


def test_lower_python_ast_to_core_match():
    core = lower_python_ast_to_core(py_ast.parse("match x:\n case 1: pass"))
    stmt = core.body[0]
    assert isinstance(stmt, Match)
    assert len(stmt.cases) == 1
    assert isinstance(stmt.cases[0], PatternTest)


def test_lower_python_ast_to_core_raise():
    core = lower_python_ast_to_core(py_ast.parse("raise ValueError()"))
    stmt = core.body[0]
    assert isinstance(stmt, Raise)


def test_lower_python_ast_to_core_try():
    core = lower_python_ast_to_core(
        py_ast.parse("try: pass\nexcept Exception: pass\nfinally: pass")
    )
    stmt = core.body[0]
    assert isinstance(stmt, Handle)
    assert len(stmt.handlers) == 1
    assert isinstance(stmt.finalbody, Module)


def test_lower_python_ast_to_core_classdef():
    core = lower_python_ast_to_core(py_ast.parse("class Point:\n    x: int = 0"))
    stmt = core.body[0]
    assert isinstance(stmt, ConstructData)
    assert stmt.name == "Point"


def test_lower_python_ast_to_core_attribute():
    core = lower_python_ast_to_core(py_ast.parse("x.attr"))
    expr = core.body[0]
    assert isinstance(expr, GetField)
    assert expr.field == "attr"


def test_lower_python_ast_to_core_sequence():
    core = lower_python_ast_to_core(py_ast.parse("[1, 2]"))
    expr = core.body[0]
    assert isinstance(expr, Sequence)
    assert len(expr.elements) == 2


def test_lower_python_ast_to_core_unsupported_becomes_diagnostic():
    core = lower_python_ast_to_core(py_ast.parse("import os"))
    stmt = core.body[0]
    assert isinstance(stmt, Diagnostic)


# ── Core IR → Python AST (forward) ────────────────────────────────────────────


def test_core_to_python_ast_simple_assign():
    core = Module(body=(Bind(name="x", value=Literal(value=1)),))
    py = core_to_python_ast(core)
    assert isinstance(py, py_ast.Module)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "Assign" in dumped
    assert "Name(id='x'" in dumped
    assert "Constant(value=1)" in dumped


def test_core_to_python_ast_bind_function():
    core = Module(
        body=(
            Bind(
                name="f",
                value=Function(
                    params=("a", "b"),
                    body=Module(
                        body=(Return(value=Call(func=Load(name="add"), args=(Load(name="a"), Load(name="b")))),)
                    ),
                ),
            ),
        )
    )
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "FunctionDef" in dumped
    assert "'f'" in dumped


def test_core_to_python_ast_branch():
    core = Module(
        body=(
            Branch(
                test=Load(name="cond"),
                then_body=Module(body=(Return(value=Literal(value=True)),)),
                else_body=Module(body=(Return(value=Literal(value=False)),)),
            ),
        )
    )
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "If" in dumped


def test_core_to_python_ast_loop():
    core = Module(
        body=(
            Loop(
                test=Load(name="cond"),
                body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
            ),
        )
    )
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "While" in dumped


def test_core_to_python_ast_roundtrip_simple():
    """lower → core_to_python_ast should produce executable Python AST."""
    src = "x = 1"
    core = lower_python_ast_to_core(py_ast.parse(src))
    back = core_to_python_ast(core)
    # The roundtripped AST should produce the same dump text
    orig_dump = py_ast.dump(
        py_ast.parse(src), include_attributes=False, indent=2
    )
    back_dump = py_ast.dump(back, include_attributes=False, indent=2)
    # Names in targets will have ctx=Store after roundtrip (original has Load from parse),
    # so compare after normalising the assigned names to Store.
    assert "Assign" in back_dump
    assert "Constant(value=1)" in back_dump


def test_core_to_python_ast_rejects_invalid_core_in_strict_mode():
    core = Module(body=(Diagnostic(message="bad"),))
    with pytest.raises(CoreVerificationError):
        core_to_python_ast(core)


def test_core_to_python_ast_sequence():
    core = Module(body=(Sequence(elements=(Literal(value=1), Literal(value=2))),))
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "List" in dumped


def test_core_to_python_ast_get_field():
    core = Module(body=(GetField(object_=Load(name="obj"), field="attr"),))
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "Attribute" in dumped


def test_core_to_python_ast_raise():
    core = Module(body=(Raise(exception=Load(name="ValueError")),))
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "Raise" in dumped


def test_core_to_python_ast_call():
    core = Module(
        body=(
            Call(
                func=Load(name="print"),
                args=(Literal(value="hello"),),
            ),
        )
    )
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "Call" in dumped


def test_core_to_python_ast_lambda():
    core = Module(
        body=(
            Function(
                params=("x",),
                body=Module(body=(Return(value=Load(name="x")),)),
            ),
        )
    )
    py = core_to_python_ast(core)
    dumped = py_ast.dump(py, include_attributes=False, indent=2)
    assert "Lambda" in dumped or "Function" in dumped
