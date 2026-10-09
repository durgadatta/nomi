"""JavaScript Core Runtime backend wrapper.

This backend keeps the runtime implementation in ``prototype/runtime/js/core_runtime.js`` and
uses the backend-neutral Core IR JSON payload as the process boundary.  It is a
first-class eval backend for tests and opt-in execution, while the JavaScript
runtime remains the browser implementation target.
"""

from __future__ import annotations

import math
import re
import shutil
from pathlib import Path

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendExecutionError,
    EvalBackendProtocolError,
    EvalBackendResult,
    EvalBackendSpec,
    register_backend,
)
from prototype.runtime.backends.json_process import run_json_process
from prototype.runtime.diagnostics import Diagnostic
from prototype.syntax.core import Module, verify_core
from prototype.syntax.core_json import core_to_json


ROOT = Path(__file__).resolve().parents[3]
JS_RUNTIME_PATH = ROOT / "prototype" / "runtime" / "js" / "core_runtime.js"
EVAL_RESULT_SCHEMA = "nomi.eval-result"
EVAL_RESULT_VERSION = 1
_RESULT_FIELDS = {
    "schema", "version", "ok", "backend", "bindings", "value", "has_value",
    "diagnostics", "stdout", "stderr",
}
_DIAGNOSTIC_FIELDS = {
    "phase", "severity", "message", "code", "span", "source_excerpt",
    "node_type", "capability", "frontend", "backend", "details",
}


def _protocol_error(reason: str) -> EvalBackendProtocolError:
    return EvalBackendProtocolError(f"js-core-runtime returned invalid result: {reason}")


def _validate_json_value(value) -> None:
    pending = [value]
    while pending:
        item = pending.pop()
        if item is None or isinstance(item, (str, bool, int)):
            continue
        if isinstance(item, float) and math.isfinite(item):
            continue
        if isinstance(item, list):
            pending.extend(item)
            continue
        if isinstance(item, dict) and all(isinstance(key, str) for key in item):
            pending.extend(item.values())
            continue
        raise _protocol_error("value is not finite JSON data")


def _decode_result(payload: dict) -> EvalBackendResult:
    if not isinstance(payload, dict) or set(payload) != _RESULT_FIELDS:
        raise _protocol_error("missing or unknown envelope fields")
    if (
        payload["schema"] != EVAL_RESULT_SCHEMA
        or type(payload["version"]) is not int
        or payload["version"] != EVAL_RESULT_VERSION
    ):
        raise _protocol_error("unsupported schema or version")
    if payload["backend"] != "js-core-runtime":
        raise _protocol_error("wrong backend identity")
    if type(payload["ok"]) is not bool or type(payload["has_value"]) is not bool:
        raise _protocol_error("ok and has_value must be Bool")
    if (
        not isinstance(payload["bindings"], dict)
        or not isinstance(payload["diagnostics"], list)
    ):
        raise _protocol_error("bindings and diagnostics have invalid shapes")
    if not all(isinstance(payload[name], str) for name in ("stdout", "stderr")):
        raise _protocol_error("stdout and stderr must be Text")
    _validate_json_value(payload["bindings"])
    _validate_json_value(payload["value"])
    if not payload["has_value"] and payload["value"] is not None:
        raise _protocol_error("an absent result cannot carry a value")
    if payload["ok"]:
        if payload["diagnostics"]:
            raise _protocol_error("successful evaluation cannot carry failure diagnostics")
        return EvalBackendResult(
            bindings=payload["bindings"],
            value=payload["value"],
            has_value=payload["has_value"],
            stdout=payload["stdout"],
            stderr=payload["stderr"],
        )
    if payload["bindings"] or payload["has_value"] or len(payload["diagnostics"]) != 1:
        raise _protocol_error("failure must carry one diagnostic and no result")
    record = payload["diagnostics"][0]
    if not isinstance(record, dict) or set(record) != _DIAGNOSTIC_FIELDS:
        raise _protocol_error("missing or unknown diagnostic fields")
    if (
        record["phase"] != "eval"
        or record["severity"] != "error"
        or record["backend"] != "js-core-runtime"
        or record["capability"] != "js-core-runtime.eval"
    ):
        raise _protocol_error("invalid diagnostic phase, severity or owner")
    if not isinstance(record["message"], str) or not record["message"]:
        raise _protocol_error("diagnostic message must be nonempty Text")
    if (
        not isinstance(record["code"], str)
        or re.fullmatch(r"NOMI-[A-Z0-9-]+", record["code"]) is None
    ):
        raise _protocol_error("invalid diagnostic code")
    if not isinstance(record["node_type"], str) or not record["node_type"]:
        raise _protocol_error("invalid exception type")
    if record["details"] != {"exception_type": record["node_type"]}:
        raise _protocol_error("invalid exception details")
    if any(record[name] is not None for name in ("span", "source_excerpt", "frontend")):
        raise _protocol_error("this producer cannot supply source positions or a frontend")
    raise EvalBackendExecutionError(
        Diagnostic(**record), stdout=payload["stdout"], stderr=payload["stderr"]
    )


JS_CORE_BACKEND_SPEC = EvalBackendSpec(
    name="js-core-runtime",
    status="prototype",
    ir_contract="Core IR JSON (nomi.core-ir v1)",
    implementation="Node.js wrapper around prototype/runtime/js/core_runtime.js",
    output_contract="nomi.eval-result v1: success or typed failure + stdout/stderr",
    capabilities=EvalBackendCapabilities(
        evaluates_native_ir=True,
        supports_full_language=False,
        supports_blocks=True,
        supports_exceptions=True,
        supports_resume=False,
        supports_python_interop=False,
        selectable_for_browser_execution=True,
        default_for_web=True,
        requires_host_capabilities=("nomi.host-capabilities",),
        selectable_for_execution=False,
    ),
    notes=(
        "first non-Python runtime backend",
        "Node wrapper consumes session-lowered Core IR; browser default uses Rust/WASM parsing plus JS lowering",
        "dispatches every currently registered CoreNode in JavaScript",
        "integers limited to +/-9007199254740991; unsupported literals fail before execution, overflow fails at the operation",
        "finite floats only; this prototype boundary does not define the target numeric tower",
        "arithmetic dispatch checks tagged operands before host evaluation; mixed text/numeric coercion is refused",
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
        try:
            payload = run_json_process(
                command,
                core_to_json(core_ir),
                cwd=ROOT,
                label="js-core-runtime",
                reject_duplicate_keys=True,
            )
        except RuntimeError as error:
            raise EvalBackendProtocolError(str(error)) from error
        return _decode_result(payload)

    def _node(self) -> str:
        node = self._node_executable or shutil.which("node")
        if node is None:
            raise EvalBackendProtocolError(
                "js-core-runtime requires Node.js on PATH"
            )
        return node


register_backend("js-core-runtime", JsCoreRuntimeBackend())
