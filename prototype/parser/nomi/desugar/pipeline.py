"""Pipeline that chains all active desugar passes in order.

Passes are derived from the syntax feature registry
(prototype/syntax/features.py) so adding a desugar pass means adding
one entry to the feature list — not editing this file.

Phases and dependencies are validated at import time: a pass in the
wrong phase or missing a declared dependency is a loud error, not a
silent ordering bug.
"""

import ast
import os
import sys

from prototype.syntax.features import get_desugar_passes
from .base import Phase

_SHOULD_CHECK_INVARIANTS = os.environ.get(
    'NOMI_DESUGAR_CHECK_INVARIANTS', ''
).lower() in ('1', 'true', 'yes')


# Derived from BUILTIN_FEATURES in prototype/syntax/features.py.
# Feature order there determines pass order here.
DESUGAR_PASSES = get_desugar_passes()

# The full pipeline is required by the reduced interpreter because it checks
# that Python-compatible surface nodes have become normal forms.  The default
# Nomi interpreter can already execute Python-parity nodes such as AugAssign,
# Assert, Pass, With, decorators, and f-strings, so it only needs the passes
# that lower Nomi-only convenience syntax.
NOMI_INTERPRETER_DESUGAR_PASSES = tuple(
    # TODO(NOMI-SUBSTRATE-033): Move default/reduced/lab pass inclusion into
    # SyntaxFeature metadata instead of filtering by pass class name.
    pass_cls for pass_cls in DESUGAR_PASSES
    if pass_cls.__name__ in {
        "PiecewiseFunction",
        "WhereClause",
        "UnderscoreLambda",
        "PositionalHole",
    }
)


def _validate_pipeline(passes):
    """Validate dependencies for *passes*.

    Every class in ``depends_on`` must appear earlier in the pass list.
    Phase annotations (syntax → semantic → cleanup) are advisory; the
    real constraint is that a pass's dependencies have already run.
    """
    seen = set()
    errors = []

    for pass_cls in passes:
        name = pass_cls.__name__
        for dep in getattr(pass_cls, 'depends_on', ()):
            if dep not in seen:
                errors.append(
                    f"Dependency violation: {name} depends on {dep.__name__} "
                    f"but {dep.__name__} has not run yet. "
                    f"Reorder passes so {dep.__name__} comes before {name}."
                )
        seen.add(pass_cls)

    if errors:
        for err in errors:
            print(f"DESUGAR PIPELINE: {err}", file=sys.stderr)
        raise ValueError(
            f"Desugar pipeline: {len(errors)} dependency violation(s). "
            f"Fix the pass order in BUILTIN_FEATURES."
        )

_validate_pipeline(DESUGAR_PASSES)


def _find_forbidden_nodes(tree: ast.AST, forbidden_types: set):
    """Walk *tree* and yield any AST node whose type is in *forbidden_types*."""
    for node in ast.walk(tree):
        if type(node) in forbidden_types:
            yield node


def _check_pass_invariants(tree: ast.Module, pass_cls, pass_name: str):
    """Validate that *pass_cls* truthfully declares its removed node types.

    After a pass runs, no AST node of a type listed in its
    ``removed_node_types`` should remain in the tree.  If one is found,
    the pass is either incomplete or its ``removed_node_types`` is wrong.
    """
    removed = set(getattr(pass_cls, 'removed_node_types', ()))
    if not removed:
        return
    survivors = list(_find_forbidden_nodes(tree, removed))
    if survivors:
        names = sorted({type(n).__name__ for n in survivors})
        raise AssertionError(
            f"Desugar invariant violation in {pass_name}: "
            f"declares it removes {names}, but {len(survivors)} node(s) "
            f"of those types survived the pass."
        )


def _run_desugar_passes(tree: ast.Module, passes) -> ast.Module:
    for pass_cls in passes:
        tree = pass_cls().visit(tree)
        if _SHOULD_CHECK_INVARIANTS:
            _check_pass_invariants(tree, pass_cls, pass_cls.__name__)
    ast.fix_missing_locations(tree)
    return tree


def desugar_module(tree: ast.Module) -> ast.Module:
    return _run_desugar_passes(tree, DESUGAR_PASSES)


def desugar_module_for_nomi_interpreter(tree: ast.Module) -> ast.Module:
    return _run_desugar_passes(tree, NOMI_INTERPRETER_DESUGAR_PASSES)


def get_removed_node_types():
    """Return the set of AST node types removed by the desugar pipeline.

    Used by the reduced interpreter to auto-derive its NotImplementedError
    overrides, keeping the two in sync when passes are added or removed.
    """
    removed = set()
    for pass_cls in DESUGAR_PASSES:
        removed.update(pass_cls.removed_node_types)
    return removed
