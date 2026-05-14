"""Function composition: ``f >>> g`` → ``(__x) => g(f(__x))``."""

import ast


class ComposeMixin:
    def compose_expr(self, items):
        if len(items) == 1:
            return items[0]

        x = ast.Name(id='__x', ctx=ast.Load())

        if str(items[1]) == '>>>':
            body = self._compose_call(items[0], x)
            i = 2
            while i < len(items):
                body = self._compose_call(items[i], body)
                i += 2
        else:
            body = self._compose_call(items[-1], x)
            i = len(items) - 3
            while i >= 0:
                body = self._compose_call(items[i], body)
                i -= 2

        param = ast.arg(arg='__x')
        params = ast.arguments(
            posonlyargs=[], args=[param], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        return ast.FunctionDef(
            name=None, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )

    @staticmethod
    def _compose_call(func, arg):
        return ast.Call(func=func, args=[arg], keywords=[])
