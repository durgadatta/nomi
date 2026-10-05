"""Legacy context scopes preserve acquisition, binding, and unwind boundaries."""

import ast
import sys
from textwrap import indent

import pytest

from prototype.interpreter.nomi.binding_error import BindingError
from prototype.parser.nomi.desugar import desugar_module
from prototype.runtime.modes import get_mode_spec


def _interpreter(mode, **bindings):
    interpreter = get_mode_spec(mode).load_interpreter_class()()
    interpreter.global_env.bindings.update(bindings)
    return interpreter


def _evaluate(interpreter, mode, source):
    tree = ast.parse(source)
    if mode == "reduced":
        tree = desugar_module(tree)
    return interpreter.eval(ast.fix_missing_locations(tree))


class Manager:
    def __init__(self, name, events, *, value=None, enter_error=None, exit_error=None, suppress=False):
        self.name = name
        self.events = events
        self.value = value
        self.enter_error = enter_error
        self.exit_error = exit_error
        self.suppress = suppress

    def __enter__(self):
        self.events.append((self.name, "enter"))
        if self.enter_error is not None:
            raise self.enter_error
        return self.value

    def __exit__(self, error_type, error, traceback):
        self.events.append((self.name, "exit", None if error_type is None else error_type.__name__))
        if self.exit_error is not None:
            raise self.exit_error
        return self.suppress


def _run_scope_case(mode, source, configure=None):
    events = []
    bindings = {
        "events": events,
        "outer": Manager("outer", events, value=(1, 2)),
        "inner": Manager("inner", events, value=3),
        "SystemExit": SystemExit,
        "KeyboardInterrupt": KeyboardInterrupt,
    }
    if configure is not None:
        configure(bindings)
    error = None
    try:
        if mode == "native":
            exec(source, bindings)
        else:
            interpreter = _interpreter(mode, **bindings)
            _evaluate(interpreter, mode, source)
            bindings = interpreter.global_env.bindings
    except BaseException as exc:
        error = exc
    return events, bindings.get("answer"), error


@pytest.mark.parametrize(
    "source, expected",
    (
        (
            "with outer:\n    events.append('body')\n",
            [("outer", "enter"), "body", ("outer", "exit", None)],
        ),
        (
            "with outer as (first, second), inner as third:\n    answer = first + second + third\n",
            [("outer", "enter"), ("inner", "enter"), ("inner", "exit", None), ("outer", "exit", None)],
        ),
        (
            "holder = {}\nwith inner as holder['value']:\n    answer = holder['value']\n",
            [("inner", "enter"), ("inner", "exit", None)],
        ),
    ),
)
def test_context_acquisition_and_assignment_match_native(interpreter_mode, source, expected):
    native_events, native_answer, native_error = _run_scope_case("native", source)
    events, answer, error = _run_scope_case(interpreter_mode, source)
    assert native_error is None
    assert error is None
    assert events == native_events == expected
    assert answer == native_answer


@pytest.mark.parametrize("failure", ("enter", "expression", "protocol", "binding"))
def test_partial_acquisition_unwinds_only_successfully_entered_managers(interpreter_mode, failure):
    def configure(bindings):
        if failure == "enter":
            bindings["inner"].enter_error = ValueError("enter failed")
        elif failure == "expression":
            def failing_expression():
                bindings["events"].append("expression")
                raise ValueError("expression failed")
            bindings["failing_expression"] = failing_expression
        elif failure == "protocol":
            bindings["inner"] = object()
        else:
            bindings["inner"].value = (3,)

    source = {
        "enter": "with outer, inner:\n    events.append('body')\n",
        "expression": "with outer, failing_expression():\n    events.append('body')\n",
        "protocol": "with outer, inner:\n    events.append('body')\n",
        "binding": "with outer, inner as (first, second):\n    events.append('body')\n",
    }[failure]
    native_events, _, native_error = _run_scope_case("native", source, configure)
    events, _, error = _run_scope_case(interpreter_mode, source, configure)
    assert isinstance(native_error, (ValueError, TypeError))
    assert type(error) is type(native_error)
    assert events == native_events
    assert "body" not in events


