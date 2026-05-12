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
from .layers.expression_transform import ExpressionLayer

_LAYERS_DIR = Path(__file__).resolve().parent / "layers"

_LAYER_ORDER = [
    "terminals.lark",
    "expressions.lark",
    "statements.lark",
    "patterns.lark",
    "bindings.lark",
    "calls.lark",
]

# Transforms run AFTER the raw parse, in this order
_LAYER_TRANSFORMS = [
    ExpressionLayer(),
]


def assemble_grammar(extra_layers=None):
    """Concatenate layer grammar files into a single Lark grammar string."""
    parts = []
    all_layers = list(_LAYER_ORDER)
    if extra_layers:
        all_layers.extend(extra_layers)
    for name in all_layers:
        path = _LAYERS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Grammar layer not found: {path}")
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def get_layer_pipeline():
    """Return the LayerPipeline that transforms the raw parse tree."""
    return LayerPipeline(list(_LAYER_TRANSFORMS))


def get_grammar_text():
    """Return the assembled grammar (cached in nomi.lark for compatibility)."""
    return assemble_grammar()
