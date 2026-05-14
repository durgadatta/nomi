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


def test_session_reset_can_clear_ast_cache():
    session = create_session(mode="nomi", cache_size=2)
    session.run(source="cached_value = 4\n")
    session.run(source="cached_value = 4\n")

    assert session._ast_cache

    session.reset(clear_cache=True)

    assert session._ast_cache == {}


def test_session_can_return_exception_without_raising():
    session = create_session(mode="nomi")

    result = session.run(source="x = missing_name\n", raise_on_error=False)

    assert not result.ok
    assert result.exception is not None
    assert result.timings["total"] >= 0


def test_session_can_reuse_cached_ast_for_repeated_source():
    session = create_session(mode="nomi", cache_size=2)

    first = session.run(source="cached_value = 4\n")
    second = session.run(source="cached_value = 4\n")

    assert first.ok
    assert second.ok
    assert "parse" in first.timings
    assert "cache" in second.timings
    assert "parse" not in second.timings


def test_session_can_capture_display_last_expression_value():
    session = create_session(mode="nomi")

    result = session.run(
        source="x = 2\nx + 3\n",
        display_last_expr=True,
    )

    assert result.ok
    assert result.has_value
    assert result.value == 5
    assert result.bindings["x"] == 2


def test_session_does_not_capture_value_when_display_is_disabled():
    session = create_session(mode="nomi")

    result = session.run(
        source="x = 2\nx + 3\n",
        display_last_expr=False,
    )

    assert result.ok
    assert not result.has_value
    assert result.value is None
