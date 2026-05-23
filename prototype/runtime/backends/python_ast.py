"""Python AST eval backend — wraps the existing interpreter behind Core IR.

This is the adapter: Core IR -> Python AST -> existing interpreter.eval().
The interpreter itself is unchanged; this backend is just the boundary layer.
"""

from __future__ import annotations

import ast as py_ast
from typing import Any

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendResult,
    EvalBackendSpec,
    register_backend,
)
from prototype.syntax.core import core_to_python_ast, verify_core

PYTHON_AST_BACKEND_SPEC = EvalBackendSpec(
    name="python-ast",
    status="implemented",
    ir_contract="Core IR (L1 nodes)",
    implementation="Python AST interpreter with eval_* dispatch",
    output_contract="dict of global bindings + optional last-expression value",
    capabilities=EvalBackendCapabilities(
        lowers_to_python_ast=True,
        supports_full_language=True,
        supports_blocks=True,
        supports_exceptions=True,
        supports_resume=True,
        supports_python_interop=True,
        selectable_for_execution=True,
    ),
    notes=(
        "current default",
        "bootstrap path",
        "wraps existing interpreter unchanged",
    ),
)


class PythonAstBackend:
    """Eval backend that lowers Core IR to Python AST and runs the interpreter."""

    spec = PYTHON_AST_BACKEND_SPEC

    def __init__(self, interpreter_cls, *, desugar=None):
        self._interpreter_cls = interpreter_cls
        self._desugar = desugar

    def evaluate(
        self, core_ir, *, display_last_expr: bool = False
    ) -> EvalBackendResult:
        """Evaluate verified Core IR through the Python AST interpreter."""
        verify_core(core_ir, strict=True)
        tree = core_to_python_ast(core_ir)
        tree = py_ast.fix_missing_locations(tree)
        if self._desugar is not None:
            tree = self._desugar(tree)
        interpreter = self._interpreter_cls()
        result = interpreter.eval(tree)
        has_value = display_last_expr and result is not None
        return EvalBackendResult(
            bindings=dict(interpreter.global_env.bindings),
            value=result,
            has_value=has_value,
        )

    def render_lowered(self, core_ir) -> str:
        """Show the Python AST this backend would evaluate."""
        verify_core(core_ir, strict=True)
        tree = core_to_python_ast(core_ir)
        tree = py_ast.fix_missing_locations(tree)
        return py_ast.dump(tree, include_attributes=False, indent=2)


def make_python_ast_backend_for_mode(mode_spec) -> PythonAstBackend:
    """Construct a PythonAstBackend from a ModeSpec's interpreter and desugar."""
    interpreter_cls = mode_spec.load_interpreter_class()
    desugar = mode_spec.load_session_lowerer()
    return PythonAstBackend(interpreter_cls, desugar=desugar)


class ModeConstructedPythonAstBackend:
    """Registry placeholder for the mode-constructed Python AST backend."""

    spec = PYTHON_AST_BACKEND_SPEC

    def evaluate(self, *args, **kwargs):
        raise RuntimeError(
            "python-ast backends are constructed from a RuntimeSession mode; "
            "use make_python_ast_backend_for_mode(mode_spec)"
        )


# Register the backend name and capabilities for inspection/validation.
register_backend("python-ast", ModeConstructedPythonAstBackend())
