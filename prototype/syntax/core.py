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
class Yield(CoreNode):
    value: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class Branch(CoreNode):
    test: CoreNode | None = None
    then_body: Module | None = None
    else_body: Module | None = None


@dataclass(frozen=True, slots=True)
class NoOp(CoreNode):
    pass


@dataclass(frozen=True, slots=True)
class Break(CoreNode):
    pass


@dataclass(frozen=True, slots=True)
class Continue(CoreNode):
    pass


@dataclass(frozen=True, slots=True)
class UnaryOp(CoreNode):
    op: str = ""
    operand: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class BinaryOp(CoreNode):
    left: CoreNode | None = None
    op: str = ""
    right: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class BooleanOp(CoreNode):
    op: str = ""
    values: tuple[CoreNode, ...] = ()


@dataclass(frozen=True, slots=True)
class CompareOp(CoreNode):
    left: CoreNode | None = None
    ops: tuple[str, ...] = ()
    comparators: tuple[CoreNode, ...] = ()


@dataclass(frozen=True, slots=True)
class ConditionalExpr(CoreNode):
    test: CoreNode | None = None
    then_value: CoreNode | None = None
    else_value: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class MappingLiteral(CoreNode):
    entries: tuple[tuple[CoreNode, CoreNode], ...] = ()


@dataclass(frozen=True, slots=True)
class GetItem(CoreNode):
    object_: CoreNode | None = None
    key: CoreNode | None = None


@dataclass(frozen=True, slots=True)
class Spread(CoreNode):
    value: CoreNode | None = None


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
    Yield,
    Branch,
    NoOp,
    Break,
    Continue,
    UnaryOp,
    BinaryOp,
    BooleanOp,
    CompareOp,
    ConditionalExpr,
    MappingLiteral,
    GetItem,
    Spread,
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
        if isinstance(value, Yield):
            lines = [f"{prefix}Yield"]
            if value.value is not None:
                lines.extend(_dump(value.value, indent + 1))
            return lines
        if isinstance(value, Branch):
            lines = [f"{prefix}Branch"]
            for child in (value.test, value.then_body, value.else_body):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, NoOp):
            return [f"{prefix}NoOp"]
        if isinstance(value, Break):
            return [f"{prefix}Break"]
        if isinstance(value, Continue):
            return [f"{prefix}Continue"]
        if isinstance(value, UnaryOp):
            lines = [f"{prefix}UnaryOp({value.op!r})"]
            if value.operand is not None:
                lines.extend(_dump(value.operand, indent + 1))
            return lines
        if isinstance(value, BinaryOp):
            lines = [f"{prefix}BinaryOp({value.op!r})"]
            for child in (value.left, value.right):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, BooleanOp):
            lines = [f"{prefix}BooleanOp({value.op!r})"]
            for child in value.values:
                lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, CompareOp):
            lines = [f"{prefix}CompareOp({value.ops!r})"]
            if value.left is not None:
                lines.extend(_dump(value.left, indent + 1))
            for child in value.comparators:
                lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, ConditionalExpr):
            lines = [f"{prefix}ConditionalExpr"]
            for child in (value.test, value.then_value, value.else_value):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, MappingLiteral):
            lines = [f"{prefix}MappingLiteral"]
            for key, item_value in value.entries:
                lines.append(f"{prefix}  entry")
                lines.extend(_dump(key, indent + 2))
                lines.extend(_dump(item_value, indent + 2))
            return lines
        if isinstance(value, GetItem):
            lines = [f"{prefix}GetItem"]
            for child in (value.object_, value.key):
                if child is not None:
                    lines.extend(_dump(child, indent + 1))
            return lines
        if isinstance(value, Spread):
            lines = [f"{prefix}Spread"]
            if value.value is not None:
                lines.extend(_dump(value.value, indent + 1))
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


def _core_pattern(node: CoreNode | None) -> ast.pattern:
    if node is None:
        return ast.MatchAs()
    if isinstance(node, Literal):
        if node.value in (None, True, False):
            return ast.MatchSingleton(value=node.value)
        return ast.MatchValue(value=ast.Constant(value=node.value))
    if isinstance(node, Load):
        return ast.MatchAs(name=None if node.name == "_" else node.name)
    if isinstance(node, Sequence):
        return ast.MatchSequence(patterns=[_core_pattern(e) for e in node.elements])
    if isinstance(node, Spread):
        if isinstance(node.value, Load) and node.value.name != "_":
            return ast.MatchStar(name=node.value.name)
        return ast.MatchStar(name=None)
    if isinstance(node, MappingLiteral):
        return ast.MatchMapping(
            keys=[_core_expr(key) for key, _ in node.entries],
            patterns=[_core_pattern(value) for _, value in node.entries],
            rest=None,
        )
    return ast.MatchValue(value=_core_expr(node))


def _core_body(module: Module | None) -> list[ast.stmt]:
    if module is None or not module.body:
        return [ast.Pass()]
    return [_core_stmt(s) for s in module.body]


# ── statement lowering dispatchers ────────────────────────────────────────────

