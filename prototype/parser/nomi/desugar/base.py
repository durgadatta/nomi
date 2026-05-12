import ast


class BaseDesugarer(ast.NodeTransformer):
    """Common helpers for all desugar passes.

    Handles recursive visitation of AST nodes embedded in tuples
    (block bodies stored in ast.keyword.value).
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
