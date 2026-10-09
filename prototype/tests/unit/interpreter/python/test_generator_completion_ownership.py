"""Independent value/event oracles for hosted continuation completion (S2)."""

import ast
import sys

import pytest

from prototype.parser.nomi.desugar import desugar_module
from prototype.runtime.modes import get_mode_spec


class Manager:
    def __init__(self, name, events, *, suppress=False, failure=None):
        self.name = name
        self.events = events
        self.suppress = suppress
        self.failure = failure

    def __enter__(self):
        self.events.append((self.name, "enter"))

    def __exit__(self, kind, error, traceback):
        self.events.append((self.name, "exit", kind.__name__ if kind else None))
        if self.failure:
            raise self.failure
        return self.suppress


def make_generator(mode, source, **bindings):
    if mode == "native":
        exec(source, bindings)
        return bindings["work"]()
    interpreter = get_mode_spec(mode).load_interpreter_class()()
    interpreter.global_env.bindings.update(bindings)
    tree = ast.parse(source)
    if mode == "reduced":
        tree = desugar_module(tree)
    interpreter.eval(ast.fix_missing_locations(tree))
    return interpreter.global_env.get("work")()


@pytest.mark.parametrize(
    "expression, inputs, expected, expected_events",
    (
        ("mark('left', 10) + (yield 'ready')", [5], 15, [("left", 10)]),
        ("(yield 'first') + mark('middle', 10) * (yield 'second')", [2, 3], 32, [("middle", 10)]),
        ("collect(mark('left', 1) + (yield 'ready'), mark('right', 3))", [2], (3, 3), [("left", 1), ("right", 3)]),
        ("collect((yield 'ready'))", [None], (None,), []),
    ),
)
def test_completed_operand_values_and_effects_survive_suspension(
    interpreter_mode, expression, inputs, expected, expected_events,
):
    for mode in ("native", interpreter_mode):
        events = []

        def mark(label, value):
            events.append((label, value))
            return value

        generator = make_generator(
            mode, f"def work():\n    result = {expression}\n    yield result\n",
            mark=mark, collect=lambda *values: values,
        )
        next(generator)
        for value in inputs:
            result = generator.send(value)
        assert result == expected
        assert events == expected_events
        with pytest.raises(StopIteration):
            next(generator)


@pytest.mark.parametrize("suppress", (False, True))
def test_failed_resumed_child_unwinds_waiting_scopes_and_reaches_handler(interpreter_mode, suppress):
    for mode in ("native", interpreter_mode):
        events = []

        def fail(value):
            events.append(("fail", value))
            raise ValueError("child failed")

        generator = make_generator(
            mode,
            "def work():\n"
            "    try:\n"
            "        with outer, inner:\n"
            "            result = fail((yield 'ready'))\n"
            "            events.append('unreachable')\n"
            "        events.append('after scope')\n"
            "    except ValueError:\n"
            "        events.append('handler')\n"
            "    finally:\n"
            "        events.append('finally')\n"
            "    yield 'done'\n",
            outer=Manager("outer", events), inner=Manager("inner", events, suppress=suppress),
            fail=fail, events=events,
        )
        assert next(generator) == "ready"
        assert generator.send(7) == "done"
        assert events == [
            ("outer", "enter"), ("inner", "enter"), ("fail", 7),
            ("inner", "exit", "ValueError"), ("outer", "exit", None if suppress else "ValueError"),
            "after scope" if suppress else "handler", "finally",
        ]


