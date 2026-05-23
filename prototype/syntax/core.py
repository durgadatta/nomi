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


@dataclass(frozen=True, slots=True)
class Loop(CoreNode):
    test: CoreNode | None = None
    body: Module | None = None
    else_body: Module | None = None


@dataclass(frozen=True, slots=True)
class Match(CoreNode):
    subject: CoreNode | None = None
    cases: tuple[CoreNode, ...] = ()


@dataclass(frozen=True, slots=True)
class PatternTest(CoreNode):
    pattern: CoreNode | None = None
    guard: CoreNode | None = None
    body: Module | None = None


@dataclass(frozen=True, slots=True)
class ConstructData(CoreNode):
    name: str = ""
    fields: tuple[tuple[str, CoreNode], ...] = ()


@dataclass(frozen=True, slots=True)
class GetField(CoreNode):
    object_: CoreNode | None = None
    field: str = ""


@dataclass(frozen=True, slots=True)
class Raise(CoreNode):
    exception: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class Handle(CoreNode):
    body: Module | None = None
    handlers: tuple[CoreNode, ...] = ()
    finalbody: Module | None = None


@dataclass(frozen=True, slots=True)
class Sequence(CoreNode):
    elements: tuple[CoreNode, ...] = ()


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
    Loop,
    Match,
    PatternTest,
    ConstructData,
    GetField,
    Raise,
    Handle,
    Sequence,
)


def verify_core(node: CoreNode, *, strict: bool = False) -> None:
    """Reject anything that is not passive Core IR.

    When *strict* is True, also reject ``Diagnostic`` nodes, ensuring the
    tree contains only executable Core IR with no unsupported fallback nodes.
    """

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
        if strict and isinstance(core_node, Diagnostic):
            raise CoreVerificationError(
                f"{path} is a Diagnostic node: {core_node.message!r}"
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
        if isinstance(value, Loop):
            lines = [f"{prefix}Loop"]
            for child in (value.test, value.body, value.else_body):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, Match):
            lines = [f"{prefix}Match"]
            if value.subject is not None:
                lines.extend(_dump(value.subject, indent + 1))
            for case in value.cases:
                lines.extend(_dump(case, indent + 1))
            return lines
        if isinstance(value, PatternTest):
            lines = [f"{prefix}PatternTest"]
            for child in (value.pattern, value.guard, value.body):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, ConstructData):
            lines = [f"{prefix}ConstructData({value.name!r})"]
            for fname, fval in value.fields:
                lines.append(f"{prefix}  field({fname!r})")
                lines.extend(_dump(fval, indent + 2))
            return lines
        if isinstance(value, GetField):
            lines = [f"{prefix}GetField({value.field!r})"]
            if value.object_ is not None:
                lines.extend(_dump(value.object_, indent + 1))
            return lines
        if isinstance(value, Raise):
            lines = [f"{prefix}Raise"]
            if value.exception is not None:
                lines.extend(_dump(value.exception, indent + 1))
            return lines
        if isinstance(value, Handle):
            lines = [f"{prefix}Handle"]
            if value.body is not None:
                lines.extend(_dump(value.body, indent + 1))
            for handler in value.handlers:
                lines.extend(_dump(handler, indent + 1))
            if value.finalbody is not None:
                lines.extend(_dump(value.finalbody, indent + 1))
            return lines
        if isinstance(value, Sequence):
            lines = [f"{prefix}Sequence"]
            for elem in value.elements:
                lines.extend(_dump(elem, indent + 1))
            return lines
        raise CoreVerificationError(f"Cannot dump {type(value).__name__}")

    return "\n".join(_dump(node, 0))


# ── Core IR → Python AST (forward lowering) ───────────────────────────────────


def core_to_python_ast(node: CoreNode) -> ast.AST:
    """Convert verified Core IR to an executable Python ``ast.AST``.

    This is the adapter that lets the Python AST backend consume Core IR
    without any changes to the existing interpreter.  The round-trip is
    deliberately explicit so future backends can target Core IR directly.
    """
    verify_core(node, strict=True)
    return _core_to_ast(node)


def _core_to_ast(node: CoreNode) -> ast.AST:
    if isinstance(node, Module):
        return ast.Module(
            body=[_core_stmt(s) for s in node.body], type_ignores=[]
        )
    raise CoreVerificationError(
        f"Cannot lower {type(node).__name__} to Python AST: not a statement"
    )


def _core_stmt(node: CoreNode) -> ast.stmt:
    a = _core_stmt_dispatch(type(node))
    if a is not None:
        return a(node)
    e = _core_expr_dispatch(type(node))
    if e is not None:
        return ast.Expr(value=e(node))
    raise CoreVerificationError(
        f"_core_stmt: unsupported CoreNode {type(node).__name__}"
    )


