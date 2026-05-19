"""Passive Nomi Core IR skeleton.

This module defines the first L1 implementation-core artifacts from
``docs/language/core_layer_separation_plan.md``.  Nothing in the runtime
depends on these nodes yet; they exist so inspection, verification, and future
direct evaluation can grow against Nomi-owned artifacts instead of Python AST.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from prototype.syntax.surface import SourceSpan, SurfaceNode


class CoreVerificationError(TypeError):
    """Raised when an object is not valid passive Core IR."""


@dataclass(frozen=True, slots=True)
class CoreNode:
    span: SourceSpan | None = None


@dataclass(frozen=True, slots=True)
class Module(CoreNode):
    body: tuple[CoreNode, ...] = ()


@dataclass(frozen=True, slots=True)
class Literal(CoreNode):
    value: Any = None


@dataclass(frozen=True, slots=True)
class Load(CoreNode):
    name: str = ""


@dataclass(frozen=True, slots=True)
class Bind(CoreNode):
    name: str = ""
    value: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class Function(CoreNode):
    params: tuple[str, ...] = ()
    body: Module | None = None


@dataclass(frozen=True, slots=True)
class Call(CoreNode):
    func: CoreNode | None = None
    args: tuple[CoreNode, ...] = ()


@dataclass(frozen=True, slots=True)
class Return(CoreNode):
    value: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class Branch(CoreNode):
    test: CoreNode | None = None
    then_body: Module | None = None
    else_body: Module | None = None


@dataclass(frozen=True, slots=True)
class Diagnostic(CoreNode):
    message: str = ""


CORE_NODE_TYPES = (
    Module,
    Literal,
    Load,
    Bind,
    Function,
    Call,
    Return,
    Branch,
    Diagnostic,
)


def verify_core(node: CoreNode) -> None:
    """Reject anything that is not passive Core IR."""

    def _verify(value, path: str) -> None:
        if value is None:
            return
        if isinstance(value, SurfaceNode):
            raise CoreVerificationError(
                f"{path} contains surface node {type(value).__name__}; "
                "lower surface syntax before Core IR verification"
            )
        if isinstance(value, CoreNode):
            if not isinstance(value, CORE_NODE_TYPES):
                raise CoreVerificationError(
                    f"{path} contains unknown CoreNode {type(value).__name__}"
                )
            _verify_node(value, path)
            return
        if isinstance(value, tuple):
            for index, item in enumerate(value):
                _verify(item, f"{path}[{index}]")
            return
        if isinstance(value, (str, int, float, bool)):
            return
        raise CoreVerificationError(
            f"{path} contains non-core value {type(value).__name__}"
        )

    def _verify_node(core_node: CoreNode, path: str) -> None:
        if not is_dataclass(core_node):
            raise CoreVerificationError(
                f"{path} is not a dataclass-backed CoreNode"
            )
        for field in fields(core_node):
            if field.name == "span":
                continue
            field_value = getattr(core_node, field.name)
            if isinstance(core_node, Literal) and field.name == "value":
                continue
            _verify(field_value, f"{path}.{field.name}")

    _verify(node, "$")


def dump_core(node: CoreNode) -> str:
    """Return a compact multi-line debug dump for passive Core IR."""
    verify_core(node)

    def _dump(value, indent: int) -> list[str]:
        prefix = "  " * indent
        if isinstance(value, Module):
            lines = [f"{prefix}Module"]
            for stmt in value.body:
                lines.extend(_dump(stmt, indent + 1))
            return lines
        if isinstance(value, Literal):
            return [f"{prefix}Literal({value.value!r})"]
        if isinstance(value, Load):
            return [f"{prefix}Load({value.name!r})"]
        if isinstance(value, Bind):
            lines = [f"{prefix}Bind({value.name!r})"]
            if value.value is not None:
                lines.extend(_dump(value.value, indent + 1))
            return lines
        if isinstance(value, Function):
            lines = [f"{prefix}Function(params={value.params!r})"]
            if value.body is not None:
                lines.extend(_dump(value.body, indent + 1))
            return lines
        if isinstance(value, Call):
            lines = [f"{prefix}Call"]
            if value.func is not None:
                lines.extend(_dump(value.func, indent + 1))
            for arg in value.args:
                lines.extend(_dump(arg, indent + 1))
            return lines
        if isinstance(value, Return):
            lines = [f"{prefix}Return"]
            if value.value is not None:
                lines.extend(_dump(value.value, indent + 1))
            return lines
        if isinstance(value, Branch):
            lines = [f"{prefix}Branch"]
            for child in (value.test, value.then_body, value.else_body):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, Diagnostic):
            return [f"{prefix}Diagnostic({value.message!r})"]
        raise CoreVerificationError(f"Cannot dump {type(value).__name__}")

    return "\n".join(_dump(node, 0))


def lower_python_ast_to_core(node: ast.AST) -> CoreNode:
    """Best-effort Python AST backend artifact -> passive Core IR.

    This is intentionally tiny and inspection-only. Unsupported Python AST
    nodes become ``Diagnostic`` nodes instead of raising, so broad programs can
    still show where Core IR coverage stops.
    """
    # TODO(NOMI-ARCH-019): Replace this Python-AST-backward projection with a
    # real Surface -> Core lowering path before any runtime, diagnostic, or
    # backend work treats Core IR as authoritative.
    if isinstance(node, ast.Module):
        return Module(body=tuple(_lower_stmt(stmt) for stmt in node.body))
    return _unsupported(node)


def _lower_stmt(node: ast.AST) -> CoreNode:
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            return Bind(
                name=str(node.targets[0].id),
                value=_lower_expr(node.value),
            )
        return _unsupported(node)
    if isinstance(node, ast.Expr):
        return _lower_expr(node.value)
    if isinstance(node, ast.Return):
        return Return(value=_lower_expr(node.value))
    if isinstance(node, ast.If):
        return Branch(
            test=_lower_expr(node.test),
            then_body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
            else_body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.orelse)),
        )
    if isinstance(node, ast.FunctionDef):
        return Bind(
            name=str(node.name),
            value=Function(
                params=tuple(str(arg.arg) for arg in node.args.args),
                body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
            ),
        )
    return _unsupported(node)


def _lower_expr(node: ast.AST | None) -> CoreNode:
    if node is None:
        return Literal(value=None)
    if isinstance(node, ast.Constant):
        return Literal(value=node.value)
    if isinstance(node, ast.Name):
        return Load(name=str(node.id))
    if isinstance(node, ast.Call):
        return Call(
            func=_lower_expr(node.func),
            args=tuple(_lower_expr(arg) for arg in node.args),
        )
    if isinstance(node, ast.FunctionDef):
        return Function(
            params=tuple(str(arg.arg) for arg in node.args.args),
            body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
        )
    return _unsupported(node)


def _unsupported(node: ast.AST) -> Diagnostic:
    return Diagnostic(message=f"unsupported Python AST: {type(node).__name__}")
