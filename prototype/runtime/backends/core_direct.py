"""Core IR direct evaluator — dispatches on CoreNode types without Python AST.

This is a prototype backend that proves the decoupling works. It handles a
minimal subset: Literal, Load, Bind, Call, Function, Return, Branch.
"""

from __future__ import annotations

from typing import Any

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendResult,
    EvalBackendSpec,
    register_backend,
)
from prototype.syntax.core import (
    Bind,
    Branch,
    Call,
    Function,
    Literal,
    Load,
    Module,
    Return,
    verify_core,
)

CORE_DIRECT_SPEC = EvalBackendSpec(
    name="core-direct",
    status="prototype",
    ir_contract="Core IR (L1 nodes)",
    implementation="Direct dispatch on CoreNode types — no Python AST indirection",
    output_contract="dict of global bindings",
    capabilities=EvalBackendCapabilities(
        evaluates_native_ir=True,
        supports_blocks=True,
        supports_exceptions=False,
        supports_resume=False,
        selectable_for_execution=False,
    ),
    notes=(
        "minimal subset proof-of-concept",
        "Literal, Load, Bind, Call, Function, Return, Branch only",
    ),
)


class _ReturnSignal(Exception):
    """Control-flow signal to unwind a function body evaluation."""

    def __init__(self, value: Any) -> None:
        self.value = value


class CoreDirectEvaluator:
    """Evaluates Core IR directly — no Python AST roundtrip."""

    spec = CORE_DIRECT_SPEC

    def __init__(self) -> None:
        self._env: dict[str, Any] = {}

    def evaluate(self, core_ir: Module) -> EvalBackendResult:
        verify_core(core_ir, strict=True)
        self._env.clear()
        for node in core_ir.body:
            self._eval_stmt(node)
        return EvalBackendResult(bindings=dict(self._env))

    # -- statement-level dispatch ------------------------------------------

    def _eval_stmt(self, node: Any) -> None:
        if isinstance(node, Bind):
            self._env[node.name] = self._eval_expr(node.value)
        elif isinstance(node, Branch):
            self._eval_branch(node)
        else:
            self._eval_expr(node)

    def _eval_branch(self, node: Branch) -> None:
        cond = self._eval_expr(node.test)
        if cond:
            branch = node.then_body
        else:
            branch = node.else_body
        if branch is not None:
            for stmt in branch.body:
                self._eval_stmt(stmt)

    # -- expression-level dispatch ----------------------------------------

    def _eval_expr(self, node: Any) -> Any:
        if node is None:
            return None
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Load):
            return self._env.get(node.name)
        if isinstance(node, Call):
            return self._eval_call(node)
        if isinstance(node, Function):
            return self._make_callable(node)
        if isinstance(node, Return):
            raise _ReturnSignal(self._eval_expr(node.value))
        return None

    # -- call / function application --------------------------------------

    def _eval_call(self, node: Call) -> Any:
        func = self._eval_expr(node.func)
        args = [self._eval_expr(a) for a in node.args]
        if callable(func):
            return func(*args)
        return None

    def _make_callable(self, node: Function):
        params = node.params
        body = node.body

        def _closure(*args: Any) -> Any:
            saved_env = dict(self._env)
            for param, arg in zip(params, args):
                self._env[param] = arg
            try:
                if body is not None:
                    for stmt in body.body:
                        self._eval_stmt(stmt)
                return None
            except _ReturnSignal as sig:
                return sig.value
            finally:
                self._env.clear()
                self._env.update(saved_env)

        return _closure


register_backend("core-direct", CoreDirectEvaluator())
