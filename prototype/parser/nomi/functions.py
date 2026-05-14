"""Nomi-specific AST-lowering mixin.

Each syntax feature's Lark-Transformer methods live in a dedicated module
under ``prototype/parser/nomi/lowering/``.  This mixin composes them so
``NomiToPythonAST`` still sees a single flat namespace.
"""

from .lowering import (
    ImplicitMulMixin,
    TypeAliasMixin,
    IfLetMixin,
    TryExprMixin,
    MatchExprMixin,
    WhereClauseMixin,
    PositionalHoleMixin,
    ComposeMixin,
    DeferMixin,
    FuncEquationMixin,
    SectionMixin,
    FuncExprMixin,
    BlockCallMixin,
)


class FunctionsMixin(
    ImplicitMulMixin,
    TypeAliasMixin,
    IfLetMixin,
    TryExprMixin,
    MatchExprMixin,
    WhereClauseMixin,
    PositionalHoleMixin,
    ComposeMixin,
    DeferMixin,
    FuncEquationMixin,
    SectionMixin,
    FuncExprMixin,
    BlockCallMixin,
):
    """Composed mixin of all Nomi-specific AST-lowering methods."""