@pytest.mark.parametrize(
    "source",
    (
        "def function():\n    with outer, inner:\n        return 7\nanswer = function()\n",
        "for value in [1]:\n    with outer, inner:\n        break\nanswer = 7\n",
        "for value in [1]:\n    with outer, inner:\n        continue\nanswer = 7\n",
    ),
)
def test_control_transfer_releases_lifo_without_an_exception_triplet(interpreter_mode, source):
    native_events, native_answer, native_error = _run_scope_case("native", source)
    events, answer, error = _run_scope_case(interpreter_mode, source)
    assert error is native_error is None
    assert answer == native_answer == 7
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", None), ("outer", "exit", None),
    ]


@pytest.mark.parametrize("exception", ("SystemExit", "KeyboardInterrupt"))
@pytest.mark.parametrize("suppress", (False, True))
def test_real_base_exceptions_unwind_and_obey_legacy_suppression(interpreter_mode, exception, suppress):
    def configure(bindings):
        bindings["inner"].suppress = suppress

    source = f"with outer, inner:\n    raise {exception}('stop')\nanswer = 7\n"
    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert type(error) is type(native_error)
    assert answer == native_answer
    assert events == native_events


def test_inner_suppression_clears_exception_before_outer_cleanup(interpreter_mode):
    def configure(bindings):
        bindings["inner"].suppress = True

    source = "with outer, inner:\n    1 / 0\nanswer = 7\n"
    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert error is native_error is None
    assert answer == native_answer == 7
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", "ZeroDivisionError"), ("outer", "exit", None),
    ]


@pytest.mark.parametrize("body", ("events.append('body')", "1 / 0"))
@pytest.mark.parametrize("outer_failure", (False, True))
def test_cleanup_replacement_attempts_each_release_once(interpreter_mode, body, outer_failure):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("inner close failed")
        if outer_failure:
            bindings["outer"].exit_error = TypeError("outer close failed")

    source = f"with outer, inner:\n    {body}\n"
    native_events, _, native_error = _run_scope_case("native", source, configure)
    events, _, error = _run_scope_case(interpreter_mode, source, configure)
    assert type(error) is type(native_error)
    assert str(error) == str(native_error)
    assert events == native_events
    assert events.count(("outer", "enter")) == 1
    assert events.count(("inner", "enter")) == 1
    assert sum(event[:2] == ("outer", "exit") for event in events if isinstance(event, tuple)) == 1
    assert sum(event[:2] == ("inner", "exit") for event in events if isinstance(event, tuple)) == 1


def test_outer_can_suppress_an_inner_cleanup_failure(interpreter_mode):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("inner close failed")
        bindings["outer"].suppress = True

    source = "with outer, inner:\n    events.append('body')\nanswer = 7\n"
    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert error is native_error is None
    assert answer == native_answer == 7
    assert events == native_events


def test_exit_is_captured_before_enter_and_ignores_instance_shadow(interpreter_mode):
    events = []

    class Captured:
        def __enter__(self):
            events.append("enter")
            self.__exit__ = lambda *args: events.append("instance exit")
            type(self).__exit__ = lambda *args: events.append("new class exit")
            return 7

        def __exit__(self, *args):
            events.append("captured exit")

    manager = Captured()
    manager.__enter__ = lambda: events.append("instance enter")
    interpreter = _interpreter(interpreter_mode, manager=manager, events=events)
    _evaluate(interpreter, interpreter_mode, "with manager as answer:\n    events.append('body')\n")
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == ["enter", "body", "captured exit"]


@pytest.mark.parametrize("descriptor", ("staticmethod", "classmethod", "inherited"))
def test_type_descriptors_are_bound_like_native_special_methods(interpreter_mode, descriptor):
    events = []

    def enter(*args):
        events.append(("enter", len(args)))
        return 7

    def exit_(*args):
        events.append(("exit", len(args), args[-3]))

    class Parent:
        __enter__ = enter
        __exit__ = exit_

    if descriptor == "staticmethod":
        class Context:
            __enter__ = staticmethod(enter)
            __exit__ = staticmethod(exit_)
        expected_counts = (0, 3)
    elif descriptor == "classmethod":
        class Context:
            __enter__ = classmethod(enter)
            __exit__ = classmethod(exit_)
        expected_counts = (1, 4)
    else:
        class Context(Parent):
            pass
        expected_counts = (1, 4)
    interpreter = _interpreter(interpreter_mode, manager=Context(), events=events)
    _evaluate(interpreter, interpreter_mode, "with manager as answer:\n    events.append('body')\n")
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == [("enter", expected_counts[0]), "body", ("exit", expected_counts[1], None)]


