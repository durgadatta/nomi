"""Hosted generators retain child-before-parent ordering across repeated pauses."""

import ast

import pytest

from prototype.runtime.modes import get_mode_spec


def _generator(mode, source, **bindings):
    interpreter = get_mode_spec(mode).load_interpreter_class()()
    interpreter.global_env.bindings.update(bindings)
    interpreter.eval(ast.parse(source))
    return interpreter.global_env.get("work")()


@pytest.mark.parametrize("values", ((10, 20), (None, 0, False), (1, 2, 3, 4)))
def test_sequential_nested_argument_yields_resume_children_before_parent(interpreter_mode, values):
    events = []

    def mark(label, value):
        events.append((label, value))
        return value

    def inner(value):
        events.append(("inner", value))
        return value

    def outer(**values):
        events.append(("outer", values.copy()))
        return values

    arguments = ", ".join(
        f"before_{index}=mark('before_{index}', {index}), value_{index}=inner((yield {index}))"
        for index in range(len(values))
    )
    generator = _generator(
        interpreter_mode,
        f"def work():\n    result = outer({arguments})\n    yield result\n",
        mark=mark, inner=inner, outer=outer,
    )
    assert next(generator) == 0
    for index, value in enumerate(values):
        observed = generator.send(value)
        if index < len(values) - 1:
            assert observed == index + 1
    expected = {}
    expected_events = []
    for index, value in enumerate(values):
        expected[f"before_{index}"] = index
        expected[f"value_{index}"] = value
        expected_events.extend(((f"before_{index}", index), ("inner", value)))
    assert observed == expected
    assert events == expected_events + [("outer", expected)]
    assert generator.paused_frames == []


def test_new_nested_frames_are_inserted_before_existing_ancestors(interpreter_mode):
    events = []

    def leaf(value):
        events.append(("leaf", value))
        return value

    def inner(value):
        events.append(("inner", value))
        return value

    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    result = outer(first=inner(leaf((yield 'one'))), second=inner(leaf((yield 'two'))))\n"
        "    yield result\n",
        leaf=leaf, inner=inner, outer=lambda **values: values,
    )
    assert next(generator) == "one"
    assert generator.send(1) == "two"
    assert generator.send(2) == {"first": 1, "second": 2}
    assert events == [("leaf", 1), ("inner", 1), ("leaf", 2), ("inner", 2)]


def test_next_resumes_nested_argument_yields_with_none(interpreter_mode):
    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    result = outer(first=inner((yield 'one')), second=inner((yield 'two')))\n"
        "    yield result\n",
        inner=lambda value: value, outer=lambda **values: values,
    )
    assert next(generator) == "one"
    assert next(generator) == "two"
    assert next(generator) == {"first": None, "second": None}


def test_yielding_expression_statement_invokes_callee_once_after_resume(interpreter_mode):
    events = []

    def mark(label, value):
        events.append((label, value))
        return value

    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    consume(mark('before', 1), (yield 'ready'), mark('after', 3))\n"
        "    yield 'done'\n",
        mark=mark, consume=lambda *values: events.append(("consume", values)),
    )
    assert next(generator) == "ready"
    assert events == [("before", 1)]
    assert generator.send(None) == "done"
    assert events == [("before", 1), ("after", 3), ("consume", (1, None, 3))]


@pytest.mark.parametrize("value", (7, False, "earlier"))
def test_next_after_a_statement_call_does_not_reuse_its_result(interpreter_mode, value):
    generator = _generator(
        interpreter_mode,
        "def work():\n    marker()\n    result = yield 'ready'\n    yield result\n",
        marker=lambda: value,
    )
    assert next(generator) == "ready"
    assert next(generator) is None


def test_resumed_failure_clears_processing_metadata(interpreter_mode):
    def fail(value):
        raise ValueError("resumed call failed")

    generator = _generator(
        interpreter_mode,
        "def work():\n    result = outer(first=fail((yield 'ready')))\n    yield result\n",
        fail=fail, outer=lambda **values: values,
    )
    assert next(generator) == "ready"
    with pytest.raises(ValueError, match="resumed call failed"):
        generator.send(1)
    assert generator._processing_frame is None
    assert generator._pause_insertion_index == 0


def test_while_body_resumes_assignment_and_each_iteration_once(interpreter_mode):
    events = []

    def mark(label, value):
        events.append((label, value))

    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    index = 0\n"
        "    while index < 3:\n"
        "        mark('before', index)\n"
        "        result = inner((yield index))\n"
        "        mark('after', result)\n"
        "        index += 1\n"
        "    yield 'done'\n",
        mark=mark, inner=lambda value: value,
    )
    assert next(generator) == 0
    assert generator.send(10) == 1
    assert generator.send(20) == 2
    assert generator.send(None) == "done"
    assert events == [
        ("before", 0), ("after", 10),
        ("before", 1), ("after", 20),
        ("before", 2), ("after", None),
    ]


def test_while_body_nested_reyield_preserves_statement_order(interpreter_mode):
    events = []
    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    while True:\n"
        "        mark('before')\n"
        "        result = outer(first=inner((yield 'one')), second=inner((yield 'two')))\n"
        "        mark('after')\n"
        "        break\n"
        "    yield result\n",
        mark=events.append, inner=lambda value: value, outer=lambda **values: values,
    )
    assert next(generator) == "one"
    assert generator.send(1) == "two"
    assert generator.send(2) == {"first": 1, "second": 2}
    assert events == ["before", "after"]


def test_while_resumed_body_retains_continue_and_break(interpreter_mode):
    events = []
    generator = _generator(
        interpreter_mode,
        "def work():\n"
        "    index = 0\n"
        "    while index < 4:\n"
        "        index += 1\n"
        "        command = yield index\n"
        "        if command == 'continue':\n"
        "            continue\n"
        "        if command == 'break':\n"
        "            break\n"
        "        mark(index)\n"
        "    yield 'done'\n",
        mark=events.append,
    )
    assert next(generator) == 1
    assert generator.send("continue") == 2
    assert generator.send("keep") == 3
    assert generator.send("break") == "done"
    assert events == [2]
