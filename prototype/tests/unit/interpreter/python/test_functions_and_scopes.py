import pytest

from prototype.interpreter.python.usage import run_eval_loop


def test_function_uses_positional_default_varargs_keywords_and_kwargs():
    bindings = run_eval_loop(
        code=(
            "def combine(a, b=2, *args, scale=1, **kwargs):\n"
            "    return (a + b + sum(args) + kwargs['extra']) * scale\n"
            "result = combine(1, 3, 4, scale=2, extra=5)\n"
        )
    )
    assert bindings["result"] == 26


def test_function_can_call_another_function():
    bindings = run_eval_loop(
        code=(
            "def double(x):\n"
            "    return x * 2\n"
            "def apply(value):\n"
            "    return double(value) + 1\n"
            "result = apply(4)\n"
        )
    )
    assert bindings["result"] == 9


def test_recursive_function_can_reference_itself():
    bindings = run_eval_loop(
        code=(
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
            "result = factorial(5)\n"
        )
    )
    assert bindings["result"] == 120


def test_global_declaration_updates_global_binding():
    bindings = run_eval_loop(
        code=(
            "counter = 0\n"
            "def bump():\n"
            "    global counter\n"
            "    counter += 1\n"
            "bump()\n"
            "bump()\n"
        )
    )
    assert bindings["counter"] == 2


def test_nonlocal_declaration_updates_enclosing_binding():
    bindings = run_eval_loop(
        code=(
            "def outer():\n"
            "    value = 1\n"
            "    def inner():\n"
            "        nonlocal value\n"
            "        value += 4\n"
            "    inner()\n"
            "    return value\n"
            "result = outer()\n"
        )
    )
    assert bindings["result"] == 5
