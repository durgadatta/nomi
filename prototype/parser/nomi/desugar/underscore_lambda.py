"""Underscore hole-filling: implicit lambdas from ``_`` placeholders.

Scala-inspired: ``_.attr``, ``_ + 1``, ``f(_)``, ``list.map(_.name)``
each expand to an arrow function where ``_`` becomes the parameter.

The scope of a hole is the **outermost** expression that contains it.
Multiple ``_`` in the same scope become parameters ``__1``, ``__2``.
"""

import ast

from .base import BaseDesugarer


class UnderscoreLambda(BaseDesugarer):
    """Replace ``_`` holes in expression position with arrow functions.

    A ``_`` in ``Load`` context is a hole **unless** ``_`` was previously
    assigned in the same scope (tracked by ``visit_Assign`` on ``_``
    targets).  This lets you use ``_`` as a throwaway variable name when
    needed, while still getting Scala-style hole-filling otherwise.
    """

    def __init__(self):
        self._underscore_is_bound = False

    def _make_lambda(self, body, param_names):
        params = [ast.arg(arg=n) for n in param_names]
        args = ast.arguments(
            posonlyargs=[], args=params, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        return ast.FunctionDef(
            name=None, args=args, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )

    @staticmethod
    def _is_hole(node):
        return (isinstance(node, ast.Name)
                and node.id == '_'
                and isinstance(node.ctx, ast.Load))

    @classmethod
    def _contains_hole(cls, node):
        if cls._is_hole(node):
            return True
        for child in ast.iter_child_nodes(node):
            if cls._contains_hole(child):
                return True
        return False

    # ── statement-level entry points (only these recurse) ──────────

    def visit_Assign(self, node):
        self._track_underscore_targets(node.targets)
        node.value = self._wrap_if_hole(node.value)
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        self._track_underscore_targets([node.target])
        if node.value:
            node.value = self._wrap_if_hole(node.value)
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        node.value = self._wrap_if_hole(node.value)
        self.generic_visit(node)
        return node

    def visit_Return(self, node):
        if node.value:
            node.value = self._wrap_if_hole(node.value)
        self.generic_visit(node)
        return node

    def visit_AugAssign(self, node):
        node.value = self._wrap_if_hole(node.value)
        self.generic_visit(node)
        return node

    def visit_For(self, node):
        self._track_underscore_targets([node.target])
        self.generic_visit(node)
        return node

    def visit_If(self, node):
        node.test = self._wrap_if_hole(node.test)
        self.generic_visit(node)
        return node

    def visit_IfExp(self, node):
        node.test = self._wrap_if_hole(node.test)
        node.body = self._wrap_if_hole(node.body)
        node.orelse = self._wrap_if_hole(node.orelse)
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        for i, arg in enumerate(node.args):
            node.args[i] = self._wrap_if_hole(arg)
        return node

    # ── no-op for match patterns (do NOT hole-fill here) ──────────

    def visit_Match(self, node):
        return node

    # ── nested statement contexts: recurse normally ────────────────

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        return node

    # ── helpers ────────────────────────────────────────────────────

    def _track_underscore_targets(self, targets):
        for t in targets:
            if isinstance(t, ast.Name) and t.id == '_':
                self._underscore_is_bound = True
            elif isinstance(t, (ast.Tuple, ast.List)):
                self._track_underscore_targets(t.elts)

    def _wrap_if_hole(self, node):
        if self._underscore_is_bound:
            return node
        if not isinstance(node, ast.AST):
            return node
        if not self._contains_hole(node):
            return node
        names, renamed = self._collect(node, [])
        return self._make_lambda(renamed, names)

    def _collect(self, node, names):
        return names, self._rename_holes(node, names)

    def _rename_holes(self, node, names):
        if self._is_hole(node):
            idx = len(names)
            names.append(f'__{idx + 1}')
            return ast.Name(id=names[-1], ctx=ast.Load())

        if isinstance(node, ast.AST):
            fields = {}
            for field, old_val in ast.iter_fields(node):
                if isinstance(old_val, list):
                    new_vals = []
                    for v in old_val:
                        if isinstance(v, ast.AST):
                            new_vals.append(self._rename_holes(v, names))
                        else:
                            new_vals.append(v)
                    fields[field] = new_vals
                elif isinstance(old_val, ast.AST):
                    fields[field] = self._rename_holes(old_val, names)
                else:
                    fields[field] = old_val
            new_node = type(node)(**fields)
            return ast.copy_location(new_node, node)
        return node
