"""Arrow-function lowering: ``(x, y) => expr`` → ``FunctionDef``."""

import ast


class FuncExprMixin:
    def func_expr(self, items):
        # Single-param: NAME "=>" test ["->" test] → [name, body] or [name, body, returns]
        if len(items) >= 2 and isinstance(items[0], str):
            if len(items) == 2:
                name, body = items
                returns = None
            else:
                name, body, returns = items
            param = ast.arg(arg=name)
            params = ast.arguments(
                posonlyargs=[], args=[param], kwonlyargs=[], kw_defaults=[],
                defaults=[], vararg=None, kwarg=None,
            )
            return ast.FunctionDef(
                name=None, args=params, body=[ast.Return(value=body)],
                decorator_list=[], returns=returns,
            )

        # Multi-param: "(" [parameters] ")" "=>" test ["->" test]
        # Route through funcdef transformer.  Extract optional returns
        # from items (after body), then build the funcdef call.
        name = None
        items.insert(0, name)
        # items is now: [name, params, body] or [name, params, body, returns]
        if len(items) == 4:
            returns = items.pop()  # extract returns
        else:
            returns = None

        expr = items[-1]
        return_node = ast.Return(value=expr)
        func_body = [return_node]
        items.insert(-1, returns)
        items[-1] = func_body
        return self.funcdef(items)
