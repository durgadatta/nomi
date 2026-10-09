"""Public JS failures retain effects; malformed transport cannot imply success."""

import copy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime import create_session, execute
from prototype.runtime.backends import (
    EvalBackendExecutionError,
    EvalBackendProtocolError,
)
from prototype.runtime.backends.js_core import JsCoreRuntimeBackend, _decode_result
from prototype.syntax.core import Module


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
NODE_REQUIRED = pytest.mark.skipif(NODE is None, reason="node is not installed")
pytestmark = pytest.mark.contract


def success_record():
    return {
        "schema": "nomi.eval-result",
        "version": 1,
        "ok": True,
        "backend": "js-core-runtime",
        "bindings": {},
        "value": None,
        "has_value": False,
        "stdout": "",
        "stderr": "",
        "diagnostics": [],
    }


def failure_record():
    record = success_record()
    record.update(
        ok=False,
        stdout="completed\n",
        stderr="warning\n",
        diagnostics=[
            {
                "phase": "eval",
                "severity": "error",
                "message": "Invalid operands",
                "code": "NOMI-OPERAND-TYPE",
                "span": None,
                "source_excerpt": None,
                "node_type": "TypeError",
                "capability": "js-core-runtime.eval",
                "frontend": None,
                "backend": "js-core-runtime",
                "details": {"exception_type": "TypeError"},
            }
        ],
    )
    return record


@NODE_REQUIRED
@pytest.mark.parametrize("use_session", [False, True])
def test_public_failure_preserves_completed_output_and_semantic_diagnostic(use_session):
    source = (
        "func observe(label, value):\n    print(label)\n    return value\n"
        "total = observe('left', 1) + observe('right', '2')\nprint('after')\n"
    )
    if use_session:
        result = create_session(eval_backend="js-core-runtime").run(
            source=source, capture_output=True, raise_on_error=False
        )
    else:
        result = execute(
            source=source, eval_backend="js-core-runtime", raise_on_error=False
        )
    assert not result.ok
    assert isinstance(result.exception, EvalBackendExecutionError)
    assert result.stdout == "left\nright\n"
    assert result.stderr == ""
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.code == "NOMI-OPERAND-TYPE"
    assert diagnostic.node_type == "TypeError"
    assert diagnostic.details == {"exception_type": "TypeError"}
    assert diagnostic.frontend == "lark-lalr"
    assert diagnostic.backend == "js-core-runtime"
    assert diagnostic.span is None and diagnostic.source_excerpt is None
    assert "Int" in diagnostic.message and "Text" in diagnostic.message
    assert "core_runtime.js" not in diagnostic.message
    assert "at CoreRuntime" not in str(result.exception)


@NODE_REQUIRED
def test_raising_preserves_typed_failure_and_completed_stdout():
    with pytest.raises(EvalBackendExecutionError) as caught:
        execute(
            source="print('before')\nprint(1 + '2')\n", eval_backend="js-core-runtime"
        )
    assert caught.value.stdout == "before\n"
    assert caught.value.stderr == ""
    assert caught.value.diagnostic.code == "NOMI-OPERAND-TYPE"


@NODE_REQUIRED
def test_cli_runtime_failure_is_a_versioned_record_without_internal_stack():
    payload = create_session().core_json(source="print('before')\nprint(1 + '2')\n")
    completed = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0 and completed.stderr == ""
    record = json.loads(completed.stdout)
    assert record["schema"] == "nomi.eval-result" and record["version"] == 1
    assert record["ok"] is False and record["stdout"] == "before\n"
    assert record["diagnostics"][0]["code"] == "NOMI-OPERAND-TYPE"
    assert "at CoreRuntime" not in completed.stdout


@NODE_REQUIRED
def test_uncaptured_failure_prints_completed_effects_once(capsys):
    result = execute(
        source="print('before')\nprint(1 + '2')\n",
        eval_backend="js-core-runtime",
        capture_output=False,
        raise_on_error=False,
    )
    assert not result.ok
    assert capsys.readouterr().out == "before\n"
    assert result.stdout == ""
    assert result.exception.stdout == "before\n"


@NODE_REQUIRED
@pytest.mark.parametrize(
    "expression, code, expected_stdout",
    [
        ("9007199254740993 + 1", "NOMI-NUMERIC-RANGE", ""),
        ("9007199254740991 + 1", "NOMI-NUMERIC-RANGE", "before\n"),
        ("1 / 0", "NOMI-RUNTIME", "before\n"),
    ],
)
def test_public_failure_distinguishes_preflight_and_completed_effects(
    expression, code, expected_stdout
):
    result = execute(
        source=f"print('before')\nprint({expression})\n",
        eval_backend="js-core-runtime",
        raise_on_error=False,
    )
    assert not result.ok
    assert result.stdout == expected_stdout
    assert result.diagnostics[0].code == code


@NODE_REQUIRED
def test_session_can_run_repaired_calculation_after_a_failed_run():
    session = create_session(eval_backend="js-core-runtime")
    failed = session.run(
        source="print(1 + '2')\n", capture_output=True, raise_on_error=False
    )
    repaired = session.run(
        source="total = 1200 * 4 + 250\nprint(total)\ntotal\n",
        capture_output=True,
        display_last_expr=True,
    )
    assert not failed.ok
    assert repaired.ok and repaired.stdout == "5050\n"
    assert repaired.has_value and repaired.value == repaired.bindings["total"] == 5050
    assert repaired.diagnostics == ()


