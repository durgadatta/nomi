"""Runtime tests for type alias declarations."""

from prototype.interpreter.helpers import get_run_eval_loop


def test_type_alias_basic(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="type UserId = str\n")
    assert bindings["UserId"] == str


def test_type_alias_multiple(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="type Age = int\ntype Name = str\nresult = Name('hello') + ' ' + str(Age(42))\n")
    assert bindings["result"] == "hello 42"
