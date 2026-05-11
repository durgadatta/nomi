"""
AST desugaring passes.

Each pass transforms a Python AST by replacing compound syntactic
forms with equivalent compositions of simpler primitives. The reduced
interpreter uses these passes so it only needs to implement the
primitive forms.
"""

import ast


class _BaseDesugarer(ast.NodeTransformer):
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


class _AugAssignDesugarer(_BaseDesugarer):
    """x += y  →  x = x + y"""

    def _to_load(self, node):
        if isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Load())
        if isinstance(node, ast.Attribute):
            return ast.Attribute(
                value=self._to_load(node.value),
                attr=node.attr,
                ctx=ast.Load(),
            )
        if isinstance(node, ast.Subscript):
            return ast.Subscript(
                value=node.value,
                slice=node.slice,
                ctx=ast.Load(),
            )
        return node

    def visit_AugAssign(self, node):
        read_target = self._to_load(node.target)
        new_value = ast.BinOp(
            left=read_target,
            op=node.op,
            right=node.value,
        )
        new_node = ast.Assign(
            targets=[node.target],
            value=new_value,
        )
        return ast.copy_location(new_node, node)


class _AssertDesugarer(_BaseDesugarer):
    """assert cond [, msg]  →  if not cond: raise AssertionError([msg])"""

    def visit_Assert(self, node):
        exc_args = [node.msg] if node.msg else []
        raise_stmt = ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='AssertionError', ctx=ast.Load()),
                args=exc_args,
                keywords=[],
            ),
            cause=None,
        )
        if_node = ast.If(
            test=ast.UnaryOp(
                op=ast.Not(),
                operand=node.test,
            ),
            body=[raise_stmt],
            orelse=[],
        )
        return ast.copy_location(if_node, node)


class _DecoratorDesugarer(_BaseDesugarer):
    """"@deco\\nfunc f(): body"  →  "func f(): body\\nf = deco(f)"

    Decorators on class definitions are desugared the same way.
    The NodeTransformer flattens returned lists into the parent body
    so multiple output statements replace a single decorated definition.
    """

    def _desugar_decorators(self, node, name):
        if not node.decorator_list:
            return node
        decorators = node.decorator_list
        node.decorator_list = []
        target = ast.Name(id=name, ctx=ast.Store())
        decorated_name = ast.Name(id=name, ctx=ast.Load())
        for deco in reversed(decorators):
            decorated_name = ast.Call(
                func=deco,
                args=[decorated_name],
                keywords=[],
            )
        assign = ast.Assign(targets=[target], value=decorated_name)
        ast.copy_location(assign, node)
        return [node, assign]

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if node.name is not None:
            return self._desugar_decorators(node, node.name)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self._desugar_decorators(node, node.name)


class _PassDesugarer(_BaseDesugarer):
    """pass  →  Expr(Constant(0))"""

    def visit_Pass(self, node):
        return ast.copy_location(
            ast.Expr(value=ast.Constant(value=0)),
            node,
        )


class _WithDesugarer(_BaseDesugarer):
    """Desugar with-statement into enter/assign/try/except/else blocks.

    with ctx as x:
        body
    →
    _mgr = ctx
    x = _mgr.__enter__()
    try: body
    except Exception as _exc:
        if not _mgr.__exit__(type(_exc), _exc, _exc.__traceback__): raise
    else:
        _mgr.__exit__(None, None, None)

    Multiple items nest outermost-first.
    """

    _counter = 0

    def _fresh_mgr(self):
        self._counter += 1
        return f"_mgr_{self._counter}"

    def _fresh_exc(self):
        self._counter += 1
        return f"_exc_{self._counter}"

    def _enter_call(self, mgr_name):
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=mgr_name, ctx=ast.Load()),
                attr="__enter__",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )

    def _exit_call(self, mgr_name, exc_type, exc_val, exc_tb):
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=mgr_name, ctx=ast.Load()),
                attr="__exit__",
                ctx=ast.Load(),
            ),
            args=[exc_type, exc_val, exc_tb],
            keywords=[],
        )

    def _build_try(self, mgr_name, exc_name, body):
        exc_ref = ast.Name(id=exc_name, ctx=ast.Load())
        return ast.Try(
            body=body,
            handlers=[ast.ExceptHandler(
                type=ast.Name(id="Exception", ctx=ast.Load()),
                name=exc_name,
                body=[ast.If(
                    test=ast.UnaryOp(
                        op=ast.Not(),
                        operand=self._exit_call(
                            mgr_name,
                            ast.Call(
                                func=ast.Name(id="type", ctx=ast.Load()),
                                args=[exc_ref],
                                keywords=[],
                            ),
                            exc_ref,
                            ast.Attribute(
                                value=exc_ref,
                                attr="__traceback__",
                                ctx=ast.Load(),
                            ),
                        ),
                    ),
                    body=[ast.Raise(exc=None, cause=None)],
                    orelse=[],
                )],
            )],
            orelse=[ast.Expr(value=self._exit_call(
                mgr_name,
                ast.Constant(value=None),
                ast.Constant(value=None),
                ast.Constant(value=None),
            ))],
            finalbody=[],
        )

    def visit_With(self, node):
        stmts = []
        inner_body = list(node.body)

        for item in reversed(node.items):
            mgr_name = self._fresh_mgr()
            exc_name = self._fresh_exc()
            try_node = self._build_try(mgr_name, exc_name, inner_body)

            item_stmts = [ast.Assign(
                targets=[ast.Name(id=mgr_name, ctx=ast.Store())],
                value=item.context_expr,
            )]
            if item.optional_vars:
                item_stmts.append(ast.Assign(
                    targets=[item.optional_vars],
                    value=self._enter_call(mgr_name),
                ))

            inner_body = item_stmts + [try_node]

        return inner_body


def desugar_module(tree: ast.Module) -> ast.Module:
    tree = _AugAssignDesugarer().visit(tree)
    tree = _AssertDesugarer().visit(tree)
    tree = _DecoratorDesugarer().visit(tree)
    tree = _PassDesugarer().visit(tree)
    tree = _WithDesugarer().visit(tree)
    ast.fix_missing_locations(tree)
    return tree