def test_validated_failure_retains_stdout_stderr_and_exception_details():
    with pytest.raises(EvalBackendExecutionError) as caught:
        _decode_result(failure_record())
    assert caught.value.stdout == "completed\n"
    assert caught.value.stderr == "warning\n"
    assert caught.value.diagnostic.node_type == "TypeError"


@pytest.mark.parametrize(
    "change",
    [
        {"schema": "foreign.result"},
        {"version": 2},
        {"version": True},
        {"ok": "false"},
        {"ok": None},
        {"has_value": "false"},
        {"bindings": []},
        {"diagnostics": None},
        {"stdout": None},
        {"stderr": 0},
        {"backend": "foreign"},
        {"value": 1},
        {"bindings": {"bad": float("inf")}},
        {"unknown": True},
    ],
)
def test_malformed_success_record_is_protocol_failure(change):
    record = success_record()
    record.update(change)
    with pytest.raises(EvalBackendProtocolError):
        _decode_result(record)


@pytest.mark.parametrize("field", list(success_record()))
def test_truncated_envelope_never_defaults_to_success(field):
    record = success_record()
    del record[field]
    with pytest.raises(EvalBackendProtocolError):
        _decode_result(record)


@pytest.mark.parametrize(
    "change",
    [
        {"phase": "parse"},
        {"severity": "warning"},
        {"message": 0},
        {"message": ""},
        {"code": None},
        {"code": "unknown"},
        {"node_type": None},
        {"details": {"exception_type": "RangeError"}},
        {"span": {"line": 1, "column": 1}},
        {"source_excerpt": "invented"},
        {"frontend": "invented"},
        {"backend": "foreign"},
        {"capability": "foreign.eval"},
        {"unknown": True},
    ],
)
def test_malformed_semantic_diagnostic_cannot_become_trusted_evidence(change):
    record = failure_record()
    record["diagnostics"][0].update(change)
    with pytest.raises(EvalBackendProtocolError):
        _decode_result(record)


@pytest.mark.parametrize(
    "change",
    [
        {"diagnostics": []},
        {"diagnostics": ["TypeError"]},
        {"bindings": {"result": 1}},
        {"has_value": True, "value": 1},
    ],
)
def test_failed_envelope_cannot_carry_a_success_result(change):
    record = failure_record()
    record.update(change)
    with pytest.raises(EvalBackendProtocolError):
        _decode_result(record)


@NODE_REQUIRED
@pytest.mark.parametrize("output", ["{", "[]", "{}", '{"ok": false, "ok": true}'])
def test_actual_bad_process_response_is_protocol_failure(tmp_path, output):
    script = tmp_path / "response.js"
    script.write_text(f"process.stdout.write({json.dumps(output)});", encoding="utf-8")
    backend = JsCoreRuntimeBackend(runtime_path=script)
    with pytest.raises(EvalBackendProtocolError):
        backend.evaluate(Module(body=()))


@NODE_REQUIRED
def test_duplicate_field_in_otherwise_complete_response_is_refused(tmp_path):
    output = json.dumps(success_record()).replace(
        '"ok": true', '"ok": false, "ok": true'
    )
    script = tmp_path / "response.js"
    script.write_text(f"process.stdout.write({json.dumps(output)});", encoding="utf-8")
    with pytest.raises(EvalBackendProtocolError, match="invalid JSON"):
        JsCoreRuntimeBackend(runtime_path=script).evaluate(Module(body=()))


def test_public_protocol_failure_has_distinct_diagnostic_and_no_untrusted_output(
    monkeypatch,
):
    import prototype.runtime.backends.js_core as backend_module

    malformed = copy.deepcopy(success_record())
    malformed.update(ok="false", stdout="untrusted\n")
    monkeypatch.setattr(
        backend_module, "run_json_process", lambda *args, **kwargs: malformed
    )
    monkeypatch.setattr(JsCoreRuntimeBackend, "_node", lambda self: "unused-node")
    result = execute(
        source="print(3)\n", eval_backend="js-core-runtime", raise_on_error=False
    )
    assert not result.ok and isinstance(result.exception, EvalBackendProtocolError)
    assert result.stdout == ""
    assert result.diagnostics[0].code == "NOMI-BACKEND-PROTOCOL"
    assert result.diagnostics[0].phase == "transport"


def test_public_validated_failure_keeps_both_output_channels(monkeypatch):
    import prototype.runtime.backends.js_core as backend_module

    monkeypatch.setattr(
        backend_module, "run_json_process", lambda *args, **kwargs: failure_record()
    )
    monkeypatch.setattr(JsCoreRuntimeBackend, "_node", lambda self: "unused-node")
    result = execute(
        source="print(3)\n", eval_backend="js-core-runtime", raise_on_error=False
    )
    assert not result.ok
    assert result.stdout == "completed\n" and result.stderr == "warning\n"
    assert result.diagnostics[0].code == "NOMI-OPERAND-TYPE"


@NODE_REQUIRED
@pytest.mark.parametrize(
    "payload",
    [
        {"schema": "foreign", "version": 1, "root": {"type": "Module", "body": []}},
        {
            "schema": "nomi.core-ir",
            "version": 2,
            "root": {"type": "Module", "body": []},
        },
        {
            "schema": "nomi.core-ir",
            "version": True,
            "root": {"type": "Module", "body": []},
        },
        {"schema": "nomi.core-ir", "version": 1, "root": {}},
        {
            "schema": "nomi.core-ir",
            "version": 1,
            "root": {"type": "Module", "body": "invalid"},
        },
    ],
)
def test_cli_refuses_malformed_request_without_fabricating_runtime_result(payload):
    completed = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        input=json.dumps(payload),
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "request failed" in completed.stderr
    assert "at CoreRuntime" not in completed.stderr
