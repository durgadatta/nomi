import ast

from prototype.parser.nomi import frontend as parser_frontends
from prototype.parser.nomi.frontend import ParserFrontendCapabilities, ParserFrontendSpec
from prototype.runtime import (
    Diagnostic,
    RuntimeEvent,
    RuntimeEventCollector,
    SEMANTIC_EVENT_KINDS,
    create_session,
    execute,
    record_block_policy_event,
    record_capability_event,
    record_decode_event,
    record_match_event,
    record_pipeline_event,
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


def test_runtime_event_exposes_v1_record_shape():
    event = RuntimeEvent(
        name="semantic.binding.constraint_failed",
        payload={"name": "age"},
        id="event-1",
        parent_id="event-0",
        phase="eval",
        kind="binding",
        action="constraint_failed",
        feature="binding-constraints",
        operation="constraint_failed",
        source_span={"line": 1, "column": 1},
        subject="age",
        value_summary="-1",
        capability="binding.constraints",
        failure_kind="constraint",
        redaction={"paths": []},
        next_step="Adjust the value.",
    )

    assert event.to_record() == {
        "id": "event-1",
        "parent_id": "event-0",
        "name": "semantic.binding.constraint_failed",
        "phase": "eval",
        "kind": "binding",
        "action": "constraint_failed",
        "feature": "binding-constraints",
        "operation": "constraint_failed",
        "span": {"line": 1, "column": 1},
        "subject": "age",
        "value_summary": "-1",
        "capability": "binding.constraints",
        "failure_kind": "constraint",
        "redaction": {"paths": []},
        "next_step": "Adjust the value.",
        "payload": {"name": "age"},
    }


def test_runtime_event_collector_assigns_stable_event_ids_and_parent_links():
    collector = RuntimeEventCollector()

    first = collector.event("runtime.first")
    second = collector.event("runtime.second", parent_id=first.id)

    assert first.id == "event-1"
    assert second.id == "event-2"
    assert second.parent_id == "event-1"


def test_runtime_event_collector_has_stable_semantic_hook_families():
    collector = RuntimeEventCollector()

    for kind in SEMANTIC_EVENT_KINDS:
        collector.semantic_event(kind, "observe", feature="test-feature")

    _, events = collector.snapshot()
    assert tuple(event.name for event in events) == tuple(
        f"semantic.{kind}.observe" for kind in SEMANTIC_EVENT_KINDS
    )
    assert events[0].payload == {
        "kind": "binding",
        "action": "observe",
        "feature": "test-feature",
    }
    assert events[0].to_record()["id"] == "event-1"
    assert events[0].to_record()["kind"] == "binding"
    assert events[0].to_record()["operation"] == "observe"


def test_runtime_event_collector_rejects_unknown_semantic_event_kind():
    collector = RuntimeEventCollector()

    try:
        collector.semantic_event("private-dialect")
    except ValueError as exc:
        assert "Unknown semantic event kind" in str(exc)
        assert "binding" in str(exc)
    else:
        raise AssertionError("unknown semantic event kind should fail")


def test_feature_event_helpers_use_shared_semantic_vocabulary():
    collector = RuntimeEventCollector()

    decode = record_decode_event(
        collector,
        "failed",
        subject="Person.age",
        value_summary="'unknown'",
        failure_kind="decode",
        redaction={"paths": ["token"]},
        next_step="Provide an integer age.",
        payload={"field_path": "age", "expected": "int"},
    )
    match = record_match_event(
        collector,
        "skipped",
        subject="case adult",
        failure_kind="guard",
        payload={"pattern": "Person(age >= 18)"},
    )
    pipeline = record_pipeline_event(
        collector,
        "stage_completed",
        subject="where",
        value_summary="12 rows",
        payload={"stage": 2},
    )
    block = record_block_policy_event(
        collector,
        "yielded",
        subject="using(open(path))",
        payload={"policy": "using"},
    )
    capability = record_capability_event(
        collector,
        "denied",
        subject="network",
        failure_kind="capability-denial",
        next_step="Grant the network capability.",
    )

    _, events = collector.snapshot()

    assert events == (decode, match, pipeline, block, capability)
    assert tuple(event.name for event in events) == (
        "semantic.decode.failed",
        "semantic.match.skipped",
        "semantic.pipeline.stage_completed",
        "semantic.block.yielded",
        "semantic.capability.denied",
    )
    assert decode.to_record() == {
        "id": "event-1",
        "parent_id": None,
        "name": "semantic.decode.failed",
        "phase": "eval",
        "kind": "decode",
        "action": "failed",
        "feature": "data-decode",
        "operation": "failed",
        "span": None,
        "subject": "Person.age",
        "value_summary": "'unknown'",
        "capability": "data.decode",
        "failure_kind": "decode",
        "redaction": {"paths": ["token"]},
        "next_step": "Provide an integer age.",
        "payload": {
            "kind": "decode",
            "action": "failed",
            "feature": "data-decode",
            "field_path": "age",
            "expected": "int",
        },
    }
    assert match.feature == "pattern-matching"
    assert match.capability == "pattern.match"
    assert pipeline.feature == "collection-flow"
    assert pipeline.capability == "flow.pipeline"
    assert block.kind == "block"
    assert block.feature == "block-policy"
    assert block.capability == "block.policy"
    assert capability.kind == "capability"
    assert capability.feature == "state-capability"
    assert capability.capability == "host.capability"


def test_feature_event_helpers_preserve_parent_links():
    collector = RuntimeEventCollector()

    parent = record_pipeline_event(collector, "entered", subject="people")
    child = record_decode_event(
        collector,
        "failed",
        subject="people[3].age",
        parent_id=parent.id,
    )

    assert parent.id == "event-1"
    assert child.id == "event-2"
    assert child.parent_id == "event-1"
    assert child.to_record()["parent_id"] == "event-1"


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


def test_execute_records_binding_constraint_failure_diagnostic_and_event():
    result = execute(
        source="age: int, age > 0 = -1\n",
        mode="nomi",
        raise_on_error=False,
    )

    assert not result.ok
    assert result.exception is not None
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.code == "NOMI-BINDING-CONSTRAINT"
    assert diagnostic.phase == "eval"
    assert diagnostic.capability == "binding.constraints"
    assert diagnostic.details["name"] == "age"
    assert diagnostic.details["binding_kind"] == "assignment"
    assert diagnostic.details["constraint_expr"] is None

    assert len(result.events) == 1
    event = result.events[0]
    assert event.name == "semantic.binding.constraint_failed"
    assert event.payload["kind"] == "binding"
    assert event.payload["action"] == "constraint_failed"
    assert event.payload["feature"] == "binding-constraints"
    assert event.payload["name"] == "age"
    assert event.feature == "binding-constraints"
    assert event.phase == "eval"
    assert event.operation == "constraint_failed"
    assert event.capability == "binding.constraints"
    assert event.failure_kind == "constraint"
    assert event.subject == "age"
    assert event.value_summary == "-1"
    assert event.to_record()["next_step"]


def test_session_records_binding_constraint_failure_diagnostic_and_event():
    session = create_session(mode="nomi")

    result = session.run(
        source="score: int, score >= 0 else \"score must be non-negative\" = -2\n",
        raise_on_error=False,
    )

    assert not result.ok
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == "NOMI-BINDING-CONSTRAINT"
    assert "score must be non-negative" in result.diagnostics[0].message
    assert result.events[0].name == "semantic.binding.constraint_failed"


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
