import ast


class BaseDesugarer(ast.NodeTransformer):
    """Base class for desugar passes. Extends ast.NodeTransformer."""
    pass


class NomiDesugarer(BaseDesugarer):
    """Desugarer base that handles Nomi-specific AST features.

    Nomi stores block-call bodies as tuples inside ast.keyword.value.
    Standard ast.NodeTransformer does not recurse into tuples, so
    we override visit_keyword to handle them.
    """

    def visit_keyword(self, node):
        self.generic_visit(node)
        if isinstance(node.value, tuple):
            node.value = tuple(self._visit_tuple_item(v) for v in node.value)
        return node

    def _visit_tuple_item(self, item):
        if isinstance(item, ast.AST):
            return self.visit(item)
        if isinstance(item, list):
            return [self._visit_tuple_item(v) for v in item]
        if isinstance(item, tuple):
            return tuple(self._visit_tuple_item(v) for v in item)
        return item
