"""
Grammar assembly — concatenates layered ``.lark`` fragments into a single
grammar string for Lark.

The fragments live in ``prototype/grammar/layers/``, one per concern.
Assembly order: terminals must come first (``%declare`` / ``%ignore`` are
position-sensitive in Lark).  The remaining layers are order-independent.
"""

from pathlib import Path

_LAYERS_DIR = Path(__file__).resolve().parent / "layers"

# Order matters: terminals must be assembled first.
_LAYER_ORDER = [
    "terminals.lark",
    "expressions.lark",
    "statements.lark",
    "patterns.lark",
    "bindings.lark",
    "calls.lark",
]


def assemble_grammar(extra_layers=None):
    """Read layer files and return a single grammar string.

    ``extra_layers`` is an optional list of additional layer file names
    that are appended after the built-in layers.  This is the primary
    extension point: to add experimental syntax, drop a ``.lark``
    fragment into ``layers/`` and pass its name here.
    """
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


def get_grammar_text():
    """Return the assembled grammar (cached in nomi.lark for compatibility)."""
    return assemble_grammar()
