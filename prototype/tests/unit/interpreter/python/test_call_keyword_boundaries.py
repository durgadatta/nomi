"""Python-hosted call construction rejects ambiguity before invoking a callee."""

import ast

import pytest

from prototype.runtime.modes import get_mode_spec


def _interpreter(mode, **bindings):
    interpreter = get_mode_spec(mode).load_interpreter_class()()
    interpreter.global_env.bindings.update(bindings)
    return interpreter


@pytest.mark.parametrize(
    "call",
    (
        "callee(value=1, **{'value': 2}, later=mark())",
        "callee(**{'value': 1}, value=2, later=mark())",
        "callee(**{'value': 1}, **{'value': 2}, later=mark())",
        "callee(value=1, value=2, later=mark())",
    ),
)
def test_duplicate_keywords_fail_before_callee_or_later_arguments(interpreter_mode, call):
    events = []
    interpreter = _interpreter(
        interpreter_mode,
        callee=lambda **kwargs: events.append("called"),
        mark=lambda: events.append("later"),
    )
    with pytest.raises(TypeError, match="multiple values for keyword argument 'value'"):
        interpreter.eval(ast.parse(call))
    assert events == []


class KeywordMapping:
    def __init__(self, values, events):
        self.values = values
        self.events = events

    def keys(self):
        self.events.append("keys")
        return self.values.keys()

    def __getitem__(self, key):
        self.events.append(("get", key))
        return self.values[key]


def test_keyword_unpacking_accepts_mapping_protocol_once(interpreter_mode):
    events = []
    interpreter = _interpreter(
        interpreter_mode,
        values=KeywordMapping({"first": 1, "second": 2}, events),
        callee=lambda **kwargs: kwargs,
    )
    interpreter.eval(ast.parse("result = callee(**values, third=3)"))
    assert interpreter.global_env.bindings["result"] == {"first": 1, "second": 2, "third": 3}
    assert events == ["keys", ("get", "first"), ("get", "second")]


def test_duplicate_mapping_key_is_not_fetched(interpreter_mode):
    events = []
    interpreter = _interpreter(
        interpreter_mode,
        values=KeywordMapping({"value": 2}, events),
        callee=lambda **kwargs: events.append("called"),
    )
    with pytest.raises(TypeError, match="multiple values for keyword argument 'value'"):
        interpreter.eval(ast.parse("callee(value=1, **values)"))
    assert events == ["keys"]


@pytest.mark.parametrize("value", ({1: 2}, {None: 2}, {(1,): 2}))
def test_keyword_unpacking_rejects_non_text_keys_before_invocation(interpreter_mode, value):
    events = []
    interpreter = _interpreter(
        interpreter_mode,
        values=value,
        callee=lambda **kwargs: events.append("called"),
    )
    with pytest.raises(TypeError, match="keywords must be strings"):
        interpreter.eval(ast.parse("callee(**values)"))
    assert events == []


@pytest.mark.parametrize("value", ([], [("value", 1)], 3, None))
def test_keyword_unpacking_rejects_non_mappings(interpreter_mode, value):
    interpreter = _interpreter(interpreter_mode, values=value, callee=lambda **kwargs: kwargs)
    with pytest.raises(TypeError, match=r"argument after \*\* must be a mapping"):
        interpreter.eval(ast.parse("callee(**values)"))


def test_mapping_key_failure_is_not_reclassified(interpreter_mode):
    class BrokenMapping:
        def keys(self):
            raise ValueError("mapping keys failed")

    interpreter = _interpreter(interpreter_mode, values=BrokenMapping(), callee=lambda **kwargs: kwargs)
    with pytest.raises(ValueError, match="mapping keys failed"):
        interpreter.eval(ast.parse("callee(**values)"))


def test_keyword_unpacking_accepts_text_subclasses(interpreter_mode):
    class Text(str):
        pass

    interpreter = _interpreter(
        interpreter_mode,
        values={Text("value"): 7},
        callee=lambda **kwargs: kwargs,
    )
    interpreter.eval(ast.parse("result = callee(**values)"))
    assert interpreter.global_env.bindings["result"] == {"value": 7}


def _prepare_generator(mode, call):
    events = []

    def mark(label, value):
        events.append(label)
        return value

    def callee(*args, **kwargs):
        events.append("called")
        return args, kwargs

    interpreter = _interpreter(mode, callee=callee, mark=mark)
    interpreter.eval(ast.parse(f"def work():\n    result = {call}\n    yield result\ngenerator = work()\n"))
    return interpreter.global_env.bindings["generator"], events


def test_keyword_yield_retains_previous_values_and_accepts_sent_none(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), second=(yield 'ready'), third=mark('third', 3))",
    )
    assert next(generator) == "ready"
    assert generator.send(None) == ((), {"first": 1, "second": None, "third": 3})
    assert events == ["first", "third", "called"]


def test_next_resumes_keyword_yield_with_none_not_an_earlier_call_result(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), second=(yield 'ready'))",
    )
    assert next(generator) == "ready"
    assert next(generator) == ((), {"first": 1, "second": None})
    assert events == ["first", "called"]


def test_nested_keyword_call_retains_its_completed_value_on_resume(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), second=callee(inner=(yield 'ready')))"
    )
    assert next(generator) == "ready"
    assert generator.send(2) == ((), {"first": 1, "second": ((), {"inner": 2})})
    assert events == ["first", "called", "called"]


def test_multiple_keyword_yields_do_not_reevaluate_previous_arguments(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), second=(yield 'two'), third=mark('third', 3), "
        "fourth=(yield 'four'), fifth=mark('fifth', 5))",
    )
    assert next(generator) == "two"
    assert generator.send(2) == "four"
    assert generator.send(4) == ((), {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5})
    assert events == ["first", "third", "fifth", "called"]


def test_starred_positional_yield_expands_the_sent_iterable(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(mark('first', 1), *(yield 'rest'), last=mark('last', 4))",
    )
    assert next(generator) == "rest"
    assert generator.send((2, 3)) == ((1, 2, 3), {"last": 4})
    assert events == ["first", "last", "called"]


def test_unpacked_keyword_yield_merges_the_sent_mapping(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), **(yield 'mapping'), third=mark('third', 3))",
    )
    assert next(generator) == "mapping"
    assert generator.send({"second": 2}) == ((), {"first": 1, "second": 2, "third": 3})
    assert events == ["first", "third", "called"]


def test_duplicate_after_keyword_yield_still_stops_invocation(interpreter_mode):
    generator, events = _prepare_generator(
        interpreter_mode,
        "callee(first=mark('first', 1), **(yield 'mapping'), third=mark('third', 3))",
    )
    assert next(generator) == "mapping"
    with pytest.raises(TypeError, match="multiple values for keyword argument 'first'"):
        generator.send({"first": 2})
    assert events == ["first"]
