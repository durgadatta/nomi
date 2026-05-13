"""Dollar hole references: ``$1``, ``$name`` → lambda parameters.

Two families of hole, distinguished by what follows the ``$``:

**Positional ``$N``** (Swift-style) — ``$1`` refers to the first parameter,
``$2`` the second.  Parameter names are auto-generated: ``__1``, ``__2``.

**Named ``$name``** — the identifier after ``$`` *is* the parameter name.
``$x + $y`` produces ``(x, y) => x + y``.  Duplicate references to the
same name map to a single parameter.

The whole containing expression is wrapped into an anonymous function.

Examples::

    $1 * 2              →  (__1) => __1 * 2
    $1 + $2             →  (__1, __2) => __1 + __2
    $x + $y             →  (x, y) => x + y
    $x + $x             →  (x) => x + x          (duplicates merged)
    $1 + $x             →  (__1, x) => __1 + x    (mixed)
    list.map($x.name)   →  list.map((x) => x.name)
"""

import ast
import re

from .base import BaseDesugarer

_DOLLAR_POS_RE = re.compile(r'^\$(\d+)$')
_DOLLAR_NAME_RE = re.compile(r'^\$[^0-9\W]\w*$')


class PositionalHole(BaseDesugarer):
    """Replace ``$N`` and ``$name`` holes with anonymous functions."""

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
    def _is_dollar_hole(node):
        return (
            isinstance(node, ast.Name)
            and node.id.startswith('$')
            and len(node.id) > 1
            and isinstance(node.ctx, ast.Load)
        )

    @classmethod
    def _contains_dollar_hole(cls, node):
        if cls._is_dollar_hole(node):
            return True
        for child in ast.iter_child_nodes(node):
            if cls._contains_dollar_hole(child):
                return True
        return False

    # ── statement-level entry points ────────────────────────────────

    def visit_Assign(self, node):
        node.value = self._wrap_if_dollar(node.value)
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if node.value:
            node.value = self._wrap_if_dollar(node.value)
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        node.value = self._wrap_if_dollar(node.value)
        self.generic_visit(node)
        return node

    def visit_Return(self, node):
        if node.value:
            node.value = self._wrap_if_dollar(node.value)
        self.generic_visit(node)
        return node

    def visit_AugAssign(self, node):
        node.value = self._wrap_if_dollar(node.value)
        self.generic_visit(node)
        return node

    def visit_If(self, node):
        node.test = self._wrap_if_dollar(node.test)
        self.generic_visit(node)
        return node

    def visit_IfExp(self, node):
        node.test = self._wrap_if_dollar(node.test)
        node.body = self._wrap_if_dollar(node.body)
        node.orelse = self._wrap_if_dollar(node.orelse)
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        for i, arg in enumerate(node.args):
            node.args[i] = self._wrap_if_dollar(arg)
        return node

    def visit_BinOp(self, node):
        node.left = self._wrap_if_dollar(node.left)
        node.right = self._wrap_if_dollar(node.right)
        return node

    def visit_Compare(self, node):
        node.left = self._wrap_if_dollar(node.left)
        for i, comp in enumerate(node.comparators):
            node.comparators[i] = self._wrap_if_dollar(comp)
        return node

    def visit_UnaryOp(self, node):
        node.operand = self._wrap_if_dollar(node.operand)
        return node

    # ── helpers ────────────────────────────────────────────────────

    def _wrap_if_dollar(self, node):
        if not isinstance(node, ast.AST):
            return node
        if not self._contains_dollar_hole(node):
            return node
        named, positions, renamed = self._collect(node)
        param_names = self._build_param_list(named, positions)
        return self._make_lambda(renamed, param_names)

    def _collect(self, node):
        """Collect named and positional hole references, return renamed tree."""
        named = {}
        positions = set()
        renamed = self._rename_holes(node, named, positions)
        return named, positions, renamed

    def _build_param_list(self, named, positions):
        """Build ordered parameter list: named params first, then positional."""
        params = list(named.keys())
        if positions:
            max_idx = max(positions)
            for i in range(1, max_idx + 1):
                params.append(f'__{i}')
        return params

    def _rename_holes(self, node, named, positions):
        if self._is_dollar_hole(node):
            hole_id = node.id
            m = _DOLLAR_POS_RE.match(hole_id)
            if m:
                num = int(m.group(1))
                positions.add(num)
                return ast.Name(id=f'__{num}', ctx=ast.Load())
            else:
                name = hole_id[1:]
                if name not in named:
                    named[name] = len(named)
                return ast.Name(id=name, ctx=ast.Load())

        if isinstance(node, ast.AST):
            fields = {}
            for field, old_val in ast.iter_fields(node):
                if isinstance(old_val, list):
                    new_vals = []
                    for v in old_val:
                        if isinstance(v, ast.AST):
                            new_vals.append(self._rename_holes(v, named, positions))
                        else:
                            new_vals.append(v)
                    fields[field] = new_vals
                elif isinstance(old_val, ast.AST):
                    fields[field] = self._rename_holes(old_val, named, positions)
                else:
                    fields[field] = old_val
            new_node = type(node)(**fields)
            return ast.copy_location(new_node, node)
        return node
