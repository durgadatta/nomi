import ast
from lark import Token


def tokval(t):
    return t.value if isinstance(t, Token) else str(t)

def ensure_name(x):
    if isinstance(x, Token):
        return x.value
    if isinstance(x, str):
        return x
    if isinstance(x, ast.Name):
        return x.id
    return str(x)

def ensure_expr(x):
    """Coerce many shapes into ast.expr; fallback to ast.parse for tokens/strings."""
    if x is None:
        return ast.Constant(value=None)
    if isinstance(x, ast.expr):
        return x
    if isinstance(x, Token):
        s = x.value
    else:
        s = str(x)
    try:
        return ast.parse(s, mode='eval').body
    except Exception:
        if s.isidentifier():
            return ast.Name(id=s, ctx=ast.Load())
        return ast.Constant(value=s)

def ensure_arg(x):
    if isinstance(x, ast.arg):
        return x
    if isinstance(x, Token):
        return ast.arg(arg=x.value, annotation=None)
    if isinstance(x, ast.Name):
        return ast.arg(arg=x.id, annotation=None)
    if isinstance(x, str):
        return ast.arg(arg=x, annotation=None)
    raise TypeError("Cannot coerce to ast.arg: %r" % (x,))

def storeify(node):
    if isinstance(node, ast.Name):
        return ast.copy_location(ast.Name(id=node.id, ctx=ast.Store()), node)
    if isinstance(node, ast.Tuple):
        elts = [storeify(e) for e in node.elts]
        return ast.copy_location(ast.Tuple(elts=elts, ctx=ast.Store()), node)
    if isinstance(node, ast.List):
        elts = [storeify(e) for e in node.elts]
        return ast.copy_location(ast.List(elts=elts, ctx=ast.Store()), node)
    return node


