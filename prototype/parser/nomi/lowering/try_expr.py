"""``try`` expression lowered to an IIFE with try/except."""

import ast


class TryExprMixin:
    def try_except_clause(self, items):
        exc_type, handler_expr = items[0], items[-1]
        exc_name = items[1] if len(items) == 3 else None
        return (exc_type, exc_name, handler_expr)

    def try_expr(self, items):
        body_expr, *clauses = items
        handlers = []
        for exc_type, exc_name, handler_expr in clauses:
            exc_node = ast.Name(id=exc_type, ctx=ast.Load())
            handlers.append(
                ast.ExceptHandler(
                    type=exc_node, name=exc_name,
                    body=[ast.Return(value=handler_expr)],
                )
            )

        try_node = ast.Try(
            body=[ast.Return(value=body_expr)],
            handlers=handlers, orelse=[], finalbody=[],
        )
        empty_args = ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        func = ast.FunctionDef(
            name=None, args=empty_args, body=[try_node],
            decorator_list=[], returns=None,
        )
        return ast.Call(func=func, args=[], keywords=[])
