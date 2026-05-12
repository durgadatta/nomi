import ast

from ....interpreter.constants import Block


class BaseDesugarer(ast.NodeTransformer):
    """Base class for desugar passes. Extends ast.NodeTransformer.

    Subclasses should declare ``removed_node_types`` as a tuple of AST
    node types that become unreachable after this pass.  The reduced
    interpreter reads this metadata to auto-generate its
    NotImplementedError guards.
    """

    removed_node_types: tuple = ()


class NomiDesugarer(BaseDesugarer):
    """Desugarer base that handles Nomi-specific AST features.

    Nomi stores block-call bodies inside ast.keyword.value as ``Block``
    instances.  Standard ast.NodeTransformer does not recurse into
    non-AST objects, so we override visit_keyword to handle them.
    """

    def visit_keyword(self, node):
        self.generic_visit(node)
        if isinstance(node.value, Block):
            node.value.body = [self.visit(stmt) for stmt in node.value.body]
            if isinstance(node.value.params, ast.AST):
                node.value.params = self.visit(node.value.params)
        return node
