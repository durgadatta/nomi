"""Independent source/protocol boundaries for the hosted continuation adapter."""

import ast
import sys
import warnings

import pytest

from prototype.runtime.modes import get_mode_spec
from prototype.tests.unit.interpreter.python.test_generator_completion_ownership import make_generator


@pytest.mark.parametrize("definition", (
    "    def inner(value=(yield 'header')):\n        pass\n",
    "    @decorate((yield 'header'))\n    def inner():\n        pass\n",
    "    class Inner((yield 'header')):\n        pass\n",
    "    class Inner(metaclass=(yield 'header')):\n        pass\n",
    "    inner = lambda value=(yield 'header'): value\n",
))
def test_definition_header_only_suspension_is_fenced_before_body_effects(
    interpreter_mode, definition,
):
    interpreter = get_mode_spec(interpreter_mode).load_interpreter_class()()
    events = []
    interpreter.global_env.bindings.update(events=events, decorate=lambda value: lambda func: func)
    interpreter.eval(ast.parse("def work():\n    events.append('body')\n" + definition))
    generator = interpreter.global_env.get("work")()
    assert events == []
    with pytest.raises(NotImplementedError, match="Hosted generator suspension through"):
        next(generator)
    assert events == []
    generator.close()


def test_nested_generator_bodies_do_not_change_enclosing_function_convention(interpreter_mode):
    interpreter = get_mode_spec(interpreter_mode).load_interpreter_class()()
    interpreter.eval(ast.parse(
        "def work():\n"
        "    def inner():\n        yield 'inner'\n"
        "    maker = lambda: (yield 'lambda')\n"
        "    class Holder:\n        def inner(self):\n            yield 'method'\n"
        "    return 7\n"
    ))
    assert interpreter.global_env.get("work")() == 7


@pytest.mark.parametrize("kind", (StopIteration, GeneratorExit))
@pytest.mark.parametrize("operation", (
    "        fail((yield 'ready'))\n",
    "        result = (yield 'ready') + operand\n",
    "        if (yield 'ready'):\n            pass\n",
    "        while (yield 'ready'):\n            break\n",
    "        target.value = (yield 'ready')\n",
    "        fail(*(yield 'ready'))\n",
    "        for value in (yield 'ready'):\n            pass\n",
    "        yield from (yield 'ready')\n",
))
def test_suspended_source_operations_deliver_actual_protocol_error_to_handler(
    interpreter_mode, operation, kind,
):
    for mode in ("native", interpreter_mode):
        error = kind("source operation")
        events = []

        class Operand:
            def __add__(self, other):
                raise error

            def __bool__(self):
                raise error

            def __iter__(self):
                raise error

            def __setattr__(self, name, value):
                raise error

        def fail(*args):
            raise error

        def observe(caught):
            events.append((caught is error, sys.exception() is error, error.__context__))

        operand = Operand()
        generator = make_generator(
            mode, "def work():\n    try:\n" + operation
            + "    except problem_kind as caught:\n        observe(caught)\n        yield 'caught'\n",
            fail=fail, operand=operand, target=operand, observe=observe, problem_kind=kind,
        )
        assert next(generator) == "ready"
        assert generator.send(operand) == "caught"
        assert events == [(True, True, None)]
        generator.close()


def test_handler_failure_restores_actual_error_for_finally(interpreter_mode):
    for mode in ("native", interpreter_mode):
        initial = ValueError("injected")
        error = StopIteration("handler")
        events = []

        def fail():
            raise error

        def observe():
            events.append((sys.exception() is error, error.__context__ is initial))

        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield 'ready'\n"
            "    except ValueError:\n        fail()\n    finally:\n        observe()\n",
            fail=fail, observe=observe,
        )
        assert next(generator) == "ready"
        with pytest.raises(RuntimeError, match="generator raised StopIteration") as caught:
            generator.throw(initial)
        assert caught.value.__cause__ is error
        assert events == [(True, True)]
        generator.close()