def test_instance_only_hooks_do_not_establish_a_context_protocol(interpreter_mode):
    events = []

    class Context:
        pass

    manager = Context()
    manager.__enter__ = lambda: events.append("enter")
    manager.__exit__ = lambda *args: events.append("exit")
    interpreter = _interpreter(interpreter_mode, manager=manager, events=events)
    with pytest.raises(TypeError):
        _evaluate(interpreter, interpreter_mode, "with manager:\n    events.append('body')\n")
    assert events == []


def test_special_method_lookup_bypasses_instance_getattribute(interpreter_mode):
    events = []

    class Context:
        def __getattribute__(self, name):
            if name in ("__enter__", "__exit__"):
                raise AttributeError("instance lookup blocked")
            return object.__getattribute__(self, name)

        def __enter__(self):
            events.append("enter")
            return 7

        def __exit__(self, *args):
            events.append("exit")

    interpreter = _interpreter(interpreter_mode, manager=Context(), events=events)
    _evaluate(interpreter, interpreter_mode, "with manager as answer:\n    events.append('body')\n")
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == ["enter", "body", "exit"]


@pytest.mark.parametrize(
    "declaration, expected",
    (
        (
            "class Context:\n    def __enter__(self, /, value=7):\n        events.append('enter')\n        return value\n"
            "    def __exit__(self, error_type, error, traceback, /):\n        events.append('exit')\n",
            ["enter", "body", "exit"],
        ),
        (
            "class Context:\n    def __enter__(self, *, value=7):\n        events.append('enter')\n        return value\n"
            "    def __exit__(self, error_type, error, traceback, *, flag=5):\n        events.append(('exit', flag))\n",
            ["enter", "body", ("exit", 5)],
        ),
        (
            "def wrap(inner):\n    def wrapper(*args, **kwargs):\n        events.append('wrapper')\n        return inner(*args, **kwargs)\n"
            "    return wrapper\nclass Context:\n    @wrap\n    def __enter__(self):\n        return 7\n"
            "    @wrap\n    def __exit__(self, error_type, error, traceback):\n        events.append('exit')\n",
            ["wrapper", "body", "wrapper", "exit"],
        ),
    ),
)
def test_interpreted_context_methods_use_ordinary_call_binding(interpreter_mode, declaration, expected):
    events = []
    interpreter = _interpreter(interpreter_mode, events=events)
    _evaluate(interpreter, interpreter_mode, f"{declaration}with Context() as answer:\n    events.append('body')\n")
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == expected


@pytest.mark.parametrize("method", ("enter", "exit"))
def test_required_context_method_arguments_reject_before_method_body(interpreter_mode, method):
    events = []
    enter_parameters = "self, *, required" if method == "enter" else "self"
    exit_parameters = "self, error_type, error, traceback, *, required" if method == "exit" else "self, error_type, error, traceback"
    source = (
        f"class Context:\n    def __enter__({enter_parameters}):\n        events.append('enter')\n        return 7\n"
        f"    def __exit__({exit_parameters}):\n        events.append('exit')\n"
        "with Context():\n    events.append('body')\n"
    )
    interpreter = _interpreter(interpreter_mode, events=events)
    with pytest.raises(TypeError):
        _evaluate(interpreter, interpreter_mode, source)
    assert events == ([] if method == "enter" else ["enter", "body"])


def test_context_defaults_observe_lexical_not_caller_scope(interpreter_mode):
    events = []
    source = (
        "def make_context():\n    captured = 7\n    class Context:\n"
        "        def __enter__(self, value=captured):\n            return value\n"
        "        def __exit__(self, error_type, error, traceback):\n            events.append('exit')\n"
        "    return Context()\n"
        "def caller():\n    captured = 99\n    with make_context() as value:\n        return value\n"
        "answer = caller()\n"
    )
    interpreter = _interpreter(interpreter_mode, events=events)
    _evaluate(interpreter, interpreter_mode, source)
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == ["exit"]


def test_acquired_handle_constraint_failure_still_releases(nomi_mode):
    events = []
    interpreter = _interpreter(nomi_mode, manager=Manager("context", events, value=-1))
    interpreter.global_env.set_constraint("handle", lambda value: value > 0)
    with pytest.raises(BindingError):
        _evaluate(interpreter, nomi_mode, "with manager as handle:\n    events.append('body')\n")
    assert events == [("context", "enter"), ("context", "exit", "BindingError")]
    assert "handle" not in interpreter.global_env.bindings


