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


def test_execute_uses_runtime_event_collector_snapshot():
    collector = RuntimeEventCollector()
    diagnostic = collector.diagnostic("careful", severity="warning")
    event = collector.event("runtime.test", payload={"ok": True})

    result = execute(source="x = 1\n", event_collector=collector)

    assert result.diagnostics == (diagnostic,)
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


def test_session_uses_runtime_event_collector_snapshot():
    session = create_session(mode="nomi")
    collector = RuntimeEventCollector()
    event = collector.event("session.test")

    result = session.run(source="x = 1\n", event_collector=collector)

    assert result.events == (event,)