def test_return_waits_for_yielding_finally_and_retains_result(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []
        generator = make_generator(
            mode,
            "def work():\n"
            "    try:\n"
            "        return 10 + (yield 'ready')\n"
            "    finally:\n"
            "        events.append('cleanup start')\n"
            "        yield 'cleanup'\n"
            "        events.append('cleanup end')\n",
            events=events,
        )
        assert next(generator) == "ready"
        assert generator.send(5) == "cleanup"
        assert events == ["cleanup start"]
        with pytest.raises(StopIteration) as stopped:
            next(generator)
        assert stopped.value.value == 15
        assert events == ["cleanup start", "cleanup end"]
        with pytest.raises(StopIteration) as stopped_again:
            next(generator)
        assert stopped_again.value.value is None


def test_cleanup_failure_replaces_child_failure_once(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []

        def fail(value):
            raise ValueError("child failed")

        generator = make_generator(
            mode,
            "def work():\n"
            "    with outer, inner:\n"
            "        fail((yield 'ready'))\n",
            outer=Manager("outer", events), inner=Manager("inner", events, failure=TypeError("cleanup failed")),
            fail=fail,
        )
        assert next(generator) == "ready"
        with pytest.raises(TypeError, match="cleanup failed") as raised:
            generator.send(None)
        assert isinstance(raised.value.__context__, ValueError)
        assert events == [
            ("outer", "enter"), ("inner", "enter"),
            ("inner", "exit", "ValueError"), ("outer", "exit", "TypeError"),
        ]
        with pytest.raises(StopIteration):
            next(generator)


def test_throw_returns_handler_yield_and_close_unwinds_scopes(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []
        generator = make_generator(
            mode,
            "def work():\n"
            "    with outer:\n"
            "        try:\n"
            "            yield 'ready'\n"
            "        except ValueError:\n"
            "            yield 'handled'\n"
            "        finally:\n"
            "            events.append('finally')\n",
            outer=Manager("outer", events), events=events,
        )
        assert next(generator) == "ready"
        assert generator.throw(ValueError("injected")) == "handled"
        generator.close()
        assert events == [("outer", "enter"), "finally", ("outer", "exit", "GeneratorExit")]
        generator.close()
        with pytest.raises(StopIteration):
            next(generator)


def test_yield_from_delivers_send_throw_close_and_child_return(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []

        def child():
            try:
                try:
                    received = yield "child ready"
                    events.append(("sent", received))
                    yield "child again"
                except ValueError:
                    yield "child handled"
                return 19
            finally:
                events.append("child finally")

        source = "def work():\n    result = yield from child()\n    yield result\n"
        generator = make_generator(mode, source, child=child)
        assert next(generator) == "child ready"
        assert generator.send(None) == "child again"
        assert generator.throw(ValueError("injected")) == "child handled"
        assert next(generator) == 19
        assert events == [("sent", None), "child finally"]
        events.clear()
        generator = make_generator(mode, source, child=child)
        assert next(generator) == "child ready"
        generator.close()
        assert events == ["child finally"]


@pytest.mark.parametrize("source", (
    "def work():\n    events.append('body')\n    result = [(yield 'ready')]\n",
    "def work():\n    events.append('body')\n    result = -(yield 'ready')\n",
))
def test_unsupported_suspension_is_rejected_before_generator_body_effects(interpreter_mode, source):
    events = []
    generator = make_generator(interpreter_mode, source, events=events)
    with pytest.raises(NotImplementedError, match="Hosted generator suspension through"):
        next(generator)
    assert events == []
    with pytest.raises(StopIteration):
        next(generator)


def test_continuation_does_not_bypass_reduced_desugaring_guard():
    interpreter = get_mode_spec("reduced").load_interpreter_class()()
    interpreter.eval(ast.parse("def work():\n    with manager:\n        yield 1\n"))
    with pytest.raises(NotImplementedError, match="With should be desugared"):
        next(interpreter.global_env.get("work")())


@pytest.mark.parametrize("complete", ("close", "return", "failure"))
def test_completion_before_first_yield_stays_closed_even_with_non_none_send(interpreter_mode, complete):
    for mode in ("native", interpreter_mode):
        generator = make_generator(mode, "def work():\n    return 7\n    yield 'unreachable'\n")
        if complete == "close":
            generator.close()
        elif complete == "failure":
            with pytest.raises(ValueError, match="injected"):
                generator.throw(ValueError("injected"))
        else:
            with pytest.raises(StopIteration) as stopped:
                next(generator)
            assert stopped.value.value == 7
        with pytest.raises(StopIteration):
            generator.send(5)


def test_generator_control_does_not_appear_as_an_active_cleanup_exception(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []

        class ObservingManager(Manager):
            def __exit__(self, kind, error, traceback):
                super().__exit__(kind, error, traceback)
                active = sys.exception()
                events.append(("active", type(active).__name__ if active else None))

        generator = make_generator(
            mode,
            "def work():\n"
            "    try:\n"
            "        raise ValueError('handled')\n"
            "    except ValueError:\n"
            "        with manager:\n"
            "            yield 'ready'\n"
            "            return 8\n",
            manager=ObservingManager("manager", events), events=events,
        )
        assert next(generator) == "ready"
        assert sys.exception() is None
        with pytest.raises(StopIteration) as stopped:
            next(generator)
        assert stopped.value.value == 8
        assert events == [("manager", "enter"), ("manager", "exit", None), ("active", "ValueError")]


def test_close_cleanup_failure_and_ignored_generator_exit_match_native(interpreter_mode):
    for mode in ("native", interpreter_mode):
        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield 'ready'\n"
            "    finally:\n        yield 'cleanup pause'\n",
        )
        assert next(generator) == "ready"
        with pytest.raises(RuntimeError, match="generator ignored GeneratorExit"):
            generator.close()
        with pytest.raises(GeneratorExit):
            next(generator)
        events = []
        generator = make_generator(
            mode, "def work():\n    with manager:\n        yield 'ready'\n",
            manager=Manager("manager", events, failure=ValueError("cleanup failed")),
        )
        assert next(generator) == "ready"
        with pytest.raises(ValueError, match="cleanup failed"):
            generator.close()
        assert events == [("manager", "enter"), ("manager", "exit", "GeneratorExit")]


def test_host_contextlib_receives_injected_errors_and_cleanup(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []
        generator = make_generator(
            mode,
            "from contextlib import contextmanager\n"
            "@contextmanager\n"
            "def scope():\n"
            "    events.append('enter')\n"
            "    try:\n"
            "        yield 7\n"
            "    except ValueError:\n"
            "        events.append('handled')\n"
            "    finally:\n"
            "        events.append('exit')\n"
            "def work():\n"
            "    with scope() as value:\n"
            "        yield value\n"
            "        raise ValueError('body')\n"
            "    yield 'done'\n",
            events=events,
        )
        assert next(generator) == 7
        assert next(generator) == "done"
        assert events == ["enter", "handled", "exit"]


def test_attached_nomi_block_error_reaches_callee_and_retries(nomi_mode):
    from prototype.interpreter.helpers import get_run_eval_loop

    result = get_run_eval_loop(nomi_mode)(code=(
        "events = []\n"
        "func retry():\n"
        "    for attempt in range(3):\n"
        "        try:\n"
        "            yield attempt\n"
        "            return\n"
        "        except ValueError:\n"
        "            events.append('caught')\n"
        "        finally:\n"
        "            events.append('cleanup')\n"
        "retry() -> attempt:\n"
        "    events.append(attempt)\n"
        "    if attempt < 2:\n"
        "        raise ValueError('retry')\n"
    ))
    assert result["events"] == [0, "caught", "cleanup", 1, "caught", "cleanup", 2, "cleanup"]
