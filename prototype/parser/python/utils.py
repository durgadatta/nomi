import ast
from lark import Token
from pathlib import Path


def ensure_expr(x):
    """
        Coerce many shapes into ast.expr; fallback to ast.parse for tokens/strings.
        
    This likely means some identifier (name/var/NAME) etc. is not handled well somewhere

    #THIS should be removed later
    """
    if isinstance(x, ast.expr):
        return x
    else:
        s = str(x)
    return ast.parse(s, mode='eval').body


# --- Helper: recursively set Store() context for LHS ---
def ensure_store(node):
    '''
    Mainly used in assignment; but there are also other implicit assignment
        - with .. as var
    '''
    lineno = getattr(node, 'lineno', 1)
    col_offset = getattr(node, 'col_offset', 0)
    
    if isinstance(node, ast.Name):
        return ast.Name(id=node.id, ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    elif isinstance(node, ast.Attribute):
        return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    elif isinstance(node, ast.Subscript):
        return ast.Subscript(value=node.value, slice=node.slice, ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    elif isinstance(node, ast.Starred):
        return ast.Starred(value=ensure_store(node.value), ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    elif isinstance(node, ast.Tuple):
        return ast.Tuple(elts=[ensure_store(e) for e in node.elts], ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    elif isinstance(node, list):
        return ast.Tuple(elts=[ensure_store(e) for e in node], ctx=ast.Store(), lineno=lineno, col_offset=col_offset)
    else:
        return node
    

# parser usage utilities
def get_parser():
    from lark import Lark
    from lark.indenter import PythonIndenter
    python_parser = Lark.open_from_package(
            "lark",
            "python.lark",
            ["grammars"],
            parser="lalr",
            postlex=PythonIndenter(),
            start="file_input",
    )
    return python_parser


def generate_ast(filename=None, code=None, dump=False):
    from .ast_ import PythonASTTransformer
    assert filename or code

    if code is None:
        code = Path(filename).read_text()
    tree = get_parser().parse(code)
    node = PythonASTTransformer().transform(tree)
    if dump:
        return ast.dump(node, include_attributes=False, indent=2)
    return node



    


