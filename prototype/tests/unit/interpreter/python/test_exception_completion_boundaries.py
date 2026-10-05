"""Synchronous hosted Try preserves handler and completion boundaries."""

import ast
import sys
from textwrap import indent

import pytest

from prototype.parser.nomi.desugar import desugar_module
from prototype.runtime.modes import get_mode_spec


def _run(mode, source, configure=None):
    events = []
    bindings = {"events": events, "SystemExit": SystemExit, "KeyboardInterrupt": KeyboardInterrupt}
    if configure is not None:
        configure(bindings)
    error = None
    try:
        if mode == "native":
            exec(source, bindings)
        else:
            interpreter = get_mode_spec(mode).load_interpreter_class()()
            interpreter.global_env.bindings.update(bindings)
            tree = ast.parse(source)
            if mode == "reduced":
                tree = desugar_module(tree)
            interpreter.eval(ast.fix_missing_locations(tree))
            bindings = interpreter.global_env.bindings
    except BaseException as exc:
        error = exc
    return events, bindings.get("answer"), error


def _context_chain(error):
    chain = []
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        chain.append((type(error).__name__, str(error)))
        error = error.__context__
    return chain


def test_bare_reraise_keeps_the_active_exception_and_runs_finally(interpreter_mode):
    source = (
        "try:\n    try:\n        1 / 0\n    except ZeroDivisionError:\n"
        "        events.append('inner handler')\n        raise\n"
        "    finally:\n        events.append('inner finally')\n"
        "except ZeroDivisionError:\n    events.append('outer handler')\n"
        "finally:\n    events.append('outer finally')\nanswer = 7\n"
    )
    native_events, native_answer, native_error = _run("native", source)
    events, answer, error = _run(interpreter_mode, source)
    assert error is native_error is None
    assert answer == native_answer == 7
    assert events == native_events == ["inner handler", "inner finally", "outer handler", "outer finally"]


@pytest.mark.parametrize(
    "source, expected_events, expected_chain",
    (
        (
            "try:\n    1 / 0\nexcept ZeroDivisionError:\n    events.append('handler')\n"
            "    raise ValueError('handler failed')\nexcept ValueError:\n    events.append('wrong handler')\n"
            "finally:\n    events.append('finally')\n",
            ["handler", "finally"], [("ValueError", "handler failed"), ("ZeroDivisionError", "division by zero")],
        ),
        (
            "try:\n    events.append('body')\nexcept ValueError:\n    events.append('wrong handler')\n"
            "else:\n    events.append('else')\n    raise ValueError('else failed')\n"
            "finally:\n    events.append('finally')\n",
            ["body", "else", "finally"], [("ValueError", "else failed")],
        ),
        (
            "try:\n    raise ValueError('body failed')\nfinally:\n"
            "    events.append('finally')\n    raise TypeError('cleanup failed')\n",
            ["finally"], [("TypeError", "cleanup failed"), ("ValueError", "body failed")],
        ),
        (
            "try:\n    1 / 0\nexcept ZeroDivisionError:\n    raise ValueError('handler failed')\n"
            "finally:\n    events.append('finally')\n    raise TypeError('cleanup failed')\n",
            ["finally"], [("TypeError", "cleanup failed"), ("ValueError", "handler failed"), ("ZeroDivisionError", "division by zero")],
        ),
    ),
)
def test_handler_else_and_finally_failures_preserve_completion_order(
    interpreter_mode, source, expected_events, expected_chain,
):
    native_events, _, native_error = _run("native", source)
    events, _, error = _run(interpreter_mode, source)
    assert events == native_events == expected_events
    assert _context_chain(error) == _context_chain(native_error) == expected_chain


@pytest.mark.parametrize("exception", ("SystemExit", "KeyboardInterrupt"))
@pytest.mark.parametrize("handler", ("Exception", "BaseException", "(SystemExit, KeyboardInterrupt)", None))
def test_real_base_exceptions_are_not_lost_or_mistaken_for_internal_control(interpreter_mode, exception, handler):
    clause = "except:" if handler is None else f"except {handler}:"
    source = (
        f"try:\n    raise {exception}('stop')\n{clause}\n    events.append('handler')\n"
        "finally:\n    events.append('finally')\nanswer = 7\n"
    )
    native_events, native_answer, native_error = _run("native", source)
    events, answer, error = _run(interpreter_mode, source)
    assert type(error) is type(native_error)
    assert events == native_events
    assert answer == native_answer


@pytest.mark.parametrize(
    "handler",
    ("int", "3", "(int, ZeroDivisionError)", "(ZeroDivisionError, int)", "(ValueError, 3)", "((ZeroDivisionError,),)"),
)
def test_invalid_exception_handler_types_reject_before_handler_body(interpreter_mode, handler):
    source = f"try:\n    1 / 0\nexcept {handler}:\n    events.append('handler')\nfinally:\n    events.append('finally')\n"
    native_events, _, native_error = _run("native", source)
    events, _, error = _run(interpreter_mode, source)
    assert isinstance(error, TypeError)
    assert isinstance(native_error, TypeError)
    assert events == native_events == ["finally"]
    assert isinstance(error.__context__, ZeroDivisionError)


