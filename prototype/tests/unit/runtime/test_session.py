from prototype.runtime import RuntimeSession, create_session


def test_session_preserves_bindings_between_runs():
    session = create_session(mode="nomi")

    first = session.run(source="x = 2\n")
    second = session.run(source="y = x + 3\n")

    assert isinstance(session, RuntimeSession)
    assert first.ok
    assert second.ok
    assert second.bindings["x"] == 2
    assert second.bindings["y"] == 5
    assert second.timings["parse"] >= 0
    assert second.timings["lower"] >= 0
    assert second.timings["eval"] >= 0


def test_session_reset_replaces_interpreter_state():
    session = create_session(mode="nomi")
    session.run(source="x = 2\n")

    session.reset()

    assert "x" not in session.bindings


def test_session_can_return_exception_without_raising():
    session = create_session(mode="nomi")

    result = session.run(source="x = missing_name\n", raise_on_error=False)

    assert not result.ok
    assert result.exception is not None
    assert result.timings["total"] >= 0
