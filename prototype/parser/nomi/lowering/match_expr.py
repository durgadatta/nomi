"""Inline and block ``match`` expressions wrapped in IIFEs."""

import ast


class MatchExprMixin:
    def case_expr(self, items):
        if len(items) == 3:
            pattern, guard, value = items
        else:
            pattern, value = items
            guard = None
        guard = self._combine_constraints_with_guard(pattern, guard)
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
        # TODO(NOMI-SUBSTRATE-031): Emit a MatchExpr surface node here and keep
        # the IIFE as a backend lowering choice, so return/scope and
        # pattern/guard/constraint failures can be explained with source spans.
        # Marker for first implementation slice:
        #   - keep case_expr() producing ast.match_case for now;
        #   - create a passive MatchExpr(subject, cases) surface shape here;
        #   - move the IIFE wrapper below into MatchExpr.lower();
        #   - add a surface-ast inspection test before changing match failure
        #     or expression-value semantics.
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
