import ast

from .base import NomiDesugarer, Phase


class With(NomiDesugarer):
    phase = Phase.semantic
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

    input_node_types = (ast.With,)
    removed_node_types = (ast.With,)
    produced_node_types = (
        ast.Assign,
        ast.Try,
        ast.ExceptHandler,
        ast.If,
        ast.Raise,
        ast.Call,
    )
    normal_forms = ("try-finally-resource-protocol",)

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
