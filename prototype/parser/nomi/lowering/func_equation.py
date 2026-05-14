"""Func-equation lowering: ``f(p) = e`` → ``FunctionDef`` with ``_nomi_eq_args``.

Adjacent same-name equations are merged by the ``PiecewiseFunction`` desugar pass.
"""

import ast


class FuncEquationMixin:
    def func_equation_no_parens(self, items):
        if len(items) == 3:
            name, param_name, body = items
            guard = None
        else:
            name, param_name, guard, body = items
        args_list = [ast.arg(arg=param_name)]
        params = ast.arguments(
            posonlyargs=[], args=args_list, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        fn = ast.FunctionDef(
            name=name, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )
        fn._nomi_eq_args = [param_name]
        if guard:
            fn._nomi_eq_guard = guard
        return fn

    def func_equation(self, items):
        if len(items) == 3:
            name, eq_args, body = items
            guard = None
        else:
            name, eq_args, guard, body = items
        if eq_args is None:
            eq_args = []
        elif not isinstance(eq_args, list):
            eq_args = [eq_args]

        args_list = []
        defaults = []
        for i, arg in enumerate(eq_args):
            if isinstance(arg, tuple):
                arg_name, arg_default = arg
                args_list.append(ast.arg(arg=arg_name))
                if arg_default is not None:
                    defaults.append(arg_default)
            elif isinstance(arg, str):
                args_list.append(ast.arg(arg=arg))
            else:
                args_list.append(ast.arg(arg=f'__{i}'))

        params = ast.arguments(
            posonlyargs=[], args=args_list, kwonlyargs=[], kw_defaults=[],
            defaults=defaults, vararg=None, kwarg=None,
        )
        fn = ast.FunctionDef(
            name=name, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )
        fn._nomi_eq_args = eq_args
        if guard:
            fn._nomi_eq_guard = guard
        return fn

    def func_eq_args(self, items):
        return items

    def name_arg(self, items):
        if len(items) == 1:
            return (items[0], None)
        return (items[0], items[1])

    def value_arg(self, items):
        return items[0]
