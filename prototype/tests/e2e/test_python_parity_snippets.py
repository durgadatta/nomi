import contextlib
import io

import pytest

from prototype.interpreter.python.usage import run_eval_loop


SNIPPETS = [
    "a, b = [1, 2]\nprint(a + b)\n",
    "values = [x * 2 for x in range(4) if x % 2 == 0]\nprint(values)\n",
    "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\nprint(factorial(5))\n",
    "try:\n    1 / 0\nexcept ZeroDivisionError:\n    print('handled')\nfinally:\n    print('cleaned')\n",
    "class Box:\n    def __init__(self, value):\n        self.value = value\nbox = Box(4)\nprint(box.value)\n",
]


def run_custom_stdout(code):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        run_eval_loop(code=code)
    return stdout.getvalue()


def run_python_stdout(code):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(code, "snippet", "exec"), {"__name__": "__main__"})
    return stdout.getvalue()


@pytest.mark.parametrize("code", SNIPPETS)
def test_python_interpreter_matches_cpython_stdout_for_snippets(code):
    assert run_custom_stdout(code) == run_python_stdout(code)
