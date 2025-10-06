import ast
from lark import Token


def ensure_name(x):
    if isinstance(x, Token):
        return x.value
    if isinstance(x, str):
        return x
    if isinstance(x, ast.Name):
        return x.id
    return str(x)

def ensure_expr(x):
    """
        Coerce many shapes into ast.expr; fallback to ast.parse for tokens/strings.
        
    This likely means some identifier (name/var/NAME) etc. is not handled well somewhere

    #THIS should be removed later
    """
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

def ensure_stmt_list(stmts):
    out = []
    stmts = stmts or []
    for n in stmts:
        if isinstance(n, ast.stmt):
            out.append(n)
        elif isinstance(n, list):
            out.extend(ensure_stmt_list(n))
        elif isinstance(n, ast.expr):
            # Only wrap true expression statements
            out.append(ast.Expr(value=n))
        else:
            raise TypeError(f"Unknown node in statement list: {type(n)}")
    return out


def tokval(t):
    return t.value if isinstance(t, Token) else str(t)


# --- Helper: recursively set Store() context for LHS ---
def ensure_store(node):
    '''
    Mainly used in assignment; but there are also other implicit assignment
        - with .. as var
    '''
    if isinstance(node, ast.Name):
        return ast.Name(id=node.id, ctx=ast.Store())
    elif isinstance(node, ast.Attribute):
        return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Store())
    elif isinstance(node, ast.Subscript):
        return ast.Subscript(value=node.value, slice=node.slice, ctx=ast.Store())
    elif isinstance(node, ast.Starred):
        # Python allows starred expressions in assignment: *a, b = ...
        return ast.Starred(value=ensure_store(node.value), ctx=ast.Store())
    elif isinstance(node, ast.Tuple):
        return ast.Tuple(elts=[ensure_store(e) for e in node.elts], ctx=ast.Store())
    elif isinstance(node, list):
        # Lark transformer may return a list for comma-separated targets
        return ast.Tuple(elts=[ensure_store(e) for e in node], ctx=ast.Store())
    else:
        return node  # unknown node types, leave as-is