def _core_expr(node: CoreNode | None) -> ast.expr | None:
    if node is None:
        return None
    a = _core_expr_dispatch(type(node))
    if a is not None:
        return a(node)
    raise CoreVerificationError(
        f"_core_expr: unsupported CoreNode {type(node).__name__}"
    )


def _core_exprs(nodes: tuple[CoreNode, ...]) -> list[ast.expr]:
    return [_core_expr(n) for n in nodes]


def _core_body(module: Module | None) -> list[ast.stmt]:
    if module is None or not module.body:
        return [ast.Pass()]
    return [_core_stmt(s) for s in module.body]


# ── statement lowering dispatchers ────────────────────────────────────────────

_STMT_DISPATCH: dict[type, object] = {}
_EXPR_DISPATCH: dict[type, object] = {}


def _stmt_handler(*types_: type):
    def dec(fn):
        for t in types_:
            _STMT_DISPATCH[t] = fn
        return fn

    return dec


def _expr_handler(*types_: type):
    def dec(fn):
        for t in types_:
            _EXPR_DISPATCH[t] = fn
        return fn

    return dec


def _core_stmt_dispatch(core_type: type):
    return _STMT_DISPATCH.get(core_type)


def _core_expr_dispatch(core_type: type):
    return _EXPR_DISPATCH.get(core_type)


# ── statement lowering handlers ───────────────────────────────────────────────


