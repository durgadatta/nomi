import ast
from lark import Token

from prototype.parser.python import ensure_expr, ensure_name, storeify

class StatementMixin():
    def suite(self, items):
        out = []
        for it in items:
            if isinstance(it, list): out.extend(it)
            elif isinstance(it, ast.stmt): out.append(it)
        return out

    def simple_stmt(self, items):
        out = []
        for it in items:
            if isinstance(it, list): out.extend(it)
            elif isinstance(it, ast.stmt): out.append(it)
        return out

    def expr_stmt(self, items):
        # detect simple assignment left '=' right
        for i, it in enumerate(items):
            if isinstance(it, Token) and it.value == '=':
                left = items[0]; right = items[i+1] if i+1 < len(items) else None
                target = storeify(left) if isinstance(left, (ast.Name, ast.Tuple, ast.List)) else left
                return ast.Assign(targets=[target], value=ensure_expr(right))
        return ast.Expr(value=ensure_expr(items[0]))

    def assign(self, items):
        """
        Build a full Python AST Assign node with correct semantics.

        Parameters:
        - items: [lhs_nodes..., rhs_node]
            lhs_nodes: single AST node or list/nested lists of AST nodes (targets)
            rhs_node: AST expression node (already fully built by transformer)
        """

        lhs_nodes = items[:-1]
        rhs_node = items[-1]

        # --- Helper: recursively set Store() context for LHS ---
        def ensure_store(node):
            if isinstance(node, ast.Name):
                return ast.Name(id=node.id, ctx=ast.Store())
            elif isinstance(node, ast.Attribute):
                return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Store())
            elif isinstance(node, ast.Subscript):
                return ast.Subscript(value=node.value, slice=node.slice, ctx=ast.Store())
            elif isinstance(node, ast.Starred):
                # Python allows starred expressions in assignment: *a, b = ...
                return ast.Starred(value=node.value, ctx=ast.Store())
            elif isinstance(node, ast.Tuple):
                return ast.Tuple(elts=[ensure_store(e) for e in node.elts], ctx=ast.Store())
            elif isinstance(node, list):
                # Lark transformer may return a list for comma-separated targets
                return ast.Tuple(elts=[ensure_store(e) for e in node], ctx=ast.Store())
            else:
                return node  # unknown node types, leave as-is

        lhs_nodes = [ensure_store(n) for n in lhs_nodes]

        # --- Wrap multiple top-level targets in a Tuple if needed ---
        if len(lhs_nodes) == 1:
            target_node = lhs_nodes[0]
        else:
            target_node = ast.Tuple(elts=lhs_nodes, ctx=ast.Store())

        # --- RHS: convert Python list to AST Tuple if needed ---
        def ensure_rhs(node):
            if isinstance(node, list):
                # recursively convert lists to AST Tuple nodes
                return ast.Tuple(elts=[ensure_rhs(e) for e in node], ctx=ast.Load())
            elif isinstance(node, ast.AST):
                return node  # already an AST node
            else:
                # raw constant
                return ast.Constant(value=node)

        rhs_node = ensure_rhs(rhs_node)

        # --- Build final Assign node ---
        return ast.Assign(targets=[target_node], value=rhs_node)




    def augassign(self, items):
        return ast.Pass()

    def return_stmt(self, items):
        if items: return ast.Return(value=ensure_expr(items[0]))
        return ast.Return(value=None)

    def pass_stmt(self, items): return ast.Pass()
    def break_stmt(self, items): return ast.Break()
    def continue_stmt(self, items): return ast.Continue()

    def import_as_name(self, items):
        if len(items) == 1: return ast.alias(name=ensure_name(items[0]), asname=None)
        return ast.alias(name=ensure_name(items[0]), asname=ensure_name(items[1]))

    def import_name(self, items):
        names = [it for it in items if isinstance(it, ast.alias)]
        return ast.Import(names=names)

    def classdef(self, items):
        name = None; bases = []; body = []
        for it in items:
            if isinstance(it, Token) and it.type == 'NAME': name = it.value
            elif isinstance(it, ast.expr): bases.append(it)
            elif isinstance(it, list): body = it
        if name is None: raise ValueError("classdef missing name")
        return ast.ClassDef(name=name, bases=bases, keywords=[], body=body or [], decorator_list=[])