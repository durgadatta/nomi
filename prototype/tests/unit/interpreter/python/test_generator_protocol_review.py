"""Protocol edges reviewed separately from the continuation implementation."""

import gc

import pytest

from prototype.tests.unit.interpreter.python.test_generator_completion_ownership import make_generator


def test_throw_generator_exit_into_closed_generator_preserves_exception(interpreter_mode):
    for mode in ("native", interpreter_mode):
        generator = make_generator(mode, "def work():\n    yield 1\n")
        generator.close()
        error = GeneratorExit("closed")
        with pytest.raises(GeneratorExit) as caught:
            generator.throw(error)
        assert caught.value is error


def test_throw_generator_exit_can_yield_cleanup_then_preserve_completion(interpreter_mode):
    for mode in ("native", interpreter_mode):
        generator = make_generator(mode, "def work():\n    try:\n        yield 1\n    finally:\n        yield 2\n")
        assert next(generator) == 1
        error = GeneratorExit("injected")
        assert generator.throw(error) == 2
        with pytest.raises(GeneratorExit) as caught:
            next(generator)
        assert caught.value is error


def test_collected_generator_cleanup_uses_its_own_local_environment(interpreter_mode):
    for mode in ("native", interpreter_mode):
        events = []
        generator = make_generator(
            mode,
            "def work():\n    local = events\n    try:\n        yield 1\n"
            "    finally:\n        local.append('closed')\n",
            events=events,
        )
        assert next(generator) == 1
        del generator
        gc.collect()
        assert events == ["closed"]


def test_stop_iteration_reaches_source_handler_before_generator_boundary(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("source")
        events = []

        def fail():
            raise error

        def observe(caught):
            import sys
            events.append((caught is error, sys.exception() is error))

        generator = make_generator(mode,
            "def work():\n    try:\n        yield 'ready'\n        fail()\n"
            "    except StopIteration as caught:\n        observe(caught)\n        yield 'caught'\n",
            fail=fail, observe=observe)
        assert next(generator) == "ready"
        assert next(generator) == "caught"
        assert events == [(True, True)]
        generator.close()


def test_thrown_stop_iteration_reaches_source_handler(interpreter_mode):
    for mode in ("native", interpreter_mode):
        generator = make_generator(mode,
            "def work():\n    try:\n        yield 'ready'\n"
            "    except StopIteration:\n        yield 'caught'\n")
        assert next(generator) == "ready"
        assert generator.throw(StopIteration("injected")) == "caught"
        generator.close()


def test_stop_iteration_cleanup_sees_actual_error_and_can_suppress(interpreter_mode):
    import sys
    for mode in ("native", interpreter_mode):
        error = StopIteration("source")
        events = []

        class Manager:
            def __enter__(self):
                pass

            def __exit__(self, kind, caught, traceback):
                events.append((kind is StopIteration, caught is error, sys.exception() is error))
                return True

        def fail():
            raise error

        generator = make_generator(mode,
            "def work():\n    with manager:\n        yield 'ready'\n        fail()\n"
            "    yield 'done'\n", manager=Manager(), fail=fail)
        assert next(generator) == "ready"
        assert next(generator) == "done"
        assert events == [(True, True, True)]
        generator.close()


def test_unhandled_stop_iteration_converts_only_at_public_generator_boundary(interpreter_mode):
    for mode in ("native", interpreter_mode):
        error = StopIteration("source")
        def fail():
            raise error
        generator = make_generator(mode,
            "def work():\n    yield 'ready'\n    fail()\n", fail=fail)
        assert next(generator) == "ready"
        with pytest.raises(RuntimeError, match="generator raised StopIteration") as caught:
            next(generator)
        assert caught.value.__cause__ is error
        assert error.__context__ is None


def test_explicit_runtime_error_from_stop_iteration_is_not_unwrapped(interpreter_mode):
    for mode in ("native", interpreter_mode):
        def fail():
            raise RuntimeError("generator raised StopIteration") from StopIteration("cause")
        generator = make_generator(mode,
            "def work():\n    try:\n        yield 'ready'\n        fail()\n"
            "    except StopIteration:\n        yield 'wrong'\n"
            "    except RuntimeError:\n        yield 'correct'\n", fail=fail)
        assert next(generator) == "ready"
        assert next(generator) == "correct"
        generator.close()


def test_generator_exit_subclass_class_can_reach_handler(interpreter_mode):
    class ExitChild(GeneratorExit):
        pass
    for mode in ("native", interpreter_mode):
        generator = make_generator(mode,
            "def work():\n    try:\n        yield 'ready'\n"
            "    except GeneratorExit:\n        yield 'handled'\n")
        assert next(generator) == "ready"
        assert generator.throw(ExitChild) == "handled"
        generator.close()


@pytest.mark.parametrize("definition", (
    "    def inner(value=(yield 'ready')):\n        pass\n",
    "    @decorate((yield 'ready'))\n    def inner():\n        pass\n",
    "    class Inner((yield 'ready')):\n        pass\n",
    "    inner = lambda value=(yield 'ready'): value\n",
))
def test_definition_time_suspension_is_fenced_before_body_effects(interpreter_mode, definition):
    # Inspect direct ASTs: reduced lowering may separately admit decorators.
    import ast
    from prototype.runtime.modes import get_mode_spec
    interpreter = get_mode_spec(interpreter_mode).load_interpreter_class()()
    events = []
    interpreter.global_env.bindings.update(events=events, decorate=lambda value: lambda func: func)
    interpreter.eval(ast.parse("def work():\n    events.append('body')\n" + definition + "    yield 'done'\n"))
    generator = interpreter.global_env.get("work")()
    with pytest.raises(NotImplementedError, match="Hosted generator suspension through"):
        next(generator)
    assert events == []