_STMT_DISPATCH: dict[type, object] = {}
_EXPR_DISPATCH: dict[type, object] = {}

_BIN_OP_TO_AST = {
    "+": ast.Add,
    "-": ast.Sub,
    "*": ast.Mult,
    "/": ast.Div,
    "//": ast.FloorDiv,
    "%": ast.Mod,
    "**": ast.Pow,
    "@": ast.MatMult,
    "<<": ast.LShift,
    ">>": ast.RShift,
    "|": ast.BitOr,
    "^": ast.BitXor,
    "&": ast.BitAnd,
}
_AST_TO_BIN_OP = {cls: token for token, cls in _BIN_OP_TO_AST.items()}

_UNARY_OP_TO_AST = {
    "+": ast.UAdd,
    "-": ast.USub,
    "~": ast.Invert,
    "not": ast.Not,
}
_AST_TO_UNARY_OP = {cls: token for token, cls in _UNARY_OP_TO_AST.items()}

_BOOL_OP_TO_AST = {
    "and": ast.And,
    "or": ast.Or,
}
_AST_TO_BOOL_OP = {cls: token for token, cls in _BOOL_OP_TO_AST.items()}

_CMP_OP_TO_AST = {
    "==": ast.Eq,
    "!=": ast.NotEq,
    "<": ast.Lt,
    "<=": ast.LtE,
    ">": ast.Gt,
    ">=": ast.GtE,
    "is": ast.Is,
    "is not": ast.IsNot,
    "in": ast.In,
    "not in": ast.NotIn,
}
_AST_TO_CMP_OP = {cls: token for token, cls in _CMP_OP_TO_AST.items()}


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


@_expr_handler(Yield)
def _lower_yield(node: Yield) -> ast.expr:
    return ast.Yield(value=_core_expr(node.value))


@_stmt_handler(Branch)
def _lower_branch(node: Branch) -> ast.stmt:
    return ast.If(
        test=_core_expr(node.test) if node.test is not None else ast.Constant(value=True),
        body=_core_body(node.then_body),
        orelse=_core_body(node.else_body) if node.else_body else [],
    )


@_stmt_handler(NoOp)
def _lower_no_op(node: NoOp) -> ast.stmt:
    return ast.Pass()


@_stmt_handler(Break)
def _lower_break(node: Break) -> ast.stmt:
    return ast.Break()


