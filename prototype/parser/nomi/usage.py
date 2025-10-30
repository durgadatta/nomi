import ast
from lark import Lark
from lark.indenter import PythonIndenter

from pathlib import Path

from .ast_ import NomiToPythonAST


def get_parser():
    '''
    TODO: make the path more robust, now assume
    the entrypoint script will be at prototype/
    '''
    grammar_path = Path().joinpath('prototype/grammar/nomi.lark')
    grammar = grammar_path.read_text()
    parser = Lark(
            grammar,
            parser="earley",
            postlex=PythonIndenter(),
            start="file_input",
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
