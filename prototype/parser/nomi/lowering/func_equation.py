"""Func-equation lowering: ``f(p) = e`` → ``FunctionDef`` with ``_nomi_eq_args``.

Adjacent same-name equations are merged by the ``PiecewiseFunction`` desugar pass.
"""

import ast


class FuncEquationMixin:
    def func_equation_no_parens_plain(self, items):
        if len(items) == 3:
            name, param_name, body = items
            returns = None
        else:
            name, param_name, body, returns = items
        return self._build_equation_function(name, [param_name], body, guard=None, returns=returns)

    def func_equation_no_parens_guarded(self, items):
        if len(items) == 4:
            name, param_name, guard, body = items
            returns = None
        else:
            name, param_name, guard, body, returns = items
        return self._build_equation_function(name, [param_name], body, guard=guard, returns=returns)

    def func_equation_plain(self, items):
        if len(items) == 3:
            name, eq_args, body = items
            returns = None
        else:
            name, eq_args, body, returns = items
        return self._build_equation_function(name, eq_args, body, guard=None, returns=returns)

    def func_equation_guarded(self, items):
        if len(items) == 4:
            name, eq_args, guard, body = items
            returns = None
        else:
            name, eq_args, guard, body, returns = items
        return self._build_equation_function(name, eq_args, body, guard=guard, returns=returns)

    def _build_equation_function(self, name, eq_args, body, guard, returns):
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
            decorator_list=[], returns=returns,
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
