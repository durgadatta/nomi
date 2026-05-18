"""Passive Nomi Core IR skeleton.

This module defines the first L1 implementation-core artifacts from
``docs/language/core_layer_separation_plan.md``.  Nothing in the runtime
depends on these nodes yet; they exist so inspection, verification, and future
direct evaluation can grow against Nomi-owned artifacts instead of Python AST.
"""

from __future__ import annotations

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
