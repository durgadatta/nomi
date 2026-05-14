import ast
from lark import Lark
from lark.indenter import PythonIndenter
from lark.lexer import PatternRE

from pathlib import Path

from .ast_ import NomiToPythonAST
from ...grammar.assemble import assemble_grammar, get_layer_pipeline


# ── parser cache ────────────────────────────────────────────────────
# Lark Earley parser construction is O(n³) in grammar size — easily
# 100+ ms even in CPython and much worse in Pyodide/WebAssembly.
# Cache by the active extra-layer tuple so syntax experiments do not
# accidentally reuse the default parser.
# TODO(NOMI-SUBSTRATE-002): Grow this into get_parser(features=[...]) once
# syntax feature manifests exist. The cache key should become the resolved
# feature set, not raw layer filenames.
_PARSER_CACHE = {}


def prefer_name_for_underscore_terminal(terminal):
    if terminal.name == "UNDERSCORE":
        terminal.pattern = PatternRE("(?!)_")


def get_parser(extra_layers=None):
    cache_key = tuple(extra_layers or ())
    if cache_key in _PARSER_CACHE:
        return _PARSER_CACHE[cache_key]
    grammar = assemble_grammar(extra_layers=extra_layers)
    parser = Lark(
            grammar,
            parser="earley",
            postlex=PythonIndenter(),
            start="file_input",
            edit_terminals=prefer_name_for_underscore_terminal,
    )
    _PARSER_CACHE[cache_key] = parser
    return parser


def parse_raw_tree(code=None, filename=None):
    """Return the raw Lark parse tree (before layer transforms)."""
    if code is None:
        code = Path(filename).read_text(encoding="utf-8")
    return get_parser().parse(code)


def parse_transformed_tree(code=None, filename=None):
    """Return the layer-transformed Lark tree (before Python AST lowering)."""
    tree = parse_raw_tree(code=code, filename=filename)
    pipeline = get_layer_pipeline()
    return pipeline.run(tree)


def generate_ast(filename=None, code=None, dump=False):
    assert filename or code
    if code is None:
        code = Path(filename).read_text()
    tree = parse_transformed_tree(code=code)

    node = NomiToPythonAST().transform(tree)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node
