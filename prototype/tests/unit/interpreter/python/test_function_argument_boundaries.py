"""Call-shape validation for the shared Python-hosted function adapter."""

import ast

import pytest

from prototype.interpreter.nomi.binding_error import BindingError
from prototype.runtime import create_session
from prototype.runtime.modes import get_mode_spec


def _interpreter(mode, **bindings):
    interpreter = get_mode_spec(mode).load_interpreter_class()()
    interpreter.global_env.bindings.update(bindings)
    return interpreter


@pytest.mark.parametrize(
    "parameters, call",
    (
        ("value", "function()"),
        ("value", "function(1, 2)"),
        ("value", "function(1, value=2)"),
        ("value", "function(1, unknown=2)"),
        ("", "function(1)"),
        ("", "function(unknown=2)"),
        ("value, /", "function(value=1)"),
        ("value, /, **extras", "function(value=1)"),
        ("value=1, /", "function(value=2)"),
        ("first=1, second=2, /", "function(second=9)"),
        ("first=1, second=2, /, named=3", "function(second=9)"),
        ("*, value", "function()"),
        ("*, value", "function(1)"),
        ("value, *, option", "function(1, 2)"),
        ("value, *, option", "function(1)"),
        ("value, *rest", "function(1, value=2)"),
        ("value, **extras", "function(1, value=2)"),
        ("value, /, named, *rest, option, **extras", "function(1, named=2)"),
    ),
)
def test_invalid_argument_shape_rejects_before_body(interpreter_mode, parameters, call):
    events = []
    interpreter = _interpreter(interpreter_mode, events=events)
    interpreter.eval(ast.parse(f"def function({parameters}):\n    events.append('body')\n"))
    with pytest.raises(TypeError):
        interpreter.eval(ast.parse(call))
    assert events == []


@pytest.mark.parametrize(
    "parameters, result, call, expected",
    (
        ("value", "value", "function(3)", 3),
        ("value", "value", "function(value=3)", 3),
        ("value=3", "value", "function()", 3),
        ("value=None", "value", "function()", None),
        ("value, /", "value", "function(3)", 3),
        ("value, /, **extras", "(value, extras)", "function(1, value=2)", (1, {"value": 2})),
        ("value=1, /, **extras", "(value, extras)", "function(value=2)", (1, {"value": 2})),
        ("first=1, second=2, /, **extras", "(first, second, extras)", "function(second=9)", (1, 2, {"second": 9})),
        ("first=1, second=2, /, **extras", "(first, second, extras)", "function(3, second=9)", (3, 2, {"second": 9})),
        ("value, *rest, **extras", "(value, rest, extras)", "function(1)", (1, (), {})),
        ("*, value", "value", "function(value=3)", 3),
        ("*, value=3", "value", "function()", 3),
        (
            "first, /, second=2, *rest, option=3, **extras",
            "(first, second, rest, option, extras)",
            "function(1, 4, 5, 6, option=7, unknown=8)",
            (1, 4, (5, 6), 7, {"unknown": 8}),
        ),
        (
            "first, /, second=2, *rest, option=3, **extras",
            "(first, second, rest, option, extras)",
            "function(1, second=4, unknown=8)",
            (1, 4, (), 3, {"unknown": 8}),
        ),
    ),
)
def test_valid_argument_mapping_preserves_formal_kinds(
    interpreter_mode, parameters, result, call, expected,
):
    interpreter = _interpreter(interpreter_mode)
    interpreter.eval(ast.parse(f"def function({parameters}):\n    return {result}\nanswer = {call}\n"))
    assert interpreter.global_env.bindings["answer"] == expected


@pytest.mark.parametrize("call", ("function()", "function(1, 2, 3)", "function(1, unknown=2)", "function(1, value=2)"))
def test_invalid_calls_do_not_evaluate_optional_defaults(interpreter_mode, call):
    events = []
    interpreter = _interpreter(interpreter_mode, mark=lambda: events.append("default"))
    interpreter.eval(ast.parse("def function(value, optional=mark()):\n    return value\n"))
    with pytest.raises(TypeError):
        interpreter.eval(ast.parse(call))
    assert events == []


@pytest.mark.parametrize("parameters, call", (("value", "function()"), ("*, value", "function()"), ("value, /, **extras", "function(value=3)")))
def test_missing_parameters_cannot_fall_back_to_lexical_names(interpreter_mode, parameters, call):
    interpreter = _interpreter(interpreter_mode, value=99)
    interpreter.eval(ast.parse(f"def function({parameters}):\n    return value\n"))
    with pytest.raises(TypeError):
        interpreter.eval(ast.parse(call))
    assert interpreter.global_env.bindings["value"] == 99