def test_ordinary_overloaded_operator_preserves_stop_iteration(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("operator")
        events = []

        class Operand:
            def __add__(self, other):
                raise error

        def observe(caught):
            events.append((caught is error, sys.exception() is error, error.__context__))

        source = (
            "try:\n    operand + operand\n"
            "except StopIteration as caught:\n    observe(caught)\n"
        )
        bindings = {"operand": Operand(), "observe": observe}
        if mode == "native":
            exec(source, bindings)
        else:
            interpreter = get_mode_spec(mode).load_interpreter_class()()
            interpreter.global_env.bindings.update(bindings)
            interpreter.eval(ast.parse(source))
        assert events == [(True, True, None)]


def test_ordinary_unary_operator_preserves_stop_iteration_after_suspension(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("unary")

        class Operand:
            def __pos__(self):
                raise error

        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield 'ready'\n        +operand\n"
            "    except StopIteration:\n        yield 'correct'\n"
            "    except TypeError:\n        yield 'wrong'\n",
            operand=Operand(),
        )
        assert next(generator) == "ready"
        assert next(generator) == "correct"
        generator.close()


@pytest.mark.parametrize("kind", (StopIteration, GeneratorExit, ValueError, TypeError))
@pytest.mark.parametrize("prior_context", (False, True))
def test_injected_protocol_error_updates_actual_source_exception_context(
    interpreter_mode, kind, prior_context,
):
    for mode in ("native", interpreter_mode):
        initial = ValueError("initial")
        injected = kind("injected")
        cause = LookupError("explicit cause")
        observations = []
        injected.__cause__ = cause
        if prior_context:
            injected.__context__ = LookupError("previous context")

        def observe():
            observations.append((sys.exception() is injected, injected.__context__ is initial))

        generator = make_generator(
            mode, "def work():\n    try:\n        raise initial\n"
            "    except ValueError:\n        try:\n            yield 'ready'\n"
            "        finally:\n            observe()\n", initial=initial, observe=observe,
        )
        assert next(generator) == "ready"
        expected_kind = RuntimeError if kind is StopIteration else kind
        with pytest.raises(expected_kind) as caught:
            generator.throw(injected)
        if kind is StopIteration:
            assert caught.value.__cause__ is injected
        else:
            assert caught.value is injected
        assert injected.__context__ is initial
        assert injected.__cause__ is cause
        assert injected.__suppress_context__
        assert observations == [(True, True)]
        generator.close()


@pytest.mark.parametrize("kind", (StopIteration, ValueError, GeneratorExit))
def test_delegated_throw_lookup_failure_keeps_source_suspended(interpreter_mode, kind):
    for mode in ("native", interpreter_mode):
        error = kind("lookup")
        events = []

        class Delegate:
            fail_lookup = True
            count = 0

            def __iter__(self):
                return self

            def __next__(self):
                self.count += 1
                return self.count

            @property
            def throw(self):
                if self.fail_lookup:
                    raise error
                return lambda injected: "delegated"

            def close(self):
                events.append("close")

        delegate = Delegate()
        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield from delegate\n"
            "    except GeneratorExit:\n        return\n"
            "    except BaseException:\n        events.append('source handler')\n        yield 'wrong'\n"
            "    finally:\n        events.append('finally')\n",
            delegate=delegate, events=events,
        )
        assert next(generator) == 1
        with pytest.raises(kind) as caught:
            generator.throw(ValueError("injected"))
        assert caught.value is error
        assert error.__context__ is None
        assert events == []
        assert next(generator) == 2
        delegate.fail_lookup = False
        assert generator.throw(ValueError("second")) == "delegated"
        generator.close()
        assert events == ["close", "finally"]


def test_cleanup_failure_keeps_original_source_error_in_its_context(interpreter_mode):
    for mode in ("native", interpreter_mode):
        original = StopIteration("body")
        replacement = ValueError("cleanup")
        events = []

        class Manager:
            def __enter__(self):
                pass

            def __exit__(self, kind, error, traceback):
                events.append((kind is StopIteration, error is original, sys.exception() is original))
                raise replacement

        def fail():
            raise original

        generator = make_generator(
            mode, "def work():\n    with manager:\n        yield 'ready'\n        fail()\n",
            manager=Manager(), fail=fail,
        )
        assert next(generator) == "ready"
        with pytest.raises(ValueError) as caught:
            next(generator)
        assert caught.value is replacement
        assert replacement.__context__ is original
        assert original.__context__ is None
        assert events == [(True, True, True)]
        generator.close()


@pytest.mark.parametrize("suspension", ("inside", "before", "none"))
def test_inner_suppression_clears_actual_error_before_outer_cleanup(interpreter_mode, suspension):
    for mode in ("native", interpreter_mode):
        error = StopIteration("body")
        events = []

        class Manager:
            def __init__(self, label, suppress):
                self.label = label
                self.suppress = suppress

            def __enter__(self):
                pass

            def __exit__(self, kind, caught, traceback):
                events.append((self.label, kind, caught, sys.exception()))
                return self.suppress

        def fail():
            raise error

        source = "def work():\n"
        if suspension == "before":
            source += "    yield 'ready'\n"
        source += "    with outer, inner:\n"
        if suspension == "inside":
            source += "        yield 'ready'\n"
        source += "        fail()\n"
        source += "    return 'done'\n" if suspension == "none" else "    yield 'done'\n"
        result = make_generator(
            mode, source,
            outer=Manager("outer", False), inner=Manager("inner", True), fail=fail,
        )
        if suspension == "none":
            assert result == "done"
        else:
            assert next(result) == "ready"
            assert next(result) == "done"
            result.close()
        assert events == [("inner", StopIteration, error, error), ("outer", None, None, None)]


def test_delegated_native_generator_failure_is_not_unwrapped(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("child source")

        def child():
            yield "ready"
            raise error

        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield from child()\n"
            "    except StopIteration:\n        yield 'wrong'\n"
            "    except RuntimeError:\n        yield 'correct'\n",
            child=child,
        )
        assert next(generator) == "ready"
        assert next(generator) == "correct"
        generator.close()


