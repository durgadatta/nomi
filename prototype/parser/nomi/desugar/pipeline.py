"""Pipeline that chains all active desugar passes in order.

Passes are derived from the syntax feature registry
(prototype/syntax/features.py) so adding a desugar pass means adding
one entry to the feature list — not editing this file.
"""

import ast

from prototype.syntax.features import get_desugar_passes


# Derived from BUILTIN_FEATURES in prototype/syntax/features.py.
# Feature order there determines pass order here.
DESUGAR_PASSES = get_desugar_passes()


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
