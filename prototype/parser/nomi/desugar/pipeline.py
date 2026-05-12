"""Pipeline that chains all active desugar passes in order."""

import ast
from typing import List, Type

from .base import BaseDesugarer
from .underscore_lambda import UnderscoreLambda
from .augassign import AugAssign
from .assert_ import Assert
from .decorator import Decorator
from .pass_ import Pass
from .with_ import With
from .fstring import FString


DESUGAR_PASSES: List[Type[BaseDesugarer]] = [
    UnderscoreLambda,
    AugAssign,
    Assert,
    Decorator,
    Pass,
    With,
    FString,
]


def desugar_module(tree: ast.Module) -> ast.Module:
    for pass_cls in DESUGAR_PASSES:
        tree = pass_cls().visit(tree)
    ast.fix_missing_locations(tree)
    return tree


def get_removed_node_types():
    """Return the set of AST node types removed by the desugar pipeline.

    Used by the reduced interpreter to auto-derive its NotImplementedError
    overrides, keeping the two in sync when passes are added or removed.
    """
    removed = set()
    for pass_cls in DESUGAR_PASSES:
        removed.update(pass_cls.removed_node_types)
    return removed
