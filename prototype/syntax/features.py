"""Syntax feature manifest registry.

Each syntax feature declares its grammar, parse-tree transforms, desugar
passes, docs, and lifecycle status in one place.  The core registries
(grammar layer order, layer transforms, desugar pipeline) are derived from
this list, so adding a feature means adding one entry here plus the
implementation module — not editing 4 separate registries.

Feature order matters: it determines the order grammar layers are assembled
and desugar passes run.  Dependencies between passes (e.g. WhereClause
needs PiecewiseFunction to have already merged adjacent definitions) are
expressed through this order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from prototype.grammar.layer import LayerTransform
    from prototype.parser.nomi.desugar.base import BaseDesugarer


@dataclass(frozen=True)
class SyntaxFeature:
    """A named language capability with its implementation pieces.

    Each feature can contribute grammar fragments, parse-tree transforms,
    and/or AST-level desugar passes.  Every contribution is optional — a
    feature that only needs a desugar pass (like ``assert`` desugaring)
    does not need to declare grammar layers.
    """

    name: str
    description: str
    status: str = "implemented"
    grammar_layers: tuple[str, ...] = ()
    layer_transforms: tuple = ()
    desugar_passes: tuple = ()

    # Lifecycle statuses:
    #   implemented      — runs by default, tested
    #   prototype-ready  — runs behind a feature flag, tests present
    #   design-needed    — semantics not settled, parse-only or hidden
    #   research-only    — aspirational, may not parse yet
    #   rejected-for-now — kept for reference, not active


# ── expression-precedence ────────────────────────────────────────────
# Not a user-visible "feature" but a parse-tree transform that the
# ExpressionLayer applies.  Registered as a feature so the layer-transform
# registry can be derived from this list.

_expression_precedence = SyntaxFeature(
    name="expression-precedence",
    description="Reorganise flat bin_expr parse tree into correct precedence/associativity",
    layer_transforms=(
        # Lazy-imported in assemble.py to break circular dependency.
        "prototype.parser.nomi.desugar.parse_tree_precedence.ExpressionLayer",
    ),
)


# ── piecewise-functions ──────────────────────────────────────────────

_piecewise_functions = SyntaxFeature(
    name="piecewise-functions",
    description="Haskell-style f(p)=e piecewise function definitions via match dispatch",
    desugar_passes=("prototype.parser.nomi.desugar.piecewise.PiecewiseFunction",),
)


# ── where-clauses ────────────────────────────────────────────────────

_where_clauses = SyntaxFeature(
    name="where-clauses",
    description="Postfix where: blocks that bind local definitions after an expression",
    desugar_passes=("prototype.parser.nomi.desugar.where_clause.WhereClause",),
)


# ── underscore-lambdas ───────────────────────────────────────────────

_underscore_lambdas = SyntaxFeature(
    name="underscore-lambdas",
    description="Scala-style _.attr and _ + 1 anonymous function shorthand",
    desugar_passes=("prototype.parser.nomi.desugar.underscore_lambda.UnderscoreLambda",),
)


# ── positional-holes ─────────────────────────────────────────────────

_positional_holes = SyntaxFeature(
    name="positional-holes",
    description="$1, $name positional hole syntax for implicit lambda parameters",
    desugar_passes=("prototype.parser.nomi.desugar.positional_hole.PositionalHole",),
)


# ── aug-assign-desugar ───────────────────────────────────────────────

_augassign = SyntaxFeature(
    name="aug-assign-desugar",
    description="Desugar x += 1 into x = x + 1 in the AST",
    desugar_passes=("prototype.parser.nomi.desugar.augassign.AugAssign",),
)


# ── assert-desugar ───────────────────────────────────────────────────

_assert = SyntaxFeature(
    name="assert-desugar",
    description="Desugar assert cond into if not cond: raise AssertionError",
    desugar_passes=("prototype.parser.nomi.desugar.assert_.Assert",),
)


# ── decorator-desugar ────────────────────────────────────────────────

_decorator = SyntaxFeature(
    name="decorator-desugar",
    description="Desugar @d f() into f = d(f) after the function definition",
    desugar_passes=("prototype.parser.nomi.desugar.decorator.Decorator",),
)


# ── pass-desugar ─────────────────────────────────────────────────────

_pass = SyntaxFeature(
    name="pass-desugar",
    description="Desugar pass into Expr(Constant(0))",
    desugar_passes=("prototype.parser.nomi.desugar.pass_.Pass",),
)


# ── with-desugar ─────────────────────────────────────────────────────

_with = SyntaxFeature(
    name="with-desugar",
    description="Desugar with ctx as x: B into try/except/else",
    desugar_passes=("prototype.parser.nomi.desugar.with_.With",),
)


# ── fstring-desugar ──────────────────────────────────────────────────

_fstring = SyntaxFeature(
    name="fstring-desugar",
    description="Desugar f'{x}' into string concatenation and format() calls",
    desugar_passes=("prototype.parser.nomi.desugar.fstring.FString",),
)


# ── registry ─────────────────────────────────────────────────────────

BUILTIN_FEATURES: list[SyntaxFeature] = [
    _expression_precedence,
    _piecewise_functions,
    _where_clauses,
    _underscore_lambdas,
    _positional_holes,
    _augassign,
    _assert,
    _decorator,
    _pass,
    _with,
    _fstring,
]


def get_layer_transforms() -> list:
    """Return ordered LayerTransform instances derived from builtin features.

    Dotted-string references are lazy-resolved and instantiated so the
    feature list does not force early imports.
    """
    from prototype.utils import resolve_dotted

    transforms = []
    for feature in BUILTIN_FEATURES:
        for ref in feature.layer_transforms:
            transform_cls = resolve_dotted(ref)
            transforms.append(transform_cls())
    return transforms


def get_desugar_passes() -> list[Type[BaseDesugarer]]:
    """Return ordered desugar-pass classes derived from builtin features.

    Classes (not instances) are returned because desugar_module
    instantiates them fresh for each module.
    """
    from prototype.utils import resolve_dotted

    passes = []
    for feature in BUILTIN_FEATURES:
        for ref in feature.desugar_passes:
            passes.append(resolve_dotted(ref))
    return passes
