import pytest

from prototype.interpreter.nomi import run_eval_loop

pytestmark = pytest.mark.smoke


def test_nomi_eval_smoke_executes_tiny_program():
    bindings = run_eval_loop(code="func add(a, b):\n    return a + b\nresult = add(2, 3)\n")
    assert bindings["result"] == 5
