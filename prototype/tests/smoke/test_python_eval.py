import pytest

from prototype.interpreter.python.usage import run_eval_loop

pytestmark = pytest.mark.smoke


def test_python_eval_smoke_executes_tiny_program():
    bindings = run_eval_loop(code="def add(a, b=1):\n    return a + b\nresult = add(4)\n")
    assert bindings["result"] == 5
