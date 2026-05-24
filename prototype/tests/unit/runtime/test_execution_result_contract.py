import ast

from prototype.parser.nomi import frontend as parser_frontends
from prototype.parser.nomi.frontend import ParserFrontendCapabilities, ParserFrontendSpec
from prototype.runtime import (
    Diagnostic,
    RuntimeEvent,
    RuntimeEventCollector,
    create_session,
    execute,
)


def test_execution_result_has_passive_diagnostics_events_and_output_fields():
    result = execute(source="print('hello')\nx = 3\n", mode="nomi")

    assert result.ok
    assert result.stdout == "hello\n"
    assert result.stderr == ""
    assert result.diagnostics == ()
    assert result.events == ()
    assert result.bindings["x"] == 3


def test_execution_result_can_carry_diagnostics_and_events():
    diagnostic = Diagnostic(message="failed", code="NOMI-TEST")
    event = RuntimeEvent(name="test.event", payload={"value": 1})

    result = execute(source="x = 1\n", diagnostics=(diagnostic,), events=(event,))

    assert result.diagnostics == (diagnostic,)
    assert result.events == (event,)


def test_diagnostic_exposes_shared_json_record_shape():
    diagnostic = Diagnostic(
        message="unsupported construct",
        severity="warning",
        phase="lower",
        code="NOMI-L001",
        span={"line": 1, "column": 1},
        source_excerpt="with x:",
        node_type="With",
        capability="js-lowerer.with",
        frontend="rust-fast-ast-wasm",
        backend="js-core-runtime",
        details={"hint": "try a simpler form"},
    )

    assert diagnostic.to_record() == {
        "phase": "lower",
        "severity": "warning",
        "message": "unsupported construct",
        "span": {"line": 1, "column": 1},
        "source_excerpt": "with x:",
        "node_type": "With",
        "capability": "js-lowerer.with",
        "frontend": "rust-fast-ast-wasm",
        "backend": "js-core-runtime",
        "code": "NOMI-L001",
        "details": {"hint": "try a simpler form"},
    }


def test_execute_uses_runtime_event_collector_snapshot():
    collector = RuntimeEventCollector()
    diagnostic = collector.diagnostic(
        "careful",
        severity="warning",
        phase="eval",
        capability="runtime.test",
    )
    event = collector.event("runtime.test", payload={"ok": True})

    result = execute(source="x = 1\n", event_collector=collector)

    assert result.diagnostics == (diagnostic,)
    assert result.diagnostics[0].to_record()["phase"] == "eval"
    assert result.diagnostics[0].to_record()["capability"] == "runtime.test"
    assert result.events == (event,)


def test_execute_preserves_output_on_returned_exception():
    result = execute(
        source="print('before')\nmissing_name\n",
        mode="nomi",
        raise_on_error=False,
    )

    assert not result.ok
    assert result.stdout == "before\n"
    assert result.stderr == ""
    assert result.exception is not None


def test_session_can_opt_into_output_capture():
    session = create_session(mode="nomi")

    result = session.run(source="print('cell')\nx = 4\n", capture_output=True)

    assert result.ok
    assert result.stdout == "cell\n"
    assert result.stderr == ""
    assert result.bindings["x"] == 4


def test_session_can_preflight_with_named_parser_frontend(monkeypatch):
    calls = []

    class FakeFrontend:
        def parse_accepts(self, *, code=None, filename=None):
            calls.append((code, filename))

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-gate", FakeFrontend())
    session = create_session(mode="nomi", parser_frontend="test-gate")

    result = session.run(source="x = 5\n", capture_output=True)

    assert result.ok
    assert result.pipeline.parser_frontend == "test-gate"
    assert result.bindings["x"] == 5
    assert calls == [("x = 5\n", None)]


def test_session_uses_python_ast_capable_parser_frontend(monkeypatch):
    calls = []

    class FakeFrontend:
        spec = ParserFrontendSpec(
            name="test-ast",
            status="test",
            grammar_format="test",
            implementation="test",
            cst_artifact="test",
            output_contract="test",
            capabilities=ParserFrontendCapabilities(lower_to_python_ast=True),
        )

        def generate_python_ast(self, *, code=None, filename=None):
            calls.append((code, filename))
            return ast.Module(
                body=[
                    ast.Assign(
                        targets=[ast.Name(id="x", ctx=ast.Store())],
                        value=ast.Constant(value=11),
                    )
                ],
                type_ignores=[],
            )

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-ast", FakeFrontend())
    session = create_session(mode="nomi", parser_frontend="test-ast")

    result = session.run(source="x = 5\n", capture_output=True)

    assert result.ok
    assert result.bindings["x"] == 11
    assert calls == [("x = 5\n", None)]


def test_session_uses_runtime_event_collector_snapshot():
    session = create_session(mode="nomi")
    collector = RuntimeEventCollector()
    event = collector.event("session.test")

    result = session.run(source="x = 1\n", event_collector=collector)

    assert result.events == (event,)
