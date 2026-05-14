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
# ExpressionLayer is lazy-imported to break circular dependency
# (assemble → parser/nomi/__init__ → usage → assemble).
_LAYER_TRANSFORMS = None

_LAYERS_DIR = Path(__file__).resolve().parent / "layers"

# TODO(NOMI-SUBSTRATE-001): Replace this hardcoded layer order with a small
# feature-manifest registry. Each syntax feature should eventually declare its
# grammar fragments, parse-tree transforms, lowering passes, docs, and tests in
# one place; this list can remain the built-in core layer order until then.
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
    """Concatenate layer grammar files into a single Lark grammar string."""
    global _GRAMMAR_CACHE
    if extra_layers is None and _GRAMMAR_CACHE is not None:
        return _GRAMMAR_CACHE
    parts = []
    all_layers = list(_LAYER_ORDER)
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
    """Return the LayerPipeline that transforms the raw parse tree."""
    global _LAYER_TRANSFORMS
    if _LAYER_TRANSFORMS is None:
        from ..parser.nomi.desugar.parse_tree_precedence import ExpressionLayer
        # TODO(NOMI-SUBSTRATE-001): Feature manifests should also contribute
        # parse-tree transforms so adding syntax does not require editing this
        # central assembly file by hand.
        _LAYER_TRANSFORMS = [ExpressionLayer()]
    return LayerPipeline(list(_LAYER_TRANSFORMS))


def get_grammar_text():
    """Return the assembled grammar (cached in nomi.ref.lark for reference)."""
    return assemble_grammar()
