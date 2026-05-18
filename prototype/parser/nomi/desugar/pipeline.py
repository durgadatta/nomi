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

from prototype.syntax.features import (
    BUILTIN_FEATURES,
    DEFAULT_DESUGAR_PROFILE,
    get_desugar_passes,
)
from prototype.utils import resolve_dotted
from .base import Phase

_SHOULD_CHECK_INVARIANTS = os.environ.get(
    'NOMI_DESUGAR_CHECK_INVARIANTS', ''
).lower() in ('1', 'true', 'yes')


_PHASE_ORDER = tuple(Phase)
_PHASE_INDEX = {phase: index for index, phase in enumerate(_PHASE_ORDER)}


def _order_passes_by_phase(passes):
    """Return passes grouped by Phase while preserving manifest order inside each group."""
    indexed = list(enumerate(passes))

    def sort_key(item):
        original_index, pass_cls = item
        phase = getattr(pass_cls, "phase", Phase.syntax)
        return (_PHASE_INDEX.get(phase, len(_PHASE_ORDER)), original_index)

    return tuple(
        pass_cls
        for _index, pass_cls in sorted(indexed, key=sort_key)
    )


# Derived from BUILTIN_FEATURES in prototype/syntax/features.py.
# Feature order there determines ordering inside each phase bucket.
DESUGAR_PASSES = _order_passes_by_phase(get_desugar_passes())

# The full pipeline is required by the reduced interpreter because it checks
# that Python-compatible surface nodes have become normal forms.  The default
# Nomi interpreter can already execute Python-parity nodes such as AugAssign,
# Assert, Pass, With, decorators, and f-strings, so feature metadata declares
# the smaller pass set it needs.
NOMI_INTERPRETER_DESUGAR_PASSES = tuple(
    _order_passes_by_phase(get_desugar_passes(profile=DEFAULT_DESUGAR_PROFILE))
)


def _validate_pipeline(passes):
    """Validate dependencies for *passes*.

    Every class in ``depends_on`` must appear earlier in the phase-ordered
    pass list, and every phase must be a declared ``Phase`` value.
    """
    seen = set()
    errors = []

    for pass_cls in passes:
        name = pass_cls.__name__
        phase = getattr(pass_cls, 'phase', Phase.syntax)
        if phase not in _PHASE_INDEX:
            errors.append(
                f"Phase violation: {name} declares unknown phase {phase!r}."
            )
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


def render_desugar_pass_table(profile: str | None = None) -> str:
    """Return a compact table of active desugar passes and their contracts."""
    passes = (
        _order_passes_by_phase(get_desugar_passes(profile=profile))
        if profile is not None
        else DESUGAR_PASSES
    )
    feature_by_pass = {}
    for feature in BUILTIN_FEATURES:
        for ref in feature.desugar_passes:
            feature_by_pass[resolve_dotted(ref)] = feature

    rows = [
        "| pass | phase | feature | profiles | removes | depends on |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for pass_cls in passes:
        feature = feature_by_pass.get(pass_cls)
        removed = ", ".join(
            node_type.__name__ for node_type in pass_cls.removed_node_types
        ) or "-"
        depends_on = ", ".join(
            dependency.__name__ for dependency in pass_cls.depends_on
        ) or "-"
        profiles = (
            ", ".join(feature.desugar_profiles)
            if feature is not None
            else "-"
        )
        rows.append(
            "| {pass_name} | {phase} | {feature} | {profiles} | "
            "{removed} | {depends} |".format(
                pass_name=pass_cls.__name__,
                phase=pass_cls.phase.value,
                feature=feature.name if feature is not None else "-",
                profiles=profiles,
                removed=removed,
                depends=depends_on,
            )
        )
    return "\n".join(rows)
