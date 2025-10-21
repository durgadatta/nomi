import ast
from lark import Tree


class ExceptionMixin:
    """Handles try/except/else/finally statements."""

    def try_stmt(self, items):
        """
        try_stmt: "try" ":" suite except_clauses ["else" ":" suite] [finally]
                | "try" ":" suite finally   -> try_finally
        """
        def extract_suite(suite_item):
            """Extract suite from Tree wrapper if needed"""
            if isinstance(suite_item, Tree):
                return suite_item.children[0] if suite_item.children else []
            return suite_item

        # try_finally case (grammar transformation)
        if len(items) == 2:
            return ast.Try(
                body=items[0],
                handlers=[],
                orelse=[],
                finalbody=extract_suite(items[1])
            )
        else:
            # Full try/except/else/finally case

            suite, except_clauses, else_suite, finally_suite = items
            else_suite = else_suite or []
            finally_suite = finally_suite or [] 

            return ast.Try(
                body=suite,
                handlers=except_clauses,
                orelse=else_suite,
                finalbody=extract_suite(finally_suite)
            )

    def except_clauses(self, items):
        """except_clauses: except_clause+"""
        return items

    def except_clause(self, items):
        """except_clause: "except" [test ["as" name]] ":" suite"""
        if len(items) == 1:
            # Bare except: "except:"
            type_node, name_node, body = None, None, items[0]
        elif len(items) == 2:
            if isinstance(items[1], str):
                # "except TypeError as e:"
                type_node, name_node, body = items[0], items[1], []
            else:
                # "except TypeError:"
                type_node, name_node, body = items[0], None, items[1]
        elif len(items) == 3:
            # "except TypeError as e: suite"
            type_node, name_node, body = items[0], items[1], items[2]
        else:
            raise ValueError(f"Unexpected except_clause structure: {items}")

        return ast.ExceptHandler(
            type=type_node if type_node else None,
            name=name_node,
            body=body if isinstance(body, list) else [body]
        )

    def try_finally(self, items):
        """try ... finally (grammar transformation)"""
        def extract_suite(suite_item):
            if isinstance(suite_item, Tree):
                return suite_item.children[0] if suite_item.children else []
            return suite_item

        return ast.Try(
            body=items[0],
            handlers=[],
            orelse=[],
            finalbody=extract_suite(items[1])
        )