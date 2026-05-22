import ast
from pathlib import Path

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
    # TODO(NOMI-ARCH-018): Keep this as the Python AST backend path while
    # future parser APIs expose Nomi Surface/Core IR as first-class artifacts.
    if not keep_surface:
        lower_surface_to_python(node)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node
