"""Operator sections: ``(+ 1)``, ``(1 +)``, ``(+)`` → lambda functions."""

import ast


class SectionMixin:
    _BINOP_CLS = {
        '*': ast.Mult, '/': ast.Div, '%': ast.Mod, '//': ast.FloorDiv,
        '@': ast.MatMult,
        '+': ast.Add, '-': ast.Sub,
        '<<': ast.LShift, '>>': ast.RShift,
        '&': ast.BitAnd, '|': ast.BitOr, '^': ast.BitXor,
    }

    def section(self, items):
        return items[0]

    def left_section(self, items):
        op_token, rhs = items
        return self._section_lambda(lambda p: ast.BinOp(
            left=ast.Name(id=p, ctx=ast.Load()),
            op=self._section_op(op_token)(), right=rhs,
        ))

    def right_section(self, items):
        lhs, op_token = items
        return self._section_lambda(lambda p: ast.BinOp(
            left=lhs, op=self._section_op(op_token)(),
            right=ast.Name(id=p, ctx=ast.Load()),
        ))

    def operator_value(self, items):
        op_token = items[0]
        op_cls = self._section_op(op_token)
        return self._section_lambda(
            lambda a, b: ast.BinOp(
                left=ast.Name(id=a, ctx=ast.Load()),
                op=op_cls(),
                right=ast.Name(id=b, ctx=ast.Load()),
            ),
            param_names=('__a', '__b'),
        )

    def _section_op(self, op_token):
        name = op_token.value if hasattr(op_token, 'value') else str(op_token)
        return self._BINOP_CLS.get(name, ast.Add)

    @staticmethod
    def _section_lambda(body_fn, param_names=('__s',)):
        params = [ast.arg(arg=n) for n in param_names]
        if len(param_names) == 1:
            ret_val = body_fn(param_names[0])
        else:
            ret_val = body_fn(*param_names)
        args = ast.arguments(
            posonlyargs=[], args=params, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        return ast.FunctionDef(
            name=None, args=args, body=[ast.Return(value=ret_val)],
            decorator_list=[], returns=None,
        )
