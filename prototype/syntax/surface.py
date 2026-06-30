"""Nomi Surface AST base classes.

Surface nodes preserve the shape of Nomi-specific syntax before it is
lowered to Python AST.  They carry source spans and a ``lower()`` method
that produces their Python AST equivalent, so the transition from surface
to backend is inspectable and reversible (for diagnostics).

TODO(NOMI-ARCH-019): Add a sibling Core IR layer and verifier so this module
does not need to encode every Nomi construct as a Python AST lowering method.

Adding a new Nomi construct:
1. Define a surface node subclass here (or in a feature-specific module).
2. Have the Lark transformer emit the surface node.
3. The ``lower_surface_to_python`` walker will call ``.lower()`` on it.

Next migration markers:
- ``MatchExpr`` should preserve subject plus cases before its current IIFE
  backend lowering. First producer:
  ``prototype/parser/nomi/lowering/match_expr.py``.
- ``BindingTarget`` should start as a passive representation shared by
  annotated assignment, parameter binding, and pattern captures before
  changing constraint semantics. Data fields are the first passive producer.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, List


# ── SourceSpan ────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class SourceSpan:
    """File, line, and column range for a source construct."""

    file: str = ""
    line: int = 0
    col: int = 0
    end_line: int = 0
    end_col: int = 0

    @classmethod
    def from_lark_meta(cls, meta, file: str = "") -> SourceSpan | None:
        """Build a SourceSpan from a Lark ``Meta`` object.

        Returns ``None`` when *meta* is empty (no position information).
        """
        if meta.empty:
            return None
        return cls(
            file=file,
            line=meta.line,
            col=meta.column,
            end_line=meta.end_line,
            end_col=meta.end_column,
        )


# ── captures_span decorator ───────────────────────────────────────────

def captures_span(method):
    """Decorator for Lark transformer methods that create SurfaceNodes.

    Uses Lark's ``visit_wrapper`` mechanism to receive the tree ``meta``
    so SourceSpan can be extracted and attached to any SurfaceNode result.
    Apply with ``@captures_span`` on the transformer method.
    """
    def wrapper(bound_method, _data, children, meta):
        result = bound_method(children)
        if isinstance(result, SurfaceNode) and meta is not None:
            span = SourceSpan.from_lark_meta(meta)
            if span is not None:
                result.span = span
        return result

    method.visit_wrapper = wrapper
    return method


# ── SurfaceNode ───────────────────────────────────────────────────────

def _is_stmt_or_surface(node) -> bool:
    """Return True if *node* is an ``ast.stmt`` or a ``SurfaceNode``.

    Used at AST assembly points so surface nodes pass through
    statement-list filters (suite bodies, module bodies, etc.)
    before ``lower_surface_to_python`` replaces them.
    """
    return isinstance(node, (ast.stmt, SurfaceNode))


class SurfaceNode:
    """Base class for Nomi-owned surface-syntax nodes.

    These are NOT Python AST nodes.  They live alongside AST nodes in
    the lowered tree and are replaced by ``lower_surface_to_python``
    before the interpreter runs.

    The ``_is_stmt_or_surface`` helper and the updated assembly points
    in the parser recognise surface nodes as valid statement-like
    entries so they are not silently dropped during AST construction.
    """

    span: SourceSpan | None = None

    def lower(self) -> ast.AST:
        """Return the Python AST equivalent of this surface node."""
        raise NotImplementedError(
            f"{type(self).__name__}.lower() is not implemented"
        )


# ── BlockCall ─────────────────────────────────────────────────────────

@dataclass(slots=True)
class BlockCall(SurfaceNode):
    """A function call with a caller-side block body.

    ``f(x) do |y|: body end``  or  ``f(x): body``

    Stores the call target, positional args, keyword args, block
    parameters, and block body as structured data before lowering to
    Python AST.
    """

    func: ast.expr
    args: List[ast.expr] = field(default_factory=list)
    keywords: List[ast.keyword] = field(default_factory=list)
    block_params: ast.expr | None = None
    block_body: List[ast.stmt] = field(default_factory=list)

    def lower(self) -> ast.AST:
        """Lower to ``ast.Call`` with a ``__block__`` keyword holding the body.

        Nested ``BlockCall`` nodes in *block_body* are lowered first so the
        resulting ``Block`` contains only pure Python AST.
        """
        from prototype.interpreter.constants import BLOCK_KWARG, Block

        call = ast.Call(
            func=self.func,
            args=self.args,
            keywords=self.keywords,
        )

        # Lower any nested surface nodes in the block body
        lowered_body = []
        for stmt in self.block_body:
            if isinstance(stmt, SurfaceNode):
                lowered_body.append(lower_surface_to_python(stmt.lower()))
            elif isinstance(stmt, ast.AST):
                lowered_body.append(stmt)
            else:
                import sys
                print(
                    f"[surface] ERROR: non-AST object {type(stmt).__name__} in "
                    f"block body — this indicates an incomplete lowering step. "
                    f"object={stmt!r}",
                    file=sys.stderr,
                )
                raise TypeError(
                    f"BlockCall.lower: expected ast.AST or SurfaceNode in block_body, "
                    f"got {type(stmt).__name__}. This indicates a missing transformer "
                    f"method for a grammar rule used inside a block call body."
                )

        block = Block(body=lowered_body, params=self.block_params)
        call.keywords.append(ast.keyword(arg=BLOCK_KWARG, value=block))
        return ast.Expr(value=call)


# ── BindingTarget / DataDecl ─────────────────────────────────────────

def _unwrap_constraint_message(
    expression: ast.expr | None,
) -> tuple[ast.expr | None, str | None]:
    if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Name)
        and expression.func.id == "__constraint_message__"
        and len(expression.args) == 2
        and isinstance(expression.args[1], ast.Constant)
        and isinstance(expression.args[1].value, str)
    ):
        return expression.args[0], expression.args[1].value
    return expression, None


@dataclass(frozen=True, slots=True)
class Constraint:
    """Passive metadata for one binding constraint.

    Runtime predicates still own enforcement today.  This record preserves the
    user-facing constraint shape so assignments, parameters, data fields,
    patterns, and block params can converge on one metadata contract.
    """

    expression: ast.expr | None
    source: str | None = None
    kind: str = "expression"
    subject: str | None = None
    message: str | None = None
    span: SourceSpan | None = None
    redaction: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_expr(
        cls,
        expression: ast.expr | None,
        *,
        kind: str = "expression",
        subject: str | None = None,
        message: str | None = None,
        span: SourceSpan | None = None,
        redaction: dict[str, Any] | None = None,
    ) -> "Constraint":
        expression, marker_message = _unwrap_constraint_message(expression)
        if message is None:
            message = marker_message
        return cls(
            expression=expression,
            source=ast.unparse(expression) if expression is not None else None,
            kind=kind,
            subject=subject,
            message=message,
            span=span,
            redaction=redaction or {},
        )


@dataclass(init=False, slots=True)
class BindingTarget:
    """A passive description of a name-introduction site.

    This record is richer than the first data-field seed but remains passive:
    it does not enforce constraints.  The current interpreter stores it next to
    the existing predicate so future data, pattern, parameter, and block paths
    can share one checked-binding shape.
    """

    name: str
    role: str
    annotation: ast.expr | None = None
    constraints: tuple[Constraint, ...] = field(default_factory=tuple)
    default: ast.expr | None = None
    target_kind: str = "name"
    capture_names: tuple[str, ...] = field(default_factory=tuple)
    structural_requirement: Any | None = None
    redaction: dict[str, Any] = field(default_factory=dict)
    message: str | None = None
    span: SourceSpan | None = None

    def __init__(
        self,
        name: str,
        role: str,
        *,
        annotation: ast.expr | None = None,
        constraint: ast.expr | None = None,
        constraints: tuple[Constraint, ...] | None = None,
        default: ast.expr | None = None,
        target_kind: str = "name",
        capture_names: tuple[str, ...] = (),
        structural_requirement: Any | None = None,
        redaction: dict[str, Any] | None = None,
        message: str | None = None,
        span: SourceSpan | None = None,
    ) -> None:
        if constraints is None:
            constraints = ()
        if constraint is not None:
            constraints = (
                *constraints,
                Constraint.from_expr(
                    constraint,
                    subject=name,
                    message=message,
                    span=span,
                    redaction=redaction,
                ),
            )
        self.name = name
        self.role = role
        self.annotation = annotation
        self.constraints = tuple(constraints)
        self.default = default
        self.target_kind = target_kind
        self.capture_names = tuple(capture_names)
        self.structural_requirement = structural_requirement
        self.redaction = redaction or {}
        self.message = message
        self.span = span

    @property
    def constraint(self) -> ast.expr | None:
        """Return the first constraint expression for legacy data-field users."""
        if not self.constraints:
            return None
        return self.constraints[0].expression


@dataclass(slots=True)
class DataField:
    """A field in a ``data`` declaration backed by a binding target."""

    target: BindingTarget

    @property
    def name(self) -> str:
        return self.target.name

    @property
    def annotation(self) -> ast.expr | None:
        return self.target.annotation

    @property
    def constraint(self) -> ast.expr | None:
        return self.target.constraint

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return self.target.constraints


@dataclass(slots=True)
class DataDecl(SurfaceNode):
    """A Nomi ``data`` declaration before backend class generation."""

    name: str
    fields: List[DataField] = field(default_factory=list)

    def lower(self) -> ast.AST:
        body = [self._make_init()]
        if self.fields:
            body.append(self._make_repr())
            body.append(self._make_eq())

        return ast.ClassDef(
            name=self.name,
            bases=[],
            keywords=[],
            body=body,
            decorator_list=[],
        )

    def _make_init(self):
        args = [ast.arg(arg="self")]
        body = []
        checks = []

        for field in self.fields:
            args.append(ast.arg(arg=field.name, annotation=field.annotation))
            body.append(
                ast.Assign(
                    targets=[
                        ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()),
                            attr=field.name,
                            ctx=ast.Store(),
                        )
                    ],
                    value=ast.Name(id=field.name, ctx=ast.Load()),
                )
            )
            if field.constraint is not None:
                checks.append(field)

        for field in checks:
            constraint_src = ast.unparse(field.constraint)
            body.append(
                ast.If(
                    test=ast.UnaryOp(op=ast.Not(), operand=field.constraint),
                    body=[
                        ast.Raise(
                            exc=ast.Call(
                                func=ast.Name(id="TypeError", ctx=ast.Load()),
                                args=[
                                    ast.Constant(
                                        value=(
                                            f"Constraint violation for field {field.name!r}"
                                            f" of {self.name!r}: {constraint_src}"
                                        )
                                    )
                                ],
                                keywords=[],
                            ),
                            cause=None,
                        )
                    ],
                    orelse=[],
                )
            )

        return ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=body,
            decorator_list=[],
            returns=None,
        )

    def _make_repr(self):
        field_names = [field.name for field in self.fields]
        parts = [f"{name}={{0.{name}!r}}" for name in field_names]
        fmt = f"{self.name}({', '.join(parts)})"

        return ast.FunctionDef(
            name="__repr__",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                ast.Return(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value=fmt),
                            attr="format",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Name(id="self", ctx=ast.Load())],
                        keywords=[],
                    )
                )
            ],
            decorator_list=[],
            returns=None,
        )

    def _make_eq(self):
        comparisons = []
        for field in self.fields:
            comparisons.append(
                ast.Compare(
                    left=ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr=field.name,
                        ctx=ast.Load(),
                    ),
                    ops=[ast.Eq()],
                    comparators=[
                        ast.Attribute(
                            value=ast.Name(id="other", ctx=ast.Load()),
                            attr=field.name,
                            ctx=ast.Load(),
                        )
                    ],
                )
            )

        if len(comparisons) == 1:
            combined = comparisons[0]
        else:
            combined = ast.BoolOp(op=ast.And(), values=comparisons)

        return ast.FunctionDef(
            name="__eq__",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self"), ast.arg(arg="other")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                ast.If(
                    test=ast.Call(
                        func=ast.Name(id="isinstance", ctx=ast.Load()),
                        args=[
                            ast.Name(id="other", ctx=ast.Load()),
                            ast.Name(id=self.name, ctx=ast.Load()),
                        ],
                        keywords=[],
                    ),
                    body=[ast.Return(value=combined)],
                    orelse=[ast.Return(value=ast.Constant(value=NotImplemented))],
                )
            ],
            decorator_list=[],
            returns=None,
        )


# ── surface → Python lowering walker ──────────────────────────────────

def lower_surface_to_python(root: ast.AST) -> ast.AST:
    """Walk *root* and replace any ``SurfaceNode`` with its ``.lower()`` result.

    Surface nodes can appear as ``ast.Expr.value``, ``ast.keyword.value``,
    or any other AST field that holds an expression or statement.  This
    walker descends into all AST fields, collects AST children, and
    replaces non-AST ``SurfaceNode`` objects.

    Returns the root (modified in place).
    """

    def _walk(node):
        """Recursively walk *node* and its children, lowering surface nodes."""
        if isinstance(node, SurfaceNode):
            return _walk(node.lower())
        if not isinstance(node, ast.AST):
            # Defensive: non-AST objects (e.g. lark.Tree) should not be
            # present in a lowered Python AST.  Log and return unchanged
            # so the rest of the pipeline can still report the error.
            if hasattr(node, 'data') and hasattr(node, 'children'):
                import sys
                print(
                    f"[surface] WARNING: lark.Tree '{(node.data)}' found in"
                    f" Python AST — this indicates an incomplete lowering step.",
                    file=sys.stderr,
                )
            # Descend into non-AST containers (Block, etc.) to catch
            # Trees hiding inside their fields.
            _walk_non_ast(node)
            return node

        for field_name, value in ast.iter_fields(node):
            if isinstance(value, SurfaceNode):
                setattr(node, field_name, _walk(value))
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    replaced = _walk(item)
                    new_list.append(replaced)
                setattr(node, field_name, new_list)
            elif isinstance(value, ast.AST):
                _walk(value)
            elif value is not None and hasattr(value, '__slots__'):
                _walk_non_ast(value)
        return node

    def _walk_non_ast(obj):
        """Descend into non-AST objects (dataclasses, Block) to find Trees."""
        slots = getattr(obj, '__slots__', None)
        if slots is None:
            return
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            if not hasattr(obj, slot):
                continue
            value = getattr(obj, slot)
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, (ast.AST, SurfaceNode)):
                        _walk(item)
                    elif type(item).__name__ == 'Tree' and hasattr(item, 'data'):
                        import sys
                        print(
                            f"[surface] WARNING: lark.Tree '{item.data}' found in"
                            f" non-AST object {type(obj).__name__}.{slot}[{i}]",
                            file=sys.stderr,
                        )
            elif isinstance(value, (ast.AST, SurfaceNode)):
                _walk(value)
            elif type(value).__name__ == 'Tree' and hasattr(value, 'data'):
                import sys
                print(
                    f"[surface] WARNING: lark.Tree '{value.data}' found in"
                    f" non-AST object {type(obj).__name__}.{slot}",
                    file=sys.stderr,
                )

    return _walk(root)