def test_context_method_parameter_constraints_are_not_bypassed(nomi_mode):
    events = []

    def accepted(value):
        events.append(("constraint", value))
        return value > 0

    source = (
        "class Context:\n    def __enter__(self, value: accepted=-1):\n        events.append('enter')\n        return value\n"
        "    def __exit__(self, error_type, error, traceback):\n        events.append('exit')\n"
        "with Context():\n    events.append('body')\n"
    )
    interpreter = _interpreter(nomi_mode, events=events, accepted=accepted)
    with pytest.raises(BindingError):
        _evaluate(interpreter, nomi_mode, source)
    assert events == [("constraint", -1)]


def test_interpreted_context_methods_honor_function_cleanup(nomi_mode):
    events = []
    source = (
        "class Context:\n    func __enter__(self):\n        defer events.append('enter cleanup')\n        return 7\n"
        "    func __exit__(self, error_type, error, traceback):\n        defer events.append('exit cleanup')\n        events.append('exit')\n"
        "with Context() as answer:\n    events.append('body')\n"
    )
    from prototype.parser.nomi.usage import generate_ast

    tree = generate_ast(code=source, dump=False)
    if nomi_mode == "reduced":
        tree = desugar_module(tree)
    interpreter = _interpreter(nomi_mode, events=events)
    interpreter.eval(ast.fix_missing_locations(tree))
    assert interpreter.global_env.bindings["answer"] == 7
    assert events == ["enter cleanup", "body", "exit", "exit cleanup"]


def test_callable_exit_hook_is_not_treated_as_a_second_context_manager(interpreter_mode):
    events = []

    class CallableExit:
        def __call__(self, error_type, error, traceback):
            events.append("resolved exit")

        def __exit__(self, *args):
            events.append("unrelated exit")

    class Context:
        __exit__ = CallableExit()

        def __enter__(self):
            events.append("enter")

    interpreter = _interpreter(interpreter_mode, manager=Context(), events=events)
    _evaluate(interpreter, interpreter_mode, "with manager:\n    events.append('body')\n")
    assert events == ["enter", "body", "resolved exit"]


@pytest.mark.parametrize("name", ("type", "BaseException", "__nomi_context_methods__"))
def test_source_shadowing_does_not_replace_reduced_scope_intrinsics(interpreter_mode, name):
    source = f"{name} = 0\nwith outer:\n    1 / 0\n"
    native_events, _, native_error = _run_scope_case("native", source)
    events, _, error = _run_scope_case(interpreter_mode, source)
    assert isinstance(error, type(native_error))
    assert isinstance(error, ZeroDivisionError)
    assert events == native_events == [("outer", "enter"), ("outer", "exit", "ZeroDivisionError")]


def test_reduced_temporary_does_not_write_a_declared_global(interpreter_mode):
    events = []
    interpreter = _interpreter(
        interpreter_mode, manager=Manager("context", events), _with_manager_1="original",
    )
    _evaluate(
        interpreter, interpreter_mode,
        "def function():\n    global _with_manager_1\n    with manager:\n        pass\nfunction()\n",
    )
    assert interpreter.global_env.bindings["_with_manager_1"] == "original"
    assert events == [("context", "enter"), ("context", "exit", None)]


@pytest.mark.parametrize(
    "subject, pattern, expected",
    (
        ("7", "_with_manager_1", 7),
        ("[1, 2]", "[first, *_with_manager_1]", [2]),
        ("{'a': 1, 'b': 2}", "{'a': first, **_with_manager_1}", {"b": 2}),
    ),
)
def test_reduced_temporaries_preserve_pattern_only_capture_names(interpreter_mode, subject, pattern, expected):
    events = []
    interpreter = _interpreter(interpreter_mode, manager=Manager("context", events))
    _evaluate(
        interpreter, interpreter_mode,
        f"match {subject}:\n    case {pattern}:\n        pass\nwith manager:\n    pass\n",
    )
    assert interpreter.global_env.bindings["_with_manager_1"] == expected
    assert events == [("context", "enter"), ("context", "exit", None)]


