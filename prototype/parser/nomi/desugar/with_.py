import ast

from prototype.interpreter.constants import CONTEXT_METHODS_HELPER

from .base import NomiDesugarer, Phase


class With(NomiDesugarer):
    """Lower the hosted protocol to captured hooks and guarded try/finally.

    manager -> (enter, exit) -> acquired value -> try bind/body
    -> exceptional exit or normal/control-transfer exit, exactly once.

    The private helper binds type-level descriptors. Python suppression is a
    compatibility behavior, not the target Resource/completion contract.
    """

    phase = Phase.semantic
    input_node_types = (ast.With,)
    removed_node_types = (ast.With,)
    produced_node_types = (
        ast.Assign, ast.Try, ast.ExceptHandler, ast.If, ast.Raise, ast.Call,
    )
    normal_forms = ("try-finally-resource-protocol",)

    def __init__(self):
        self._counter = 0
        self._names = set()

    def visit_Module(self, node):
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                self._names.add(child.id)
            elif isinstance(child, ast.arg):
                self._names.add(child.arg)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self._names.add(child.name)
            elif isinstance(child, ast.ExceptHandler) and child.name:
                self._names.add(child.name)
            elif isinstance(child, ast.alias):
                self._names.add(child.asname or child.name.split('.')[0])
            elif isinstance(child, (ast.Global, ast.Nonlocal)):
                self._names.update(child.names)
            elif isinstance(child, (ast.MatchAs, ast.MatchStar)) and child.name:
                self._names.add(child.name)
            elif isinstance(child, ast.MatchMapping) and child.rest:
                self._names.add(child.rest)
        return self.generic_visit(node)

    def _fresh(self, role):
        while True:
            self._counter += 1
            name = f"_with_{role}_{self._counter}"
            if name not in self._names:
                self._names.add(name)
                return name

    def _name(self, name, *, store=False):
        return ast.Name(id=name, ctx=ast.Store() if store else ast.Load())

    def _assign(self, name, value):
        return ast.Assign(targets=[self._name(name, store=True)], value=value)

    def _call(self, name, *args):
        return ast.Call(func=self._name(name), args=list(args), keywords=[])

    def _builtin(self, name):
        node = self._name(f"__nomi_builtin_{name}__")
        node._nomi_builtin_reference = name
        return node

    def visit_With(self, node):
        node = self.generic_visit(node)
        body = list(node.body)
        for item in reversed(node.items):
            manager, enter, exit_method, value, exceptional, error = (
                self._fresh(role) for role in ('manager', 'enter', 'exit', 'value', 'exceptional', 'error')
            )
            protected = list(body)
            if item.optional_vars:
                protected.insert(0, ast.Assign(targets=[item.optional_vars], value=self._name(value)))
            triplet = (
                ast.Call(func=self._builtin('type'), args=[self._name(error)], keywords=[]), self._name(error),
                ast.Attribute(value=self._name(error), attr='__traceback__', ctx=ast.Load()),
            )
            scope = ast.Try(
                body=protected,
                handlers=[ast.ExceptHandler(
                    type=self._builtin('BaseException'), name=error,
                    body=[
                        self._assign(exceptional, ast.Constant(value=True)),
                        ast.If(
                            test=ast.UnaryOp(op=ast.Not(), operand=self._call(exit_method, *triplet)),
                            body=[ast.Raise(exc=None, cause=None)], orelse=[],
                        ),
                    ],
                )],
                orelse=[],
                finalbody=[ast.If(
                    test=ast.UnaryOp(op=ast.Not(), operand=self._name(exceptional)),
                    body=[ast.Expr(value=self._call(
                        exit_method, *(ast.Constant(value=None) for _ in range(3)),
                    ))],
                    orelse=[],
                )],
            )
            body = [
                self._assign(manager, item.context_expr),
                ast.Assign(
                    targets=[ast.Tuple(elts=[self._name(enter, store=True), self._name(exit_method, store=True)], ctx=ast.Store())],
                    value=ast.Call(func=self._builtin(CONTEXT_METHODS_HELPER), args=[self._name(manager)], keywords=[]),
                ),
                self._assign(value, self._call(enter)),
                self._assign(exceptional, ast.Constant(value=False)),
                scope,
            ]
        return body
