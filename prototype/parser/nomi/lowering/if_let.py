"""If-let, while-let, and guard statements lowered to ``match``."""

import ast


class IfLetMixin:
    def if_let_stmt(self, items):
        """if_let_stmt: 'if' pattern '=' test ':' suite ['else' ':' suite]"""
        if len(items) == 4:
            pattern, expr, body, else_body = items
        else:
            pattern, expr, body = items
            else_body = []

        match_case = ast.match_case(pattern=pattern, body=body)
        wildcard = ast.match_case(
            pattern=ast.MatchAs(pattern=None),
            body=else_body if else_body else [],
        )
        return ast.Match(subject=expr, cases=[match_case, wildcard])

    def while_let_stmt(self, items):
        """while_let_stmt: 'while' pattern '=' test ':' suite"""
        pattern, expr, body = items
        match_case = ast.match_case(pattern=pattern, guard=None, body=body)
        wildcard = ast.match_case(
            pattern=ast.MatchAs(pattern=None),
            guard=None,
            body=[ast.Break()],
        )
        return ast.While(
            test=ast.Constant(value=True),
            body=[ast.Match(subject=expr, cases=[match_case, wildcard])],
            orelse=[],
        )

    def guard_stmt(self, items):
        """guard_stmt: 'guard' pattern '=' test ':' suite"""
        pattern, expr, failure_body = items
        match_case = ast.match_case(
            pattern=pattern, guard=None, body=[ast.Pass()],
        )
        wildcard = ast.match_case(
            pattern=ast.MatchAs(pattern=None),
            guard=None,
            body=failure_body,
        )
        return ast.Match(subject=expr, cases=[match_case, wildcard])