def test_simple_generator_suspension_retains_scopes_until_normal_completion(interpreter_mode):
    events = []
    interpreter = _interpreter(
        interpreter_mode, outer=Manager("outer", events), inner=Manager("inner", events), events=events,
    )
    _evaluate(
        interpreter, interpreter_mode,
        "def work():\n    with outer, inner:\n        yield 1\n        events.append('resumed')\n"
        "        yield 2\n    events.append('after scope')\ngenerator = work()\n",
    )
    generator = interpreter.global_env.bindings["generator"]
    assert next(generator) == 1
    assert events == [("outer", "enter"), ("inner", "enter")]
    assert next(generator) == 2
    assert events == [("outer", "enter"), ("inner", "enter"), "resumed"]
    with pytest.raises(StopIteration):
        next(generator)
    assert events == [
        ("outer", "enter"), ("inner", "enter"), "resumed",
        ("inner", "exit", None), ("outer", "exit", None), "after scope",
    ]


def test_failure_in_direct_resumed_body_unwinds_acquired_scopes(interpreter_mode):
    if interpreter_mode == "reduced":
        pytest.skip("Failure in a paused child Try still needs ancestor-frame unwind delivery")
    events = []
    interpreter = _interpreter(
        interpreter_mode, outer=Manager("outer", events), inner=Manager("inner", events), events=events,
    )
    _evaluate(
        interpreter, interpreter_mode,
        "def work():\n    with outer, inner:\n        yield 1\n        raise ValueError('resume failed')\n"
        "    events.append('after scope')\ngenerator = work()\n",
    )
    generator = interpreter.global_env.bindings["generator"]
    assert next(generator) == 1
    assert events == [("outer", "enter"), ("inner", "enter")]
    with pytest.raises(ValueError, match="resume failed"):
        next(generator)
    assert events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", "ValueError"), ("outer", "exit", "ValueError"),
    ]


def test_descriptor_getter_lookup_bypasses_its_type_metaclass(interpreter_mode):
    def run(mode):
        events = []

        class DescriptorMeta(type):
            def __getattribute__(cls, name):
                if name == "__get__":
                    events.append("metaclass lookup")
                    return lambda *args: lambda *info: events.append("spoofed hook")
                return type.__getattribute__(cls, name)

        class Hook(metaclass=DescriptorMeta):
            def __init__(self, name):
                self.name = name

            def __get__(self, instance, owner):
                events.append((self.name, "bind"))

                def bound(*args):
                    events.append((self.name, "call"))

                return bound

        class Context:
            __enter__ = Hook("enter")
            __exit__ = Hook("exit")

        source = "with manager:\n    events.append('body')\n"
        if mode == "native":
            exec(source, {"manager": Context(), "events": events})
        else:
            interpreter = _interpreter(mode, manager=Context(), events=events)
            _evaluate(interpreter, mode, source)
        return events

    assert run(interpreter_mode) == run("native") == [
        ("exit", "bind"), ("enter", "bind"), ("enter", "call"), "body", ("exit", "call"),
    ]


def _error_context_chain(error):
    chain = []
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        chain.append((type(error).__name__, str(error)))
        error = error.__context__
    return chain


@pytest.mark.parametrize(
    "source, earlier_error",
    (
        ("def function():\n    with outer, inner:\n        return 7\nfunction()\n", False),
        ("for value in [1]:\n    with outer, inner:\n        break\n", False),
        ("for value in [1]:\n    with outer, inner:\n        continue\n", False),
        (
            "def function():\n    try:\n        1 / 0\n    except ZeroDivisionError:\n"
            "        with outer, inner:\n            return 7\nfunction()\n",
            True,
        ),
    ),
)
def test_cleanup_failure_keeps_real_context_without_private_control_signals(interpreter_mode, source, earlier_error):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("close failed")

    native_events, _, native_error = _run_scope_case("native", source, configure)
    events, _, error = _run_scope_case(interpreter_mode, source, configure)
    expected_chain = [("ValueError", "close failed")]
    if earlier_error:
        expected_chain.append(("ZeroDivisionError", "division by zero"))
    assert isinstance(error, ValueError)
    assert _error_context_chain(error) == _error_context_chain(native_error) == expected_chain
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", None), ("outer", "exit", "ValueError"),
    ]


@pytest.mark.parametrize(
    "source, expected_answer",
    (
        (
            "def function():\n    with outer, inner:\n        return 7\n"
            "    events.append('after scope')\n    return 8\nanswer = function()\n",
            8,
        ),
        (
            "for value in [1]:\n    with outer, inner:\n        break\n"
            "    events.append('after scope')\nanswer = 8\n",
            8,
        ),
        (
            "for value in [1]:\n    with outer, inner:\n        continue\n"
            "    events.append('after scope')\nanswer = 8\n",
            8,
        ),
    ),
)
def test_suppressed_cleanup_failure_cancels_pending_control_transfer(interpreter_mode, source, expected_answer):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("inner close failed")
        bindings["outer"].suppress = True

    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert error is native_error is None
    assert answer == native_answer == expected_answer
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", None), ("outer", "exit", "ValueError"), "after scope",
    ]


