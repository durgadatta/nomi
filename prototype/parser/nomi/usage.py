import ast
from lark import Lark
from lark.indenter import PythonIndenter
from lark.lexer import PatternRE

from pathlib import Path

from .ast_ import NomiToPythonAST
from ...grammar.assemble import assemble_grammar


def prefer_name_for_underscore_terminal(terminal):
    if terminal.name == "UNDERSCORE":
        terminal.pattern = PatternRE("(?!)_")


def get_parser(extra_layers=None):
    grammar = assemble_grammar(extra_layers=extra_layers)
    parser = Lark(
            grammar,
            parser="earley",
            postlex=PythonIndenter(),
            start="file_input",
            edit_terminals=prefer_name_for_underscore_terminal,
    )
    return parser


def generate_ast(filename=None, code=None, dump=False):
    assert filename or code
    if code is None:
        code = Path(filename).read_text()
    tree = get_parser().parse(code)
    node = NomiToPythonAST().transform(tree)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node