@_stmt_handler(Continue)
def _lower_continue(node: Continue) -> ast.stmt:
    return ast.Continue()


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
            pat = _core_pattern(c.pattern)
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
        body = [ast.Pass()]
        if isinstance(h, PatternTest):
            if h.pattern is not None and not (
                isinstance(h.pattern, Load) and h.pattern.name == "_"
            ):
                exc_type = _core_expr(h.pattern)
            body = _core_body(h.body)
        elif isinstance(h, Bind):
            exc_name = h.name
            exc_type = _core_expr(h.value)
        else:
            exc_type = _core_expr(h) if h is not None else None
        handlers.append(
            ast.ExceptHandler(
                type=exc_type,
                name=exc_name,
                body=body,
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
    return ast.FunctionDef(
        name=None,
        args=ast.arguments(
            args=[ast.arg(arg=p) for p in node.params],
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=_core_body(node.body),
    )


@_expr_handler(UnaryOp)
def _lower_unary_op(node: UnaryOp) -> ast.expr:
    try:
        op_type = _UNARY_OP_TO_AST[node.op]
    except KeyError as exc:
        raise CoreVerificationError(f"Unknown unary op {node.op!r}") from exc
    return ast.UnaryOp(
        op=op_type(),
        operand=(
            _core_expr(node.operand)
            if node.operand is not None
            else ast.Constant(value=None)
        ),
    )


@_expr_handler(BinaryOp)
def _lower_binary_op(node: BinaryOp) -> ast.expr:
    try:
        op_type = _BIN_OP_TO_AST[node.op]
    except KeyError as exc:
        raise CoreVerificationError(f"Unknown binary op {node.op!r}") from exc
    return ast.BinOp(
        left=(
            _core_expr(node.left)
            if node.left is not None
            else ast.Constant(value=None)
        ),
        op=op_type(),
        right=(
            _core_expr(node.right)
            if node.right is not None
            else ast.Constant(value=None)
        ),
    )


@_expr_handler(BooleanOp)
def _lower_boolean_op(node: BooleanOp) -> ast.expr:
    try:
        op_type = _BOOL_OP_TO_AST[node.op]
    except KeyError as exc:
        raise CoreVerificationError(f"Unknown boolean op {node.op!r}") from exc
    return ast.BoolOp(
        op=op_type(),
        values=_core_exprs(node.values),
    )


@_expr_handler(CompareOp)
def _lower_compare_op(node: CompareOp) -> ast.expr:
    try:
        ops = [_CMP_OP_TO_AST[op]() for op in node.ops]
    except KeyError as exc:
        raise CoreVerificationError(f"Unknown compare op {exc.args[0]!r}") from exc
    return ast.Compare(
        left=(
            _core_expr(node.left)
            if node.left is not None
            else ast.Constant(value=None)
        ),
        ops=ops,
        comparators=_core_exprs(node.comparators),
    )


@_expr_handler(ConditionalExpr)
def _lower_conditional_expr(node: ConditionalExpr) -> ast.expr:
    return ast.IfExp(
        test=(
            _core_expr(node.test)
            if node.test is not None
            else ast.Constant(value=False)
        ),
        body=(
            _core_expr(node.then_value)
            if node.then_value is not None
            else ast.Constant(value=None)
        ),
        orelse=(
            _core_expr(node.else_value)
            if node.else_value is not None
            else ast.Constant(value=None)
        ),
    )


@_expr_handler(MappingLiteral)
def _lower_mapping_literal(node: MappingLiteral) -> ast.expr:
    return ast.Dict(
        keys=[_core_expr(key) for key, _ in node.entries],
        values=[_core_expr(value) for _, value in node.entries],
    )


@_expr_handler(GetItem)
def _lower_get_item(node: GetItem) -> ast.expr:
    return ast.Subscript(
        value=(
            _core_expr(node.object_)
            if node.object_ is not None
            else ast.Name(id="_")
        ),
        slice=(
            _core_expr(node.key)
            if node.key is not None
            else ast.Constant(value=None)
        ),
        ctx=ast.Load(),
    )


@_expr_handler(Spread)
def _lower_spread(node: Spread) -> ast.expr:
    return ast.Starred(
        value=(
            _core_expr(node.value)
            if node.value is not None
            else ast.Constant(value=None)
        ),
        ctx=ast.Load(),
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
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            return Bind(
                name=str(node.target.id),
                value=_lower_expr(node.value),
            )
        return _unsupported(node)
    if isinstance(node, ast.Expr):
        return _lower_expr(node.value)
    if isinstance(node, ast.Return):
        return Return(value=_lower_expr(node.value))
    if isinstance(node, ast.Pass):
        return NoOp()
    if isinstance(node, ast.Break):
        return Break()
    if isinstance(node, ast.Continue):
        return Continue()
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
                    pattern=_lower_pattern(case.pattern),
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
    if isinstance(node, ast.Yield):
        return Yield(value=_lower_expr(node.value))
    if isinstance(node, ast.UnaryOp):
        return UnaryOp(
            op=_AST_TO_UNARY_OP.get(type(node.op), type(node.op).__name__),
            operand=_lower_expr(node.operand),
        )
    if isinstance(node, ast.BinOp):
        return BinaryOp(
            left=_lower_expr(node.left),
            op=_AST_TO_BIN_OP.get(type(node.op), type(node.op).__name__),
            right=_lower_expr(node.right),
        )
    if isinstance(node, ast.BoolOp):
        return BooleanOp(
            op=_AST_TO_BOOL_OP.get(type(node.op), type(node.op).__name__),
            values=tuple(_lower_expr(value) for value in node.values),
        )
    if isinstance(node, ast.Compare):
        return CompareOp(
            left=_lower_expr(node.left),
            ops=tuple(
                _AST_TO_CMP_OP.get(type(op), type(op).__name__)
                for op in node.ops
            ),
            comparators=tuple(_lower_expr(c) for c in node.comparators),
        )
    if isinstance(node, ast.IfExp):
        return ConditionalExpr(
            test=_lower_expr(node.test),
            then_value=_lower_expr(node.body),
            else_value=_lower_expr(node.orelse),
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
    if isinstance(node, ast.Subscript):
        return GetItem(
            object_=_lower_expr(node.value),
            key=_lower_expr(node.slice),
        )
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return Sequence(
            elements=tuple(_lower_expr(elt) for elt in node.elts),
        )
    if isinstance(node, ast.Dict):
        entries: list[tuple[CoreNode, CoreNode]] = []
        for key, value in zip(node.keys, node.values):
            entries.append((_lower_expr(key), _lower_expr(value)))
        return MappingLiteral(entries=tuple(entries))
    if isinstance(node, ast.Starred):
        return Spread(value=_lower_expr(node.value))
    return _unsupported(node)


def _lower_pattern(node: ast.AST | None) -> CoreNode:
    if node is None:
        return Load(name="_")
    if isinstance(node, ast.MatchValue):
        return _lower_expr(node.value)
    if isinstance(node, ast.MatchSingleton):
        return Literal(value=node.value)
    if isinstance(node, ast.MatchAs):
        return Load(name=node.name or "_")
    if isinstance(node, ast.MatchSequence):
        return Sequence(elements=tuple(_lower_pattern(p) for p in node.patterns))
    if isinstance(node, ast.MatchStar):
        return Spread(value=Load(name=node.name or "_"))
    if isinstance(node, ast.MatchMapping):
        entries: list[tuple[CoreNode, CoreNode]] = []
        for key, pattern in zip(node.keys, node.patterns):
            entries.append((_lower_expr(key), _lower_pattern(pattern)))
        return MappingLiteral(entries=tuple(entries))
    return _unsupported(node)


def _unsupported(node: ast.AST) -> Diagnostic:
    return Diagnostic(message=f"unsupported Python AST: {type(node).__name__}")
