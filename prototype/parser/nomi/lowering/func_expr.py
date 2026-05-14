"""Arrow-function lowering: ``(x, y) => expr`` → ``FunctionDef``."""

import ast


class FuncExprMixin:
    def func_expr(self, items):
        # Single-param: NAME "=>" test → [name, body]
        if len(items) == 2 and isinstance(items[0], str):
            name, body = items
            param = ast.arg(arg=name)
            params = ast.arguments(
                posonlyargs=[], args=[param], kwonlyargs=[], kw_defaults=[],
                defaults=[], vararg=None, kwarg=None,
            )
            return ast.FunctionDef(
                name=None, args=params, body=[ast.Return(value=body)],
                decorator_list=[], returns=None,
            )

        # Multi-param: "(" [parameters] ")" "=>" test
        name = None
        items.insert(0, name)
        expr = items[-1]
        return_node = ast.Return(value=expr)
        func_body = [return_node]
        items.insert(-1, None)
        items[-1] = func_body
        return self.funcdef(items)
