"""
Verify that every active desugar pass in the pipeline has a corresponding
NotImplementedError override in the reduced interpreter, and vice versa.

This prevents the situation where a desugar pass is added but the
interpreter override is forgotten (the reduced interpreter silently
delegates to the parent), or an override is added but the desugar
pass is never wired into the pipeline.

The reduced interpreter now auto-derives its overrides from the
pipeline's ``removed_node_types`` metadata, so this test validates
that the metadata is correct and complete.
"""

import ast

from prototype.parser.nomi.desugar.pipeline import (
    DESUGAR_PASSES,
    get_removed_node_types,
)
from prototype.interpreter.reduced import Interpreter
from prototype.syntax.features import BUILTIN_FEATURES, SUGAR_LAYER
from prototype.utils import resolve_dotted


def _reduced_override_names():
    overrides = set()
    for name in dir(Interpreter):
        if not name.startswith('eval_'):
            continue
        method = getattr(Interpreter, name)
        if method is None:
            continue
        if getattr(method, '__code__', None) is None:
            continue
        import inspect
        try:
            src = inspect.getsource(method)
        except OSError:
            continue
        # Only detect desugar stubs, not general NotImplementedError usage
        if 'desugared at parse time' in src:
            overrides.add(name)
    return overrides


def _expected_override_names():
    removed = get_removed_node_types()
    return {f'eval_{t.__name__}' for t in removed}


def test_desugar_removed_types_match():
    """Every AST type a desugar pass claims to remove must actually be
    removed (its visit_ method must exist on the desugarer)."""
    for pass_cls in DESUGAR_PASSES:
        for node_type in pass_cls.removed_node_types:
            visit_name = f'visit_{node_type.__name__}'
            assert hasattr(pass_cls, visit_name), (
                f"{pass_cls.__name__} declares removed_node_types={node_type.__name__} "
                f"but has no {visit_name} method"
            )


def test_every_desugar_pass_has_reduced_override():
    """Every removed node type has a NotImplementedError override in the
    reduced interpreter."""
    expected = _expected_override_names()
    actual = _reduced_override_names()
    missing = expected - actual
    assert not missing, (
        f"Reduced interpreter is missing NotImplementedError overrides: {missing}"
    )


def test_every_reduced_override_has_desugar_pass():
    """Every NotImplementedError override in the reduced interpreter
    corresponds to a node type that a desugar pass claims to remove."""
    expected = _expected_override_names()
    actual = _reduced_override_names()
    extra = actual - expected
    assert not extra, (
        f"Reduced interpreter has NotImplementedError overrides with no "
        f"corresponding desugar pass: {extra}"
    )


def test_all_desugar_passes_are_registered():
    """The pipeline DESUGAR_PASSES list is not empty and all classes
    are proper BaseDesugarer subclasses."""
    from prototype.parser.nomi.desugar.base import BaseDesugarer

    assert len(DESUGAR_PASSES) >= 3, "Expected at least 3 desugar passes"
    for pass_cls in DESUGAR_PASSES:
        assert issubclass(pass_cls, BaseDesugarer), (
            f"{pass_cls} is not a BaseDesugarer subclass"
        )


def test_desugar_pass_features_are_declared_as_sugar_reductions():
    """Every active desugar pass should be owned by an L4 feature.

    Reduced mode is the current guard that syntax reductions happened before
    evaluation.  This keeps that guard aligned with the newer feature-layer
    metadata until Core IR verification takes over.
    """
    feature_passes = {}
    for feature in BUILTIN_FEATURES:
        for ref in feature.desugar_passes:
            feature_passes[resolve_dotted(ref)] = feature

    missing = set(DESUGAR_PASSES) - set(feature_passes)
    assert not missing, f"Desugar passes missing SyntaxFeature owner: {missing}"

    for pass_cls in DESUGAR_PASSES:
        feature = feature_passes[pass_cls]
        assert feature.layer == SUGAR_LAYER
        assert feature.reduces_to
        assert feature.runtime_hooks_allowed in {"none", "temporary"}
