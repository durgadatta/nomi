import ast
import sys
from pathlib import Path

from lark import Tree as LarkTree

from . import frontend as _frontend
from .ast_ import NomiToPythonAST
from .frontend import (
    DEFAULT_FRONTEND,
    GRAMMAR_VERSION,
    ParserCacheKey,
    RawTreeCacheKey,
    get_parser_frontend,
)
from ...syntax.surface import lower_surface_to_python


def _find_unlowered_trees(node, path="root", _seen=None):
    """Walk *node* and return a list of ``(path, tree_data)`` for any Lark
    Tree objects still present after the Lark→Python-AST transformation.

    Descends into ``ast.AST``, ``SurfaceNode`` dataclasses, lists, tuples,
    and any object with ``__slots__`` or ``__dict__``.  Each entry identifies
    the containment path and the unhandled grammar rule name.
    """
    if _seen is None:
        _seen = set()
    obj_id = id(node)
    if obj_id in _seen:
        return []
    _seen.add(obj_id)

    found = []
    if isinstance(node, LarkTree):
        found.append((path, node.data))
        return found

    fields = None
    if isinstance(node, ast.AST):
        fields = [(f, getattr(node, f, None)) for f in node._fields]
    elif hasattr(node, "__slots__"):
        slots = node.__slots__
        if isinstance(slots, str):
            slots = (slots,)
        fields = [(f, getattr(node, f, None)) for f in slots if hasattr(node, f)]
    elif hasattr(node, "__dict__") and not isinstance(node, type):
        fields = list(node.__dict__.items())

    if fields is not None:
        for field_name, value in fields:
            if isinstance(value, LarkTree):
                found.append((f"{path}.{field_name}", value.data))
            elif isinstance(value, (list, tuple)):
                for i, item in enumerate(value):
                    found.extend(
                        _find_unlowered_trees(item, f"{path}.{field_name}[{i}]", _seen)
                    )
            elif value is not None and not isinstance(value, (str, int, float, bool, bytes)):
                found.extend(
                    _find_unlowered_trees(value, f"{path}.{field_name}", _seen)
                )
    return found


# Compatibility aliases for tests and debugging code that inspect the current
# cache directly. New parser work should go through the frontend object instead.
_DEFAULT_FRONTEND = get_parser_frontend(DEFAULT_FRONTEND)
_PARSER_CACHE = _frontend._PARSER_CACHE
_RAW_TREE_CACHE = _frontend._RAW_TREE_CACHE


def _preserve_positions_default():
    return _frontend.preserve_positions_default()


def _parser_cache_key(extra_layers=None, preserve_positions=None) -> ParserCacheKey:
    return _DEFAULT_FRONTEND.parser_cache_key(
        extra_layers=extra_layers,
        preserve_positions=preserve_positions,
    )


def get_parser(extra_layers=None, preserve_positions=None):
    return _DEFAULT_FRONTEND.get_parser(
        extra_layers=extra_layers,
        preserve_positions=preserve_positions,
    )


def parse_raw_tree(code=None, filename=None, preserve_positions=None):
    """Return the raw Lark parse tree (before layer transforms)."""
    return _DEFAULT_FRONTEND.parse_raw_tree(
        code=code,
        filename=filename,
        preserve_positions=preserve_positions,
    )


def parse_transformed_tree(code=None, filename=None, preserve_positions=None):
    """Return the layer-transformed Lark tree (before Python AST lowering)."""
    return _DEFAULT_FRONTEND.parse_transformed_tree(
        code=code,
        filename=filename,
        preserve_positions=preserve_positions,
    )


def generate_ast(
    filename=None, code=None, dump=False, keep_surface=False,
    preserve_positions=None,
):
    """Parse *filename* or *code*, lower to Python AST, and return it.

    Intermediate surface nodes (Nomi-owned constructs that Python AST
    cannot represent naturally) are lowered in-place before returning,
    unless *keep_surface* is True (for inspection/debugging).
    """
    assert filename or code
    if code is None:
        code = Path(filename).read_text()
    tree = parse_transformed_tree(
        code=code,
        filename=filename,
        preserve_positions=preserve_positions,
    )

    node = NomiToPythonAST().transform(tree)
    if not isinstance(node, ast.AST):
        raise TypeError(
            f"generate_ast: NomiToPythonAST.transform returned {type(node).__name__}, "
            f"expected an ast.AST node. This indicates a missing transformer method "
            f"for one or more grammar rules."
        )
    unlowered = _find_unlowered_trees(node)
    if unlowered:
        rules = sorted({data for _, data in unlowered})
        paths = [f"{p} ({d})" for p, d in unlowered[:5]]
        if len(unlowered) > 5:
            paths.append(f"... and {len(unlowered) - 5} more")
        detail = "\n  ".join(paths)
        print(
            f"[nomi] ERROR: {len(unlowered)} Lark Tree(s) leaked into Python AST "
            f"after NomiToPythonAST.transform. Unhandled grammar rules: {rules}\n"
            f"  {detail}",
            file=sys.stderr,
        )
        raise TypeError(
            f"generate_ast: {len(unlowered)} unhandled grammar rule(s) — "
            f"{', '.join(rules)}. Add a transformer method for each rule "
            f"or mark it as inlined (?) in the grammar."
        )
    # TODO(NOMI-ARCH-018): Keep this as the Python AST backend path while
    # future parser APIs expose Nomi Surface/Core IR as first-class artifacts.
    if not keep_surface:
        lower_surface_to_python(node)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node
