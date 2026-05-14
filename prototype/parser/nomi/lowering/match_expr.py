"""Inline and block ``match`` expressions wrapped in IIFEs."""

import ast


class MatchExprMixin:
    def case_expr(self, items):
        if len(items) == 3:
            pattern, guard, value = items
        else:
            pattern, value = items
            guard = None
        return ast.match_case(
            pattern=pattern, guard=guard, body=[ast.Return(value=value)],
        )

    def case_block_expr(self, items):
        return self.case_expr(items)

    def match_inline(self, items):
        return self._match_expr_iife(items)

    def match_block_expr(self, items):
        return self._match_expr_iife(items)

    def _match_expr_iife(self, items):
        subject, *cases = items
        match_node = ast.Match(subject=subject, cases=cases)
        empty_args = ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        func = ast.FunctionDef(
            name=None, args=empty_args, body=[match_node],
            decorator_list=[], returns=None,
        )
        return ast.Call(func=func, args=[], keywords=[])

    def assign_match_block(self, items):
        return self.assign(items)

    def return_match_block(self, items):
        return ast.Return(value=items[0])
