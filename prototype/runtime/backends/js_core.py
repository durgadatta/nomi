"""JavaScript Core Runtime backend wrapper.

This backend keeps the runtime implementation in ``prototype/runtime/js/core_runtime.js`` and
uses the backend-neutral Core IR JSON payload as the process boundary.  It is a
first-class eval backend for tests and opt-in execution, while the JavaScript
runtime remains the browser implementation target.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendResult,
    EvalBackendSpec,
    register_backend,
)
from prototype.syntax.core import Module, verify_core
from prototype.syntax.core_json import core_to_json


ROOT = Path(__file__).resolve().parents[3]
JS_RUNTIME_PATH = ROOT / "prototype" / "runtime" / "js" / "core_runtime.js"


JS_CORE_BACKEND_SPEC = EvalBackendSpec(
    name="js-core-runtime",
    status="prototype",
    ir_contract="Core IR JSON (nomi.core-ir v1)",
    implementation="Node.js wrapper around prototype/runtime/js/core_runtime.js",
    output_contract="bindings + optional value + stdout/stderr",
    capabilities=EvalBackendCapabilities(
        evaluates_native_ir=True,
        supports_full_language=False,
        supports_blocks=True,
        supports_exceptions=True,
        supports_resume=False,
        supports_python_interop=False,
        selectable_for_execution=False,
    ),
    notes=(
        "first non-Python runtime backend",
        "Node wrapper consumes session-lowered Core IR; browser default uses Rust/WASM parsing plus JS lowering",
        "dispatches every currently registered CoreNode in JavaScript",
    ),
)


class JsCoreRuntimeBackend:
    """Evaluate serialized Core IR through the JavaScript runtime."""

    spec = JS_CORE_BACKEND_SPEC

    def __init__(
        self,
        *,
        node_executable: str | None = None,
        runtime_path: Path = JS_RUNTIME_PATH,
    ) -> None:
        self._node_executable = node_executable
        self._runtime_path = runtime_path

    def fork(self) -> "JsCoreRuntimeBackend":
        return JsCoreRuntimeBackend(
            node_executable=self._node_executable,
            runtime_path=self._runtime_path,
        )

    def evaluate(
        self, core_ir: Module, *, display_last_expr: bool = False
    ) -> EvalBackendResult:
        verify_core(core_ir, strict=True)
        command = [self._node(), str(self._runtime_path)]
        if display_last_expr:
            command.append("--display-last-expr")
        completed = subprocess.run(
            command,
            input=core_to_json(core_ir),
            text=True,
            capture_output=True,
            cwd=ROOT,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(
                "js-core-runtime failed"
                + (f": {detail}" if detail else "")
            )
        payload = json.loads(completed.stdout)
        return EvalBackendResult(
            bindings=dict(payload.get("bindings", {})),
            value=payload.get("value"),
            has_value=bool(payload.get("has_value")),
            diagnostics=tuple(payload.get("diagnostics", ())),
            stdout=str(payload.get("stdout", "")),
            stderr=str(payload.get("stderr", "")),
        )

    def _node(self) -> str:
        node = self._node_executable or shutil.which("node")
        if node is None:
            raise RuntimeError(
                "js-core-runtime requires Node.js on PATH"
            )
        return node


register_backend("js-core-runtime", JsCoreRuntimeBackend())