@_stmt_handler(Bind)
def _lower_bind(node: Bind) -> ast.stmt:
    if node.value is not None and isinstance(node.value, Function):
        fn = node.value
        return ast.FunctionDef(
            name=node.name,
            args=ast.arguments(
                args=[ast.arg(arg=p) for p in fn.params],
                posonlyargs=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=_core_body(fn.body),
        )
    return ast.Assign(
        targets=[ast.Name(id=node.name, ctx=ast.Store())],
        value=_core_expr(node.value) if node.value is not None else ast.Constant(
            value=None
        ),
    )


@_stmt_handler(Return)
def _lower_return(node: Return) -> ast.stmt:
    return ast.Return(value=_core_expr(node.value))


@_stmt_handler(Branch)
def _lower_branch(node: Branch) -> ast.stmt:
    return ast.If(
        test=_core_expr(node.test) if node.test is not None else ast.Constant(value=True),
        body=_core_body(node.then_body),
        orelse=_core_body(node.else_body) if node.else_body else [],
    )


@_stmt_handler(Loop)
def _lower_loop(node: Loop) -> ast.stmt:
    return ast.While(
        test=_core_expr(node.test) if node.test is not None else ast.Constant(value=True),
        body=_core_body(node.body),
        orelse=_core_body(node.else_body) if node.else_body else [],
    )


@_stmt_handler(Match)
def _lower_match(node: Match) -> ast.stmt:
    cases: list[ast.match_case] = []
    for c in node.cases:
        if isinstance(c, PatternTest):
            pat = _core_expr(c.pattern) if c.pattern is not None else ast.MatchAs()
            guard = _core_expr(c.guard)
            cases.append(
                ast.match_case(
                    pattern=pat, guard=guard, body=_core_body(c.body)
                )
            )
        else:
            cases.append(
                ast.match_case(
                    pattern=ast.MatchAs(),
                    guard=None,
                    body=[
                        ast.Expr(value=ast.Constant(value=f"unmatched case: {type(c).__name__}"))
                    ],
                )
            )
    return ast.Match(
        subject=_core_expr(node.subject) if node.subject is not None else ast.Name(id="_"),
        cases=cases,
    )


@_stmt_handler(Raise)
def _lower_raise(node: Raise) -> ast.stmt:
    return ast.Raise(exc=_core_expr(node.exception))


@_stmt_handler(Handle)
def _lower_handle(node: Handle) -> ast.stmt:
    handlers: list[ast.ExceptHandler] = []
    for h in node.handlers:
        exc_type: ast.expr | None = None
        exc_name: str | None = None
        if isinstance(h, Bind):
            exc_name = h.name
            exc_type = _core_expr(h.value)
        else:
            exc_type = _core_expr(h) if h is not None else None
        handlers.append(
            ast.ExceptHandler(
                type=exc_type,
                name=exc_name,
                body=[ast.Pass()] if not isinstance(h, PatternTest) else _core_body(
                    Module(body=tuple())
                ),
            )
        )
    return ast.Try(
        body=_core_body(node.body),
        handlers=handlers,
        orelse=[],
        finalbody=_core_body(node.finalbody) if node.finalbody else [],
    )


@_stmt_handler(ConstructData)
def _lower_construct_data(node: ConstructData) -> ast.stmt:
    field_assigns: list[ast.stmt] = []
    ann_assign = ast.AnnAssign(
        target=ast.Name(id=node.name),
        annotation=ast.Name(id="type"),
        value=ast.Constant(value=None),
        simple=1,
    )
    field_assigns.append(ann_assign)
    return ast.ClassDef(
        name=node.name,
        bases=[],
        keywords=[],
        body=[ann_assign] if not field_assigns else field_assigns,
        decorator_list=[],
    )


# ── expression lowering handlers ──────────────────────────────────────────────


@_expr_handler(Literal)
def _lower_literal(node: Literal) -> ast.expr:
    return ast.Constant(value=node.value)


@_expr_handler(Load)
def _lower_load(node: Load) -> ast.expr:
    return ast.Name(id=node.name, ctx=ast.Load())


@_expr_handler(Call)
def _lower_call(node: Call) -> ast.expr:
    return ast.Call(
        func=_core_expr(node.func) if node.func is not None else ast.Name(id="<unknown>"),
        args=_core_exprs(node.args),
        keywords=[],
    )


@_expr_handler(Function)
def _lower_function(node: Function) -> ast.expr:
    if node.body and node.body.body:
        inner = node.body.body[0]
        if isinstance(inner, Return):
            body_expr = _core_expr(inner.value)
        else:
            body_expr = _core_expr(inner) if isinstance(inner, CoreNode) else ast.Constant(value=None)
    else:
        body_expr = ast.Constant(value=None)
    return ast.Lambda(
        args=ast.arguments(
            args=[ast.arg(arg=p) for p in node.params],
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=body_expr,
    )


@_expr_handler(GetField)
def _lower_get_field(node: GetField) -> ast.expr:
    return ast.Attribute(
        value=_core_expr(node.object_) if node.object_ is not None else ast.Name(id="_"),
        attr=node.field,
    )


@_expr_handler(Sequence)
def _lower_sequence(node: Sequence) -> ast.expr:
    return ast.List(elts=_core_exprs(node.elements))


@_expr_handler(Loop)
def _lower_loop_expr(node: Loop) -> ast.expr:
    return ast.ListComp(
        elt=_core_expr(Literal(value=None)),
        generators=[
            ast.comprehension(
                target=ast.Name(id="_"),
                iter=_core_expr(node.test) if node.test is not None else ast.Name(id="_"),
                ifs=[],
                is_async=0,
            )
        ],
    )


# ── Python AST → Core IR (backward projection) ────────────────────────────────


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
    if isinstance(node, ast.While):
        return Loop(
            test=_lower_expr(node.test),
            body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
            else_body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.orelse)),
        )
    if isinstance(node, ast.For):
        return Loop(
            test=_lower_expr(node.iter),
            body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
            else_body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.orelse)),
        )
    if isinstance(node, ast.Match):
        cases: list[CoreNode] = []
        for case in node.cases:
            cases.append(
                PatternTest(
                    pattern=_lower_expr(case.pattern),
                    guard=_lower_expr(case.guard),
                    body=Module(body=tuple(_lower_stmt(stmt) for stmt in case.body)),
                )
            )
        return Match(
            subject=_lower_expr(node.subject),
            cases=tuple(cases),
        )
    if isinstance(node, ast.Raise):
        return Raise(exception=_lower_expr(node.exc))
    if isinstance(node, ast.Try):
        handlers: list[CoreNode] = []
        for handler in node.handlers:
            h = PatternTest(
                pattern=_lower_expr(handler.type),
                guard=None,
                body=Module(body=tuple(_lower_stmt(stmt) for stmt in handler.body)),
            )
            handlers.append(h)
        return Handle(
            body=Module(body=tuple(_lower_stmt(stmt) for stmt in node.body)),
            handlers=tuple(handlers),
            finalbody=Module(body=tuple(_lower_stmt(stmt) for stmt in node.finalbody)),
        )
    if isinstance(node, ast.ClassDef):
        fields: list[tuple[str, CoreNode]] = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.append((str(stmt.target.id), _lower_expr(stmt.value)))
        return ConstructData(name=str(node.name), fields=tuple(fields))
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
    if isinstance(node, ast.Attribute):
        return GetField(
            object_=_lower_expr(node.value),
            field=str(node.attr),
        )
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return Sequence(
            elements=tuple(_lower_expr(elt) for elt in node.elts),
        )
    return _unsupported(node)


def _unsupported(node: ast.AST) -> Diagnostic:
    return Diagnostic(message=f"unsupported Python AST: {type(node).__name__}")
