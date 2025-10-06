
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
        """
        items[0] = test
        items[1] = suite (body)
        items[2] = elifs (list of (test, body) tuples)
        items[3] = else_suite (optional)
        """
        test = items[0]
        if not isinstance(test, ast.expr):
            raise TypeError(f"If test must be an expression, got {type(test)}")

        body = ensure_stmt_list(items[1])

        # Ensure elifs is a list of tuples
        elifs = items[2] if len(items) > 2 else []

        # Ensure else_suite is always a list
        else_suite = ensure_stmt_list(items[3]) if len(items) > 3 else []

        # Start with orelse being the else suite (always a list)
        orelse_node = else_suite

        # Process elifs in reverse to nest If nodes
        for elif_item in reversed(elifs):
            if not (isinstance(elif_item, tuple) and len(elif_item) == 2):
                raise TypeError(f"Elif item must be a (test, body) tuple, got {type(elif_item)}")
            elif_test, elif_body = elif_item
            elif_body_list = ensure_stmt_list(elif_body)
            nested_if = ast.If(
                test=elif_test,
                body=elif_body_list,
                orelse=orelse_node   # Always a list
            )
            orelse_node = [nested_if]

        # orelse_node is now guaranteed to be a list
        return ast.If(test=test, body=body, orelse=orelse_node)

    def while_stmt(self, items):
        test = items[0]; body = items[1] if len(items) > 1 else []; orelse = items[2] if len(items) > 2 else []
        return ast.While(test=ensure_expr(test), body=body, orelse=orelse)

    def for_stmt(self, items):
        target = items[0]; iter_expr = items[1]; body = items[2] if len(items) > 2 else []; 
        orelse = items[3] if len(items) > 3 else []
        if orelse is None:
            # ast complains othewise; thse might be handled at single place
            # where statemetns are normalized
            orelse = []

        targ = storeify(target) if isinstance(target, (ast.Name, ast.Tuple, ast.List)) else target
        return ast.For(target=targ, iter=ensure_expr(iter_expr), body=body, orelse=orelse, type_comment=None)
    
    def _to_expr(self, node):
        if isinstance(node, tuple) or isinstance(node, list):
            if len(node) == 1:
                return node[0]
            else:
                return ast.Tuple(elts=[self._to_expr(n) for n in node], ctx=ast.Load())
        return node

    # --- comp_for / comp_if ---
    def comp_for(self, items):
        target, iter_, *rest = items
        target = self._to_expr(target)

        # nested comp_iter
        generators = []
        if rest:
            nested = rest[0]
            if isinstance(nested, (tuple, list)):
                generators.extend(nested)
            else:
                generators.append(nested)

        return [ast.comprehension(target=target, iter=iter_, ifs=[], is_async=0)] + generators

    def comp_if(self, items):
        test, *rest = items
        if rest:
            sub_iter = rest[0]
            if isinstance(sub_iter, (tuple, list)):
                sub_iter[0].ifs.append(test)
                return sub_iter
            else:
                sub_iter.ifs.append(test)
                return [sub_iter]
        else:
            # fallback dummy comprehension to avoid None target
            dummy = ast.comprehension(
                target=ast.Name(id='_dummy', ctx=ast.Load()),
                iter=ast.List(elts=[], ctx=ast.Load()),
                ifs=[test],
                is_async=0
            )
            return [dummy]

    # --- all comprehension types ---
    def list_comp(self, items):
        elt, *comp_iter = items
        generators = comp_iter[0] if comp_iter else []
        return ast.ListComp(elt=self._to_expr(elt), generators=generators)

    def set_comp(self, items):
        elt, *comp_iter = items
        generators = comp_iter[0] if comp_iter else []
        return ast.SetComp(elt=self._to_expr(elt), generators=generators)

    def dict_comp(self, items):
        key, value, *comp_iter = items
        generators = comp_iter[0] if comp_iter else []
        return ast.DictComp(key=self._to_expr(key), value=self._to_expr(value), generators=generators)

    def gen_exp(self, items):
        elt, *comp_iter = items
        generators = comp_iter[0] if comp_iter else []
        return ast.GeneratorExp(elt=self._to_expr(elt), generators=generators)