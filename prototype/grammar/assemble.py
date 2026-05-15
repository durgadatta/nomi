"""
Grammar assembly — composes layered ``.lark`` fragments into a single
grammar string, and builds the corresponding parse-tree transform pipeline.

Each layer defines:
  - a grammar fragment (``.lark`` file in ``layers/``)
  - an optional ``LayerTransform`` (Python module alongside the fragment)

The pipeline::

    Source → assembled grammar → raw Lark Tree
          → LayerTransform chain → final Lark Tree
          → NomiToPythonAST → Python AST → desugar → Interpreter
"""

from pathlib import Path

from .layer import LayerPipeline


# Transforms run AFTER the raw parse, in this order.
# Derived lazily from the feature registry so adding a layer transform
# does not require editing this file.
_LAYER_TRANSFORMS = None

_LAYERS_DIR = Path(__file__).resolve().parent / "layers"

# Core grammar layers are always present in this order.  Syntax features
# that add new grammar fragments declare extra_layers in their manifest
# (prototype/syntax/features.py) and are appended after the core.
_LAYER_ORDER = [
    "terminals.lark",
    "expressions.lark",
    "statements.lark",
    "patterns.lark",
    "bindings.lark",
    "calls.lark",
]


# ── grammar cache ───────────────────────────────────────────────────
# Avoid re-reading six .lark files from Pyodide's virtual filesystem
# on every parse.  The grammar is static at runtime; cache it.
_GRAMMAR_CACHE = None


def assemble_grammar(extra_layers=None):
    """Concatenate layer grammar files into a single Lark grammar string.

    Extra grammar layers declared by features in the syntax registry
    are appended after the base layers.  The *extra_layers* parameter
    allows ad-hoc experimental layers on top (for syntax prototyping).
    """
    global _GRAMMAR_CACHE
    if extra_layers is None and _GRAMMAR_CACHE is not None:
        return _GRAMMAR_CACHE
    from prototype.syntax.features import get_extra_grammar_layers
    parts = []
    all_layers = list(_LAYER_ORDER) + get_extra_grammar_layers()
    if extra_layers:
        all_layers.extend(extra_layers)
    for name in all_layers:
        path = _LAYERS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Grammar layer not found: {path}")
        parts.append(path.read_text(encoding="utf-8"))
    grammar = "\n\n".join(parts)
    if extra_layers is None:
        _GRAMMAR_CACHE = grammar
    return grammar


def get_layer_pipeline():
    """Return the LayerPipeline that transforms the raw parse tree.

    Layer transforms are derived from the syntax feature registry
    (prototype/syntax/features.py) so adding a parse-tree transform
    does not require editing this assembly file.
    """
    global _LAYER_TRANSFORMS
    if _LAYER_TRANSFORMS is None:
        from prototype.syntax.features import get_layer_transforms
        _LAYER_TRANSFORMS = get_layer_transforms()
    return LayerPipeline(list(_LAYER_TRANSFORMS))


def get_grammar_text():
    """Return the assembled grammar (cached in nomi.ref.lark for reference)."""
    return assemble_grammar()
