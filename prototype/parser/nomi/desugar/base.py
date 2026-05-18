import ast
import enum

from ....interpreter.constants import Block


class Phase(enum.Enum):
    """Desugar phases, guaranteed to run in this order.

    ``syntax``: pure AST form replacement — no new control flow, no
        new scopes, no semantic change.
    ``semantic``: introduces new control flow, scopes, IIFEs, raises,
        or execution-order changes.
    ``cleanup``: post-processing that does not change semantics
        (fix locations, validate invariants, remove temporary markers).
    """

    syntax = "syntax"
    semantic = "semantic"
    cleanup = "cleanup"


class BaseDesugarer(ast.NodeTransformer):
    """Base class for desugar passes. Extends ast.NodeTransformer.

    Subclasses should declare:
    - ``phase``: the Phase this pass runs in (default: syntax).
    - ``depends_on``: tuple of BaseDesugarer subclasses that must run
      before this pass.
    - ``input_node_types``: tuple of AST node types this pass expects to
      consume or inspect.
    - ``removed_node_types``: tuple of AST node types that become
      unreachable after this pass.
    - ``produced_node_types``: tuple of AST node types this pass may synthesize
      as its lowered representation.
    - ``normal_forms``: tuple of Nomi normal-form names produced by the pass.
    """

    phase: Phase = Phase.syntax
    depends_on: tuple = ()
    input_node_types: tuple = ()
    removed_node_types: tuple = ()
    produced_node_types: tuple = ()
    normal_forms: tuple[str, ...] = ()

    def generic_visit(self, node):
        node = super().generic_visit(node)
        where_body = getattr(node, '_nomi_where_body', None)
        if where_body is not None:
            node._nomi_where_body = self._visit_statement_list(where_body)
        return node

    def _visit_statement_list(self, statements):
        visited = []
        for stmt in statements:
            transformed = self.visit(stmt)
            if transformed is None:
                continue
            if isinstance(transformed, list):
                visited.extend(transformed)
            else:
                visited.append(transformed)
        return visited


class NomiDesugarer(BaseDesugarer):
    """Desugarer base that handles Nomi-specific AST features.

    Nomi stores block-call bodies inside ast.keyword.value as ``Block``
    instances.  Standard ast.NodeTransformer does not recurse into
    non-AST objects, so we override visit_keyword to handle them.
    """

    def visit_keyword(self, node):
        self.generic_visit(node)
        if isinstance(node.value, Block):
            # TODO(NOMI-SUBSTRATE-010): Defer BlockCall→Python-AST lowering
            # until after desugar passes run, so desugar passes can work with
            # the clean BlockCall surface node instead of this Block-in-keyword
            # hack. BlockCall already exists; the remaining work is reordering
            # the pipeline to run desugar before lower_surface_to_python.
            node.value.body = [self.visit(stmt) for stmt in node.value.body]
            if isinstance(node.value.params, ast.AST):
                node.value.params = self.visit(node.value.params)
        return node
