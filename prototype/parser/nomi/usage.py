import ast
import os
from lark import Lark
from lark.lexer import PatternRE

from pathlib import Path

from .ast_ import NomiToPythonAST
from .postlexer import NomiPostLexer
from ...grammar.assemble import assemble_grammar, get_layer_pipeline
from ...syntax.surface import lower_surface_to_python
from ...syntax.features import get_extra_grammar_layers


# ── parser cache ────────────────────────────────────────────────────
# Lark parser construction is noticeably more expensive than reusing a parser,
# especially in Pyodide/WebAssembly. Cache by the resolved extra-layer tuple so
# syntax experiments do not accidentally reuse the wrong parser.
_PARSER_CACHE = {}

# ── parse result cache ──────────────────────────────────────────────
# Cache raw parse trees by source-content hash so repeated parses of unchanged
# source (REPL, test suite, incremental editing) are instant.
_RAW_TREE_CACHE: dict[tuple[int, bool], object] = {}


def prefer_name_for_underscore_terminal(terminal):
    if terminal.name == "UNDERSCORE":
        terminal.pattern = PatternRE("(?!)_")


def _truthy_env(name):
    return os.environ.get(name, "").lower() in {"1", "true", "yes", "on"}


def _preserve_positions_default():
    return _truthy_env("NOMI_PARSER_SPANS")


def get_parser(extra_layers=None, preserve_positions=None):
    # Resolve extra layers: feature-derived layers + any experimental ad-hoc layers.
    resolved = tuple(get_extra_grammar_layers()) + (tuple(extra_layers) if extra_layers else ())
    if preserve_positions is None:
        preserve_positions = _preserve_positions_default()
    key = (resolved, preserve_positions)
    if key in _PARSER_CACHE:
        return _PARSER_CACHE[key]
    grammar = assemble_grammar(extra_layers=extra_layers)
    parser = Lark(
            grammar,
            parser="lalr",
            lexer="basic",
            postlex=NomiPostLexer(),
            start="file_input",
            edit_terminals=prefer_name_for_underscore_terminal,
            propagate_positions=preserve_positions,
    )
    _PARSER_CACHE[key] = parser
    return parser


def parse_raw_tree(code=None, filename=None, preserve_positions=None):
    """Return the raw Lark parse tree (before layer transforms)."""
    if code is None:
        code = Path(filename).read_text(encoding="utf-8")
    if preserve_positions is None:
        preserve_positions = _preserve_positions_default()
    key = (hash(code), preserve_positions)
    cached = _RAW_TREE_CACHE.get(key)
    if cached is not None:
        return cached
    tree = get_parser(preserve_positions=preserve_positions).parse(code)
    _RAW_TREE_CACHE[key] = tree
    return tree


def parse_transformed_tree(code=None, filename=None, preserve_positions=None):
    """Return the layer-transformed Lark tree (before Python AST lowering)."""
    tree = parse_raw_tree(
        code=code, filename=filename,
        preserve_positions=preserve_positions,
    )
    pipeline = get_layer_pipeline()
    return pipeline.run(tree)


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
    tree = parse_transformed_tree(code=code, preserve_positions=preserve_positions)

    node = NomiToPythonAST().transform(tree)
    if not keep_surface:
        lower_surface_to_python(node)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node