def test_multiple_cleanup_failures_retain_the_earlier_real_error_in_order(interpreter_mode):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("inner close failed")
        bindings["outer"].exit_error = TypeError("outer close failed")

    source = (
        "def function():\n    try:\n        1 / 0\n    except ZeroDivisionError:\n"
        "        with outer, inner:\n            return 7\nfunction()\n"
    )
    native_events, _, native_error = _run_scope_case("native", source, configure)
    events, _, error = _run_scope_case(interpreter_mode, source, configure)
    assert _error_context_chain(error) == _error_context_chain(native_error) == [
        ("TypeError", "outer close failed"), ("ValueError", "inner close failed"),
        ("ZeroDivisionError", "division by zero"),
    ]
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"),
        ("inner", "exit", None), ("outer", "exit", "ValueError"),
    ]


@pytest.mark.parametrize(
    "source",
    (
        "with outer:\n    events.append('body')\nanswer = 7\n",
        "def function():\n    with outer:\n        return 7\nanswer = function()\n",
    ),
)
@pytest.mark.parametrize("raises_on_truth", (False, True))
def test_cleanup_result_is_not_truth_tested_without_an_error(interpreter_mode, source, raises_on_truth):
    def configure(bindings):
        class ExitResult:
            def __bool__(self):
                bindings["events"].append("truth test")
                if raises_on_truth:
                    raise ValueError("cleanup result must not be tested")
                return True

        bindings["outer"].suppress = ExitResult()

    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert error is native_error is None
    assert answer == native_answer == 7
    assert events == native_events
    assert "truth test" not in events


@pytest.mark.parametrize("outer_failure", (False, True))
def test_normal_close_failure_retains_an_enclosing_handled_error(interpreter_mode, outer_failure):
    def configure(bindings):
        bindings["inner"].exit_error = ValueError("inner close failed")
        if outer_failure:
            bindings["outer"].exit_error = TypeError("outer close failed")

    source = (
        "try:\n    1 / 0\nexcept ZeroDivisionError:\n"
        "    with outer, inner:\n        events.append('body')\n"
    )
    native_events, _, native_error = _run_scope_case("native", source, configure)
    events, _, error = _run_scope_case(interpreter_mode, source, configure)
    expected_chain = [("ValueError", "inner close failed"), ("ZeroDivisionError", "division by zero")]
    if outer_failure:
        expected_chain.insert(0, ("TypeError", "outer close failed"))
    assert _error_context_chain(error) == _error_context_chain(native_error) == expected_chain
    assert events == native_events == [
        ("outer", "enter"), ("inner", "enter"), "body",
        ("inner", "exit", None), ("outer", "exit", "ValueError"),
    ]


@pytest.mark.parametrize("transfer", ("return", "break", "continue"))
@pytest.mark.parametrize("earlier_error", (False, True))
@pytest.mark.parametrize("bare_reraise", (False, True))
def test_transfer_cleanup_observes_only_the_native_active_exception(
    interpreter_mode, transfer, earlier_error, bare_reraise,
):
    def configure(bindings):
        class ObservingManager(Manager):
            def __exit__(self, error_type, error, traceback):
                super().__exit__(error_type, error, traceback)
                active = sys.exception()
                self.events.append(("active", None if active is None else type(active).__name__))
                if bare_reraise:
                    raise

        bindings["outer"] = ObservingManager("outer", bindings["events"])

    if transfer == "return":
        source = "def function():\n    with outer:\n        return 7\nanswer = function()\n"
    else:
        source = f"for value in [1]:\n    with outer:\n        {transfer}\nanswer = 7\n"
    if earlier_error:
        source = "try:\n    1 / 0\nexcept ZeroDivisionError:\n" + indent(source, "    ")
    native_events, native_answer, native_error = _run_scope_case("native", source, configure)
    events, answer, error = _run_scope_case(interpreter_mode, source, configure)
    assert type(error) is type(native_error)
    assert _error_context_chain(error) == _error_context_chain(native_error)
    assert answer == native_answer
    assert events == native_events == [
        ("outer", "enter"), ("outer", "exit", None),
        ("active", "ZeroDivisionError" if earlier_error else None),
    ]
