"""Piecewise function definitions: merge contiguous ``f(p) = e`` stmts.

Haskell-style::

    fact(1) = 1
    fact(n) = fact(n - 1) * n

Merges into a single ``func`` with ``match`` dispatch::

    func fact(__0):
        match __0:
            case 1: return 1
            case n: return fact(n - 1) * n

Contiguous ``func_equation`` statements with the same name are merged.
The order is preserved (first match wins, like Haskell).
"""

import ast

from .base import BaseDesugarer


class PiecewiseFunction(BaseDesugarer):
    """Merge adjacent ``func_equation`` ``FunctionDef``\s into one match-dispatch function."""

    def visit_Module(self, node):
        self.generic_visit(node)
        new_body = []
        i = 0
        while i < len(node.body):
            stmt = node.body[i]
            if isinstance(stmt, ast.FunctionDef) and self._is_equation(stmt):
                group = self._collect_group(node.body, i)
                if len(group) >= 2:
                    merged = self._merge(group)
                    new_body.append(merged)
                    i += len(group)
                    continue
            new_body.append(stmt)
            i += 1
        node.body = new_body
        return node

    @staticmethod
    def _is_equation(node):
        return (
            isinstance(node, ast.FunctionDef)
            and hasattr(node, '_nomi_eq_args')
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Return)
        )

    @staticmethod
    def _collect_group(body, start):
        name = body[start].name
        group = []
        for i in range(start, len(body)):
            stmt = body[i]
            if PiecewiseFunction._is_equation(stmt) and stmt.name == name:
                group.append(stmt)
            else:
                break
        return group

    def _merge(self, group):
        first = group[0]
        param_count = len(first.args.args)
        synth_name = first.args.args[0].arg if param_count == 1 else '__0'

        cases = []
        for eq in group:
            eq_args = getattr(eq, '_nomi_eq_args', [])
            guard = getattr(eq, '_nomi_eq_guard', None)
            pattern = self._build_pattern(eq_args)
            cases.append(ast.match_case(pattern=pattern, guard=guard, body=eq.body))

        subject = ast.Name(id=synth_name, ctx=ast.Load())
        match_stmt = ast.Match(subject=subject, cases=cases)

        synth_args = ast.arguments(
            posonlyargs=[], args=[ast.arg(arg=synth_name)],
            kwonlyargs=[], kw_defaults=[], defaults=[],
            vararg=None, kwarg=None,
        )

        return ast.FunctionDef(
            name=first.name, args=synth_args,
            body=[match_stmt], decorator_list=[], returns=None,
        )

    def _build_pattern(self, eq_args):
        patterns = []
        for arg in eq_args:
            if isinstance(arg, str):
                patterns.append(ast.MatchAs(pattern=None, name=arg))
            elif isinstance(arg, ast.Constant):
                patterns.append(ast.MatchValue(value=arg))
            elif isinstance(arg, ast.Name):
                patterns.append(ast.MatchAs(pattern=None, name=arg.id))
            else:
                patterns.append(ast.MatchAs(pattern=None))
        if len(patterns) == 1:
            return patterns[0]
        return ast.MatchSequence(patterns=patterns)
