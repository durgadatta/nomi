import ast
from typing import Any

class ExpressionMixin:
    BINARY_OPERATORS = {
        ast.Add: lambda l, r: l + r,
        ast.Sub: lambda l, r: l - r,
        ast.Mult: lambda l, r: l * r,
        ast.Div: lambda l, r: l / r,
        ast.FloorDiv: lambda l, r: l // r,
        ast.Mod: lambda l, r: l % r,
        ast.Pow: lambda l, r: l ** r,
        ast.LShift: lambda l, r: l << r,
        ast.RShift: lambda l, r: l >> r,
        ast.BitOr: lambda l, r: l | r,
        ast.BitXor: lambda l, r: l ^ r,
        ast.BitAnd: lambda l, r: l & r,
        ast.MatMult: lambda l, r: l @ r,
    }

    UNARY_OPERATORS = {
        ast.Invert: lambda o: ~o,
        ast.Not: lambda o: not o,
        ast.UAdd: lambda o: +o,
        ast.USub: lambda o: -o,
    }

    _EVAL_TARGET_DISPATCH = {
        ast.Name: '_eval_target_name',
        ast.Attribute: '_eval_target_attr',
        ast.Subscript: '_eval_target_subscript',
    }

    def eval_target(self, node: ast.expr) -> Any:
        handler = self._EVAL_TARGET_DISPATCH.get(type(node))
        if handler:
            return getattr(self, handler)(node)
        raise NotImplementedError(
            f"Target evaluation {node.__class__.__name__} not supported "
            f"at line {self.get_lineno(node)}"
        )

    def _eval_target_name(self, node):
        return self.current_env.get(node.id)

    def _eval_target_attr(self, node):
        return getattr(self.eval(node.value), node.attr)

    def _eval_target_subscript(self, node):
        return self.eval(node.value)[self.eval(node.slice)]

    def eval_Global(self, node: ast.Global) -> None:
        self.current_env.declared_globals.update(node.names)

    def eval_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.current_env.declared_nonlocals.update(node.names)

    def eval_Expr(self, node: ast.Expr) -> Any:
        return self.eval(node.value)

    def eval_BoolOp(self, node: ast.BoolOp) -> bool:
        value = self.eval(node.values[0])
        if isinstance(node.op, ast.And):
            for v in node.values[1:]:
                value = value and self.eval(v)
                if not value:
                    break
        elif isinstance(node.op, ast.Or):
            for v in node.values[1:]:
                value = value or self.eval(v)
                if value:
                    break
        return value

    def eval_NamedExpr(self, node: ast.NamedExpr) -> Any:
        value = self.eval(node.value)
        self.assign_target(node.target, value)
        return value

    def eval_BinOp(self, node: ast.BinOp) -> Any:
        left = self.eval(node.left)
        right = self.eval(node.right)
        return self.apply_operator(left, node.op, right, node)

    def apply_operator(self, left, op, right, node=None):
        """Apply binary operator with proper error handling."""
        try:
            operator = self.BINARY_OPERATORS.get(type(op))
            if operator:
                return operator(left, right)
            else:
                raise TypeError(f"Unsupported operator {type(op).__name__}")
        except Exception as e:
            # Don't wrap common Python exceptions
            if isinstance(e, (ZeroDivisionError, TypeError, ValueError, AttributeError)):
                # Re-raise built-in exceptions as-is so they can be caught by try/except
                raise
            else:
                # Only wrap truly unexpected exceptions
                lineno = self.get_lineno(node) if node else "unknown"
                raise TypeError(f"Unsupported operand types for {type(op).__name__}: '{type(left).__name__}' and '{type(right).__name__}' at line {lineno}") from e
        
    def eval_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.eval(node.operand)
        func = self.UNARY_OPERATORS.get(type(node.op))
        if func is None:
            raise NotImplementedError(f"Unary operator {type(node.op).__name__} not supported at line {self.get_lineno(node)}")
        try:
            return func(operand)
        except Exception as e:
            raise TypeError(f"Unsupported operand type for {type(node.op).__name__}: '{type(operand).__name__}' at line {self.get_lineno(node)}") from e



    def eval_IfExp(self, node: ast.IfExp) -> Any:
        return self.eval(node.body) if self.eval(node.test) else self.eval(node.orelse)

    def eval_Starred(self, node: ast.Starred) -> Any:
        return self.eval(node.value)

    def eval_Name(self, node: ast.Name) -> Any:
        try:
            if isinstance(node.ctx, ast.Load):
                return self.current_env.get(node.id)
            elif isinstance(node.ctx, ast.Store):
                # This should return the name for assignment, but your assignment logic
                # should handle the actual storage
                return node.id
            elif isinstance(node.ctx, ast.Del):
                self.current_env.delete(node.id)
                return None
        except NameError:
            raise NameError(f"name '{node.id}' is not defined at line {self.get_lineno(node)}")
        
    def eval_Compare(self, node: ast.Compare) -> bool:
        left = self.eval(node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = self.eval(comp)
            if not self.apply_cmp_operator(left, op, right):
                return False
            left = right
        return True
    
