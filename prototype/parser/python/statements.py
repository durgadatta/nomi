import ast
from lark import Token

from prototype.parser.python import ensure_expr, ensure_name, storeify

class StatementMixin():
    def suite(self, items):
        out = []
        for it in items:
            if isinstance(it, list): out.extend(it)
            elif isinstance(it, ast.stmt): out.append(it)
        return out

    def simple_stmt(self, items):
        out = []
        for it in items:
            if isinstance(it, list): out.extend(it)
            elif isinstance(it, ast.stmt): out.append(it)
        return out

    def expr_stmt(self, items):
        # detect simple assignment left '=' right
        for i, it in enumerate(items):
            if isinstance(it, Token) and it.value == '=':
                left = items[0]; right = items[i+1] if i+1 < len(items) else None
                target = storeify(left) if isinstance(left, (ast.Name, ast.Tuple, ast.List)) else left
                return ast.Assign(targets=[target], value=ensure_expr(right))
        return ast.Expr(value=ensure_expr(items[0]))

    def pass_stmt(self, items): return ast.Pass()
    def break_stmt(self, items): return ast.Break()
    def continue_stmt(self, items): return ast.Continue()



