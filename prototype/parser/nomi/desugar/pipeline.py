"""Pipeline that chains all active desugar passes in order."""

import ast

from .augassign import AugAssign
from .assert_ import Assert
from .decorator import Decorator
from .pass_ import Pass
from .with_ import With
from .fstring import FString


def desugar_module(tree: ast.Module) -> ast.Module:
    tree = AugAssign().visit(tree)
    tree = Assert().visit(tree)
    tree = Decorator().visit(tree)
    tree = Pass().visit(tree)
    tree = With().visit(tree)
    tree = FString().visit(tree)
    ast.fix_missing_locations(tree)
    return tree
