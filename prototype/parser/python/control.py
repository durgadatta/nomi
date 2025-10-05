
import ast
from prototype.parser.python import ensure_expr, storeify

import ast

def ensure_stmt_list(stmts):
    out = []
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

class ControlMixin:
    def elif_(self, items):
        # items[0] = test (ast.expr), items[1] = suite (list or nodes)
        test_node = items[0]
        if not isinstance(test_node, ast.expr):
            raise TypeError(f"Elif test must be an expression, got {type(test_node)}")
        body_list = ensure_stmt_list(items[1])
        return (test_node, body_list)

    def elifs(self, items):
        # items is a list of elif_ results (each a (test, body) tuple)
        return items  # Return the list of (test, body) tuples as-is

    def if_stmt(self, items):
        # items[0] = test, items[1] = suite, items[2] = elifs, items[3] = else suite (optional)
        test = items[0]
        if not isinstance(test, ast.expr):
            raise TypeError(f"If test must be an expression, got {type(test)}")
        body = ensure_stmt_list(items[1])
        elifs = items[2] if len(items) > 2 else []  # List of (test, body) tuples from elif_
        else_suite = items[3] if len(items) > 3 else None  # Optional else suite

        # Initialize orelse as empty list
        orelse_node = []

        # Handle else suite (if present)
        if else_suite is not None:
            orelse_node = ensure_stmt_list(else_suite)

        # Process elifs in reverse to build nested If nodes
        for elif_item in reversed(elifs):
            if not (isinstance(elif_item, tuple) and len(elif_item) == 2):
                raise TypeError(f"Elif item must be a (test, body) tuple, got {type(elif_item)}")
            elif_test, elif_body = elif_item
            if not isinstance(elif_test, ast.expr):
                raise TypeError(f"Elif test must be an expression, got {type(elif_test)}")
            if not isinstance(elif_body, list) or not all(isinstance(x, ast.stmt) for x in elif_body):
                raise TypeError(f"Elif body must be a list of statements, got {elif_body}")
            # Create nested If for elif
            nested_if = ast.If(
                test=elif_test,
                body=elif_body,  # Already processed by ensure_stmt_list in elif_
                orelse=orelse_node
            )
            orelse_node = [nested_if]

        return ast.If(test=test, body=body, orelse=orelse_node)

    
    def while_stmt(self, items):
        test = items[0]; body = items[1] if len(items) > 1 else []; orelse = items[2] if len(items) > 2 else []
        return ast.While(test=ensure_expr(test), body=body, orelse=orelse)

    def for_stmt(self, items):
        target = items[0]; iter_expr = items[1]; body = items[2] if len(items) > 2 else []; orelse = items[3] if len(items) > 3 else []
        targ = storeify(target) if isinstance(target, (ast.Name, ast.Tuple, ast.List)) else target
        return ast.For(target=targ, iter=ensure_expr(iter_expr), body=body, orelse=orelse, type_comment=None)

    # basic comprehensions: best-effort placeholders for many shapes
    def comp_for(self, items):
        target = items[-2]; iter_ = items[-1]
        return ast.comprehension(target=storeify(target), iter=ensure_expr(iter_), ifs=[], is_async=0)

    def list_comprehension(self, items):
        return ast.ListComp(elt=ensure_expr(items[0]) if items else ast.Constant(None), generators=[])
