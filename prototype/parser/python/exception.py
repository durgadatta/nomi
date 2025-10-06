import ast

class ExceptionMixin:
    """Handles try/except/else/finally statements."""

    def except_clause(self, items):
        """
        items: [type?, name?, suite]
        returns ast.ExceptHandler
        """
        exc_type = exc_name = None
        body = []

        # Determine positions
        if len(items) == 1:
            # Only suite
            body = self.ensure_stmt_list(items[0])
        elif len(items) == 2:
            # type or suite + name?
            if isinstance(items[0], ast.expr):
                exc_type = items[0]
            elif isinstance(items[0], str):
                exc_name = items[0]
            body = self.ensure_stmt_list(items[1])
        elif len(items) == 3:
            exc_type = items[0]
            exc_name = items[1]
            body = self.ensure_stmt_list(items[2])

        return ast.ExceptHandler(type=exc_type, name=exc_name, body=body)

    def try_stmt(self, items):
        """
        items: [try_suite, except_handlers, else_suite?, finally_suite?]
        returns ast.Try
        """
        try_suite = self.ensure_stmt_list(items[0])

        # Ensure handlers is always a list
        handlers = items[1]
        if isinstance(handlers, ast.ExceptHandler):
            handlers = [handlers]  # wrap single handler into list

        # Optional else and finally
        else_suite = self.ensure_stmt_list(items[2]) if len(items) > 2 else []
        finally_suite = self.ensure_stmt_list(items[3]) if len(items) > 3 else []

        return ast.Try(
            body=try_suite,
            handlers=handlers,
            orelse=else_suite,
            finalbody=finally_suite,
        )

    def try_finally(self, items):
        """
        try ... finally
        items: [try_suite, finally_suite]
        """
        try_suite = self.ensure_stmt_list(items[0])
        finally_suite = self.ensure_stmt_list(items[1])
        return ast.Try(
            body=try_suite,
            handlers=[],       # no except
            orelse=[],         # no else
            finalbody=finally_suite
        )

    def ensure_stmt_list(self, node):
        #TODO: this is a general thing; consolidate this clean-up 
        """Normalize suite to a list of statements."""
        if node is None:
            return []
        if isinstance(node, list):
            return node
        return [node]
