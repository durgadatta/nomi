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
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import List, Optional


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
            else:
                lowered_body.append(stmt)

        block = Block(body=lowered_body, params=self.block_params)
        call.keywords.append(ast.keyword(arg=BLOCK_KWARG, value=block))
        return ast.Expr(value=call)


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
        return node

    return _walk(root)
