"""Display-value boundaries for persistent native prototype sessions."""

import ast

import pytest

from prototype.runtime import create_session


@pytest.fixture(
    params=[
        pytest.param(("python", None, False), id="python-default"),
        pytest.param(("nomi", None, False), id="nomi-default"),
        pytest.param(("reduced", None, False), id="reduced-default"),
        pytest.param(("nomi", "python-ast", False), id="explicit-python-ast"),
        pytest.param(("nomi", "python-ast", True), id="core-python-ast-adapter"),
        pytest.param(("nomi", "core-runtime", False), id="core-runtime"),
    ]
)
def binding_session(request, monkeypatch):
    mode, backend, use_core_ir = request.param
    if use_core_ir:
        monkeypatch.setenv("NOMI_USE_CORE_IR", "1")
    else:
        monkeypatch.delenv("NOMI_USE_CORE_IR", raising=False)
    return create_session(mode=mode, eval_backend=backend, cache_size=3)


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
@pytest.mark.parametrize(
    ("source", "value"),
    [
        ("6 * 7\n", 42),
        ("0\n", 0),
        ("False\n", False),
        ("None\n", None),
        ("''\n", ""),
        ("[]\n", []),
    ],
)
def test_one_expression_cell_captures_value_even_when_it_is_falsy(mode, source, value):
    result = create_session(mode=mode).run(
        source=source, display_last_expr=True, capture_output=True
    )
    assert result.ok
    assert result.has_value is True
    assert result.value == value
    assert type(result.value) is type(value)
    assert result.stdout == result.stderr == ""


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
def test_single_call_expression_is_evaluated_once_when_displayed(mode):
    session = create_session(mode=mode)
    keyword = "def" if mode == "python" else "func"
    session.run(
        source=(
            "calls = []\n"
            f"{keyword} produce():\n"
            "    calls.append(1)\n"
            "    print('once')\n"
            "    return 42\n"
        )
    )
    result = session.run(
        source="produce()\n", display_last_expr=True, capture_output=True
    )
    assert result.has_value is True
    assert result.value == 42
    assert result.stdout == "once\n"
    assert session.bindings["calls"] == [1]


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
def test_cached_and_supplied_single_expression_asts_keep_display_values(mode):
    session = create_session(mode=mode, cache_size=1)
    first = session.run(source="6 * 7\n", display_last_expr=True)
    cached = session.run(source="6 * 7\n", display_last_expr=True)
    supplied = session.run(tree=ast.parse("6 * 7\n"), display_last_expr=True)
    assert first.has_value is cached.has_value is supplied.has_value is True
    assert first.value == cached.value == supplied.value == 42
    assert "parse" in first.timings
    assert "cache" in cached.timings
    assert "parse" not in cached.timings


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
@pytest.mark.parametrize("source", ["\n", "value = 42\n"])
def test_empty_or_statement_cell_has_no_display_value(mode, source):
    result = create_session(mode=mode).run(source=source, display_last_expr=True)
    assert result.ok
    assert result.has_value is False
    assert result.value is None


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
def test_display_disabled_still_evaluates_once_without_capturing_value(mode):
    result = create_session(mode=mode).run(
        source="print('once')\n", display_last_expr=False, capture_output=True
    )
    assert result.ok
    assert result.has_value is False
    assert result.value is None
    assert result.stdout == "once\n"


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
def test_failed_last_expression_does_not_claim_a_display_value(mode):
    result = create_session(mode=mode).run(
        source="1 / 0\n",
        display_last_expr=True,
        capture_output=True,
        raise_on_error=False,
    )
    assert result.ok is False
    assert result.has_value is False
    assert result.value is None
    assert isinstance(result.exception, ZeroDivisionError)
    assert result.diagnostics
    assert result.diagnostics[0].phase == "eval"


@pytest.mark.parametrize("mode", ["nomi", "reduced"])
def test_block_call_remains_a_statement_result(mode):
    session = create_session(mode=mode)
    session.run(source="func once():\n    yield\ncount = 0\n")
    result = session.run(
        source="once():\n    count = count + 1\n",
        display_last_expr=True,
        capture_output=True,
    )
    assert result.ok
    assert result.has_value is False
    assert result.value is None
    assert session.bindings["count"] == 1


def test_result_keeps_name_associations_across_later_and_cached_runs(binding_session):
    session = binding_session
    first = session.run(source="x = 1\n")
    second = session.run(source="x = 2\ny = 3\n")
    cached = session.run(source="x = 2\ny = 3\n")

    assert "cache" in cached.timings
    assert first.bindings["x"] == 1
    assert "y" not in first.bindings
    assert second.bindings["x"] == cached.bindings["x"] == 2
    assert first.bindings is not session.bindings
    assert second.bindings is not cached.bindings


def test_editing_result_name_associations_does_not_mutate_the_session(binding_session):
    session = binding_session
    result = session.run(source="x = 1\n")
    result.bindings["x"] = 99
    result.bindings["artifact_only"] = True

    assert session.bindings["x"] == 1
    assert "artifact_only" not in session.bindings


def test_failed_run_and_recovery_leave_historical_result_names_intact(binding_session):
    session = binding_session
    earlier = session.run(source="x = 1\n")
    failed = session.run(source="x = 2\n1 / 0\n", raise_on_error=False)
    recovered = session.run(source="x = 3\ny = 4\n")

    assert not failed.ok
    assert failed.bindings == {}
    assert earlier.bindings["x"] == 1
    assert "y" not in earlier.bindings
    assert recovered.bindings["x"] == 3


@pytest.mark.parametrize("clear_cache", [False, True])
def test_reset_does_not_retarget_historical_result_bindings(binding_session, clear_cache):
    session = binding_session
    earlier = session.run(source="x = 1\n")
    old_live_bindings = session.bindings
    session.reset(clear_cache=clear_cache)
    replayed = session.run(source="x = 1\n")

    assert earlier.bindings is not old_live_bindings
    assert earlier.bindings is not session.bindings
    assert earlier.bindings["x"] == replayed.bindings["x"] == 1
    assert ("cache" in replayed.timings) is not clear_cache


@pytest.mark.parametrize("mode", ["python", "nomi", "reduced"])
def test_binding_snapshot_is_shallow_and_does_not_copy_mutable_values_or_handles(mode):
    session = create_session(mode=mode)
    handle = object()
    session.bindings["handle"] = handle
    result = session.run(source="items = []\n")
    items = session.bindings["items"]
    session.run(source="items.append(1)\n")

    assert result.bindings is not session.bindings
    assert result.bindings["items"] is items
    assert result.bindings["items"] == [1]
    assert result.bindings["handle"] is handle
