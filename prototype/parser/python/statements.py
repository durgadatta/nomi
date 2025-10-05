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
        if len(items) >= 2:
            target = items[0]; value = items[-1]
            if isinstance(target, ast.Name): target = storeify(target)
            return ast.Assign(targets=[target], value=ensure_expr(value))
        return ast.Pass()

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