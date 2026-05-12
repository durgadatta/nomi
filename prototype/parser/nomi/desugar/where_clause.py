"""Where clause desugar: local bindings for assignments.

Haskell-inspired::

    result = x + y where:
        x = 10
        y = compute(20)

Desugars to an immediately-invoked function::

    func __where_1():
        x = 10
        y = compute(20)
        return x + y
    result = __where_1()

The where-body bindings are local to the expression.
"""

import ast

from .base import BaseDesugarer


class WhereClause(BaseDesugarer):
    """Desugar ``_nomi_where_body`` on statements into wrapper functions."""

    _counter = 0

    def visit_Module(self, node):
        self.generic_visit(node)
        # Run piecewise merging on the where-bodies before extracting
        from .piecewise import PiecewiseFunction
        pw = PiecewiseFunction()
        new_body = []
        for stmt in node.body:
            where_body = getattr(stmt, '_nomi_where_body', None)
            if where_body is not None:
                # Merge piecewise equations in the where-body
                fake_module = ast.Module(body=list(where_body), type_ignores=[])
                fake_module = pw.visit(fake_module)
                stmt._nomi_where_body = fake_module.body
            new_body.append(stmt)
        node.body = new_body

        # Now desugar the where clauses
        new_body = []
        for stmt in node.body:
            where_body = getattr(stmt, '_nomi_where_body', None)
            if where_body is None:
                new_body.append(stmt)
                continue

            delattr(stmt, '_nomi_where_body')

            if isinstance(stmt, ast.FunctionDef):
                # func_equation with where: wrap body in where-bindings
                orig_return = stmt.body[-1] if stmt.body else None
                stmt.body = where_body + ([orig_return] if orig_return else [])
                new_body.append(stmt)
                continue

            self._counter += 1
            fn_name = f'__where_{self._counter}'

            if isinstance(stmt, ast.Assign):
                value_expr = stmt.value
                targets = stmt.targets
            elif isinstance(stmt, ast.Expr):
                value_expr = stmt.value
                targets = None
            else:
                new_body.append(stmt)
                continue

            where_body.append(ast.Return(value=value_expr))
            wrapper = ast.FunctionDef(
                name=fn_name,
                args=ast.arguments(
                    posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
                    defaults=[], vararg=None, kwarg=None,
                ),
                body=where_body,
                decorator_list=[], returns=None,
            )
            new_body.append(wrapper)

            if targets is not None:
                call = ast.Call(
                    func=ast.Name(id=fn_name, ctx=ast.Load()),
                    args=[], keywords=[],
                )
                new_body.append(ast.Assign(targets=targets, value=call))
            else:
                new_body.append(ast.Expr(value=ast.Call(
                    func=ast.Name(id=fn_name, ctx=ast.Load()),
                    args=[], keywords=[],
                )))

        node.body = new_body
        return node