@pytest.mark.parametrize("handler, caught", (("()", False), ("(ValueError, ZeroDivisionError)", True)))
def test_flat_exception_tuple_matching_and_empty_tuple_match_native(interpreter_mode, handler, caught):
    source = f"try:\n    1 / 0\nexcept {handler}:\n    events.append('handler')\nfinally:\n    events.append('finally')\n"
    native_events, _, native_error = _run("native", source)
    events, _, error = _run(interpreter_mode, source)
    assert type(error) is type(native_error)
    assert events == native_events == (["handler", "finally"] if caught else ["finally"])


@pytest.mark.parametrize("matching", (True, False))
def test_exception_matching_uses_real_subtypes_not_virtual_metaclass_membership(interpreter_mode, matching):
    def configure(bindings):
        class ExceptionMeta(type):
            def __instancecheck__(self, instance):
                bindings["events"].append("instance hook")
                return True

            def __subclasscheck__(self, subclass):
                bindings["events"].append("subclass hook")
                return True

        class HookError(ValueError, metaclass=ExceptionMeta):
            pass

        class ChildError(HookError):
            pass

        bindings["HookError"] = HookError
        bindings["RaisedError"] = ChildError if matching else TypeError

    source = (
        "try:\n    raise RaisedError('problem')\nexcept HookError:\n    events.append('matching handler')\n"
        "except TypeError:\n    events.append('fallback handler')\nfinally:\n    events.append('finally')\n"
        "answer = 7\n"
    )
    native_events, native_answer, native_error = _run("native", source, configure)
    events, answer, error = _run(interpreter_mode, source, configure)
    assert error is native_error is None
    # Native raising may normalize the exception via a subclass hook; matching
    # must add no virtual-membership calls beyond that native sequence.
    assert events == native_events
    assert events[-2:] == ["matching handler" if matching else "fallback handler", "finally"]
    assert "instance hook" not in events
    assert answer == native_answer == 7


@pytest.mark.parametrize(
    "source, expected_events, expected_answer",
    (
        (
            "def function():\n    try:\n        return 7\n    except:\n        events.append('wrong handler')\n"
            "    finally:\n        events.append('finally')\nanswer = function()\n",
            ["finally"], 7,
        ),
        (
            "def function():\n    try:\n        return 7\n    finally:\n        events.append('finally')\n        return 8\n"
            "answer = function()\n",
            ["finally"], 8,
        ),
        (
            "for value in [1, 2]:\n    try:\n        break\n    except:\n        events.append('wrong handler')\n"
            "    finally:\n        events.append(value)\nanswer = 7\n",
            [1], 7,
        ),
        (
            "for value in [1, 2]:\n    try:\n        continue\n    except:\n        events.append('wrong handler')\n"
            "    finally:\n        events.append(value)\nanswer = 7\n",
            [1, 2], 7,
        ),
    ),
)
@pytest.mark.filterwarnings("ignore:'return' in a 'finally' block:SyntaxWarning")
def test_finally_preserves_or_explicitly_replaces_control_transfer(
    interpreter_mode, source, expected_events, expected_answer,
):
    native_events, native_answer, native_error = _run("native", source)
    events, answer, error = _run(interpreter_mode, source)
    assert error is native_error is None
    assert events == native_events == expected_events
    assert answer == native_answer == expected_answer


def _pending_try_source(origin, transfer, operation):
    statement = "return 7" if transfer == "return" else transfer
    if origin == "body":
        scope = f"try:\n    {statement}\nexcept ZeroDivisionError:\n    events.append('wrong handler')\n"
    elif origin == "handler":
        scope = f"try:\n    1 / 0\nexcept ZeroDivisionError:\n    {statement}\n"
    else:
        scope = (
            "try:\n    events.append('body')\nexcept ZeroDivisionError:\n    events.append('wrong handler')\n"
            f"else:\n    {statement}\n"
        )
    scope += f"finally:\n    {operation}()\n"
    if transfer == "return":
        return "def function():\n" + indent(scope, "    ") + "answer = function()\n"
    return "for value in [1]:\n" + indent(scope, "    ") + "answer = 7\n"


@pytest.mark.parametrize("origin", ("body", "handler", "else"))
@pytest.mark.parametrize("transfer", ("return", "break", "continue"))
@pytest.mark.parametrize("operation", ("observe", "reraise"))
def test_pending_transfer_finally_observes_native_active_exception(
    interpreter_mode, origin, transfer, operation,
):
    def configure(bindings):
        def observe():
            active = sys.exception()
            bindings["events"].append(("active", None if active is None else type(active).__name__))

        def reraise():
            observe()
            raise

        bindings.update(observe=observe, reraise=reraise)

    source = _pending_try_source(origin, transfer, operation)
    native_events, native_answer, native_error = _run("native", source, configure)
    events, answer, error = _run(interpreter_mode, source, configure)
    assert type(error) is type(native_error)
    assert _context_chain(error) == _context_chain(native_error)
    assert answer == native_answer
    assert events == native_events
    assert events[-1] == ("active", None)