def test_defaults_bind_in_declaration_order_in_lexical_frame(interpreter_mode):
    events = []

    def mark(label, value):
        events.append(label)
        return value

    interpreter = _interpreter(interpreter_mode, mark=mark, outer=10)
    interpreter.eval(ast.parse(
        "def function(first=mark('first', outer), second=mark('second', first + 1), "
        "*rest, third=mark('third', second + sum(rest))):\n"
        "    return first, second, rest, third\n"
        "def caller():\n    outer = 100\n    return function()\n"
        "answer = caller()\nouter = 20\nnext_answer = function()\n"
        "explicit = function(1, 2, 3, 4, third=5)\n"
        "variadic = function(1, 2, 3, 4)\n"
    ))
    assert interpreter.global_env.bindings["answer"] == (10, 11, (), 11)
    assert interpreter.global_env.bindings["next_answer"] == (20, 21, (), 21)
    assert interpreter.global_env.bindings["explicit"] == (1, 2, (3, 4), 5)
    assert interpreter.global_env.bindings["variadic"] == (1, 2, (3, 4), 9)
    assert events == ["first", "second", "third", "first", "second", "third", "third"]


def test_positional_only_keyword_collisions_preserve_extra_keyword_order(interpreter_mode):
    interpreter = _interpreter(interpreter_mode)
    interpreter.eval(ast.parse(
        "def function(first=1, second=2, /, *rest, named=3, **extras):\n"
        "    return first, second, list(extras.items())\n"
        "answer = function(before=4, second=9, named=5, rest=6, first=7, extras=8, after=10)\n"
    ))
    assert interpreter.global_env.bindings["answer"] == (
        1, 2, [("before", 4), ("second", 9), ("rest", 6), ("first", 7), ("extras", 8), ("after", 10)],
    )


@pytest.mark.parametrize(
    "declaration, good_call, bad_call, expected",
    (
        ("function = lambda value, *, option=2: value + option\n", "function(3)", "function()", 5),
        ("def function(value, *, option=2):\n    yield value + option\n", "next(function(3))", "function()", 5),
        (
            "class Receiver:\n    def method(self, value, /, *, option=2):\n        return value + option\n"
            "function = Receiver().method\n",
            "function(3)", "function(value=3)", 5,
        ),
        (
            "def decorate(inner):\n    def wrapper(*args, **kwargs):\n        return inner(*args, **kwargs)\n"
            "    return wrapper\n@decorate\ndef function(value, *, option=2):\n    return value + option\n",
            "function(3)", "function()", 5,
        ),
    ),
)
def test_callable_forms_share_the_validation_boundary(
    interpreter_mode, declaration, good_call, bad_call, expected,
):
    interpreter = _interpreter(interpreter_mode)
    interpreter.eval(ast.parse(f"{declaration}answer = {good_call}\n"))
    assert interpreter.global_env.bindings["answer"] == expected
    with pytest.raises(TypeError):
        interpreter.eval(ast.parse(bad_call))


def test_call_shape_validation_precedes_parameter_constraints(nomi_mode):
    events = []

    def positive(value):
        events.append(("constraint", value))
        return value > 0

    interpreter = _interpreter(nomi_mode, positive=positive, events=events)
    interpreter.eval(ast.parse("def function(value: positive, *, required):\n    events.append('body')\n    return value\n"))
    with pytest.raises(TypeError):
        interpreter.eval(ast.parse("function(1)"))
    assert events == []
    interpreter.eval(ast.parse("answer = function(1, required=2)"))
    assert interpreter.global_env.bindings["answer"] == 1
    assert events == [("constraint", 1), "body"]
    with pytest.raises(BindingError):
        interpreter.eval(ast.parse("function(-1, required=2)"))
    assert events == [("constraint", 1), "body", ("constraint", -1)]


def test_parser_to_python_hosted_backend_retains_named_call_boundary(interpreter_mode):
    session = create_session(mode=interpreter_mode, eval_backend="python-ast")
    keyword = "def" if interpreter_mode == "python" else "func"
    session.run(source=f"{keyword} function(value):\n    return value\nanswer = function(value=3)\n")
    assert session.bindings["answer"] == 3
    result = session.run(source="function(3, value=4)\n", raise_on_error=False)
    assert isinstance(result.exception, TypeError)
    assert result.diagnostics