def test_thrown_stop_iteration_reaches_delegated_native_handler(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("delegated injection")
        events = []

        def child():
            try:
                yield "ready"
            except StopIteration as caught:
                events.append((caught is error, sys.exception() is error, error.__context__))
                yield "caught"
            return 19

        generator = make_generator(
            mode, "def work():\n    result = yield from child()\n    yield result\n", child=child,
        )
        assert next(generator) == "ready"
        assert generator.throw(error) == "caught"
        assert events == [(True, True, None)]
        assert next(generator) == 19
        generator.close()


def test_source_call_keyword_names_are_not_consumed_by_transport(interpreter_mode):
    for mode in ("native", interpreter_mode):
        generator = make_generator(
            mode,
            "def work():\n    result = echo(operation=(yield 'ready'), args=2, kwargs=3)\n"
            "    yield result\n",
            echo=lambda **values: values,
        )
        assert next(generator) == "ready"
        assert generator.send(1) == {"operation": 1, "args": 2, "kwargs": 3}
        generator.close()


@pytest.mark.parametrize("kind", (StopIteration, GeneratorExit))
def test_throw_class_and_value_preserves_instance_and_constructor_arguments(interpreter_mode, kind):
    for mode in ("native", interpreter_mode):
        events = []
        original = kind("supplied")

        def observe(caught):
            events.append((caught, caught.args, sys.exception() is caught))

        source = (
            "def work():\n    try:\n        yield 'ready'\n"
            "    except BaseException as caught:\n        observe(caught)\n        yield 'caught'\n"
        )
        for value in (original, ("one", "two"), None):
            generator = make_generator(mode, source, observe=observe)
            assert next(generator) == "ready"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                assert generator.throw(kind, value) == "caught"
            observed, arguments, active = events[-1]
            assert active
            if value is original:
                assert observed is original
            elif value is None:
                assert arguments == ()
            else:
                assert arguments == ("one", "two")
            generator.close()


@pytest.mark.parametrize("kind", (StopIteration, GeneratorExit))
def test_invalid_throw_traceback_does_not_construct_error_or_resume_source(interpreter_mode, kind):
    for mode in ("native", interpreter_mode):
        events = []

        class Error(kind):
            def __init__(self, *args):
                events.append(args)
                super().__init__(*args)

        generator = make_generator(mode, "def work():\n    yield 'ready'\n    yield 'done'\n")
        assert next(generator) == "ready"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            with pytest.raises(TypeError):
                generator.throw(Error, "value", 123)
        assert events == []
        assert next(generator) == "done"
        generator.close()


@pytest.mark.parametrize("operation", ("close", "throw"))
@pytest.mark.parametrize("kind", (StopIteration, ValueError, GeneratorExit))
def test_delegated_close_lookup_failure_is_reported_without_source_delivery(
    interpreter_mode, operation, kind, monkeypatch,
):
    for mode in ("native", interpreter_mode):
        error = kind("close lookup")
        injected = GeneratorExit("injected")
        records = []
        events = []
        monkeypatch.setattr(sys, "unraisablehook", records.append)

        class Delegate:
            def __iter__(self):
                return self

            def __next__(self):
                return "ready"

            @property
            def close(self):
                raise error

        generator = make_generator(
            mode,
            "def work():\n    try:\n        yield from delegate\n"
            "    except (StopIteration, ValueError):\n        events.append('handler')\n        yield 'wrong'\n"
            "    finally:\n        events.append('finally')\n",
            delegate=Delegate(), events=events,
        )
        assert next(generator) == "ready"
        if operation == "close":
            assert generator.close() is None
        else:
            with pytest.raises(GeneratorExit) as caught:
                generator.throw(injected)
            assert caught.value is injected
        assert events == ["finally"]
        assert len(records) == 1
        assert records[0].exc_type is kind
        assert records[0].exc_value is error
        assert records[0].exc_traceback is not None
        assert records[0].err_msg.startswith("Exception ignored while closing generator ")
        assert records[0].object is None
        assert error.__context__ is None
        generator.close()
        assert len(records) == 1


def test_delegated_close_lookup_failure_has_safe_default_stderr_report(interpreter_mode, monkeypatch, capsys):
    events = []

    class Delegate:
        def __iter__(self):
            return self

        def __next__(self):
            return "ready"

        @property
        def close(self):
            raise ValueError("close lookup")

    monkeypatch.setattr(sys, "unraisablehook", sys.__unraisablehook__)
    generator = make_generator(
        interpreter_mode,
        "def work():\n    try:\n        yield from delegate\n"
        "    finally:\n        events.append('finally')\n",
        delegate=Delegate(), events=events,
    )
    assert next(generator) == "ready"
    assert generator.close() is None
    assert events == ["finally"]
    stderr = capsys.readouterr().err
    assert "Exception ignored while closing generator " in stderr
    assert "ValueError: close lookup" in stderr
    generator.close()
